"""
Herbal Clinic OS - V2.4.2 - Connection Fix
Fix: 'NoneType' object has no attribute '_instance' + Worksheet not found
Solution: Direct gspread client from secrets.toml
Same Sheet ID & secrets.toml - Auth Muted till V2.5
"""
import streamlit as st
import pandas as pd
from datetime import date
import time

st.set_page_config(page_title="Herbal Clinic OS - V2.4.2", layout="wide", page_icon="🌿")

# --- Imports ---
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError as e:
    GSPREAD_AVAILABLE = False
    st.error(f"gspread missing: {e} - add to requirements.txt: gspread, google-auth")

# --- UI Lang ---
LANG = st.sidebar.selectbox("Language / زبان", ["Urdu + English", "English", "اردو"], index=0)
def tr(en, ur):
    return en if LANG=="English" else ur if LANG=="اردو" else f"{en} / {ur}"

st.sidebar.success("V2.4.2 - Connection Fix")
st.sidebar.info("Fix: _instance bug\nFather/Spouse ✅\nColumn Fix ✅")

# --- CONNECTION FIX V2.4.2 ---
STANDARD_HEADERS = [
    "DailyNumber", "Date", "Name", "FatherName", "Age", "Gender", 
    "Phone", "Address", "City",
    "BP", "Pulse", "Weight", "Height", "Temperament", "History", "Complaint", "Diagnosis", "Treatment", "Fees", "Status"
]
FATHER_SPOUSE_LABEL = "Father Name / Spouse Name / باپ / سپاس کا نام"

@st.cache_resource
def get_client_and_sheet_id():
    """Direct gspread from secrets.toml - no _instance"""
    try:
        # secrets.toml structure: [connections.gsheets] -> spreadsheet = "ID" + service account keys
        gsheets_secrets = st.secrets["connections"]["gsheets"]
        spreadsheet_id = gsheets_secrets.get("spreadsheet", "")
        
        # Build credentials dict - remove spreadsheet key
        creds_dict = {}
        for k,v in gsheets_secrets.items():
            if k != "spreadsheet":
                creds_dict[k] = v
        
        # Agar credentials nested hain (kabhi kabhi esa hota hai)
        if "type" not in creds_dict and len(creds_dict)==1:
            # maybe gsheets contains single key with all creds?
            first_key = list(creds_dict.keys())[0]
            if isinstance(creds_dict[first_key], dict):
                creds_dict = creds_dict[first_key]
        
        # Required scopes
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        return client, spreadsheet_id, None
    except Exception as e:
        return None, None, f"{e}"

def get_ws_headers_v2(sheet_name):
    client, spreadsheet_id, err = get_client_and_sheet_id()
    if err:
        return None, None, [f"Secrets Error: {err}"]
    try:
        sh = client.open_by_key(spreadsheet_id)
        # List all sheets for debug
        all_titles = [ws.title for ws in sh.worksheets()]
        # Find sheet case-insensitive
        target_ws = None
        for ws in sh.worksheets():
            if ws.title.lower() == sheet_name.lower():
                target_ws = ws
                break
        if not target_ws:
            return None, all_titles, [f"Worksheet '{sheet_name}' not found. Available: {all_titles}"]
        
        headers = target_ws.row_values(1)
        return target_ws, all_titles, headers
    except Exception as e:
        return None, None, [f"Error: {e}"]

def append_row_fixed(sheet_name, data_dict):
    ws, all_titles, headers_or_err = get_ws_headers_v2(sheet_name)
    if ws is None:
        st.error(f"❌ {sheet_name} - {headers_or_err} | All Sheets: {all_titles}")
        return False
    
    actual_headers = headers_or_err
    # Auto extend if old 9 cols
    if len(actual_headers) < len(STANDARD_HEADERS):
        try:
            ws.update('A1:T1', [STANDARD_HEADERS])
            actual_headers = STANDARD_HEADERS
            st.toast(f"Headers extended to 20 cols for {sheet_name}", icon="🔧")
            time.sleep(1)
        except Exception as e:
            st.warning(f"Header extend fail: {e}")
    
    # Build row in actual order
    row = []
    for h in actual_headers:
        found = ""
        for k,v in data_dict.items():
            if k.lower() == h.lower():
                found = v
                break
        row.append(found)
    
    try:
        ws.append_row(row)
        return True
    except Exception as e:
        st.error(f"Append Error: {e}")
        return False

def read_sheet_fixed(sheet_name):
    client, spreadsheet_id, err = get_client_and_sheet_id()
    if err:
        st.error(f"Connection Error: {err}")
        return pd.DataFrame()
    try:
        sh = client.open_by_key(spreadsheet_id)
        ws = None
        for w in sh.worksheets():
            if w.title.lower() == sheet_name.lower():
                ws = w
                break
        if not ws:
            return pd.DataFrame()
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        df = df.dropna(how='all')
        return df
    except Exception as e:
        st.error(f"Read {sheet_name} Error: {e}")
        return pd.DataFrame()

