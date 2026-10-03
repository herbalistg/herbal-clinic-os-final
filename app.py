"""
Herbal Clinic OS - V2.4.6.1 - Hotfix for NameError
================================================================
BUG FIX: NameError: name 'read_v246' is not defined
CAUSE: Function name mismatch - def read_sheet_v246 but called read_v246
FIX: All calls unified to read_sheet_v246 and append_v246

PLANNING (Same as V2.4.6 - User Notes = Planning):
1. PatientID Format:
   - Full Unique (System): NP_{number}_{clinic_phone} Example: NP_1_123456789
   - Display to User: Sirf NP_1 dikhana, phone hidden (system pehchan ke liye)
   - Uniqueness: Har clinic ka NP_1 hoga to mix, is liye phone suffix se unique

2. ClinicPhone:
   - Till V2.5 Muted: secrets.toml me clinic_phone = "123456789" (temporary)
   - After V2.5: Signup form se auto
   - Location: [connections.gsheets] clinic_phone OR [clinic] phone

3. DailyNumber:
   - Har clinic ka apna daily counter, rozana 1 se shuru
   - Logic: ClinicPhone + Date filter count + 1

4. Form Display:
   - Top pe auto-generate before Personal Info:
     - Patient ID Display: NP_1
     - Daily Number: 1
     - Full System ID hidden: NP_1_123456789

5. Sheet: 22 cols - PatientID, ClinicPhone, DailyNumber, Date, Name, FatherName (باپ/سپاس), ...

6. Planning Rule: User notes = planning, confirm if contradiction, comment in code

7. Future: ClinicPhone se filter karke daily/weekly graph

8. Deep Debug Rule: Full debug before giving code

Version: V2.4.6.1 Hotfix | Same Sheet ID: 1D4x7wioVZy... | Auth Muted till V2.5
================================================================
"""
import streamlit as st
import pandas as pd
from datetime import date
import time
import re

st.set_page_config(page_title="Herbal Clinic OS V2.4.6.1", layout="wide", page_icon="🌿")

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    st.error("Missing: gspread, google-auth")
    st.stop()

STANDARD_HEADERS_V246 = [
    "PatientID", "ClinicPhone", "DailyNumber", "Date", "Name", "FatherName", "Age", "Gender",
    "Phone", "Address", "City",
    "BP", "Pulse", "Weight", "Height", "Temperament", "History", "Complaint", "Diagnosis", "Treatment", "Fees", "Status"
]
FATHER_SPOUSE_LABEL = "Father Name / Spouse Name / باپ / سپاس کا نام"
DEFAULT_CLINIC_PHONE = "123456789"

def get_clinic_phone():
    """PLANNING: Till V2.5 use 123456789 from secrets, After from signup"""
    try:
        if "clinic" in st.secrets and "phone" in st.secrets["clinic"]:
            return str(st.secrets["clinic"]["phone"]).strip()
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            gs = st.secrets["connections"]["gsheets"]
            if "clinic_phone" in gs:
                return str(gs["clinic_phone"]).strip()
        if "clinic_phone" in st.secrets:
            return str(st.secrets["clinic_phone"]).strip()
        return DEFAULT_CLINIC_PHONE
    except:
        return DEFAULT_CLINIC_PHONE

@st.cache_resource
def get_client_v246():
    try:
        if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
            return None, None, "connections.gsheets not found"
        spreadsheet_id = st.secrets["connections"]["gsheets"].get("spreadsheet", "")
        if not spreadsheet_id:
            return None, None, "spreadsheet ID empty"
        if "gcp_service_account" not in st.secrets:
            return None, None, f"gcp_service_account not found. Found: {list(st.secrets.keys())}"
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sh = client.open_by_key(spreadsheet_id)
        return client, spreadsheet_id, None
    except Exception as e:
        return None, None, f"Connection Error: {e}"

def get_ws_v246(sheet_name):
    client, sid, err = get_client_v246()
    if err:
        return None, None, None, err
    try:
        sh = client.open_by_key(sid)
        all_titles = [w.title for w in sh.worksheets()]
        target = None
        for w in sh.worksheets():
            if w.title.strip().lower() == sheet_name.strip().lower():
                target = w
                break
        if not target:
            return None, all_titles, None, f"Sheet '{sheet_name}' not found. Available: {all_titles}"
        headers = target.row_values(1)
        return target, all_titles, headers, None
    except Exception as e:
        return None, None, None, f"Sheet error: {e}"

def read_sheet_v246(sheet_name):
    """FIXED: Unified name - was read_v246 causing NameError"""
    ws, titles, headers, err = get_ws_v246(sheet_name)
    if err:
        return pd.DataFrame()
    try:
        try:
            df = pd.DataFrame(ws.get_all_records())
        except:
            vals = ws.get_all_values()
            if len(vals) < 2:
                return pd.DataFrame()
            df = pd.DataFrame(vals[1:], columns=vals[0])
        return df.replace('', pd.NA).dropna(how='all')
    except:
        return pd.DataFrame()

