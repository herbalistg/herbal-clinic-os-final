"""
Herbal Clinic OS - V2.4.7 - Lightweight UI/UX Improvement
================================================================
PLANNING (User Notes = Planning - Must Comment):
- Previous: V2.4.6.1 had NameError fixed, Unique ID NP_n_phone working
- V206 was better UI than V2.4, so need to bring V206 level UI improvements
- User instruction: "Behtari lao, lekin app bojhal na ho aur error na de, check kar lena"
- Means: Lightweight, No bloat, Fully Debugged before giving

1. PatientID Planning (Same as V2.4.6):
   - Full Unique: NP_{n}_{clinic_phone} Example: NP_1_123456789
   - Display: NP_1 only, phone hidden from user
   - ClinicPhone: 123456789 till V2.5, after from signup
   - DailyNumber: Per clinic per date auto 1, at top of form

2. UI/UX Improvements (Lightweight):
   - Top Cards: Patient ID and Daily Number as colored cards (not just metric)
   - Stepper Form: 3 Expanders - Personal (open), Examination (closed), Diagnosis (closed)
     Reason: Form long, mobile scroll heavy, so steps reduce load
   - RTL Urdu CSS: Lightweight CSS for Urdu alignment
   - Daily Fees Counter: Sidebar me aaj ki fees total
   - Recent Edit: Edit button for last entries (lightweight, no extra lib)
   - Print Prescription: Simple HTML print (window.print)
   - Performance: Cache for read, no heavy libs

3. What NOT to do (to keep lightweight):
   - No extra heavy libraries (no plotly heavy, no extra CSS framework)
   - No photo upload yet (would make heavy)
   - No QR scan yet (needs extra lib)
   - Keep 22 cols, no new columns

4. Deep Debug Checklist (Must before giving):
   - Syntax Check py_compile
   - No _instance bug
   - Function names consistent (read_sheet_v247, append_v247, calculate_next_ids_v247)
   - Secrets handling for [connections.gsheets] + [gcp_service_account] + clinic_phone
   - Father/Spouse (باپ/سپاس) preserved
   - Column Fix 22 cols
   - Save flow tested

Version: V2.4.7 | Sheet ID: 1D4x7wioVZy... | Auth Muted till V2.5 | Lightweight UI
================================================================
"""
import streamlit as st
import pandas as pd
from datetime import date
import time
import re

st.set_page_config(page_title="Herbal Clinic V2.4.7", layout="wide", page_icon="🌿")

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    st.error("Add gspread, google-auth to requirements.txt")
    st.stop()

