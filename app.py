import streamlit as st
import pandas as pd
from datetime import datetime

# Page setting aur styling
st.set_page_config(page_title="Chiller Khata", page_icon="🥛", layout="wide")
st.title("🥛 Papa Milk Chiller Management System")
st.markdown("---")

# Data ko temporary store karne ke liye (Real app me yeh database me jayega)
if 'persons' not in st.session_state:
    st.session_state.persons = pd.DataFrame(columns=["ID", "Name", "Type", "Milk_Type"])
if 'records' not in st.session_state:
    st.session_state.records = pd.DataFrame(columns=["Date", "Shift", "Name", "Type", "Liters", "Fat", "Temp", "Rate", "Total", "Paid", "Remaining"])

# ================= SIDEBAR: RATE CUSTOMIZATION =================
st.sidebar.header("⚙️ Rate & Quality Settings")
base_rate_bhains = st.sidebar.number_input("Bhains Milk Base Rate (6.0% Fat)", value=180)
base_rate_gaaye = st.sidebar.number_input("Gaaye Milk Base Rate (4.0% Fat)", value=140)
fat_bonus = st.sidebar.number_input("Bonus/Deduction per 0.1% Fat", value=2.0)

# ================= TAB 1: LOGO AUR NAYE LOG ADD KARNA =================
tab1, tab2, tab3 = st.tabs(["👥 Naya Khata (Add People)", "📝 Daily Entry (Doodh/Hisaab)", "🖨️ Report & Print"])

with tab1:
    st.subheader("Naye Client ya Customer ka Naam Register Karein")
    with st.form("add_person_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            p_name = st.text_input("Bande Ka Name")
        with col2:
            p_type = st.selectbox("Type", ["Client (Jis se doodh lete hain)", "Customer (Jise doodh bechte hain)"])
        with col3:
            p_milk = st.selectbox("Doodh ki Qism", ["Bhains", "Gaaye"])
        
        submit_p = st.form_submit_button("Khata Me Add Karein")
        
        if submit_p and p_name:
            new_id = f"ID-{len(st.session_state.persons) + 101}"
            new_person = pd.DataFrame([[new_id, p_name, p_type, p_milk]], columns=["ID", "Name", "Type", "Milk_Type"])
            st.session_state.persons = pd.concat([st.session_state.persons, new_person], ignore_index=True)
            st.success(f"✅ {p_name} ko kamyabi se register kar liya gaya hai!")

    # Registered Logon ki list
    if not st.session_state.persons.empty:
        st.write("### 📋 Mojooda Khata List:")
        st.dataframe(st.session_state.persons, use_container_width=True)

# ================= TAB 2: DAILY ENTRY LOGIC =================
with tab2:
    st.subheader("Subah / Shaam Ki Entry Aur Len-Den")
    if st.session_state.persons.empty:
        st.warning("⚠️ Pehle Tab 1 me ja kar kuch logon ke naam add karein!")
    else:
        with st.form("daily_entry_form"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                e_date = st.date_input("Tareekh Select Karein", datetime.now())
                e_shift = st.selectbox("Shift", ["Subah (Morning)", "Shaam (Evening)"])
            with c2:
                e_name = st.selectbox("Banda Select Karein", st.session_state.persons["Name"].tolist())
                e_liters = st.number_input("Total Doodh (Liters)", min_value=0.0, step=0.5)
            with c3:
                e_fat = st.number_input("Fat %", min_value=0.0, max_value=12.0, value=6.0, step=0.1)
                e_temp = st.number_input("Temperature (°C)", value=4.0, step=0.5)
            with c4:
                e_paid = st.number_input("Paise Diye / Liye (Cash Transaction)", min_value=0.0, step=50.0)

            submit_e = st.form_submit_button("Entry Mehfooz Karein")

            if submit_e:
                # Bande ki details nikalna
                p_info = st.session_state.persons[st.session_state.persons["Name"] == e_name].iloc[0]
                p_type = p_info["Type"]
                m_type = p_info["Milk_Type"]

                # AUTOMATIC RATE LOGIC (Fat standard ke mutabiq)
                if m_type == "Bhains":
                    # Standard 6.0 fat pe base rate, baqi upar niche bonus
                    calculated_rate = base_rate_bhains + ((e_fat - 6.0) * 10 * fat_bonus)
                else:
                    # Standard 4.0 fat pe base rate
                    calculated_rate = base_rate_gaaye + ((e_fat - 4.0) * 10 * fat_bonus)

                total_amount = e_liters * calculated_rate
                remaining = total_amount - e_paid

                # Record save karna
                new_record = pd.DataFrame([[e_date, e_shift, e_name, p_type, e_liters, e_fat, e_temp, calculated_rate, total_amount, e_paid, remaining]], 
                                          columns=["Date", "Shift", "Name", "Type", "Liters", "Fat", "Temp", "Rate", "Total", "Paid", "Remaining"])
                st.session_state.records = pd.concat([st.session_state.records, new_record], ignore_index=True)
                st.success(f"🎉 Entry Save Ho Gayi! Rate Laga: Rs. {calculated_rate:.2f} per Liter. Total Bill: Rs. {total_amount:.2f}")

# ================= TAB 3: FILTRATION & PRINTING =================
with tab3:
    st.subheader("🖨️ Hisab Kitab Aur Print Out")
    if st.session_state.records.empty:
        st.info("Abhi tak koi entry nahi hui.")
    else:
        # Date and Person Filter
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            start_d = st.date_input("Kab Se (Start Date)", datetime.now())
        with f_col2:
            end_d = st.date_input("Kab Tak (End Date)", datetime.now())
            
        search_name = st.selectbox("Kis Bande Ka Record Dekhna Hai?", ["Sab Ka Ek Saath"] + st.session_state.persons["Name"].tolist())

        # Filter Data
        df_filtered = st.session_state.records[
            (st.session_state.records["Date"] >= start_d) & 
            (st.session_state.records["Date"] <= end_d)
        ]
        
        if search_name != "Sab Ka Ek Saath":
            df_filtered = df_filtered[df_filtered["Name"] == search_name]

        st.write("### 📊 Filtered Data Summary:")
        st.dataframe(df_filtered, use_container_width=True)

        # Calculations
        total_doodh = df_filtered["Liters"].sum()
        total_pese = df_filtered["Total"].sum()
        total_paid = df_filtered["Paid"].sum()
        total_bakaya = df_filtered["Remaining"].sum()

        # Display Summary Cards
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Total Doodh (Liters)", f"{total_doodh} L")
        sc2.metric("Total Rakam (Rs.)", f"{total_pese}/-")
        sc3.metric("Ada Shuda (Paid)", f"{total_paid}/-")
        sc4.metric("Kul Bakaya (Remaining)", f"{total_bakaya}/-")

        st.markdown("---")
        st.info("💡 **Print Karne Ka Tareeqa:** Apne Laptop ya Mobile par **Ctrl + P** dabayein, yeh page safai se PDF me save ya print ho jaye ga!")