def calculate_next_ids():
    """PLANNING: Per clinic next IDs"""
    clinic_phone = get_clinic_phone()
    df = read_sheet_v246("New_patient")
    next_patient_num = 1
    next_daily_num = 1
    
    if not df.empty and "ClinicPhone" in df.columns:
        clinic_df = df[df["ClinicPhone"].astype(str).str.strip() == str(clinic_phone).strip()]
        if not clinic_df.empty and "PatientID" in clinic_df.columns:
            nums = []
            for pid in clinic_df["PatientID"].astype(str):
                m = re.search(r'NP_(\d+)_', pid)
                if m:
                    try:
                        nums.append(int(m.group(1)))
                    except:
                        pass
                else:
                    m2 = re.search(r'NP_(\d+)', pid)
                    if m2:
                        try:
                            nums.append(int(m2.group(1)))
                        except:
                            pass
            if nums:
                next_patient_num = max(nums) + 1
        
        today_str = str(date.today())
        if "Date" in df.columns:
            today_clinic = clinic_df[clinic_df["Date"].astype(str) == today_str]
            if not today_clinic.empty:
                next_daily_num = len(today_clinic) + 1
    elif not df.empty:
        next_patient_num = len(df) + 1
        today_str = str(date.today())
        if "Date" in df.columns:
            today_df = df[df["Date"].astype(str) == today_str]
            next_daily_num = len(today_df) + 1
    
    full_patient_id = f"NP_{next_patient_num}_{clinic_phone}"
    display_patient_id = f"NP_{next_patient_num}"
    return display_patient_id, full_patient_id, next_daily_num, clinic_phone

def append_v246(sheet_name, data_dict):
    ws, titles, headers, err = get_ws_v246(sheet_name)
    if err:
        st.error(f"❌ {err}")
        return False
    if len(headers) < len(STANDARD_HEADERS_V246):
        try:
            ws.update('A1', [STANDARD_HEADERS_V246], value_input_option='USER_ENTERED')
            headers = STANDARD_HEADERS_V246
            st.toast(f"Headers extended to {len(STANDARD_HEADERS_V246)} cols", icon="✅")
            time.sleep(0.8)
        except Exception as e:
            st.warning(f"Header extend fail: {e}")
    
    row = []
    for h in headers:
        v = ""
        for k, val in data_dict.items():
            if k.strip().lower() == h.strip().lower():
                v = str(val) if val is not None else ""
                break
        row.append(v)
    
    if len(row) < len(headers):
        row += [""] * (len(headers)-len(row))
    
    try:
        ws.append_row(row, value_input_option='USER_ENTERED')
        return True
    except Exception as e:
        st.error(f"Save error: {e}")
        return False

# --- UI ---
st.title("🌿 Herbal Clinic OS - V2.4.6.1 Hotfix")
st.caption(f"Fix: NameError read_v246 | PatientID: NP_n_{get_clinic_phone()} | Display NP_n only")

clinic_phone = get_clinic_phone()
st.sidebar.success(f"V2.4.6.1 Hotfix\nClinic: {clinic_phone}\nDisplay: NP_n only")
st.sidebar.info(f"Full: NP_n_{clinic_phone}\nPhone hidden")

tabs = st.tabs(["🔧 Debug", "🧑‍⚕️ New Patient (Auto ID)", "📋 Recent", "📊 Graph"])

with tabs[0]:
    st.subheader("Debug V2.4.6.1 - NameError Fixed")
    client, sid, err = get_client_v246()
    if err:
        st.error(err)
    else:
        st.success(f"✅ Connected: {sid[:20]}... | ClinicPhone: {clinic_phone}")
        ws, titles, headers, err2 = get_ws_v246("New_patient")
        if err2:
            st.error(err2)
        else:
            st.success(f"✅ Sheet | Headers {len(headers)}/{len(STANDARD_HEADERS_V246)}")
            st.json(headers)
            disp_id, full_id, daily_n, cphone = calculate_next_ids()
            st.info(f"Next: Display={disp_id}, Full={full_id}, Daily={daily_n}")
            if len(headers) < len(STANDARD_HEADERS_V246):
                if st.button("🔧 Fix to 22 Cols", type="primary"):
                    ws.update('A1', [STANDARD_HEADERS_V246], value_input_option='USER_ENTERED')
                    st.success("Fixed to 22")
                    time.sleep(1)
                    st.rerun()