# --- HEADER ---
st.title(tr("🌿 Herbal Clinic OS - V2.4.2 (Connection Fixed)", "🌿 ہربل کلینک - V2.4.2 کنکشن فکس"))
st.caption("Fix: 'NoneType _instance' + 'Worksheet not found' | Same Sheet ID")

tabs = st.tabs([tr("🔧 Debug Connection", "🔧 کنکشن چیک"), tr("🧑‍⚕️ New Patient", "🧑‍⚕️ نیا مریض"), tr("📋 Recent", "📋 حالیہ"), tr("🔍 Search", "🔍 تلاش")])

with tabs[0]:
    st.subheader("Connection & Sheets Debug - V2.4.2")
    client, sid, err = get_client_and_sheet_id()
    if err:
        st.error(f"Secrets Error: {err}")
        st.code(f"st.secrets keys: {list(st.secrets['connections']['gsheets'].keys()) if 'connections' in st.secrets and 'gsheets' in st.secrets['connections'] else 'NO gsheets in secrets'}")
    else:
        st.success(f"✅ Connected | Spreadsheet ID: {sid[:20]}...")
        ws, all_titles, headers = get_ws_headers_v2("New_patient")
        if ws:
            st.success(f"✅ Worksheet 'New_patient' FOUND")
            st.write(f"All 20 Sheets: {all_titles}")
            st.json(headers)
            st.write(f"Count: {len(headers)} / Expected: 20")
            if len(headers) < 20:
                if st.button("🔧 Fix Headers to 20 Columns Now", type="primary"):
                    ws.update('A1:T1', [STANDARD_HEADERS])
                    st.success("Fixed! 20 columns set")
                    st.rerun()
            else:
                st.success("✅ Headers OK - 20 cols")
        else:
            st.error(f"❌ {headers}")
            st.write(f"Available sheets: {all_titles}")

with tabs[1]:
    st.subheader(tr("New Patient - V2.4.2 Fixed", "نیا مریض - V2.4.2 فکس"))
    with st.form("new_patient_242", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            daily_no = st.text_input("Daily Number", value=str(int(time.time())%10000))
            name = st.text_input("Patient Name * / مریض نام *")
            father_spouse = st.text_input(FATHER_SPOUSE_LABEL, placeholder="For male: Father, female: Spouse")
        with c2:
            age = st.number_input("Age / عمر", 0,120,30)
            gender = st.selectbox("Gender / جنس", ["Male / مرد","Female / عورت"])
            phone = st.text_input("Phone * / فون *")
        with c3:
            city = st.text_input("City", "Bhai Pheru")
            address = st.text_area("Address", height=68)
            date_val = st.date_input("Date", value=date.today())
        st.markdown("---")
        a1,a2,a3,a4 = st.columns(4)
        with a1:
            bp = st.text_input("BP", placeholder="120/80")
            pulse = st.text_input("Pulse")
        with a2:
            weight = st.text_input("Weight")
            height = st.text_input("Height")
        with a3:
            temperament = st.selectbox("Mizaj / مزاج", ["Garm / گرم","Sard / سرد","Khushk / خشک","Tar / تر","Garm Khushk","Garm Tar","Sard Khushk","Sard Tar","Mutadil / معتدل"])
        with a4:
            fees = st.text_input("Fees", "500")
            status = st.selectbox("Status", ["New / نیا","Follow-up","Cured"])
        b1,b2 = st.columns(2)
        with b1:
            history = st.text_area("Past History")
            complaint = st.text_area("Complaint / شکایت (Optional)")
        with b2:
            diagnosis = st.text_area("Diagnosis")
            treatment = st.text_area("Treatment")
        
        submitted = st.form_submit_button("💾 Save Patient - V2.4.2", type="primary", use_container_width=True)
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
                with st.spinner("Saving with Direct gspread..."):
                    ok = append_row_fixed("New_patient", data_dict)
                    if ok:
                        st.success(f"✅ Saved! {name} | Daily: {daily_no}")
                        st.balloons()
                    else:
                        st.error("Save failed - see Debug tab")

with tabs[2]:
    df = read_sheet_fixed("New_patient")
    if not df.empty:
        st.write(f"Total: {len(df)}")
        st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)
        last = df.tail(1).T
        st.dataframe(last, use_container_width=True)
    else:
        st.info("No data or sheet empty")

with tabs[3]:
    df = read_sheet_fixed("New_patient")
    if not df.empty:
        term = st.text_input("Search Name/Phone/Father")
        if term:
            mask = df.astype(str).apply(lambda x: x.str.contains(term, case=False, na=False)).any(axis=1)
            st.dataframe(df[mask], use_container_width=True)

st.caption("V2.4.2 | Direct gspread | No _instance | Auto 20 cols | Father/Spouse (باپ/سپاس) | Auth Muted till V2.5")
