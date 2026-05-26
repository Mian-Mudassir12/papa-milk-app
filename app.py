import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration and theme setup
st.set_page_config(page_title="Papa Milk Chiller Pro", page_icon="🥛", layout="wide")
st.title("🥛 Papa Milk Chiller & Khata Management System")
st.markdown("---")

# Initialize Sessions for Database (Temporary storage for Web App)
if 'users' not in st.session_state:
    st.session_state.users = pd.DataFrame(columns=["Phone", "Name", "Type", "Milk_Type"])
if 'milk_entries' not in st.session_state:
    st.session_state.milk_entries = pd.DataFrame(columns=["Date", "Shift", "Phone", "Name", "Type", "Milk_Type", "Liters", "Fat", "LR", "Temp", "Calculated_Rate", "Total_Bill"])
if 'khata_entries' not in st.session_state:
    st.session_state.khata_entries = pd.DataFrame(columns=["Date", "Phone", "Name", "Type", "Description", "Debit_Paid", "Credit_Received"])

# ================= ⚙️ SETTINGS PAGE (ALAG CONFIGURATION) =================
st.sidebar.header("⚙️ System Master Settings")
st.sidebar.markdown("### 🐄 Base Rates (Standard Quality)")
base_bhains = st.sidebar.number_input("Bhains Base Rate (6.0% Fat, 28 LR)", value=180)
base_gaaye = st.sidebar.number_input("Gaaye Base Rate (4.0% Fat, 26 LR)", value=140)
base_bakri = st.sidebar.number_input("Bakri Base Rate", value=150)

st.sidebar.markdown("### 📈 Quality Formulas (Auto Backend Calculation)")
fat_factor = st.sidebar.number_input("Rate Change per 0.1% Fat (+/-)", value=2.0)
lr_factor = st.sidebar.number_input("Rate Change per 1.0 LR (+/-)", value=1.0)
temp_penalty = st.sidebar.number_input("Penalty if Temp > 4°C (Per Degree)", value=3.0)

# ================= 📊 MAIN DASHBOARD (PROFIT & LOSS) =================
st.header("📈 Business Live Dashboard (Profit & Loss)")
total_milk_in = st.session_state.milk_entries[st.session_state.milk_entries["Type"] == "Client (Supplier)"]["Liters"].sum()
total_milk_out = st.session_state.milk_entries[st.session_state.milk_entries["Type"] == "Customer (Buyer)"]["Liters"].sum()

total_expense = st.session_state.milk_entries[st.session_state.milk_entries["Type"] == "Client (Supplier)"]["Total_Bill"].sum()
total_revenue = st.session_state.milk_entries[st.session_state.milk_entries["Type"] == "Customer (Buyer)"]["Total_Bill"].sum()

# Extra items expense/income from khata
extra_expense = st.session_state.khata_entries["Debit_Paid"].sum()
extra_income = st.session_state.khata_entries["Credit_Received"].sum()

net_profit = (total_revenue + extra_income) - (total_expense + extra_expense)

d_col1, d_col2, d_col3, d_col4 = st.columns(4)
d_col1.metric("📥 Total Doodh Aya", f"{total_milk_in} Liters")
d_col2.metric("📤 Total Doodh Gaya", f"{total_milk_out} Liters")

if net_profit >= 0:
    d_col3.metric("💰 Net Profit (Faida)", f"Rs. {net_profit}/-", delta=f"Rs. {net_profit}")
else:
    d_col3.metric("📉 Net Loss (Nuqsan)", f"Rs. {net_profit}/-", delta=f"Rs. {net_profit}", delta_color="inverse")

# Pending Balances Summary
pending_from_customers = (st.session_state.milk_entries[st.session_state.milk_entries["Type"] == "Customer (Buyer)"]["Total_Bill"].sum() + 
                          st.session_state.khata_entries[st.session_state.khata_entries["Type"] == "Customer (Buyer)"]["Debit_Paid"].sum()) - \
                         st.session_state.khata_entries[st.session_state.khata_entries["Type"] == "Customer (Buyer)"]["Credit_Received"].sum()

