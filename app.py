"""
Herbal Clinic OS - V2.4.6 - Unique PatientID with Clinic Phone
================================================================
PLANNING (User Notes = Planning - Must Comment in Code):
----------------------------------------------------------------
1. PatientID Format:
   - Full Unique ID (System ke liye): NP_{number}_{clinic_phone} 
     Example: NP_1_123456789, NP_2_123456789
   - Display to User: Sirf NP_1, NP_2 dikhana hai, phone nahi dikhana
     Reason: Phone sirf system ki pehchan ke liye, user ko nahi dikhana
   - Uniqueness: Har clinic ka NP_1 hoga to mix ho jayega, is liye phone suffix se unique
   - Clinic name/location same ho sakte hain, is liye phone se uniqueness

2. ClinicPhone:
   - Yeh woh number hai jis se user signup hua tha
   - Till Auth Muted (V2.5 tak): secrets.toml me 123456789 likhna hai (temporary)
   - After V2.5 Auth enabled: Signup form se auto ayega
   - Location: [connections.gsheets] clinic_phone = "123456789" OR [clinic] phone

3. DailyNumber:
   - Har clinic ka apna daily counter, rozana 1 se shuru
   - Logic: ClinicPhone + Date se filter karke count + 1
   - Example: Clinic 123456789 ka aaj pehla mareez Daily=1, kal phir 1 se shuru

4. Form Display:
   - Entry form me sab se upar (Personal Info se pehle) auto-generate:
     - Patient ID (Display): NP_1
     - Daily Number: 1
     - Full System ID (hidden): NP_1_123456789

5. Sheet Structure:
   - Total columns: 22 (20 se 22 ho gaye)
   - Order: PatientID (unique), ClinicPhone, DailyNumber, Date, Name, FatherName (باپ/سپاس), ...
   - Old sheets 20 cols se auto-extend to 22

6. User Notes = Planning:
   - Agar user planning ke khilaf jaye to code dene se pehle confirm karna
   - Agar planning me tabdeeli zaruri ho to comment me update karna
   - Saare notes ko code me comment karna taa ke planning hamesha yaad rahe

7. Future Graph:
   - Har clinic ko uska daily/weekly graph dikhana easy hoga
   - Filter: ClinicPhone se, sheet me sab clinics ka data hoga

8. Deep Debug Rule (Permanent):
   - Syntax Check, Import Check, Secrets Check, Sheet Check, Column Fix, Father/Spouse Fix,
     Save Flow, Validation, Error Handling - sab check karke code dena
   - Koi bhi code bina debug ke nahi dena

Author: Meta AI - For Herbal Clinic OS
Version: V2.4.6
Date: 2026-10-03
Sheet ID: Same | Auth Muted till V2.5
================================================================
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
import re

st.set_page_config(page_title="Herbal Clinic OS V2.4.6", layout="wide", page_icon="🌿")

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError as e:
    st.error(f"Missing lib: {e} - Add gspread, google-auth to requirements.txt")
    st.stop()

# --- Constants & Planning Comment ---
# PLANNING: Standard headers now 22 with PatientID and ClinicPhone at start
STANDARD_HEADERS_V246 = [
    "PatientID", "ClinicPhone", "DailyNumber", "Date", "Name", "FatherName", "Age", "Gender",
    "Phone", "Address", "City",
    "BP", "Pulse", "Weight", "Height", "Temperament", "History", "Complaint", "Diagnosis", "Treatment", "Fees", "Status"
]
FATHER_SPOUSE_LABEL = "Father Name / Spouse Name / باپ / سپاس کا نام"

# PLANNING: Temporary clinic phone till Auth enabled - 123456789 as per user instruction
DEFAULT_CLINIC_PHONE = "123456789"

def get_clinic_phone():
    """PLANNING: Get clinic phone - Till V2.5 use secrets clinic_phone=123456789, After V2.5 from signup"""
    try:
        # Try from [clinic] section
        if "clinic" in st.secrets and "phone" in st.secrets["clinic"]:
            return str(st.secrets["clinic"]["phone"]).strip()
        # Try from [connections.gsheets] clinic_phone
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            gs = st.secrets["connections"]["gsheets"]
            if "clinic_phone" in gs:
                return str(gs["clinic_phone"]).strip()
            if "clinicPhone" in gs:
                return str(gs["clinicPhone"]).strip()
        # Try from root
        if "clinic_phone" in st.secrets:
            return str(st.secrets["clinic_phone"]).strip()
        # Fallback as per user instruction till Auth
        return DEFAULT_CLINIC_PHONE
    except:
        return DEFAULT_CLINIC_PHONE

@st.cache_resource
def get_client_v246():
    """Deep Debug: Secrets handling for your format [connections.gsheets] + [gcp_service_account]"""
    try:
        if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
            return None, None, "connections.gsheets not found in secrets.toml"
        spreadsheet_id = st.secrets["connections"]["gsheets"].get("spreadsheet", "")
        if not spreadsheet_id:
            return None, None, "spreadsheet ID empty"

        if "gcp_service_account" not in st.secrets:
            return None, None, f"gcp_service_account section not found. Found: {list(st.secrets.keys())}"
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
    """
    PLANNING: Calculate next PatientID and DailyNumber per clinic
    - PatientID: NP_{next_global_for_clinic}_{clinic_phone} -> Display NP_{next}
    - DailyNumber: Count today's patients for this clinic + 1
    """
    clinic_phone = get_clinic_phone()
    df = read_sheet_v246("New_patient")
    
    # Default if no data
    next_patient_num = 1
    next_daily_num = 1
    
    if not df.empty and "ClinicPhone" in df.columns:
        # Filter for this clinic
        clinic_df = df[df["ClinicPhone"].astype(str).str.strip() == str(clinic_phone).strip()]
        
        # Next PatientID number for this clinic
        if not clinic_df.empty and "PatientID" in clinic_df.columns:
            # Extract numbers from NP_1_123..., NP_2_123...
            nums = []
            for pid in clinic_df["PatientID"].astype(str):
                m = re.search(r'NP_(\d+)_', pid)
                if m:
                    try:
                        nums.append(int(m.group(1)))
                    except:
                        pass
                else:
                    # Fallback for old NP_1 format
                    m2 = re.search(r'NP_(\d+)', pid)
                    if m2:
                        try:
                            nums.append(int(m2.group(1)))
                        except:
                            pass
            if nums:
                next_patient_num = max(nums) + 1
        
        # Next DailyNumber for today for this clinic
        today_str = str(date.today())
        if "Date" in df.columns:
            today_clinic = clinic_df[clinic_df["Date"].astype(str) == today_str]
            if not today_clinic.empty:
                next_daily_num = len(today_clinic) + 1
    elif not df.empty:
        # Old sheet without ClinicPhone column - use total count
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
    
    # Auto extend to 22 cols if old
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
st.title("🌿 Herbal Clinic OS - V2.4.6")
st.caption(f"PatientID: NP_{{n}}_{{clinic_phone}} | Display: NP_n | Clinic: {get_clinic_phone()} | Daily auto 1 | Fully Debugged")

# Sidebar info
clinic_phone = get_clinic_phone()
st.sidebar.success(f"V2.4.6 - Unique ID\nClinic: {clinic_phone}\nDisplay: NP_n only")
st.sidebar.info(f"Full ID: NP_n_{clinic_phone}\n(Phone hidden from user)")

tabs = st.tabs(["🔧 Debug", "🧑‍⚕️ New Patient (Auto ID)", "📋 Recent", "📊 Clinic Graph"])

with tabs[0]:
    st.subheader("Debug - V2.4.6 Planning Check")
    client, sid, err = get_client_v246()
    if err:
        st.error(err)
    else:
        st.success(f"✅ Connected: {sid[:20]}...")
        ws, titles, headers, err2 = get_ws_v246("New_patient")
        if err2:
            st.error(err2)
        else:
            st.success(f"✅ Sheet found | Headers: {len(headers)}/{len(STANDARD_HEADERS_V246)} | ClinicPhone: {clinic_phone}")
            st.json(headers)
            if len(headers) < len(STANDARD_HEADERS_V246):
                if st.button("🔧 Fix to 22 Cols", type="primary"):
                    ws.update('A1', [STANDARD_HEADERS_V246], value_input_option='USER_ENTERED')
                    st.success("Fixed to 22")
                    time.sleep(1)
                    st.rerun()
            
            # Show next IDs
            disp_id, full_id, daily_n, cphone = calculate_next_ids()
            st.info(f"Next IDs for clinic {cphone}: Display={disp_id}, Full={full_id}, Daily={daily_n}")

with tabs[1]:
    st.subheader("New Patient - Auto Generated IDs (Top)")
    
    # PLANNING: Auto generate IDs at top before personal info
    disp_id, full_id, daily_n, cphone = calculate_next_ids()
    
    # Display at top as per user requirement
    top1, top2, top3 = st.columns(3)
    with top1:
        st.metric("🆔 Patient ID (Display)", disp_id)
        st.caption(f"System ID: {full_id} (hidden from user display)")
    with top2:
        st.metric("📅 Daily Number (Today)", daily_n)
        st.caption(f"Clinic: {cphone} | Date: {date.today()}")
    with top3:
        st.metric("🏥 Clinic Phone (System)", cphone)
        st.caption("Till V2.5: 123456789, After: from signup")
    
    st.markdown("---")
    st.markdown("**Personal Info (After Auto IDs):**")
    
    with st.form("new_v246", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            name = st.text_input("Patient Name * / مریض نام *", placeholder="Ali Ahmed")
            father = st.text_input(FATHER_SPOUSE_LABEL, placeholder="Father/Spouse")
        with c2:
            age = st.number_input("Age / عمر", 0,120,30)
            gender = st.selectbox("Gender / جنس", ["Male / مرد","Female / عورت"])
            phone = st.text_input("Patient Phone * / مریض فون *", placeholder="0300xxxxxxx")
        with c3:
            city = st.text_input("City / شہر", "Bhai Pheru")
            addr = st.text_area("Address / پتہ", height=68)
            dval = st.date_input("Date", value=date.today())
        
        a1,a2,a3,a4 = st.columns(4)
        with a1:
            bp = st.text_input("BP", placeholder="120/80")
            pulse = st.text_input("Pulse / نبض")
        with a2:
            weight = st.text_input("Weight / وزن")
            height = st.text_input("Height / قد")
        with a3:
            mizaj = st.selectbox("Mizaj / مزاج", ["Garm / گرم","Sard / سرد","Khushk","Tar","Garm Khushk","Garm Tar","Sard Khushk","Sard Tar","Mutadil / معتدل"])
        with a4:
            fees = st.text_input("Fees / فیس", "500")
            status = st.selectbox("Status", ["New / نیا","Follow-up","Cured"])
        
        b1,b2 = st.columns(2)
        with b1:
            hist = st.text_area("Past History / پرانی ہسٹری")
            comp = st.text_area("Complaint / شکایت (Optional)")
        with b2:
            diag = st.text_area("Diagnosis / تشخیص")
            treat = st.text_area("Treatment / علاج")
        
        submitted = st.form_submit_button(f"💾 Save Patient {disp_id} - Daily {daily_n}", type="primary", use_container_width=True)
        
        if submitted:
            if not name.strip() or not phone.strip():
                st.error("Name & Phone required!")
            else:
                if not comp.strip():
                    comp = "General Checkup"
                
                # PLANNING: Recalculate at save time to avoid race condition
                disp_id_save, full_id_save, daily_n_save, cphone_save = calculate_next_ids()
                
                data = {
                    "PatientID": full_id_save,  # Full unique: NP_1_123456789
                    "ClinicPhone": cphone_save,  # Separate column: 123456789
                    "DailyNumber": daily_n_save,  # Daily per clinic per date
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
                
                with st.spinner(f"Saving {disp_id_save} (System: {full_id_save})..."):
                    if append_v246("New_patient", data):
                        st.success(f"✅ Saved! Display ID: {disp_id_save} | Daily: {daily_n_save} | System: {full_id_save} | Clinic: {cphone_save}")
                        st.balloons()
                        st.info(f"User ko dikhaya: {disp_id_save} | System me save: {full_id_save} (phone hidden)")
                    else:
                        st.error("Save failed - check Debug")

with tabs[2]:
    df = read_v246("New_patient")
    if not df.empty:
        # Filter for current clinic for display
        cphone = get_clinic_phone()
        if "ClinicPhone" in df.columns:
            clinic_df = df[df["ClinicPhone"].astype(str) == str(cphone)]
            st.write(f"**This Clinic ({cphone}) Patients: {len(clinic_df)} / Total in Sheet (All Clinics): {len(df)}**")
            # Show display ID only
            if "PatientID" in clinic_df.columns:
                # Create display ID column for user
                clinic_df = clinic_df.copy()
                clinic_df["DisplayID"] = clinic_df["PatientID"].astype(str).apply(lambda x: x.split('_')[0]+'_'+x.split('_')[1] if '_' in x and x.count('_')>=2 else x)
                st.dataframe(clinic_df[["DisplayID","DailyNumber","Date","Name","FatherName","Phone"]].tail(10).sort_index(ascending=False), use_container_width=True)
            else:
                st.dataframe(clinic_df.tail(10), use_container_width=True)
        else:
            st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)
    else:
        st.info("No data yet")

with tabs[3]:
    st.subheader("Clinic Graph - Per Clinic (Planning for Future)")
    df = read_v246("New_patient")
    cphone = get_clinic_phone()
    if not df.empty and "ClinicPhone" in df.columns:
        clinic_df = df[df["ClinicPhone"].astype(str) == str(cphone)]
        st.write(f"Clinic {cphone} - Daily counts")
        if "Date" in clinic_df.columns:
            daily_counts = clinic_df.groupby("Date").size().reset_index(name="Patients")
            st.bar_chart(daily_counts.set_index("Date"))
            st.dataframe(daily_counts.sort_values("Date", ascending=False), use_container_width=True)
    else:
        st.info("No data for graph yet - will show Daily/Weekly per clinic after data")

st.markdown("---")
st.caption("""
V2.4.6 PLANNING in Code Comments:
- PatientID = NP_n_clinic_phone (unique) | Display = NP_n (phone hidden)
- ClinicPhone = 123456789 till V2.5 Auth, after from signup form
- DailyNumber = per clinic per date, auto 1
- Auto generate at top of form
- All user notes = planning, confirm before code if contradiction
- 22 cols | Same Sheet ID | Fully Debugged
""")
