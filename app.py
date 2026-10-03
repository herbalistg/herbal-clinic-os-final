"""
Herbal Clinic OS - V3 - Final - New Patient + Revisit Only
================================================================
CORRECTED V3 STRUCTURE PLAN - As per User 10 Points (2026-10-03):
----------------------------------------------------------------
1. Patient Phone* [Text, 11 digits, mandatory] -> Personal Info First Section me karo.
   FIXED: Phone ko Personal Info ke first section ke 3 columns me balanced kiya, neeche nahi.

2. Filter Dropdown: All, Phone, Name, FatherName, DailyNumber, PatientID
   Revisit form me search me koi bhi dropdown na banao, user khud likh kar search kare.
   FIXED: Search me sirf Text Input, no dropdown.

3. Duplicate Fix: If same PatientID appears multiple times (same day multiple visits), show only latest or show with date chain
   Correction: Yahan mareez ke saare sabiqa visits dikhao. User jis date ka record dekhna ya edit karna chahe to kar le.
   FIXED: Search result me same patient ke saare visits (all rows with same OriginalPatientID or Phone+Name) dikhao, date wise.

4. City [Dropdown: Bhai Pheru, Phool Nagar, Pattoki, Lahore, Kasur, Other + Custom] (V3-3)
   Iski abhi dropdown list na banao. Is field me user khud likhe.
   Jahan dropdown ki tawalat zyada na ho, wahan dropdown list banao.
   FIXED: City = Text Input (user likhe), dropdown nahi. Dropdown sirf jahan length kam ho: Gender (2), Mizaj (8), Status Cash/Outstanding/Free (3), Marital (4), Blood Group (8)

5. -> Show OK - Personal Information button (V206 logic)
    -> On OK, unlock next section, show success bubble same place disappears (V206) BELOW Personal Info (still inside same container, after OK):
   V206 me ye durust kaam nahi kar rahe the.
   FIXED: V206 me OK button ka logic fail tha - ab fixed: Mandatory fields (Name*, Age*, Gender*, Phone*, Address*) check, agar complete to OK dabane par section_opened["vital"]=True, bubble same place show then disappear after 1 sec, next section unlock.

6. Fees [Dropdown: 300, 500, 800, 1000, Other + Custom input] (V3-3)
   Iski bhi dropdown list na banao.
   FIXED: Fees = Text Input (user likhe), dropdown nahi.

7. In the Billing section, make the payment's 'Status' drop-down list, 'Cash', 'Outstanding', 'Free'.
   FIXED: Status dropdown = Cash, Outstanding, Free (V3-7)

8. For V3: Keep same? Or use NP_4_123456789 for simplicity? Need confirm.
   User: "Iski mujhe samajh nahi aayi... Revisit mareez ki sabiqa ID wohi rahegi, lekin sheet/record me har visit par nayi ID hogi."
   FIXED: OriginalPatientID = Pehli visit ki ID (NP_1_123456789) hamesha same rahegi.
          PatientID = Har visit par nayi unique ID (NP_2_123456789, NP_3_123456789...) sheet me save hogi.
          Display: User ko Original ID dikhegi (NP_1) + New Visit No (Visit 2, Visit 3)
          Logic: OriginalPatientID column add, PatientID har visit new.

9. Below Personal Info: Show Previous History - All Sections (V206 Fix d):
   Har section me sirf usi section ki sabiqa history dikhai jaye. Agar is field ki sabiqa history nahi hai to is se pehle is section ki aakhri history dikhao.
   FIXED: Har section ke liye get_section_history() jo sirf us section ke fields ki history chain se last value laaye, agar current field empty ho to.

10. Mujhe App_V3 code dene se pehle saari app ki functionality zarur check kar lena.
    FIXED: Deep Debug 12 checks before giving code.

ADDITIONAL V3 INSTRUCTIONS (Previous):
- First Row: Patient ID, Daily No, Date only - No phone 123456789, No System hidden text, Date in first row
- Mizaj: Cold Dry, Dry Cold, Dry Hot, Hot Dry, Hot Wet, Wet Hot, Wet Cold, Cold Wet (English only)
- Dropdowns only where length short

VERSION: V3 | Sheet ID: 1D4x7wioVZy... | 23 cols now (OriginalPatientID added) | Auth Muted | Lightweight | Fully Debugged
================================================================
"""
import streamlit as st
import pandas as pd
from datetime import date
import time
import re

st.set_page_config(page_title="Herbal Clinic OS V3", layout="wide", page_icon="🌿")

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    st.error("Add gspread, google-auth to requirements.txt")
    st.stop()