with tabs[1]:
    st.subheader("New Patient - Auto IDs at Top")
    disp_id, full_id, daily_n, cphone = calculate_next_ids()
    
    top1, top2, top3 = st.columns(3)
    with top1:
        st.metric("🆔 Patient ID", disp_id)
        st.caption(f"System: {full_id} (hidden)")
    with top2:
        st.metric("📅 Daily No", daily_n)
        st.caption(f"Clinic {cphone} | {date.today()}")
    with top3:
        st.metric("🏥 Clinic", cphone)
        st.caption("Till V2.5: 123456789")
    
    st.markdown("---")
    with st.form("new_v2461", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            name = st.text_input("Patient Name *")
            father = st.text_input(FATHER_SPOUSE_LABEL)
        with c2:
            age = st.number_input("Age", 0,120,30)
            gender = st.selectbox("Gender", ["Male / مرد","Female / عورت"])
            phone = st.text_input("Patient Phone *")
        with c3:
            city = st.text_input("City", "Bhai Pheru")
            addr = st.text_area("Address", height=60)
            dval = st.date_input("Date", value=date.today())
        
        a1,a2,a3,a4 = st.columns(4)
        with a1:
            bp = st.text_input("BP", placeholder="120/80")
            pulse = st.text_input("Pulse")
        with a2:
            weight = st.text_input("Weight")
            height = st.text_input("Height")
        with a3:
            mizaj = st.selectbox("Mizaj", ["Garm / گرم","Sard / سرد","Khushk","Tar","Garm Khushk","Garm Tar","Sard Khushk","Sard Tar","Mutadil"])
        with a4:
            fees = st.text_input("Fees", "500")
            status = st.selectbox("Status", ["New / نیا","Follow-up","Cured"])
        
        b1,b2 = st.columns(2)
        with b1:
            hist = st.text_area("History")
            comp = st.text_area("Complaint (Optional)")
        with b2:
            diag = st.text_area("Diagnosis")
            treat = st.text_area("Treatment")
        
        if st.form_submit_button(f"💾 Save {disp_id} - Daily {daily_n}", type="primary", use_container_width=True):
            if not name.strip() or not phone.strip():
                st.error("Name & Phone required")
            else:
                if not comp.strip():
                    comp = "General Checkup"
                disp_save, full_save, daily_save, cphone_save = calculate_next_ids()
                data = {
                    "PatientID": full_save,
                    "ClinicPhone": cphone_save,
                    "DailyNumber": daily_save,
                    "Date": str(dval),
                    "Name": name.strip(),
                    "FatherName": father.strip(),
                    "Age": age,
                    "Gender": gender,
                    "Phone": phone.strip(),
                    "Address": addr.strip(),
                    "City": city.strip(),
                    "BP": bp.strip(),
                    "Pulse": pulse.strip(),
                    "Weight": weight.strip(),
                    "Height": height.strip(),
                    "Temperament": mizaj,
                    "History": hist.strip(),
                    "Complaint": comp.strip(),
                    "Diagnosis": diag.strip(),
                    "Treatment": treat.strip(),
                    "Fees": fees.strip(),
                    "Status": status
                }
                with st.spinner(f"Saving {disp_save}..."):
                    if append_v246("New_patient", data):
                        st.success(f"✅ Saved! Display: {disp_save} | Daily: {daily_save} | System: {full_save}")
                        st.balloons()
                    else:
                        st.error("Save failed")

with tabs[2]:
    df = read_sheet_v246("New_patient")
    if not df.empty:
        cphone = get_clinic_phone()
        if "ClinicPhone" in df.columns:
            clinic_df = df[df["ClinicPhone"].astype(str) == str(cphone)]
            st.write(f"This Clinic ({cphone}): {len(clinic_df)} / All Clinics Total: {len(df)}")
            if not clinic_df.empty:
                clinic_df = clinic_df.copy()
                clinic_df["DisplayID"] = clinic_df["PatientID"].astype(str).apply(lambda x: '_'.join(x.split('_')[:2]) if x.count('_')>=2 else x)
                st.dataframe(clinic_df[["DisplayID","DailyNumber","Date","Name","FatherName","Phone"]].tail(10).sort_index(ascending=False), use_container_width=True)
                st.dataframe(clinic_df.tail(1).T, use_container_width=True)
        else:
            st.dataframe(df.tail(10), use_container_width=True)
    else:
        st.info("No data")

with tabs[3]:
    df = read_sheet_v246("New_patient")
    cphone = get_clinic_phone()
    if not df.empty and "ClinicPhone" in df.columns:
        clinic_df = df[df["ClinicPhone"].astype(str) == str(cphone)]
        if not clinic_df.empty and "Date" in clinic_df.columns:
            daily_counts = clinic_df.groupby("Date").size().reset_index(name="Patients")
            st.bar_chart(daily_counts.set_index("Date"))
            st.dataframe(daily_counts.sort_values("Date", ascending=False), use_container_width=True)
    else:
        st.info("No graph data yet")

st.caption("V2.4.6.1 Hotfix: NameError read_v246 fixed -> read_sheet_v246 | Planning in comments | 22 cols | Same ID")