d_col4.metric("⏳ Kul Bakaya (Market Balance)", f"Rs. {pending_from_customers}/-")
st.markdown("---")

# ================= TABS SEPARATION =================
tab_client, tab_customer, tab_reg, tab_report = st.tabs([
    "📥 CLIENT DASHBOARD (Supplier)", 
    "📤 CUSTOMER DASHBOARD (Buyer)", 
    "👥 REGISTER NEW PERSON", 
    "🖨️ SEARCH & PRINT REPORTS"
])

# ================= TAB: REGISTER NEW PERSON =================
with tab_reg:
    st.subheader("👥 Naya Banda Register Karein (Compulsory Phone Number)")
    with st.form("reg_form", clear_on_submit=True):
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            u_name = st.text_input("Bande Ka Naam")
        with rc2:
            u_phone = st.text_input("Mobile Number (Compulsory / Search ID)")
        with rc3:
            u_type = st.selectbox("Bande ki Qism", ["Client (Supplier)", "Customer (Buyer)"])
        
        u_milk = st.selectbox("Doodh Ki Type", ["Bhains", "Gaaye", "Bakri"])
        submit_user = st.form_submit_button("Account Banayein")
        
        if submit_user:
            if not u_name or not u_phone:
                st.error("⚠️ Naam aur Phone Number dono likhna zaroori hain!")
            elif u_phone in st.session_state.users["Phone"].values:
                st.warning("⚠️ Yeh Phone Number pehle se register hai!")
            else:
                new_u = pd.DataFrame([[u_phone, u_name, u_type, u_milk]], columns=["Phone", "Name", "Type", "Milk_Type"])
                st.session_state.users = pd.concat([st.session_state.users, new_u], ignore_index=True)
                st.success(f"✅ {u_name} ka alag khata account ban gaya hai!")

# ================= TAB: CLIENT DASHBOARD (SUPPLIER) =================
with tab_client:
    st.subheader("📥 Doodh Lene Wali Entry (Suppliers)")
    clients_list = st.session_state.users[st.session_state.users["Type"] == "Client (Supplier)"]
    
    if clients_list.empty:
        st.info("Abhi tak koi Client register nahi hua.")
    else:
        with st.form("client_entry_form"):
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                c_date = st.date_input("Date", datetime.now(), key="c_date")
                c_shift = st.selectbox("Shift", ["Subah (Morning)", "Shaam (Evening)"], key="c_shift")
            with cc2:
                c_select = st.selectbox("Client Chunyein", clients_list["Name"].tolist())
                c_liters = st.number_input("Kitna Doodh Aya (Liters)", min_value=0.0, step=1.0)
            with cc3:
                c_fat = st.number_input("Fat %", min_value=0.0, max_value=12.0, value=6.0, step=0.1, key="c_fat")
                c_lr = st.number_input("LR Quality", min_value=0, max_value=40, value=28)
                c_temp = st.number_input("Temperature (°C)", value=4.0, key="c_temp")
                
            submit_client = st.form_submit_button("Client Entry Save Karein")
            
            if submit_client and c_liters > 0:
                user_row = clients_list[clients_list["Name"] == c_select].iloc[0]
                m_type = user_row["Milk_Type"]
                
                # Auto backend calculation logic for client
                base = base_bhains if m_type == "Bhains" else (base_gaaye if m_type == "Gaaye" else base_bakri)
                std_fat = 6.0 if m_type == "Bhains" else 4.0
                std_lr = 28 if m_type == "Bhains" else 26
                
                calc_rate = base + ((c_fat - std_fat) * 10 * fat_factor) + ((c_lr - std_lr) * lr_factor)
                if c_temp > 4.0:
                    calc_rate -= (c_temp - 4.0) * temp_penalty
                    
                total_bill = c_liters * calc_rate
                
                new_entry = pd.DataFrame([[c_date, c_shift, user_row["Phone"], c_select, "Client (Supplier)", m_type, c_liters, c_fat, c_lr, c_temp, calc_rate, total_bill]], 
                                         columns=["Date", "Shift", "Phone", "Name", "Type", "Milk_Type", "Liters", "Fat", "LR", "Temp", "Calculated_Rate", "Total_Bill"])
                st.session_state.milk_entries = pd.concat([st.session_state.milk_entries, new_entry], ignore_index=True)
                st.success(f"🎉 Entry Saved! Rate: Rs. {calc_rate:.2f}/L | Bill: Rs. {total_bill:.2f}")