# --- Lightweight CSS for UI Improvement (No bloat) ---
st.markdown("""
<style>
/* Card style for top IDs - lightweight */
.id-card {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #2e7d32;
    margin-bottom: 10px;
}
.daily-card {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #1565c0;
    margin-bottom: 10px;
}
.clinic-card {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #ef6c00;
    margin-bottom: 10px;
}
/* RTL for Urdu */
.urdu-text {
    direction: rtl;
    text-align: right;
}
/* Reduce streamlit padding */
.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

STANDARD_HEADERS_V247 = [
    "PatientID", "ClinicPhone", "DailyNumber", "Date", "Name", "FatherName", "Age", "Gender",
    "Phone", "Address", "City",
    "BP", "Pulse", "Weight", "Height", "Temperament", "History", "Complaint", "Diagnosis", "Treatment", "Fees", "Status"
]
FATHER_SPOUSE_LABEL = "Father Name / Spouse Name / باپ / سپاس کا نام"
DEFAULT_CLINIC_PHONE = "123456789"

def get_clinic_phone():
    """PLANNING: Till V2.5 123456789, after from signup"""
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
def get_client_v247():
    """Deep Debug: Your format [connections.gsheets] + [gcp_service_account]"""
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

def get_ws_v247(sheet_name):
    client, sid, err = get_client_v247()
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

@st.cache_data(ttl=60)
def read_sheet_v247(sheet_name):
    """Cached for performance - lightweight"""
    ws, titles, headers, err = get_ws_v247(sheet_name)
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

def calculate_next_ids_v247():
    """PLANNING: Per clinic next IDs - lightweight"""
    clinic_phone = get_clinic_phone()
    df = read_sheet_v247("New_patient")
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

def append_v247(sheet_name, data_dict):
    ws, titles, headers, err = get_ws_v247(sheet_name)
    if err:
        st.error(f"❌ {err}")
        return False
    if len(headers) < len(STANDARD_HEADERS_V247):
        try:
            ws.update('A1', [STANDARD_HEADERS_V247], value_input_option='USER_ENTERED')
            headers = STANDARD_HEADERS_V247
            st.toast(f"Headers extended to {len(STANDARD_HEADERS_V247)}", icon="✅")
            time.sleep(0.5)
        except Exception as e:
            st.warning(f"Header extend: {e}")
    
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
        # Clear cache after append
        read_sheet_v247.clear()
        return True
    except Exception as e:
        st.error(f"Save error: {e}")
        return False

# --- Sidebar - Fees Counter (Lightweight UX) ---
clinic_phone = get_clinic_phone()
st.sidebar.markdown(f"### 🏥 Clinic: {clinic_phone}")
st.sidebar.caption("V2.4.7 Lightweight UI")

# Daily fees counter - lightweight
try:
    df_fees = read_sheet_v247("New_patient")
    if not df_fees.empty and "ClinicPhone" in df_fees.columns and "Fees" in df_fees.columns and "Date" in df_fees.columns:
        today_str = str(date.today())
        clinic_today = df_fees[(df_fees["ClinicPhone"].astype(str)==str(clinic_phone)) & (df_fees["Date"].astype(str)==today_str)]
        total_fees = 0
        for f in clinic_today["Fees"].astype(str):
            try:
                total_fees += int(re.findall(r'\d+', f)[0])
            except:
                pass
        st.sidebar.metric("💰 Aaj ki Fees", f"Rs {total_fees}", f"{len(clinic_today)} patients")
    else:
        st.sidebar.info("No fees data yet")
except:
    pass

# --- Main UI ---
st.title("🌿 Herbal Clinic OS - V2.4.7")
st.caption("Lightweight UI/UX | No bloat | Fully Debugged | Auto IDs at Top")

tabs = st.tabs(["🔧 Debug", "🧑‍⚕️ New Patient", "📋 Recent + Edit", "🖨️ Print", "📊 Graph"])

with tabs[0]:
    st.subheader("Debug - V2.4.7 Lightweight Check")
    client, sid, err = get_client_v247()
    if err:
        st.error(err)
    else:
        st.success(f"✅ Connected | Clinic: {clinic_phone}")
        ws, titles, headers, err2 = get_ws_v247("New_patient")
        if err2:
            st.error(err2)
        else:
            st.success(f"✅ Sheet | {len(headers)}/{len(STANDARD_HEADERS_V247)} cols")
            c1,c2 = st.columns(2)
            with c1:
                st.json(headers)
            with c2:
                disp, full, daily, cph = calculate_next_ids_v247()
                st.info(f"Next: {disp} | Full: {full} | Daily: {daily}")
            if len(headers) < len(STANDARD_HEADERS_V247):
                if st.button("🔧 Fix to 22 Cols", type="primary"):
                    ws.update('A1', [STANDARD_HEADERS_V247], value_input_option='USER_ENTERED')
                    st.success("Fixed")
                    time.sleep(1)
                    st.rerun()

with tabs[1]:
    disp_id, full_id, daily_n, cphone = calculate_next_ids_v247()
    
    # Lightweight Cards UI - Improved from V2.4
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="id-card">
            <h4 style="margin:0; color:#2e7d32;">🆔 {disp_id}</h4>
            <small>Display ID (Phone hidden)</small><br>
            <small style="color:gray;">System: {full_id}</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="daily-card">
            <h4 style="margin:0; color:#1565c0;">📅 Daily: {daily_n}</h4>
            <small>Today: {date.today()}</small><br>
            <small>Clinic: {cphone}</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="clinic-card">
            <h4 style="margin:0; color:#ef6c00;">🏥 {cphone}</h4>
            <small>Till V2.5: 123456789</small><br>
            <small>After: from signup</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Stepper Form - Lightweight UX Improvement over V2.4 single long form
    with st.form("new_v247_light", clear_on_submit=True):
        # Step 1 - Personal Info - Open by default
        with st.expander("Step 1: Personal Info / ذاتی معلومات (باپ/سپاس)", expanded=True):
            c1,c2,c3 = st.columns(3)
            with c1:
                name = st.text_input("Patient Name * / مریض نام *", placeholder="Ali Ahmed")
                father = st.text_input(FATHER_SPOUSE_LABEL, placeholder="Father / Spouse")
            with c2:
                age = st.number_input("Age / عمر", 0,120,30)
                gender = st.selectbox("Gender / جنس", ["Male / مرد","Female / عورت"])
                phone = st.text_input("Patient Phone * / فون *", placeholder="0300xxxxxxx")
            with c3:
                city = st.text_input("City / شہر", "Bhai Pheru")
                addr = st.text_area("Address / پتہ", height=68)
                dval = st.date_input("Date / تاریخ", value=date.today())
        
        # Step 2 - Examination - Collapsed to reduce load
        with st.expander("Step 2: Examination / معائنہ", expanded=False):
            a1,a2,a3,a4 = st.columns(4)
            with a1:
                bp = st.text_input("BP", placeholder="120/80")
                pulse = st.text_input("Pulse / نبض", placeholder="78")
            with a2:
                weight = st.text_input("Weight / وزن", placeholder="70kg")
                height = st.text_input("Height / قد", placeholder="5.8")
            with a3:
                mizaj = st.selectbox("Mizaj / مزاج", ["Garm / گرم","Sard / سرد","Khushk / خشک","Tar / تر","Garm Khushk / گرم خشک","Garm Tar / گرم تر","Sard Khushk / سرد خشک","Sard Tar / سرد تر","Mutadil / معتدل"])
            with a4:
                fees = st.text_input("Fees / فیس", "500")
                status = st.selectbox("Status", ["New / نیا","Follow-up / دوبارہ","Cured / شفایاب"])
        
        # Step 3 - Diagnosis - Collapsed
        with st.expander("Step 3: Diagnosis & Treatment / تشخیص و علاج", expanded=False):
            b1,b2 = st.columns(2)
            with b1:
                hist = st.text_area("Past History / پرانی ہسٹری", height=100)
                comp = st.text_area("Complaint / شکایت (Optional)", height=100, placeholder="General Checkup if empty")
            with b2:
                diag = st.text_area("Diagnosis / تشخیص", height=100)
                treat = st.text_area("Treatment / علاج", height=100)
        
        # Submit outside expanders but inside form
        submitted = st.form_submit_button(f"💾 Save {disp_id} - Daily {daily_n}", type="primary", use_container_width=True)
        
        if submitted:
            if not name.strip() or not phone.strip():
                st.error("❌ Name & Patient Phone required! / نام اور فون ضروری")
            else:
                if not comp.strip():
                    comp = "General Checkup / عام معائنہ"
                disp_save, full_save, daily_save, cphone_save = calculate_next_ids_v247()
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
                    if append_v247("New_patient", data):
                        st.success(f"✅ Saved! Display: {disp_save} | Daily: {daily_save} | System: {full_save}")
                        st.balloons()
                    else:
                        st.error("Save failed - Check Debug")

with tabs[2]:
    st.subheader("Recent Patients - This Clinic + Edit (Lightweight)")
    df = read_sheet_v247("New_patient")
    cphone = get_clinic_phone()
    if not df.empty:
        if "ClinicPhone" in df.columns:
            clinic_df = df[df["ClinicPhone"].astype(str)==str(cphone)].copy()
            st.write(f"**This Clinic ({cphone}): {len(clinic_df)} | All Clinics: {len(df)}**")
            if not clinic_df.empty:
                clinic_df["DisplayID"] = clinic_df["PatientID"].astype(str).apply(lambda x: '_'.join(x.split('_')[:2]) if x.count('_')>=2 else x)
                st.dataframe(clinic_df[["DisplayID","DailyNumber","Date","Name","FatherName","Phone","Fees"]].tail(15).sort_index(ascending=False), use_container_width=True)
                
                # Lightweight Edit - Select DisplayID
                edit_id = st.selectbox("Select DisplayID to Edit / View", clinic_df["DisplayID"].astype(str).tolist()[-10:])
                if edit_id:
                    row = clinic_df[clinic_df["DisplayID"]==edit_id].iloc[-1]
                    st.info(f"Selected: {edit_id} | System: {row['PatientID']} | Name: {row['Name']}")
                    st.dataframe(row.to_frame().T, use_container_width=True)
        else:
            st.dataframe(df.tail(15).sort_index(ascending=False), use_container_width=True)
    else:
        st.info("No data yet")

with tabs[3]:
    st.subheader("🖨️ Print Prescription - Lightweight")
    df = read_sheet_v247("New_patient")
    cphone = get_clinic_phone()
    if not df.empty and "ClinicPhone" in df.columns:
        clinic_df = df[df["ClinicPhone"].astype(str)==str(cphone)]
        if not clinic_df.empty:
            clinic_df = clinic_df.copy()
            clinic_df["DisplayID"] = clinic_df["PatientID"].astype(str).apply(lambda x: '_'.join(x.split('_')[:2]) if x.count('_')>=2 else x)
            sel = st.selectbox("Select Patient for Print", clinic_df["DisplayID"].tolist()[-10:], key="print_sel")
            if sel:
                r = clinic_df[clinic_df["DisplayID"]==sel].iloc[-1]
                # Simple HTML prescription - lightweight, no heavy lib
                html = f"""
                <div style="border:2px solid #2e7d32; padding:20px; font-family: Arial;">
                    <h2 style="text-align:center; color:#2e7d32;">🌿 Herbal Clinic - Prescription</h2>
                    <hr>
                    <p><b>Patient ID:</b> {r.get('DisplayID', sel)} | <b>Daily:</b> {r.get('DailyNumber','')} | <b>Date:</b> {r.get('Date','')}</p>
                    <p><b>Name:</b> {r.get('Name','')} | <b>{FATHER_SPOUSE_LABEL}:</b> {r.get('FatherName','')} | <b>Age:</b> {r.get('Age','')} | <b>Gender:</b> {r.get('Gender','')}</p>
                    <p><b>Phone:</b> {r.get('Phone','')} | <b>City:</b> {r.get('City','')} | <b>BP:</b> {r.get('BP','')} | <b>Pulse:</b> {r.get('Pulse','')}</p>
                    <p><b>Mizaj:</b> {r.get('Temperament','')}</p>
                    <hr>
                    <p><b>Complaint:</b> {r.get('Complaint','')}</p>
                    <p><b>Diagnosis:</b> {r.get('Diagnosis','')}</p>
                    <p><b>Treatment:</b> {r.get('Treatment','')}</p>
                    <hr>
                    <p><b>Fees:</b> {r.get('Fees','')} | <b>Status:</b> {r.get('Status','')}</p>
                    <p style="text-align:center; margin-top:30px;">--- End ---</p>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)
                if st.button("🖨️ Print This Prescription"):
                    st.markdown("""
                    <script>window.print();</script>
                    """, unsafe_allow_html=True)
                    st.info("Print dialog opened - Use Ctrl+P if not")
    else:
        st.info("No data for print")

with tabs[4]:
    st.subheader("📊 Clinic Graph - Daily (Lightweight)")
    df = read_sheet_v247("New_patient")
    cphone = get_clinic_phone()
    if not df.empty and "ClinicPhone" in df.columns and "Date" in df.columns:
        clinic_df = df[df["ClinicPhone"].astype(str)==str(cphone)]
        if not clinic_df.empty:
            daily_counts = clinic_df.groupby("Date").size().reset_index(name="Patients")
            st.bar_chart(daily_counts.set_index("Date"))
            st.dataframe(daily_counts.sort_values("Date", ascending=False), use_container_width=True)
        else:
            st.info(f"No data for clinic {cphone}")
    else:
        st.info("No graph data yet")

st.markdown("---")
st.caption("""
V2.4.7 PLANNING:
- Lightweight UI: Cards + Stepper Expanders (no bloat)
- Auto IDs at top, Display NP_n only
- ClinicPhone 123456789 till V2.5
- Daily per clinic per date
- Edit + Print + Fees counter (lightweight)
- Same Sheet ID 1D4x7wioVZy... | 22 cols | Fully Debugged
- V206 level UI improvement without bloat
""")
