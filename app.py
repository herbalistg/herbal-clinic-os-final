"""
Herbal Clinic OS - V2.4.1 Hotfix
- Complaint required bug fixed
- Auto header extend to 20 cols
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
import time

try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    GSheetsConnection = None

st.set_page_config(page_title="Herbal Clinic OS - V2.4.1", layout="wide", page_icon="🌿")

LANG = st.sidebar.selectbox("Language / زبان", ["Urdu + English", "English", "اردو"], index=0)
def tr(en, ur):
    return en if LANG=="English" else ur if LANG=="اردو" else f"{en} / {ur}"

st.sidebar.success("V2.4.1 - Hotfix")
st.sidebar.info("Fix: Complaint optional + Auto Header Extend")

conn = st.connection("gsheets", type=GSheetsConnection) if GSheetsConnection else None

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
    try:
        ws, actual_headers = get_ws_headers(sheet_name)
        if not ws:
            st.error(f"Worksheet {sheet_name} not found")
            return False
        if len(actual_headers) < len(STANDARD_NEW_PATIENT_HEADERS) and sheet_name == "New_patient":
            try:
                ws.update('A1:T1', [STANDARD_NEW_PATIENT_HEADERS])
                actual_headers = STANDARD_NEW_PATIENT_HEADERS
            except: pass
        row_to_append = []
        for h in actual_headers:
            val = ""
            for k,v in data_dict.items():
                if k.strip().lower() == h.strip().lower():
                    val = v
                    break
            row_to_append.append(val)
        if len(actual_headers) < 5:
            return False
        ws.append_row(row_to_append)
        return True
    except Exception as e:
        st.error(f"Append Error: {e}")
        return False

def read_sheet_df(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df = df.dropna(how='all')
        return df
    except Exception as e:
        return pd.DataFrame()

st.title(tr("🌿 Herbal Clinic OS - V2.4.1 Hotfix", "🌿 ہربل کلینک - V2.4.1 فکس"))
st.caption("Complaint Optional + Header Auto-Extend Fix")

tabs = st.tabs([tr("🔧 Debug", "🔧 چیک"), tr("🧑‍⚕️ New Patient", "🧑‍⚕️ نیا مریض"), tr("🔍 Revisit", "🔍 تلاش"), tr("📋 Recent", "📋 حالیہ"), tr("📚 Herbs", "📚 لغت")])

with tabs[0]:
    if st.button("Show Actual Headers"):
        ws, headers = get_ws_headers("New_patient")
        st.json(headers)
        st.write(f"Count: {len(headers)} / Expected: {len(STANDARD_NEW_PATIENT_HEADERS)}")
        if len(headers) < 20:
            if st.button("Auto Fix to 20 Cols Now"):
                ws.update('A1:T1', [STANDARD_NEW_PATIENT_HEADERS])
                st.success("Fixed to 20 cols")
                st.rerun()

with tabs[1]:
    with st.form("new_patient_v24_fix", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            daily_no = st.text_input("Daily Number / روزانہ نمبر", value=str(int(time.time())%10000))
            name = st.text_input("Patient Name * / مریض کا نام *")
            father_spouse = st.text_input(FATHER_SPOUSE_LABEL)
        with c2:
            age = st.number_input("Age / عمر", 0,120,30)
            gender = st.selectbox("Gender / جنس", ["Male / مرد","Female / عورت"])
            phone = st.text_input("Phone * / فون *")
        with c3:
            city = st.text_input("City / شہر", "Bhai Pheru")
            address = st.text_area("Address / پتہ", height=68)
            date_val = st.date_input("Date / تاریخ", value=date.today())
        st.markdown("---")
        a1,a2,a3,a4 = st.columns(4)
        with a1:
            bp = st.text_input("BP", placeholder="120/80")
            pulse = st.text_input("Pulse / نبض")
        with a2:
            weight = st.text_input("Weight / وزن")
            height = st.text_input("Height / قد")
        with a3:
            temperament = st.selectbox("Temperament / مزاج", ["Garm / گرم","Sard / سرد","Khushk / خشک","Tar / تر","Garm Khushk","Garm Tar","Sard Khushk","Sard Tar","Mutadil / معتدل"])
        with a4:
            fees = st.text_input("Fees / فیس", "500")
            status = st.selectbox("Status", ["New / نیا","Follow-up","Cured"])
        b1,b2 = st.columns(2)
        with b1:
            history = st.text_area("Past History / پرانی ہسٹری")
            complaint = st.text_area("Current Complaint / شکایت (Optional now)")  # Optional
        with b2:
            diagnosis = st.text_area("Diagnosis / تشخیص")
            treatment = st.text_area("Treatment / علاج")
        submitted = st.form_submit_button("💾 Save Patient - V2.4.1", type="primary", use_container_width=True)
        if submitted:
            if not name or not phone:
                st.error("Name and Phone required!")
            else:
                if not complaint:
                    complaint = "General Checkup"
                data_dict = {
                    "DailyNumber": daily_no, "Date": str(date_val), "Name": name, "FatherName": father_spouse,
                    "Age": age, "Gender": gender, "Phone": phone, "Address": address, "City": city,
                    "BP": bp, "Pulse": pulse, "Weight": weight, "Height": height, "Temperament": temperament,
                    "History": history, "Complaint": complaint, "Diagnosis": diagnosis, "Treatment": treatment,
                    "Fees": fees, "Status": status
                }
                with st.spinner("Saving..."):
                    ok = append_row_mapping("New_patient", data_dict)
                    if ok:
                        st.success(f"✅ Saved! {name} | {daily_no}")
                        st.balloons()
                    else:
                        st.error("Save fail - Check Debug")

with tabs[2]:
    df = read_sheet_df("New_patient")
    if not df.empty:
        term = st.text_input("Search Name/Phone/Daily")
        if term:
            mask = df.astype(str).apply(lambda x: x.str.contains(term, case=False, na=False)).any(axis=1)
            st.dataframe(df[mask], use_container_width=True)
        else:
            st.dataframe(df.tail(10), use_container_width=True)

with tabs[3]:
    df = read_sheet_df("New_patient")
    if not df.empty:
        st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)

with tabs[4]:
    st.info("Herbs Dictionary - V2.4")