# ================= TAB: CUSTOMER DASHBOARD (BUYER) =================
with tab_customer:
    st.subheader("📤 Doodh Bechne Aur Khata Kharcha Entry (Customers)")
    cust_list = st.session_state.users[st.session_state.users["Type"] == "Customer (Buyer)"]
    
    if cust_list.empty:
        st.info("Abhi tak koi Customer register nahi hua.")
    else:
        st.markdown("### 1. Daily Doodh Sale")
        with st.form("customer_milk_form"):
            cu1, cu2, cu3 = st.columns(3)
            with cu1:
                cu_date = st.date_input("Date", datetime.now(), key="cu_date")
                cu_shift = st.selectbox("Shift", ["Subah (Morning)", "Shaam (Evening)"], key="cu_shift")
            with cu2:
                cu_select = st.selectbox("Customer Chunyein", cust_list["Name"].tolist())
                cu_liters = st.number_input("Kitna Doodh Diya (Liters)", min_value=0.0, step=1.0)
            with cu3:
                cu_fat = st.number_input("Fat %", min_value=0.0, max_value=12.0, value=6.0, step=0.1, key="cu_fat")
                cu_temp = st.number_input("Temperature (°C)", value=4.0, key="cu_temp")
                
            submit_cust = st.form_submit_button("Sale Entry Save Karein")
            
            if submit_cust and cu_liters > 0:
                user_row = cust_list[cust_list["Name"] == cu_select].iloc[0]
                m_type = user_row["Milk_Type"]
                
                base = base_bhains if m_type == "Bhains" else (base_gaaye if m_type == "Gaaye" else base_bakri)
                std_fat = 6.0 if m_type == "Bhains" else 4.0
                
                calc_rate = base + ((cu_fat - std_fat) * 10 * fat_factor)
                if cu_temp > 4.0:
                    calc_rate -= (cu_temp - 4.0) * temp_penalty
                    
                total_bill = cu_liters * calc_rate
                
                new_entry = pd.DataFrame([[cu_date, cu_shift, user_row["Phone"], cu_select, "Customer (Buyer)", m_type, cu_liters, cu_fat, 0, cu_temp, calc_rate, total_bill]], 
                                         columns=["Date", "Shift", "Phone", "Name", "Type", "Milk_Type", "Liters", "Fat", "LR", "Temp", "Calculated_Rate", "Total_Bill"])
                st.session_state.milk_entries = pd.concat([st.session_state.milk_entries, new_entry], ignore_index=True)
                st.success(f"🎉 Sale Entry Saved! Rate: Rs. {calc_rate:.2f}/L | Total: Rs. {total_bill:.2f}")

        st.markdown("---")
        st.markdown("### 2. Khata Transaction (Paise Diye/Liye ya Khal/Chokara ka Hisab)")
        with st.form("khata_form"):
            kh1, kh2, kh3 = st.columns(3)
            with kh1:
                k_date = st.date_input("Transaction Date", datetime.now())
                k_select = st.selectbox("Banda Chunyein (Client/Customer)", st.session_state.users["Name"].tolist())
            with kh2:
                k_desc = st.selectbox("Khate Ki Detial", ["Cash Payment Received", "Cash Advance Given", "Khal Di/Li", "Chokara Di/Li", "Other Expense"])
                k_amount = st.number_input("Rakam / Amount (Rs.)", min_value=0.0, step=50.0)
            with kh3:
                k_mode = st.selectbox("Transaction Type", ["Paise Hum Ne Diye / Kharcha (Debit)", "Paise Hum Ne Liye / Income (Credit)"])
                
            submit_khata = st.form_submit_button("Khata Record Save Karein")
            
            if submit_khata and k_amount > 0:
                user_row = st.session_state.users[st.session_state.users["Name"] == k_select].iloc[0]
                u_phone = user_row["Phone"]
                u_type = user_row["Type"]
                
                debit = k_amount if "Debit" in k_mode else 0.0
                credit = k_amount if "Credit" in k_mode else 0.0
                
                new_khata = pd.DataFrame([[k_date, u_phone, k_select, u_type, k_desc, debit, credit]], 
                                         columns=["Date", "Phone", "Name", "Type", "Description", "Debit_Paid", "Credit_Received"])
                st.session_state.khata_entries = pd.concat([st.session_state.khata_entries, new_khata], ignore_index=True)
                st.success(f"✅ Khata Record Updated for {k_select} ({k_desc}: Rs. {k_amount})")