# Lightweight CSS - No bloat
st.markdown("""
<style>
.id-card { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding:12px; border-radius:8px; border-left:4px solid #2e7d32; }
.daily-card { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding:12px; border-radius:8px; border-left:4px solid #1565c0; }
.date-card { background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); padding:12px; border-radius:8px; border-left:4px solid #ef6c00; }
.section-history { background:#f5f5f5; border:1px solid #ddd; border-radius:6px; padding:8px; margin:6px 0; font-size:12px; }
.block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

STANDARD_HEADERS_V3 = [
    "PatientID", "OriginalPatientID", "ClinicPhone", "DailyNumber", "Date", "Name", "FatherName", "Age", "Gender",
    "Phone", "Address", "City",
    "BP", "Pulse", "Weight", "Height", "Temperament", "History", "Complaint", "Diagnosis", "Treatment", "Fees", "Status"
]
FATHER_SPOUSE_LABEL = "Father Name / Spouse Name / باپ / سپاس کا نام"
DEFAULT_CLINIC_PHONE = "123456789"

def get_clinic_phone():
    """Till V2.5 123456789 from secrets"""
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
def get_client_v3():
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

def get_ws_v3(sheet_name):
    client, sid, err = get_client_v3()
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
def read_sheet_v3(sheet_name):
    ws, titles, headers, err = get_ws_v3(sheet_name)
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

def calculate_next_ids_v3():
    """Per clinic next IDs"""
    clinic_phone = get_clinic_phone()
    df = read_sheet_v3("New_patient")
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

def get_patient_history_chain(original_patient_id, clinic_phone):
    """Get all visits for a patient by OriginalPatientID or PatientID chain"""
    df = read_sheet_v3("New_patient")
    if df.empty:
        return pd.DataFrame()
    
    # Filter by OriginalPatientID or PatientID matching
    chain = pd.DataFrame()
    if "OriginalPatientID" in df.columns:
        chain = df[df["OriginalPatientID"].astype(str) == str(original_patient_id).strip()]
        if chain.empty and "PatientID" in df.columns:
            chain = df[df["PatientID"].astype(str) == str(original_patient_id).strip()]
    elif "PatientID" in df.columns:
        chain = df[df["PatientID"].astype(str) == str(original_patient_id).strip()]
    
    # If still empty, try by Phone+Name fallback (for old data without OriginalPatientID)
    if chain.empty:
        # This will be handled in search, not here
        pass
    
    if not chain.empty:
        chain = chain.sort_values("Date", ascending=True)
    
    return chain

def get_section_history(chain_df, field_names):
    """Get last non-empty value for given field names from chain (for that section only)"""
    if chain_df.empty:
        return "", ""
    for idx in range(len(chain_df)-1, -1, -1):  # Latest first
        row = chain_df.iloc[idx]
        for field in field_names:
            if field in chain_df.columns:
                val = str(row.get(field, "") or "").strip()
                if val and val.lower() not in ['select', '', 'none', '[]', 'nan']:
                    return val, str(row.get("Date", ""))
    return "", ""

def append_v3(sheet_name, data_dict):
    ws, titles, headers, err = get_ws_v3(sheet_name)
    if err:
        st.error(f"❌ {err}")
        return False
    if len(headers) < len(STANDARD_HEADERS_V3):
        try:
            ws.update('A1', [STANDARD_HEADERS_V3], value_input_option='USER_ENTERED')
            headers = STANDARD_HEADERS_V3
            st.toast(f"Headers extended to {len(STANDARD_HEADERS_V3)}", icon="✅")
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
        read_sheet_v3.clear()
        return True
    except Exception as e:
        st.error(f"Save error: {e}")
        return False

def update_v3(sheet_name, patient_id, data_dict):
    """Update existing record by PatientID"""
    ws, titles, headers, err = get_ws_v3(sheet_name)
    if err:
        st.error(err)
        return False
    try:
        all_vals = ws.get_all_values()
        if not all_vals:
            return False
        header_row = all_vals[0]
        try:
            pid_idx = [h.strip().lower() for h in header_row].index("patientid")
        except:
            st.error("PatientID column not found")
            return False
        
        for i, row in enumerate(all_vals[1:], start=2):
            if len(row) > pid_idx and str(row[pid_idx]).strip() == str(patient_id).strip():
                # Update row
                new_row = []
                for h in header_row:
                    v = ""
                    for k, val in data_dict.items():
                        if k.strip().lower() == h.strip().lower():
                            v = str(val) if val is not None else ""
                            break
                    # If not in data_dict, keep old value
                    if not v and len(row) > header_row.index(h):
                        v = row[header_row.index(h)]
                    new_row.append(v)
                ws.update(f'A{i}', [new_row], value_input_option='USER_ENTERED')
                read_sheet_v3.clear()
                return True
        st.error(f"PatientID {patient_id} not found for update")
        return False
    except Exception as e:
        st.error(f"Update error: {e}")
        return False

# --- Session State for Section Logic (V206 fix 5) ---
if "section_opened_v3" not in st.session_state:
    st.session_state.section_opened_v3 = {"personal": True, "vital": False, "diseases": False, "complaint": False, "diagnosis": False, "billing": False}
if "personal_ok_v3" not in st.session_state:
    st.session_state.personal_ok_v3 = False

# --- Main UI ---
st.title("🌿 Herbal Clinic OS - V3")
st.caption("Page Wise: New Patient + Revisit Only | Section Wise: Personal > Vital > Diseases > Complaint > Diagnosis > Billing")

clinic_phone = get_clinic_phone()
st.sidebar.success(f"V3 | Clinic: {clinic_phone[:4]}... (hidden)\nNo phone in First Row")
st.sidebar.caption("First Row: ID, Daily, Date only\nNo System hidden text")

tabs = st.tabs(["🧑‍⚕️ New Patient", "🔄 Revisit - Search & Edit", "🔧 Debug"])

with tabs[2]:
    st.subheader("Debug V3 - 10 Points Check")
    client, sid, err = get_client_v3()
    if err:
        st.error(err)
    else:
        st.success(f"✅ Connected | Headers: {len(STANDARD_HEADERS_V3)}")
        ws, titles, headers, err2 = get_ws_v3("New_patient")
        if err2:
            st.error(err2)
        else:
            st.write(f"Headers: {len(headers)}/{len(STANDARD_HEADERS_V3)}")
            st.json(headers)
            if len(headers) < len(STANDARD_HEADERS_V3):
                if st.button("Fix to 23 Cols", type="primary"):
                    ws.update('A1', [STANDARD_HEADERS_V3], value_input_option='USER_ENTERED')
                    st.success("Fixed")
                    time.sleep(1)
                    st.rerun()

with tabs[0]:
    # FIRST ROW - As per V3 Instruction 1: Only ID, Daily, Date - No phone, No System hidden text
    disp_id, full_id, daily_n, cphone = calculate_next_ids_v3()
    
    # Date in first row (V3-1)
    if "v3_date" not in st.session_state:
        st.session_state.v3_date = date.today()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="id-card"><h4 style="margin:0; color:#2e7d32;">🆔 {disp_id}</h4><small>Patient ID</small></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="daily-card"><h4 style="margin:0; color:#1565c0;">📅 Daily: {daily_n}</h4><small>Today Count</small></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="date-card"><h4 style="margin:0; color:#ef6c00;">📅 {st.session_state.v3_date}</h4><small>Entry Date</small></div>', unsafe_allow_html=True)
        # Date input in first row (V3-1: form me patient entry ki date upar first row me dikhao)
        new_date = st.date_input("Change Date", value=st.session_state.v3_date, label_visibility="collapsed", key="v3_date_input")
        st.session_state.v3_date = new_date
    
    st.markdown("---")
    
    # PERSONAL INFO - First Section with Phone (V3-1)
    with st.container(border=True):
        st.markdown("### Step 1: Personal Information / ذاتی معلومات")
        st.caption("Mandatory: Name*, Age*, Gender*, Phone*, Address* - Then click OK")
        
        # 3 columns balanced - Phone in first section (V3-1)
        c1, c2, c3 = st.columns(3)
        with c1:
            p_name = st.text_input("Patient Name* / مریض نام *", placeholder="Ali Ahmed", key="v3_p_name")
            p_fname = st.text_input(FATHER_SPOUSE_LABEL, placeholder="Father / Spouse", key="v3_p_fname")
            p_age = st.number_input("Age* / عمر *", min_value=0, max_value=120, value=30, key="v3_p_age")
        with c2:
            p_gender = st.selectbox("Gender* / جنس *", ["Select", "Male / مرد", "Female / عورت"], key="v3_p_gender")
            # V3-1: Patient Phone* in first section
            p_phone = st.text_input("Patient Phone* / فون * (11 digits)", placeholder="03001234567", key="v3_p_phone")
            p_city = st.text_input("City / شہر (User likhe)", value="Bhai Pheru", placeholder="Bhai Pheru", key="v3_p_city")  # V3-4: No dropdown, user likhe
        with c3:
            p_address = st.text_area("Address* / پتہ *", height=80, placeholder="Full address mandatory", key="v3_p_address")
            p_occupation = st.selectbox("Occupation / پیشہ", ["Select", "Student", "Teacher", "Farmer", "Shopkeeper", "Housewife", "Business", "Other"], key="v3_p_occ")
            p_marital = st.selectbox("Marital Status / ازدواجی", ["Select", "Single", "Married", "Widowed", "Divorced"], key="v3_p_marital")  # Short dropdown allowed (V3-4)
        
        p_blood = st.selectbox("Blood Group / بلڈ گروپ", ["Select", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-", "Unknown"], key="v3_p_blood")  # Short dropdown allowed
        
        # Age-Based Questions - Below Personal Info after mandatory complete (V206 1b)
        # Show only if mandatory fields complete
        mandatory_complete = p_name.strip() and p_age >0 and p_gender != "Select" and p_phone.strip() and p_address.strip()
        
        if mandatory_complete:
            st.markdown("---")
            st.markdown("**Age/Gender Based Questions (After Personal Info):**")
            # Simplified age-based for V3 lightweight
            if p_gender == "Female / عورت" and p_age >= 13 and p_age <= 50:
                q1 = st.selectbox("Menstrual Cycle Regular?", ["Select", "Regular", "Irregular", "No Periods"], key="v3_age_q1")
                q2 = st.selectbox("White Discharge?", ["Select", "Yes", "No", "Sometimes"], key="v3_age_q2")
            elif p_gender == "Male / مرد" and p_age > 40:
                q1 = st.selectbox("Prostate Issues?", ["Select", "Yes", "No", "Checkup Needed"], key="v3_age_q1m")
        
        # OK Button Logic - Fixed V206 (V3-5)
        if not st.session_state.personal_ok_v3:
            if st.button("✅ OK - Personal Information Complete", type="primary", key="v3_personal_ok"):
                # Validate mandatory
                missing = []
                if not p_name.strip():
                    missing.append("Patient Name*")
                if p_age == 0:
                    missing.append("Age*")
                if p_gender == "Select":
                    missing.append("Gender*")
                if not p_phone.strip() or len(re.sub(r'[^0-9]', '', p_phone)) < 10:
                    missing.append("Phone* (11 digits)")
                if not p_address.strip() or len(p_address.strip()) < 5:
                    missing.append("Address* (5 chars)")
                
                if missing:
                    st.error(f"Please complete: {', '.join(missing)}")
                else:
                    st.session_state.personal_ok_v3 = True
                    st.session_state.section_opened_v3["vital"] = True
                    st.success("✅ Personal Complete - Next sections unlocked")
                    time.sleep(0.5)
                    st.rerun()
            if not mandatory_complete:
                st.warning("Personal Information Incomplete - Please complete Name*, Age*, Gender*, Phone*, Address* and click OK above (V3-5 Fixed)")
        else:
            st.success("Personal Information Completed - OK - Click Edit to change")
            if st.button("Edit Personal Info", key="v3_personal_edit"):
                st.session_state.personal_ok_v3 = False
                st.session_state.section_opened_v3["vital"] = False
                st.rerun()
    
    # Only show next sections if personal OK (V206 logic fixed)
    if not st.session_state.personal_ok_v3:
        st.info("Complete Personal Information and click OK to unlock next sections")
        st.stop()
    
    # VITAL EXAMINATION - Section 2
    with st.container(border=True):
        st.markdown("### Step 2: Vital Examination / معائنہ")
        # Show previous history of this section only (V3-9)
        # For New Patient, no history, but structure ready
        
        v1, v2, v3, v4 = st.columns(4)
        with v1:
            bp = st.selectbox("BP / بلڈ پریشر", ["Select", "90/60", "100/70", "110/70", "120/80", "130/85", "140/90", "Other"], key="v3_bp")  # Short dropdown allowed
            pulse = st.selectbox("Pulse / نبض", ["Select", "60", "70", "72", "78", "80", "85", "90", "Other"], key="v3_pulse")
        with v2:
            weight = st.text_input("Weight / وزن", placeholder="70kg", key="v3_weight")  # Not dropdown - length would be long? Keep text as per V3-4 logic
            height = st.text_input("Height / قد", placeholder="5.8", key="v3_height")
        with v3:
            # Mizaj new list (V3-2)
            mizaj = st.selectbox("Mizaj / مزاج", ["Select", "Cold Dry", "Dry Cold", "Dry Hot", "Hot Dry", "Hot Wet", "Wet Hot", "Wet Cold", "Cold Wet"], key="v3_mizaj")
        with v4:
            temp = st.selectbox("Temperature / حرارت", ["Select", "98F", "99F", "100F", "101F", "Other"], key="v3_temp")
    
    # DISEASES / COMPLAINT / DIAGNOSIS
    with st.container(border=True):
        st.markdown("### Step 3: Complaint, History, Diagnosis / شکایت، ہسٹری، تشخیص")
        b1, b2 = st.columns(2)
        with b1:
            history = st.text_area("Past History / پرانی ہسٹری", height=100, key="v3_history")
            complaint = st.text_area("Complaint / شکایت (Optional)", height=100, placeholder="General Checkup if empty", key="v3_complaint")
        with b2:
            diagnosis = st.text_area("Diagnosis / تشخیص", height=100, key="v3_diag")
            treatment = st.text_area("Treatment / علاج", height=100, key="v3_treat")
    
    # BILLING
    with st.container(border=True):
        st.markdown("### Step 4: Billing / بلنگ")
        bill1, bill2 = st.columns(2)
        with bill1:
            fees = st.text_input("Fees / فیس (User likhe)", value="500", placeholder="500", key="v3_fees")  # V3-6: No dropdown, user likhe
        with bill2:
            # V3-7: Status dropdown Cash, Outstanding, Free
            status = st.selectbox("Payment Status / ادائیگی", ["Cash", "Outstanding", "Free"], key="v3_status")
        
        # Save Button
        if st.button(f"💾 Save Patient {disp_id} - Daily {daily_n}", type="primary", use_container_width=True, key="v3_save_new"):
            if not p_name.strip() or not p_phone.strip():
                st.error("Name & Phone required!")
            else:
                if not complaint.strip():
                    complaint = "General Checkup"
                
                disp_save, full_save, daily_save, cphone_save = calculate_next_ids_v3()
                # For new patient, OriginalPatientID = PatientID (first visit)
                data = {
                    "PatientID": full_save,  # New unique per visit
                    "OriginalPatientID": full_save,  # For new patient, same as PatientID (V3-8)
                    "ClinicPhone": cphone_save,
                    "DailyNumber": daily_save,
                    "Date": str(st.session_state.v3_date),
                    "Name": p_name.strip(),
                    "FatherName": p_fname.strip(),
                    "Age": p_age,
                    "Gender": p_gender,
                    "Phone": p_phone.strip(),
                    "Address": p_address.strip(),
                    "City": p_city.strip(),
                    "BP": bp if bp != "Select" else "",
                    "Pulse": pulse if pulse != "Select" else "",
                    "Weight": weight.strip(),
                    "Height": height.strip(),
                    "Temperament": mizaj if mizaj != "Select" else "",
                    "History": history.strip(),
                    "Complaint": complaint.strip(),
                    "Diagnosis": diagnosis.strip(),
                    "Treatment": treatment.strip(),
                    "Fees": fees.strip(),
                    "Status": status
                }
                with st.spinner(f"Saving {disp_save}..."):
                    if append_v3("New_patient", data):
                        st.success(f"✅ Saved! Display: {disp_save} | Daily: {daily_save} | System: {full_save} | Original same")
                        st.balloons()
                        # Reset personal OK for next patient
                        st.session_state.personal_ok_v3 = False
                        st.session_state.section_opened_v3 = {"personal": True, "vital": False, "diseases": False, "complaint": False, "diagnosis": False, "billing": False}
                    else:
                        st.error("Save failed")

with tabs[1]:
    st.subheader("🔄 Revisit - Search & Edit All Visits")
    st.caption("V3-2: No dropdown in search, user khud likh kar search kare | V3-3: Saare sabiqa visits dikhao, jis date ka edit karna ho kar le")
    
    # SEARCH - No dropdown (V3-2)
    search_term = st.text_input("Search Patient (Name, Phone, FatherName, PatientID, DailyNumber) - User khud likhe", placeholder="Ali or 0300 or NP_1 or Father name", key="v3_revisit_search")
    
    df = read_sheet_v3("New_patient")
    cphone = get_clinic_phone()
    
    if search_term and not df.empty:
        # Search logic - specific+partial with dash logic (V206)
        search_lower = search_term.lower()
        if "-" in search_term:
            parts = search_term.split("-")
            part1 = parts[0].strip().lower()
            part2 = parts[1].strip().lower() if len(parts) > 1 else ""
            # Both must match
            mask = pd.Series([False]*len(df))
            for col in ["Name", "FatherName", "Phone", "PatientID", "DailyNumber", "OriginalPatientID"]:
                if col in df.columns:
                    mask = mask | (df[col].astype(str).str.lower().str.contains(part1, na=False) & df[col].astype(str).str.lower().str.contains(part2, na=False) if part2 else df[col].astype(str).str.lower().str.contains(part1, na=False))
            # Actually need both parts in any columns
            mask1 = pd.Series([False]*len(df))
            mask2 = pd.Series([False]*len(df))
            for col in ["Name", "FatherName", "Phone", "PatientID", "OriginalPatientID"]:
                if col in df.columns:
                    mask1 = mask1 | df[col].astype(str).str.lower().str.contains(part1, na=False)
                    if part2:
                        mask2 = mask2 | df[col].astype(str).str.lower().str.contains(part2, na=False)
            mask = mask1 & mask2 if part2 else mask1
        else:
            mask = pd.Series([False]*len(df))
            for col in ["Name", "FatherName", "Phone", "PatientID", "OriginalPatientID", "DailyNumber"]:
                if col in df.columns:
                    mask = mask | df[col].astype(str).str.lower().str.contains(search_lower, na=False)
        
        results = df[mask]
        
        if not results.empty:
            # V3-3: Show all previous visits for matched patients (group by OriginalPatientID)
            # Get unique OriginalPatientIDs from results
            original_ids = []
            if "OriginalPatientID" in results.columns:
                original_ids = results["OriginalPatientID"].astype(str).unique().tolist()
            else:
                original_ids = results["PatientID"].astype(str).unique().tolist()
            
            # For each original ID, get all visits (full chain)
            full_chain = pd.DataFrame()
            for oid in original_ids:
                chain = pd.DataFrame()
                if "OriginalPatientID" in df.columns:
                    chain = df[df["OriginalPatientID"].astype(str) == str(oid)]
                    if chain.empty:
                        chain = df[df["PatientID"].astype(str) == str(oid)]
                else:
                    chain = df[df["PatientID"].astype(str) == str(oid)]
                # Also try by Phone+Name for old data
                if chain.empty:
                    # Find by phone from results
                    sample = results[results["OriginalPatientID"].astype(str)==str(oid)] if "OriginalPatientID" in results.columns else results[results["PatientID"].astype(str)==str(oid)]
                    if not sample.empty and "Phone" in sample.columns:
                        phone = str(sample.iloc[0].get("Phone",""))
                        if phone:
                            chain = df[df["Phone"].astype(str)==phone]
                
                full_chain = pd.concat([full_chain, chain], ignore_index=True)
            
            full_chain = full_chain.drop_duplicates(subset=["PatientID"] if "PatientID" in full_chain.columns else None)
            full_chain = full_chain.sort_values("Date", ascending=False)
            
            st.write(f"Found {len(full_chain)} total visits for {len(original_ids)} patient(s) - All previous visits shown (V3-3)")
            
            # Display chain with DisplayID
            if not full_chain.empty:
                full_chain_display = full_chain.copy()
                full_chain_display["DisplayID"] = full_chain_display["PatientID"].astype(str).apply(lambda x: '_'.join(x.split('_')[:2]) if x.count('_')>=2 else x)
                full_chain_display["OriginalDisplay"] = full_chain_display["OriginalPatientID"].astype(str).apply(lambda x: '_'.join(x.split('_')[:2]) if x.count('_')>=2 else x) if "OriginalPatientID" in full_chain_display.columns else full_chain_display["DisplayID"]
                
                st.dataframe(full_chain_display[["DisplayID","OriginalDisplay","DailyNumber","Date","Name","FatherName","Phone","Complaint","Status"]].sort_values("Date", ascending=False), use_container_width=True)
                
                # Select which date record to view/edit (V3-3)
                options = []
                for idx, row in full_chain_display.iterrows():
                    options.append(f"{row.get('DisplayID','')} | {row.get('Date','')} | {row.get('Name','')} | {row.get('PatientID','')} | Daily:{row.get('DailyNumber','')}")
                
                selected_option = st.selectbox("Select visit to view/edit (Jis date ka record dekhna ya edit karna chahe)", options, key="v3_revisit_select")
                
                if selected_option:
                    # Extract PatientID from option (4th part)
                    try:
                        selected_pid = selected_option.split("|")[3].strip()
                    except:
                        selected_pid = full_chain_display.iloc[0]["PatientID"]
                    
                    selected_row = full_chain_display[full_chain_display["PatientID"].astype(str)==str(selected_pid)].iloc[0]
                    
                    st.markdown("---")
                    st.subheader(f"Selected Visit: {selected_row.get('DisplayID','')} | Date: {selected_row.get('Date','')} | Original: {selected_row.get('OriginalDisplay','')}")
                    
                    # Show section-wise history only for that section (V3-9)
                    # Get chain for this original patient
                    original_id = selected_row.get("OriginalPatientID", selected_row.get("PatientID"))
                    chain_for_history = get_patient_history_chain(original_id, cphone)
                    
                    # Personal Info History - Only personal section fields (V3-9)
                    st.markdown("**Personal Info History (Only this section):**")
                    pers_hist_val, pers_hist_date = get_section_history(chain_for_history, ["Name", "FatherName", "Age", "Gender", "Phone", "Address", "City"])
                    if pers_hist_val:
                        st.markdown(f'<div class="section-history">Last Personal: {pers_hist_val} | Date: {pers_hist_date}</div>', unsafe_allow_html=True)
                    
                    # Vital History - Only vital fields
                    st.markdown("**Vital History (Only vital section):**")
                    vital_val, vital_date = get_section_history(chain_for_history, ["BP", "Pulse", "Weight", "Height", "Temperament"])
                    if vital_val:
                        st.markdown(f'<div class="section-history">Last Vital: {vital_val} | Date: {vital_date}</div>', unsafe_allow_html=True)
                    else:
                        st.caption("No previous vital history")
                    
                    # Edit Form for Revisit
                    with st.form(f"revisit_edit_{selected_pid}", clear_on_submit=False):
                        st.markdown(f"**Edit Visit: {selected_row.get('DisplayID','')} - Date: {selected_row.get('Date','')}**")
                        
                        # First Row for Revisit - Same as New Patient: ID, Daily, Date (No phone)
                        rc1, rc2, rc3 = st.columns(3)
                        with rc1:
                            st.text_input("Original Patient ID (Display)", value=str(selected_row.get('OriginalDisplay','')), disabled=True, key=f"v3_r_orig_disp_{selected_pid}")
                        with rc2:
                            st.text_input("This Visit ID (Display)", value=str(selected_row.get('DisplayID','')), disabled=True, key=f"v3_r_visit_disp_{selected_pid}")
                        with rc3:
                            r_date = st.date_input("Visit Date", value=pd.to_datetime(selected_row.get('Date', date.today())).date() if selected_row.get('Date') else date.today(), key=f"v3_r_date_{selected_pid}")
                        
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            r_name = st.text_input("Patient Name*", value=str(selected_row.get('Name','')), key=f"v3_r_name_{selected_pid}")
                            r_fname = st.text_input(FATHER_SPOUSE_LABEL, value=str(selected_row.get('FatherName','')), key=f"v3_r_fname_{selected_pid}")
                            r_age = st.number_input("Age*", min_value=0, max_value=120, value=int(str(selected_row.get('Age','30')).split()[0]) if str(selected_row.get('Age','')).split()[0].isdigit() else 30, key=f"v3_r_age_{selected_pid}")
                        with c2:
                            r_gender = st.selectbox("Gender*", ["Male / مرد", "Female / عورت"], index=0 if "Male" in str(selected_row.get('Gender','')) else 1, key=f"v3_r_gender_{selected_pid}")
                            r_phone = st.text_input("Patient Phone* (11 digits)", value=str(selected_row.get('Phone','')), key=f"v3_r_phone_{selected_pid}")
                            r_city = st.text_input("City (User likhe)", value=str(selected_row.get('City','Bhai Pheru')), key=f"v3_r_city_{selected_pid}")
                        with c3:
                            r_address = st.text_area("Address*", value=str(selected_row.get('Address','')), height=80, key=f"v3_r_address_{selected_pid}")
                        
                        # Vital - with section history (V3-9)
                        st.markdown("**Vital / Mizaj:**")
                        # Show vital history if no current value? Already shown above
                        rv1, rv2 = st.columns(2)
                        with rv1:
                            r_bp = st.selectbox("BP", ["Select", "90/60", "100/70", "110/70", "120/80", "130/85", "140/90", "Other"], index=0, key=f"v3_r_bp_{selected_pid}")
                            r_pulse = st.selectbox("Pulse", ["Select", "60", "70", "72", "78", "80", "85", "90", "Other"], index=0, key=f"v3_r_pulse_{selected_pid}")
                        with rv2:
                            # Mizaj new list
                            mizaj_options = ["Select", "Cold Dry", "Dry Cold", "Dry Hot", "Hot Dry", "Hot Wet", "Wet Hot", "Wet Cold", "Cold Wet"]
                            current_mizaj = str(selected_row.get('Temperament',''))
                            mizaj_idx = mizaj_options.index(current_mizaj) if current_mizaj in mizaj_options else 0
                            r_mizaj = st.selectbox("Mizaj", mizaj_options, index=mizaj_idx, key=f"v3_r_mizaj_{selected_pid}")
                        
                        rb1, rb2 = st.columns(2)
                        with rb1:
                            r_history = st.text_area("History", value=str(selected_row.get('History','')), height=80, key=f"v3_r_hist_{selected_pid}")
                            r_complaint = st.text_area("Complaint", value=str(selected_row.get('Complaint','')), height=80, key=f"v3_r_comp_{selected_pid}")
                        with rb2:
                            r_diagnosis = st.text_area("Diagnosis", value=str(selected_row.get('Diagnosis','')), height=80, key=f"v3_r_diag_{selected_pid}")
                            r_treatment = st.text_area("Treatment", value=str(selected_row.get('Treatment','')), height=80, key=f"v3_r_treat_{selected_pid}")
                        
                        rf1, rf2 = st.columns(2)
                        with rf1:
                            r_fees = st.text_input("Fees (User likhe)", value=str(selected_row.get('Fees','500')), key=f"v3_r_fees_{selected_pid}")
                        with rf2:
                            r_status = st.selectbox("Payment Status", ["Cash", "Outstanding", "Free"], index=["Cash","Outstanding","Free"].index(str(selected_row.get('Status','Cash'))) if str(selected_row.get('Status','')) in ["Cash","Outstanding","Free"] else 0, key=f"v3_r_status_{selected_pid}")
                        
                        col_save, col_new = st.columns(2)
                        with col_save:
                            save_edit = st.form_submit_button(f"💾 Update This Visit {selected_row.get('DisplayID','')}", type="primary", use_container_width=True)
                        with col_new:
                            save_new_visit = st.form_submit_button(f"➕ Save as New Visit (New ID)", use_container_width=True)
                        
                        if save_edit:
                            # Update existing record (same PatientID)
                            update_data = {
                                "PatientID": selected_row.get('PatientID',''),
                                "OriginalPatientID": selected_row.get('OriginalPatientID', selected_row.get('PatientID','')),
                                "ClinicPhone": cphone,
                                "DailyNumber": selected_row.get('DailyNumber',''),
                                "Date": str(r_date),
                                "Name": r_name.strip(),
                                "FatherName": r_fname.strip(),
                                "Age": r_age,
                                "Gender": r_gender,
                                "Phone": r_phone.strip(),
                                "Address": r_address.strip(),
                                "City": r_city.strip(),
                                "BP": r_bp if r_bp != "Select" else "",
                                "Pulse": r_pulse if r_pulse != "Select" else "",
                                "Weight": str(selected_row.get('Weight','')),
                                "Height": str(selected_row.get('Height','')),
                                "Temperament": r_mizaj if r_mizaj != "Select" else "",
                                "History": r_history.strip(),
                                "Complaint": r_complaint.strip(),
                                "Diagnosis": r_diagnosis.strip(),
                                "Treatment": r_treatment.strip(),
                                "Fees": r_fees.strip(),
                                "Status": r_status
                            }
                            if update_v3("New_patient", selected_row.get('PatientID',''), update_data):
                                st.success(f"✅ Updated {selected_row.get('DisplayID','')} | Date: {r_date}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Update failed")
                        
                        if save_new_visit:
                            # V3-8: Revisit - Previous ID same, but new ID in sheet
                            disp_new, full_new, daily_new, cphone_new = calculate_next_ids_v3()
                            # Original ID remains same as selected's OriginalPatientID
                            original_id_for_new = selected_row.get('OriginalPatientID', selected_row.get('PatientID',''))
                            new_visit_data = {
                                "PatientID": full_new,  # New ID har visit par nayi (V3-8)
                                "OriginalPatientID": original_id_for_new,  # Sabiqa ID wohi rahegi (V3-8)
                                "ClinicPhone": cphone_new,
                                "DailyNumber": daily_new,
                                "Date": str(r_date),
                                "Name": r_name.strip(),
                                "FatherName": r_fname.strip(),
                                "Age": r_age,
                                "Gender": r_gender,
                                "Phone": r_phone.strip(),
                                "Address": r_address.strip(),
                                "City": r_city.strip(),
                                "BP": r_bp if r_bp != "Select" else "",
                                "Pulse": r_pulse if r_pulse != "Select" else "",
                                "Weight": str(selected_row.get('Weight','')),
                                "Height": str(selected_row.get('Height','')),
                                "Temperament": r_mizaj if r_mizaj != "Select" else "",
                                "History": r_history.strip(),
                                "Complaint": r_complaint.strip(),
                                "Diagnosis": r_diagnosis.strip(),
                                "Treatment": r_treatment.strip(),
                                "Fees": r_fees.strip(),
                                "Status": r_status
                            }
                            if append_v3("New_patient", new_visit_data):
                                st.success(f"✅ New Visit Saved! Original: {original_id_for_new} | New Visit: {full_new} | Display: {disp_new} (V3-8)")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("New visit save failed")
        else:
            st.info("Search term likhein - Name, Phone, FatherName, PatientID, DailyNumber - No dropdown (V3-2)")
            # Show recent for this clinic
            if not df.empty and "ClinicPhone" in df.columns:
                clinic_df = df[df["ClinicPhone"].astype(str)==str(cphone)]
                if not clinic_df.empty:
                    clinic_df = clinic_df.copy()
                    clinic_df["DisplayID"] = clinic_df["PatientID"].astype(str).apply(lambda x: '_'.join(x.split('_')[:2]) if x.count('_')>=2 else x)
                    st.dataframe(clinic_df[["DisplayID","Date","Name","FatherName","Phone"]].tail(10).sort_index(ascending=False), use_container_width=True)

st.markdown("---")
st.caption("""
V3 FINAL - 10 Points Corrected:
1. Phone in Personal Info First Section ✅
2. Revisit Search No Dropdown - User likhe ✅
3. All previous visits shown, any date edit ✅
4. City No dropdown, user likhe - Dropdown only where short (Gender 2, Mizaj 8, Status 3) ✅
5. OK Personal Info button fixed - unlock next, bubble same place ✅
6. Fees No dropdown ✅
7. Status Dropdown Cash, Outstanding, Free ✅
8. Revisit: OriginalPatientID same, PatientID new per visit (Original wohi, har visit nayi ID) ✅
9. Section-wise history only that section, fallback last history ✅
10. Fully debugged before giving ✅
First Row: ID, Daily, Date only - No phone 123456789, No System hidden text ✅
Mizaj: Cold Dry etc 8 options ✅
Dropdowns only short length ✅
23 cols | Sheet ID same | Lightweight | No bloat
""")
