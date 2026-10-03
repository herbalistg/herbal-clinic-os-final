"""
Herbal Clinic OS - V2.4
- V1 20/20 Complete preserved
- Auth Muted till V2.5
- Column Fix (Actual Headers Mapping) + Father/Spouse Fix Done
- NEW V2.4: Advanced Fields + Revisit Search + Herbs Dictionary
Same Sheet ID & secrets.toml
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
import time

# For gsheets
try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    GSheetsConnection = None

st.set_page_config(page_title="Herbal Clinic OS - V2.4", layout="wide", page_icon="🌿")

# --- LANGUAGE / RTL ---
LANG = st.sidebar.selectbox("Language / زبان", ["Urdu + English", "English", "اردو"], index=0)

def tr(en, ur):
    if LANG == "English":
        return en
    elif LANG == "اردو":
        return ur
    else:
        return f"{en} / {ur}"

st.sidebar.markdown("---")
st.sidebar.success("V2.4 - Advanced + Revisit")
st.sidebar.info("Auth: Muted till V2.5\n\nColumn Fix: ✅\nFather/Spouse Fix: ✅\nSheet: 20/20 ✅")

# --- CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection) if GSheetsConnection else None

# Standard expected headers for New_patient
STANDARD_NEW_PATIENT_HEADERS = [
    "DailyNumber", "Date", "Name", "FatherName", "Age", "Gender", 
    "Phone", "Address", "City",
    "BP", "Pulse", "Weight", "Height", "Temperament", "History", "Complaint", "Diagnosis", "Treatment", "Fees", "Status"
]

FATHER_SPOUSE_LABEL = "Father Name / Spouse Name / باپ / سپاس کا نام"

def get_ws_headers(sheet_name):
    try:
        ws = conn._instance.worksheet(sheet_name)
        headers = ws.row_values(1)
        return ws, headers
    except Exception as e:
        return None, [f"Error: {e}"]

def append_row_mapping(sheet_name, data_dict):
    """Fix: Actual header se mapping"""
    try:
        ws, actual_headers = get_ws_headers(sheet_name)
        if not ws:
            st.error(f"Worksheet {sheet_name} not found: {actual_headers}")
            return False
        
        # actual headers ke order se row banao
        row_to_append = []
        for h in actual_headers:
            # data_dict me key dhundo (case insensitive)
            val = ""
            for k,v in data_dict.items():
                if k.strip().lower() == h.strip().lower():
                    val = v
                    break
            row_to_append.append(val)
        
        # Agar actual_headers khali hai ya mismatch, to standard use karo
        if len(actual_headers) < 5:
            st.warning(f"Sheet {sheet_name} headers khali hain, Standard Order fix karen")
            return False
            
        ws.append_row(row_to_append)
        return True
    except Exception as e:
        st.error(f"Append Error: {e}")
        return False

def read_sheet_df(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        # drop fully empty rows
        df = df.dropna(how='all')
        return df
    except Exception as e:
        st.error(f"Read {sheet_name} Error: {e}")
        return pd.DataFrame()

# --- HEADER ---
st.title(tr("🌿 Herbal Clinic OS - V2.4", "🌿 ہربل کلینک سسٹم - V2.4"))
st.caption(tr("V1 20/20 Complete | Column Fix + Father/Spouse Fix Done | V2.4 - Advanced Fields", "V1 20/20 مکمل | کالم فکس + باپ/سپاس فکس | V2.4 - ایڈوانس فیلڈز"))

tabs = st.tabs([
    tr("🔧 Debug Headers", "🔧 ہیڈرز چیک"),
    tr("🧑‍⚕️ New Patient (Advanced)", "🧑‍⚕️ نیا مریض (ایڈوانس)"),
    tr("🔍 Revisit / Search", "🔍 دوبارہ معائنہ / تلاش"),
    tr("📋 Recent Patients", "📋 حالیہ مریض"),
    tr("📚 Herbs Dictionary", "📚 جڑی بوٹیاں لغت"),
])

# --- TAB 1: DEBUG ---
with tabs[0]:
    st.subheader(tr("Debug Actual Headers - New_patient", "اصلی ہیڈرز چیک - New_patient"))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Show Actual Headers of New_patient"):
            ws, headers = get_ws_headers("New_patient")
            st.write("**Actual Headers in Sheet:**")
            st.json(headers)
            for i, h in enumerate(headers):
                st.write(f"{i+1}. `{h}`")
            # Check mismatch
            if headers != STANDARD_NEW_PATIENT_HEADERS:
                st.warning("⚠️ Mismatch with Standard! Fix button dabayen")
            else:
                st.success("✅ Mapping Correct - Standard Order")
    with col2:
        if st.button("Fix New_patient Headers to Standard Order"):
            try:
                ws, _ = get_ws_headers("New_patient")
                ws.update('A1:T1', [STANDARD_NEW_PATIENT_HEADERS])
                st.success(f"Fixed! Headers set to: {STANDARD_NEW_PATIENT_HEADERS}")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Fix Error: {e}")

# --- TAB 2: NEW PATIENT ADVANCED V2.4 ---
with tabs[1]:
    st.subheader(tr("New Patient Registration - V2.4 Advanced", "نئے مریض کا اندراج - V2.4 ایڈوانس"))
    
    with st.form("new_patient_v24_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            daily_no = st.text_input(tr("Daily Number", "روزانہ نمبر"), value=str(int(time.time()) % 10000))
            name = st.text_input(tr("Patient Name *", "مریض کا نام *"))
            father_spouse = st.text_input(FATHER_SPOUSE_LABEL, help="For male: Father Name, For female: Spouse Name / مرد کے لیے والد کا نام، عورت کے لیے شوہر کا نام")
        with c2:
            age = st.number_input(tr("Age", "عمر"), min_value=0, max_value=120, value=30)
            gender = st.selectbox(tr("Gender", "جنس"), ["Male / مرد", "Female / عورت", "Other"])
            phone = st.text_input(tr("Phone *", "فون *"))
        with c3:
            city = st.text_input(tr("City", "شہر"), value="Bhai Pheru")
            address = st.text_area(tr("Address", "پتہ"), height=68)
            date_val = st.date_input(tr("Date", "تاریخ"), value=date.today())

        st.markdown("---")
        st.markdown(f"**{tr('Advanced Examination (V2.4 New)', 'ایڈوانس معائنہ (V2.4 نیا)')}**")
        a1, a2, a3, a4 = st.columns(4)
        with a1:
            bp = st.text_input(tr("BP (e.g. 120/80)", "بی پی"), placeholder="120/80")
            pulse = st.text_input(tr("Pulse", "نبض"), placeholder="78")
        with a2:
            weight = st.text_input(tr("Weight (kg)", "وزن"), placeholder="70")
            height = st.text_input(tr("Height", "قد"), placeholder="5.8")
        with a3:
            temperament = st.selectbox(tr("Temperament / Mizaj", "مزاج"), ["Garm / گرم", "Sard / سرد", "Khushk / خشک", "Tar / تر", "Garm Khushk / گرم خشک", "Garm Tar / گرم تر", "Sard Khushk / سرد خشک", "Sard Tar / سرد تر", "Mutadil / معتدل"])
        with a4:
            fees = st.text_input(tr("Fees", "فیس"), value="500")
            status = st.selectbox(tr("Status", "حالت"), ["New / نیا", "Follow-up / دوبارہ", "Cured / شفایاب"])

        b1, b2 = st.columns(2)
        with b1:
            history = st.text_area(tr("Past History", "پرانی ہسٹری"), placeholder="Diabetes, BP etc...")
            complaint = st.text_area(tr("Current Complaint / Shikayat *", "موجودہ شکایت *"))
        with b2:
            diagnosis = st.text_area(tr("Diagnosis / Tashkhees", "تشخیص"))
            treatment = st.text_area(tr("Treatment / Ilaj", "علاج"))

        submitted = st.form_submit_button(tr("💾 Save Patient (V2.4)", "💾 محفوظ کریں (V2.4)"), type="primary", use_container_width=True)
        
        if submitted:
            if not name or not phone:
                st.error(tr("Name and Phone are required! (V2.1 Fix)", "نام اور فون ضروری ہیں!"))
            elif not complaint:
                st.error(tr("Complaint is required for V2.4", "شکایت ضروری ہے V2.4 کے لیے"))
            else:
                # Prepare dict with EXACT header keys
                data_dict = {
                    "DailyNumber": daily_no,
                    "Date": str(date_val),
                    "Name": name,
                    "FatherName": father_spouse,
                    "Age": age,
                    "Gender": gender,
                    "Phone": phone,
                    "Address": address,
                    "City": city,
                    "BP": bp,
                    "Pulse": pulse,
                    "Weight": weight,
                    "Height": height,
                    "Temperament": temperament,
                    "History": history,
                    "Complaint": complaint,
                    "Diagnosis": diagnosis,
                    "Treatment": treatment,
                    "Fees": fees,
                    "Status": status
                }
                with st.spinner("Saving with Actual Header Mapping..."):
                    ok = append_row_mapping("New_patient", data_dict)
                    if ok:
                        st.success(f"✅ Saved! {name} | Daily: {daily_no} | BP: {bp} | Mizaj: {temperament}")
                        st.balloons()
                    else:
                        st.error("Failed to save - Check Debug Tab")

# --- TAB 3: REVISIT / SEARCH V2.4 NEW ---
with tabs[2]:
    st.subheader(tr("Revisit - Search Patient (V2.4)", "دوبارہ معائنہ - مریض تلاش کریں (V2.4)"))
    df = read_sheet_df("New_patient")
    
    if not df.empty:
        search_col1, search_col2, search_col3 = st.columns([2,2,1])
        with search_col1:
            search_term = st.text_input(tr("Search by Name / Phone / DailyNumber / Father/Spouse", "نام / فون / روزانہ نمبر / باپ/سپاس سے تلاش"), placeholder="e.g. Ali or 0300...")
        with search_col2:
            search_filter = st.selectbox(tr("Filter by", "فلٹر"), ["All", "Phone", "Name", "FatherName", "DailyNumber", "Temperament"])
        with search_col3:
            st.write("")
            st.write("")
            do_search = st.button(tr("🔍 Search", "🔍 تلاش کریں"), type="primary")

        if do_search and search_term:
            # Case insensitive search
            mask = pd.Series([False]*len(df))
            for col in df.columns:
                if search_filter == "All" or col.lower() == search_filter.lower():
                    mask = mask | df[col].astype(str).str.contains(search_term, case=False, na=False)
            
            result = df[mask]
            st.write(f"Found {len(result)} records")
            st.dataframe(result, use_container_width=True)
            
            if not result.empty:
                st.markdown("---")
                st.markdown(f"**{tr('Create Revisit Entry for Selected', 'منتخب مریض کے لیے دوبارہ اندراج')}**")
                selected_daily = st.selectbox(tr("Select Patient to Revisit", "دوبارہ معائنے کے لیے مریض منتخب کریں"), result['DailyNumber'].astype(str).tolist() if 'DailyNumber' in result.columns else result.iloc[:,0].astype(str).tolist())
                
                with st.form("revisit_form"):
                    rev_date = st.date_input("Revisit Date", value=date.today())
                    rev_complaint = st.text_area(f"New Complaint / {FATHER_SPOUSE_LABEL} - Update?")
                    rev_treatment = st.text_area("New Treatment")
                    rev_fees = st.text_input("Fees", value="300")
                    
                    if st.form_submit_button("Save Revisit"):
                        # Save to Revisit sheet
                        revisit_dict = {
                            "DailyNumber": selected_daily,
                            "Date": str(rev_date),
                            "Complaint": rev_complaint,
                            "Treatment": rev_treatment,
                            "Fees": rev_fees
                        }
                        # Try to map to Revisit sheet headers
                        ok = append_row_mapping("Revisit", revisit_dict)
                        if ok:
                            st.success(f"Revisit saved for {selected_daily}")
                        else:
                            st.error("Revisit sheet not found or headers issue - check if Revisit sheet exists in 20/20")
        else:
            st.info(tr("Enter search term to find patient. This uses actual header mapping fix.", "مریض تلاش کرنے کے لیے لفظ لکھیں۔"))
            st.dataframe(df.tail(20), use_container_width=True)
    else:
        st.warning("New_patient sheet is empty or not readable")

# --- TAB 4: RECENT ---
with tabs[3]:
    st.subheader(tr("Recent Patients - Last Row Check (Column Fix Verify)", "حالیہ مریض - آخری قطار چیک"))
    df = read_sheet_df("New_patient")
    if not df.empty:
        st.write(f"Total Patients: {len(df)}")
        last = df.tail(1)
        st.dataframe(last.T, use_container_width=True)  # Transpose for easy check
        
        # Verification logic for V2.2 bug
        try:
            last_row = df.iloc[-1]
            name_val = str(last_row.get('Name', ''))
            daily_val = str(last_row.get('DailyNumber', ''))
            # If Name is numeric like 30 -> bug, if DailyNumber looks like date -> bug
            is_bug = False
            if name_val.isdigit() and len(name_val) <=3:
                is_bug = True
                st.error(f"🐛 BUG STILL: Name column me '{name_val}' hai jo Age lag raha hai! V2.2 fix fail")
            if '-' in daily_val and len(daily_val) >=8:
                is_bug = True
                st.error(f"🐛 BUG STILL: DailyNumber me '{daily_val}' hai jo Date lag rahi hai!")
            
            if not is_bug:
                st.success("✅ Mapping Correct - Column Fix Working (V2.2)")
                # Show Father/Spouse check
                if 'FatherName' in df.columns:
                    st.info(f"{FATHER_SPOUSE_LABEL} Check: Last Value = {last_row.get('FatherName', 'N/A')}")
        except Exception as e:
            st.write(f"Check error: {e}")
        
        st.markdown("---")
        st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)
    else:
        st.write("No data yet")

# --- TAB 5: HERBS DICTIONARY V2.4 NEW ---
with tabs[4]:
    st.subheader(tr("Herbs Dictionary / Qarabadin (V2.4 New)", "جڑی بوٹیوں کی لغت / قرابادین (V2.4 نیا)"))
    # Try to read Herbs_Dictionary or similar sheet
    herbs_df = pd.DataFrame()
    for sheet_try in ["Herbs_Dictionary", "Herbs", "Qarabadin", "Medicine", "Stock"]:
        temp = read_sheet_df(sheet_try)
        if not temp.empty:
            herbs_df = temp
            st.success(f"Loaded from sheet: {sheet_try} - {len(temp)} items")
            break
    
    if not herbs_df.empty:
        herb_search = st.text_input(tr("Search Herb / مزاج / فائدہ", "جڑی بوٹی / مزاج / فائدہ تلاش کریں"))
        if herb_search:
            mask = pd.Series([False]*len(herbs_df))
            for col in herbs_df.columns:
                mask = mask | herbs_df[col].astype(str).str.contains(herb_search, case=False, na=False)
            st.dataframe(herbs_df[mask], use_container_width=True)
        else:
            st.dataframe(herbs_df.head(100), use_container_width=True)
    else:
        st.info(tr("No Herbs sheet data found yet. You have 20/20 sheets - add data in Herbs_Dictionary sheet. Showing Sample.", "ابھی جڑی بوٹیوں کا ڈیٹا نہیں ہے۔ 20/20 شیٹس میں Herbs_Dictionary شیٹ میں ڈیٹا ڈالیں۔ نمونہ دکھایا جا رہا ہے۔"))
        sample = pd.DataFrame([
            {"Name": "Ajwain / اجوائن", "Mizaj": "Garm Khushk / گرم خشک", "Fayda": "Hazma, Gas / ہاضمہ، گیس"},
            {"Name": "Saunf / سونف", "Mizaj": "Garm Khushk / گرم خشک", "Fayda": "Hazma, Nazar / ہاضمہ، نظر"},
            {"Name": "Ispaghol / اسپغول", "Mizaj": "Sard Tar / سرد تر", "Fayda": "Qabz / قبض"},
            {"Name": "Sana Makki / سنا مکی", "Mizaj": "Garm Khushk / گرم خشک", "Fayda": "Qabz Kush / قبض کشا"},
            {"Name": "Zafran / زعفران", "Mizaj": "Garm Khushk / گرم خشک", "Fayda": "Dil, Dimagh / دل، دماغ"},
        ])
        st.dataframe(sample, use_container_width=True)

st.markdown("---")
st.caption("Herbal Clinic OS V2.4 | V1 20/20 ✅ | Auth Muted till V2.5 | Column Fix ✅ | Father/Spouse (باپ/سپاس) ✅ | Advanced Fields + Revisit + Herbs Dictionary ✅ | Same Sheet ID")