# ================= 🖨️ TAB: SEARCH & PRINT REPORTS =================
with tab_report:
    st.subheader("🔍 Filter Records By Name, Phone, or Date")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        search_query = st.text_input("👤 Search by Name or Mobile Number")
    with col_s2:
        s_date = st.date_input("Start Date (Yahan Se)", datetime.now())
    with col_s3:
        e_date = st.date_input("End Date (Yahan Tak)", datetime.now())
        
    if not st.session_state.users.empty:
        # Filter Logic
        filtered_entries = st.session_state.milk_entries[
            (st.session_state.milk_entries["Date"] >= s_date) & (st.session_state.milk_entries["Date"] <= e_date)
        ]
        filtered_khata = st.session_state.khata_entries[
            (st.session_state.khata_entries["Date"] >= s_date) & (st.session_state.khata_entries["Date"] <= e_date)
        ]
        
        if search_query:
            filtered_entries = filtered_entries[(filtered_entries["Name"].str.contains(search_query, case=False)) | (filtered_entries["Phone"].str.contains(search_query))]
            filtered_khata = filtered_khata[(filtered_khata["Name"].str.contains(search_query, case=False)) | (filtered_khata["Phone"].str.contains(search_query))]
            
        st.markdown(f"### 📋 Milk Records ({s_date} to {e_date})")
        st.dataframe(filtered_entries, use_container_width=True)
        
        st.markdown("### 📝 Financial Ledger (Khata Transaction History)")
        st.dataframe(filtered_khata, use_container_width=True)
        
        # Summary Calculations
        total_l = filtered_entries["Liters"].sum()
        total_b = filtered_entries["Total_Bill"].sum()
        total_dr = filtered_khata["Debit_Paid"].sum()
        total_cr = filtered_khata["Credit_Received"].sum()
        
        # Final Statement
        st.markdown("---")
        st.markdown(f"## 🖨️ Final Statement Summary: {search_query}")
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Total Milk Quantity", f"{total_l} Liters")
        sc2.metric("Total Doodh Ka Bill", f"Rs. {total_b}/-")
        
        balance = (total_b + total_dr) - total_cr
        sc3.metric("Net Payable/Receivable Balance (Net Bakaya)", f"Rs. {balance}/-")
        
        st.info("💡 **Print Report Guide:** Agar aapko sirf is customer ka print nikalna hai, toh filter set karein aur keyboard par **Ctrl + P** (ya Mobile me Share -> Print) dabayein. Yeh poora page bina kisi faltu button ke saaf sutra PDF me print ho jaye ga!")
    else:
        st.warning("System me abhi tak koi data majood nahi hai.")
