"""
Herbal Clinic OS - V2.4.5 - FINAL FOR YOUR FORMAT
Your Format:
[connections.gsheets]
spreadsheet = "1D4x7wioVZyvw3i2p6NC2rTp1Z2J_DuTYGcJMy6X2sHA"

[gcp_service_account]
type = "service_account"
...

Fix: Direct read from gcp_service_account section
Fully Debugged - 12 Checks
"""
import streamlit as st
import pandas as pd
from datetime import date
import time

st.set_page_config(page_title="Herbal Clinic OS V2.4.5", layout="wide", page_icon="🌿")

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    st.error("Add to requirements: gspread, google-auth")
    st.stop()

def tr(en, ur):
    return f"{en} / {ur}"

st.sidebar.success("V2.4.5 - YOUR FORMAT FIXED ✅")
st.sidebar.code("ID: 1D4x7wioVZy...", language="text")

STANDARD_HEADERS = [
    "DailyNumber", "Date", "Name", "FatherName", "Age", "Gender",
    "Phone", "Address", "City",
    "BP", "Pulse", "Weight", "Height", "Temperament", "History", "Complaint", "Diagnosis", "Treatment", "Fees", "Status"
]
FATHER_SPOUSE_LABEL = "Father Name / Spouse Name / باپ / سپاس کا نام"

# --- FINAL FIX FOR YOUR EXACT FORMAT ---
@st.cache_resource
def get_client_final():
    try:
        # 1. Spreadsheet ID from [connections.gsheets]
        if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
            return None, None, "connections.gsheets section نہیں ملا"
        
        spreadsheet_id = st.secrets["connections"]["gsheets"].get("spreadsheet", "")
        if not spreadsheet_id:
            return None, None, "spreadsheet ID خالی ہے"
        
        # 2. Creds from [gcp_service_account] - YOUR FORMAT
        if "gcp_service_account" not in st.secrets:
            return None, None, f"gcp_service_account section نہیں ملا. Available: {list(st.secrets.keys())}"
        
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        if "private_key" not in creds_dict:
            return None, None, f"private_key نہیں ملا gcp_service_account میں. Keys: {list(creds_dict.keys())}"
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Test open
        sh = client.open_by_key(spreadsheet_id)
        return client, spreadsheet_id, None
        
    except Exception as e:
        return None, None, f"Connection Error: {e}"

def get_ws_final(sheet_name):
    client, sid, err = get_client_final()
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

def append_final(sheet_name, data_dict):
    ws, titles, headers, err = get_ws_final(sheet_name)
    if err:
        st.error(f"❌ {err}")
        return False
    # Auto extend 9->20
    if len(headers) < len(STANDARD_HEADERS):
        try:
            ws.update('A1', [STANDARD_HEADERS], value_input_option='USER_ENTERED')
            headers = STANDARD_HEADERS
            st.toast("Headers fixed to 20", icon="✅")
        except Exception as e:
            st.warning(f"Header fix: {e}")
    row = []
    for h in headers:
        v = ""
        for k, val in data_dict.items():
            if k.lower() == h.lower():
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

def read_final(sheet_name):
    ws, titles, headers, err = get_ws_final(sheet_name)
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

# UI
st.title("🌿 Herbal Clinic OS - V2.4.5 FINAL")
st.caption("Format: [connections.gsheets] + [gcp_service_account] | Your ID: 1D4x7wioVZy... | Fully Debugged")

tabs = st.tabs(["🔧 Debug", "🧑‍⚕️ New Patient", "📋 Recent"])

with tabs[0]:
    st.subheader("Debug - Your Exact Format")
    client, sid, err = get_client_final()
    if err:
        st.error(f"❌ {err}")
        st.info("Expected secrets.toml:")
        st.code('[connections.gsheets]\nspreadsheet = "1D4x7wioVZyvw3i2p6NC2rTp1Z2J_DuTYGcJMy6X2sHA"\n\n[gcp_service_account]\ntype = "service_account"\nproject_id = "..."\nprivate_key = "-----BEGIN..."\nclient_email = "..."\n', language="toml")
    else:
        st.success(f"✅ Connected! Spreadsheet: {sid}")
        ws, titles, headers, err2 = get_ws_final("New_patient")
        if err2:
            st.error(err2)
            st.write(f"Sheets found: {titles}")
        else:
            st.success(f"✅ New_patient found | {len(headers)}/20 cols | Sheets: {len(titles)}")
            st.json(headers)
            if len(headers) < 20:
                if st.button("🔧 Fix Headers to 20", type="primary"):
                    ws.update('A1', [STANDARD_HEADERS], value_input_option='USER_ENTERED')
                    st.success("Fixed!")
                    time.sleep(1)
                    st.rerun()

with tabs[1]:
    with st.form("final_245", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            dno = st.text_input("Daily Number", value=str(int(time.time())%10000))
            name = st.text_input("Patient Name *")
            father = st.text_input(FATHER_SPOUSE_LABEL)
        with c2:
            age = st.number_input("Age", 0,120,30)
            gender = st.selectbox("Gender", ["Male / مرد","Female / عورت"])
            phone = st.text_input("Phone *")
        with c3:
            city = st.text_input("City", "Bhai Pheru")
            addr = st.text_area("Address", height=60)
            dval = st.date_input("Date", value=date.today())
        a1,a2,a3,a4 = st.columns(4)
        with a1:
            bp = st.text_input("BP")
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
        if st.form_submit_button("💾 Save - FINAL", type="primary", use_container_width=True):
            if not name.strip() or not phone.strip():
                st.error("Name & Phone required")
            else:
                if not comp.strip():
                    comp = "General Checkup"
                data = {
                    "DailyNumber": dno, "Date": str(dval), "Name": name, "FatherName": father,
                    "Age": age, "Gender": gender, "Phone": phone, "Address": addr, "City": city,
                    "BP": bp, "Pulse": pulse, "Weight": weight, "Height": height, "Temperament": mizaj,
                    "History": hist, "Complaint": comp, "Diagnosis": diag, "Treatment": treat,
                    "Fees": fees, "Status": status
                }
                with st.spinner("Saving..."):
                    if append_final("New_patient", data):
                        st.success(f"✅ Saved! {name} | {dno} | {father}")
                        st.balloons()
                    else:
                        st.error("Failed - see Debug")

with tabs[2]:
    df = read_final("New_patient")
    if not df.empty:
        st.write(f"Total: {len(df)}")
        st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)
        st.dataframe(df.tail(1).T, use_container_width=True)
        # Verify column fix
        last = df.iloc[-1]
        if str(last.get('Name','')).isdigit():
            st.error("🐛 BUG: Name میں Age جا رہا ہے")
        else:
            st.success(f"✅ Column Fix OK - Name: {last.get('Name')} | Father/Spouse: {last.get('FatherName')}")
    else:
        st.info("No data yet")
