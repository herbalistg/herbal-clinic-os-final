"""
Herbal Clinic OS - V3.1 Fixed - Based on V3 Final + V206 Full Sections
================================================================
Fixes as per user latest instructions:
1. Vital: BP [High, Very high, Normal, Low, Very low] + figure input, Pulse [Fast, Very fast, Normal, Weak, Very weak] + figure, Temp [High, Very high, Normal, Low, Very low] + figure
   Mizaj list ok but custom write allowed, Age/Gender full from V206, Diseases entire section from V206
   Billing complete, No balloons - small popup instead
2. Revisit Search entire section from V206
3. Revisit Search KeyError fixed
   Remove extra texts - English only clean

V206 Sections Imported:
- BODY_PARTS, DISEASE_RELATED_QUESTIONS, DISEASE_RELATED_DROPDOWNS, LISTS
- Age/Gender based questions full
- Diseases section full with Add Disease logic
- Revisit search with dash logic, duplicate fix, history chain

================================================================
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
import re

st.set_page_config(page_title="Herbal Clinic V3.1", layout="wide", page_icon="🌿")

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    st.error("Add gspread, google-auth")
    st.stop()

# Clean CSS - English only
st.markdown("""
<style>
.id-card { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding:12px; border-radius:8px; border-left:4px solid #2e7d32; }
.daily-card { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding:12px; border-radius:8px; border-left:4px solid #1565c0; }
.date-card { background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); padding:12px; border-radius:8px; border-left:4px solid #ef6c00; }
.popup-success { background: linear-gradient(135deg, #2E7D5B, #4CAF50); color:white; padding:12px; border-radius:10px; text-align:center; font-weight:700; box-shadow:0 4px 12px rgba(46,125,91,0.3); margin:8px 0; }
.section-history { background:#f5f5f5; border:1px solid #ddd; border-radius:6px; padding:8px; margin:6px 0; font-size:12px; }
.block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# V206 LISTS Imported
BODY_PARTS = {
  "Select": ["Select"],
  "Head": ["Select", "Headache", "Migraine", "Dizziness", "Hair Fall", "Head Heaviness"],
  "Eyes": ["Select", "Eye Pain", "Blurred Vision", "Red Eyes", "Watery Eyes", "Itchy Eyes"],
  "Nose": ["Select", "Runny Nose", "Nose Block", "Sinus", "Nose Bleed", "Sneezing"],
  "Mouth": ["Select", "Mouth Ulcer", "Bad Breath", "Toothache", "Gum Bleeding", "Dry Mouth"],
  "Throat": ["Select", "Sore Throat", "Tonsillitis", "Hoarseness", "Difficulty Swallowing"],
  "Chest": ["Select", "Chest Pain", "Cough", "Asthma", "Breathlessness", "Cold/Cough"],
  "Stomach": ["Select", "Gas/Bloating", "Acidity/GERD", "IBS", "Constipation", "Digestive Weakness", "Nausea", "Vomiting"],
  "Liver": ["Select", "Liver Weakness", "Jaundice", "Fatty Liver", "Liver Pain"],
  "Kidney": ["Select", "Kidney Stones", "Kidney Pain", "Burning Urination", "Frequent Urination"],
  "Joints": ["Select", "Joint Pain", "Back Pain", "Sciatica", "Arthritis", "Knee Pain", "Shoulder Pain"],
  "Skin": ["Select", "Skin Disease", "Allergy", "Itching", "Eczema", "Psoriasis", "Pimples"],
  "Heart": ["Select", "BP High", "BP Low", "Palpitation", "Chest Tightness"],
  "General": ["Select", "Fever", "Diabetes", "Anxiety", "Insomnia", "General Weakness", "Anemia", "Obesity", "Piles", "Leucorrhoea", "Menstrual Irregularity", "Infertility", "Fatigue"],
}

DISEASE_RELATED_QUESTIONS = {
  "Head": ["Pain Type", "Timing", "Associated Nausea?"],
  "Eyes": ["Vision Effect?", "Pain on Movement?", "Discharge Type?"],
  "Nose": ["Discharge Color?", "Allergy Trigger?", "Smell Loss?"],
  "Mouth": ["Eating Difficulty?", "Duration of Ulcer?", "Bleeding?"],
  "Throat": ["Fever with Throat?", "Voice Change?", "Swallowing Pain Level?"],
  "Chest": ["Cough Type?", "Worse at Night?", "Sputum Color?"],
  "Stomach": ["Relation to Food?", "Bowel Type?", "Appetite Effect?"],
  "Liver": ["Appetite Loss?", "Yellow Urine?", "Abdominal Swelling?"],
  "Kidney": ["Pain Radiation?", "Urine Color?", "Swelling in Feet?"],
  "Joints": ["Stiffness Morning?", "Worse on Movement?", "Swelling?"],
  "Skin": ["Itching Severity?", "Spread Area?", "Seasonal?"],
  "Heart": ["Palpitation Frequency?", "Exertion Effect?", "Sweating?"],
  "General": ["Onset?", "Severity?", "Family History?"],
}

DISEASE_RELATED_DROPDOWNS = {
  "Head": {"Pain Type": ["Select","Throbbing","Sharp","Dull","Pressure","Tightness"], "Timing": ["Select","Morning","Evening","Night","Continuous","Intermittent"], "Associated Nausea?": ["Select","Yes","No","Sometimes"]},
  "Throat": {"Fever with Throat?": ["Select","Yes High Fever","Yes Low Fever","No Fever","On and Off"], "Voice Change?": ["Select","No Change","Hoarseness","Loss of Voice","Rough Voice"], "Swallowing Pain Level?": ["Select","Mild","Moderate","Severe","Only on Swallowing","Continuous"]},
  "Chest": {"Cough Type?": ["Select","Dry","Wet","Productive","Whooping","Barking"], "Worse at Night?": ["Select","Yes Worse at Night","No","Same Day Night","Only Night"], "Sputum Color?": ["Select","White","Yellow","Green","Bloody","None","Clear"]},
  "General": {"Onset?": ["Select","Sudden","Gradual","Since Birth","Since Childhood","Recent"], "Severity?": ["Select","Mild","Moderate","Severe","Very Severe"], "Family History?": ["Select","Yes","No","Father Side","Mother Side","Both Sides"]},
}

LISTS = {
  "gender": ["Select","Male","Female"],
  "duration": ["Select","Day","Week","Month","Year","Since Birth","Since Childhood"],
  "severity": ["Select","Mild","Moderate","Severe","Very Mild","Very Severe"],
  "blood_group": ["Select","A+","A-","B+","B-","O+","O-","AB+","AB-","Unknown"],
  "marital": ["Select","Single","Married","Widowed","Divorced"],
  "occupation": ["Select","Student","Teacher","Farmer","Shopkeeper","Laborer","Driver","Housewife","Business","Engineer","Government Job","Private Job","Retired","Unemployed","Other"],
}

STANDARD_HEADERS_V3 = ["PatientID","OriginalPatientID","ClinicPhone","DailyNumber","Date","Name","FatherName","Age","Gender","Phone","Address","City","BP","Pulse","Weight","Height","Temperament","Diseases","History","Complaint","Diagnosis","Treatment","Fees","Status","Total","Paid","Balance","PaymentMethod"]
FATHER_LABEL = "Father / Spouse Name"
DEFAULT_CLINIC_PHONE = "123456789"

def show_popup(message):
    st.markdown(f'<div class="popup-success">{message}</div>', unsafe_allow_html=True)
    st.toast(message, icon="✅")

def get_clinic_phone():
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
            return None, None, f"gcp_service_account not found"
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
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
            return None, all_titles, None, f"Sheet '{sheet_name}' not found"
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

def get_age_based_questions(age_str, gender):
    try:
        age = int(str(age_str).strip().split()[0])
    except:
        return []
    questions = []
    gender = str(gender).lower()
    if "female" in gender:
        if age >= 10 and age <= 12:
            questions = [("Menarche Started?", ["Select","Yes","No"], "female_menarche"), ("Age of First Period?", "text", "female_menarche_age")]
        elif age >= 13 and age <= 50:
            questions = [("Menstrual Cycle Regular?", ["Select","Regular","Irregular","No Periods"], "female_cycle"), ("Menstrual Flow?", ["Select","Normal","Heavy","Light","Scanty"], "female_flow"), ("Number of Pregnancies?", ["Select","0","1","2","3","4+"], "female_preg_count"), ("Any Miscarriage?", ["Select","Yes","No"], "female_miscarriage"), ("Using Contraception?", ["Select","Yes","No"], "female_contraception"), ("White Discharge?", ["Select","Yes","No","Sometimes"], "female_leucorrhoea")]
        elif age > 50:
            questions = [("Menopause Age?", "text", "female_menopause_age"), ("Menopause Symptoms?", ["Select","Hot Flashes","Mood Swings","No Symptoms","Other"], "female_menopause_sym"), ("HRT Taken?", ["Select","Yes","No"], "female_hrt")]
    elif "male" in gender:
        if age >= 12 and age <= 18:
            questions = [("Puberty Changes Started?", ["Select","Yes","No"], "male_puberty"), ("Voice Change?", ["Select","Yes","No","In Progress"], "male_voice"), ("Beard Growth?", ["Select","Yes","No","Starting"], "male_beard")]
        elif age >= 19 and age <= 40:
            questions = [("Marital Status Effect?", ["Select","Single","Married","Issues"], "male_marital_effect"), ("Sexual Health Concerns?", ["Select","Yes","No","Sometimes"], "male_sexual"), ("Nightfall Frequency?", ["Select","Never","Rarely","Sometimes","Often"], "male_nightfall")]
        elif age > 40:
            questions = [("Prostate Issues?", ["Select","Yes","No","Checkup Needed"], "male_prostate"), ("Urine Stream Weak?", ["Select","Yes","No"], "male_urine_weak"), ("Erectile Issues?", ["Select","Yes","No","Sometimes"], "male_erectile")]
    if age < 5:
        questions += [("Birth History Normal?", ["Select","Normal","C-Section","Premature","Complications"], "child_birth"), ("Vaccination Complete?", ["Select","Yes","No","Partial"], "child_vaccination")]
    elif age >= 5 and age <= 12:
        questions += [("School Performance?", ["Select","Good","Average","Poor"], "child_school"), ("Growth Normal?", ["Select","Normal","Delayed","Advanced"], "child_growth")]
    return questions

def append_v3(sheet_name, data_dict):
    ws, titles, headers, err = get_ws_v3(sheet_name)
    if err:
        st.error(f"{err}")
        return False
    if len(headers) < len(STANDARD_HEADERS_V3):
        try:
            ws.update('A1', [STANDARD_HEADERS_V3], value_input_option='USER_ENTERED')
            headers = STANDARD_HEADERS_V3
            time.sleep(0.5)
        except Exception as e:
            st.warning(f"Header: {e}")
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
    ws, titles, headers, err = get_ws_v3(sheet_name)
    if err:
        return False
    try:
        all_vals = ws.get_all_values()
        if not all_vals:
            return False
        header_row = all_vals[0]
        try:
            pid_idx = [h.strip().lower() for h in header_row].index("patientid")
        except:
            return False
        for i, row in enumerate(all_vals[1:], start=2):
            if len(row) > pid_idx and str(row[pid_idx]).strip() == str(patient_id).strip():
                new_row = []
                for h in header_row:
                    v = ""
                    for k, val in data_dict.items():
                        if k.strip().lower() == h.strip().lower():
                            v = str(val) if val is not None else ""
                            break
                    if not v and len(row) > header_row.index(h):
                        try:
                            v = row[header_row.index(h)]
                        except:
                            v = ""
                    new_row.append(v)
                ws.update(f'A{i}', [new_row], value_input_option='USER_ENTERED')
                read_sheet_v3.clear()
                return True
        return False
    except Exception as e:
        st.error(f"Update error: {e}")
        return False

def parse_date_search(s):
    try:
        s = str(s).strip()
        if not s:
            return None
        if "-" not in s:
            if s.isdigit() and 1 <= int(s) <= 31:
                return {"day": int(s), "month": None, "year": None, "raw": s}
            return {"day": None, "month": None, "year": None, "raw": s, "partial": s}
        parts = s.split("-")
        if len(parts) == 3 and len(parts[0]) == 4 and parts[0].isdigit():
            try:
                year = int(parts[0]) if parts[0] else None
                month = int(parts[1]) if parts[1] else None
                day = int(parts[2]) if parts[2] else None
                return {"day": day, "month": month, "year": year, "raw": s}
            except:
                return {"day": None, "month": None, "year": None, "raw": s, "partial": s}
        if s.startswith("--") and len(parts) >= 3:
            try:
                year_part = parts[2] if len(parts) > 2 else parts[-1]
                if year_part.isdigit() and len(year_part) == 4:
                    return {"day": None, "month": None, "year": int(year_part), "raw": s}
            except:
                pass
        if s.startswith("-") and not s.startswith("--"):
            try:
                month = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
                return {"day": None, "month": month, "year": None, "raw": s}
            except:
                pass
        if len(parts) == 2:
            try:
                d = int(parts[0]) if parts[0].isdigit() else None
                m = int(parts[1]) if parts[1].isdigit() else None
                return {"day": d, "month": m, "year": None, "raw": s}
            except:
                return {"day": None, "month": None, "year": None, "raw": s, "partial": s}
        if len(parts) == 3:
            try:
                d = int(parts[0]) if parts[0].isdigit() else None
                m = int(parts[1]) if parts[1].isdigit() else None
                y = int(parts[2]) if parts[2].isdigit() else None
                return {"day": d, "month": m, "year": y, "raw": s}
            except:
                return {"day": None, "month": None, "year": None, "raw": s, "partial": s}
        return {"day": None, "month": None, "year": None, "raw": s, "partial": s}
    except:
        return None

def match_date_record(record_date_str, search_parsed):
    try:
        if not search_parsed:
            return False
        if "partial" in search_parsed and search_parsed.get("day") is None and search_parsed.get("month") is None and search_parsed.get("year") is None:
            raw = str(search_parsed.get("raw","")).strip().lower()
            if raw.isdigit() and 1 <= int(raw) <= 31:
                try:
                    if "-" in record_date_str:
                        parts = record_date_str.split("-")
                        if len(parts) >= 3:
                            rec_day = int(parts[2][:2]) if parts[2][:2].isdigit() else None
                            if rec_day is not None:
                                return rec_day == int(raw)
                    return False
                except:
                    return False
            else:
                return raw in str(record_date_str).lower()
        rec_str = str(record_date_str).strip()
        if not rec_str:
            return False
        rec_day = None
        rec_month = None
        rec_year = None
        try:
            if "-" in rec_str:
                rp = rec_str.split("-")
                if len(rp) >= 3:
                    if len(rp[0]) == 4 and rp[0].isdigit():
                        rec_year = int(rp[0]) if rp[0].isdigit() else None
                        rec_month = int(rp[1]) if rp[1].isdigit() else None
                        rec_day = int(rp[2][:2]) if rp[2][:2].isdigit() else None
                    else:
                        rec_day = int(rp[0]) if rp[0].isdigit() else None
                        rec_month = int(rp[1]) if rp[1].isdigit() else None
                        rec_year = int(rp[2][:4]) if len(rp[2])>=4 and rp[2][:4].isdigit() else None
        except:
            pass
        sd = search_parsed.get("day")
        sm = search_parsed.get("month")
        sy = search_parsed.get("year")
        if sd is not None and sm is not None and sy is not None:
            return (rec_day == sd and rec_month == sm and rec_year == sy)
        if sd is not None and sm is not None:
            return (rec_day == sd and rec_month == sm)
        if sd is not None and sm is None and sy is None:
            return rec_day == sd
        if sm is not None and sd is None and sy is None:
            return rec_month == sm
        if sy is not None and sd is None and sm is None:
            return rec_year == sy
        if sm is not None and sy is not None and sd is None:
            return (rec_month == sm and rec_year == sy)
        return False
    except:
        return False

# Session
if "section_opened_v3" not in st.session_state:
    st.session_state.section_opened_v3 = {"personal": True, "vital": False, "diseases": False, "complaint": False, "diagnosis": False, "billing": False}
if "personal_ok_v3" not in st.session_state:
    st.session_state.personal_ok_v3 = False
if "patient_diseases" not in st.session_state:
    st.session_state.patient_diseases = []
if "form_version" not in st.session_state:
    st.session_state.form_version = 0

clinic_phone = get_clinic_phone()
st.title("Herbal Clinic OS - V3.1")
tabs = st.tabs(["New Patient", "Revisit", "Debug"])

with tabs[2]:
    st.subheader("Debug V3.1")
    client, sid, err = get_client_v3()
    if err:
        st.error(err)
    else:
        st.success(f"Connected | Clinic hidden")
        ws, titles, headers, err2 = get_ws_v3("New_patient")
        if err2:
            st.error(err2)
        else:
            st.write(f"Headers: {len(headers)}/{len(STANDARD_HEADERS_V3)}")
            st.json(headers)
            if len(headers) < len(STANDARD_HEADERS_V3):
                if st.button("Fix Headers", type="primary"):
                    ws.update('A1', [STANDARD_HEADERS_V3], value_input_option='USER_ENTERED')
                    st.success("Fixed")
                    time.sleep(1)
                    st.rerun()

with tabs[0]:
    disp_id, full_id, daily_n, cphone = calculate_next_ids_v3()
    if "v3_date" not in st.session_state:
        st.session_state.v3_date = date.today()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="id-card"><h4 style="margin:0; color:#2e7d32;">{disp_id}</h4><small>Patient ID</small></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="daily-card"><h4 style="margin:0; color:#1565c0;">Daily: {daily_n}</h4><small>Today Count</small></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="date-card"><h4 style="margin:0; color:#ef6c00;">{st.session_state.v3_date}</h4><small>Entry Date</small></div>', unsafe_allow_html=True)
        st.session_state.v3_date = st.date_input("Date", value=st.session_state.v3_date, label_visibility="collapsed", key="v3_date_input")
    
    st.markdown("---")
    
    with st.container(border=True):
        st.markdown("#### Personal Information")
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            p_name = st.text_input("Patient Name*", placeholder="Ali Ahmed", key=f"v3_p_name_{st.session_state.form_version}")
            p_fname = st.text_input(FATHER_LABEL, placeholder="Father / Spouse", key=f"v3_p_fname_{st.session_state.form_version}")
            p_age = st.number_input("Age*", min_value=0, max_value=120, value=30, key=f"v3_p_age_{st.session_state.form_version}")
        with pc2:
            p_gender = st.selectbox("Gender*", ["Select","Male","Female"], key=f"v3_p_gender_{st.session_state.form_version}")
            p_phone = st.text_input("Patient Phone* (11 digits)", placeholder="03001234567", key=f"v3_p_phone_{st.session_state.form_version}")
            p_city = st.text_input("City", value="Bhai Pheru", key=f"v3_p_city_{st.session_state.form_version}")
        with pc3:
            p_address = st.text_area("Address*", height=80, placeholder="Full address", key=f"v3_p_address_{st.session_state.form_version}")
            p_occ = st.selectbox("Occupation", LISTS["occupation"], key=f"v3_p_occ_{st.session_state.form_version}")
            p_marital = st.selectbox("Marital Status", LISTS["marital"], key=f"v3_p_marital_{st.session_state.form_version}")
        p_blood = st.selectbox("Blood Group", LISTS["blood_group"], key=f"v3_p_blood_{st.session_state.form_version}")
        
        # Age/Gender Based Questions Full from V206
        mandatory_complete = p_name.strip() and p_age >0 and p_gender != "Select" and p_phone.strip() and p_address.strip()
        if mandatory_complete:
            age_qs = get_age_based_questions(str(p_age), p_gender)
            if age_qs:
                st.markdown("**Age / Gender Based Questions:**")
                cols = st.columns(2)
                for idx, (q_label, q_type, q_key) in enumerate(age_qs):
                    col = cols[idx % 2]
                    with col:
                        if isinstance(q_type, list):
                            st.selectbox(q_label, q_type, key=f"v3_age_q_{q_key}_{st.session_state.form_version}")
                        else:
                            st.text_input(q_label, key=f"v3_age_q_{q_key}_{st.session_state.form_version}")
        
        if not st.session_state.personal_ok_v3:
            if st.button("OK - Personal Information", type="primary", key="v3_personal_ok"):
                missing = []
                if not p_name.strip(): missing.append("Patient Name*")
                if p_age == 0: missing.append("Age*")
                if p_gender == "Select": missing.append("Gender*")
                if not p_phone.strip() or len(re.sub(r'[^0-9]', '', p_phone)) < 10: missing.append("Phone* (11 digits)")
                if not p_address.strip() or len(p_address.strip()) < 5: missing.append("Address* (5 chars)")
                if missing:
                    st.error(f"Missing: {', '.join(missing)}")
                else:
                    st.session_state.personal_ok_v3 = True
                    st.session_state.section_opened_v3["vital"] = True
                    show_popup("Personal Complete")
                    time.sleep(0.5)
                    st.rerun()
            if not mandatory_complete:
                st.warning("Complete Name*, Age*, Gender*, Phone*, Address* and click OK")
        else:
            st.success("Personal Completed - Click Edit to change")
            if st.button("Edit Personal Info", key="v3_personal_edit"):
                st.session_state.personal_ok_v3 = False
                st.session_state.section_opened_v3["vital"] = False
                st.rerun()
    
    if not st.session_state.personal_ok_v3:
        st.info("Complete Personal Information and click OK to unlock next sections")
        st.stop()
    
    # Vital - BP, Pulse, Temp with figure option + Mizaj custom
    with st.container(border=True):
        st.markdown("#### Vital Examination")
        v1, v2, v3, v4 = st.columns(4)
        with v1:
            bp_option = st.selectbox("BP", ["Select","High","Very high","Normal","Low","Very low","Other - Write figure"], key=f"v3_bp_opt_{st.session_state.form_version}")
            if bp_option == "Other - Write figure":
                bp = st.text_input("BP figure", placeholder="e.g., 120/80", key=f"v3_bp_fig_{st.session_state.form_version}")
            else:
                bp = bp_option if bp_option != "Select" else ""
        with v2:
            pulse_option = st.selectbox("Pulse", ["Select","Fast","Very fast","Normal","Weak","Very weak","Other - Write figure"], key=f"v3_pulse_opt_{st.session_state.form_version}")
            if pulse_option == "Other - Write figure":
                pulse = st.text_input("Pulse figure", placeholder="e.g., 78", key=f"v3_pulse_fig_{st.session_state.form_version}")
            else:
                pulse = pulse_option if pulse_option != "Select" else ""
        with v3:
            temp_option = st.selectbox("Temperature", ["Select","High","Very high","Normal","Low","Very low","Other - Write figure"], key=f"v3_temp_opt_{st.session_state.form_version}")
            if temp_option == "Other - Write figure":
                temp = st.text_input("Temp figure", placeholder="e.g., 98.6F", key=f"v3_temp_fig_{st.session_state.form_version}")
            else:
                temp = temp_option if temp_option != "Select" else ""
        with v4:
            mizaj_option = st.selectbox("Mizaj", ["Select","Cold Dry","Dry Cold","Dry Hot","Hot Dry","Hot Wet","Wet Hot","Wet Cold","Cold Wet","Other - Write"], key=f"v3_mizaj_opt_{st.session_state.form_version}")
            if mizaj_option == "Other - Write":
                mizaj = st.text_input("Mizaj custom", placeholder="Write mizaj", key=f"v3_mizaj_custom_{st.session_state.form_version}")
            else:
                mizaj = mizaj_option if mizaj_option != "Select" else ""
        v5, v6 = st.columns(2)
        with v5:
            weight = st.text_input("Weight", placeholder="70kg", key=f"v3_weight_{st.session_state.form_version}")
        with v6:
            height = st.text_input("Height", placeholder="5.8", key=f"v3_height_{st.session_state.form_version}")
    
    # Diseases Section Full from V206
    with st.container(border=True):
        st.markdown("#### Diseases")
        dc1, dc2, dc3, dc4 = st.columns([3,3,2,2])
        with dc1:
            body_part = st.selectbox("Body Part*", list(BODY_PARTS.keys()), key=f"v3_body_part_{st.session_state.form_version}")
            sub_diseases = BODY_PARTS.get(body_part, ["Select"])
        with dc2:
            disease = st.selectbox(f"Disease in {body_part}*", sub_diseases, key=f"v3_disease_sub_{st.session_state.form_version}")
        with dc3:
            no_options = ["Select","1","2","3","4","5","6","7","8","9","10","Other"]
            d_no_sel = st.selectbox("No/Count*", no_options, key=f"v3_no_sel_{st.session_state.form_version}")
            if d_no_sel == "Other":
                d_no = st.text_input("Enter Count", key=f"v3_no_{st.session_state.form_version}")
            else:
                d_no = d_no_sel if d_no_sel != "Select" else ""
        with dc4:
            d_duration = st.selectbox("Duration*", LISTS["duration"], key=f"v3_dur_{st.session_state.form_version}")
        
        all_fields_complete = body_part != "Select" and disease != "Select" and str(d_no).strip() != "" and d_duration != "Select"
        if all_fields_complete:
            st.markdown(f"**Related Questions for {body_part} - {disease}**")
            related_qs = DISEASE_RELATED_QUESTIONS.get(body_part, DISEASE_RELATED_QUESTIONS["General"])
            dd_map = DISEASE_RELATED_DROPDOWNS.get(body_part, {})
            cq1, cq2, cq3 = st.columns(3)
            with cq1:
                q1_label = related_qs[0] if len(related_qs)>0 else "Severity"
                q1_options = dd_map.get(q1_label, LISTS["severity"])
                rq1 = st.selectbox(q1_label, q1_options, key=f"v3_rel_q1_{st.session_state.form_version}")
            with cq2:
                q2_label = related_qs[1] if len(related_qs)>1 else "Trigger"
                q2_options = dd_map.get(q2_label, ["Select","Yes","No","Sometimes"])
                rq2 = st.selectbox(q2_label, q2_options, key=f"v3_rel_q2_{st.session_state.form_version}")
            with cq3:
                q3_label = related_qs[2] if len(related_qs)>2 else "Associated Symptom"
                q3_options = dd_map.get(q3_label, ["Select","Nausea","Burning","Pain","Itching","None","Other"])
                rq3 = st.selectbox(q3_label, q3_options, key=f"v3_rel_q3_{st.session_state.form_version}")
        else:
            rq1 = rq2 = rq3 = "Select"
            if body_part != "Select" and disease != "Select":
                st.info("Complete No/Count* and Duration* to see Related Questions")
        
        if st.button("Add Disease +", key=f"v3_add_disease_{st.session_state.form_version}", use_container_width=True):
            if body_part=="Select":
                st.error("Select Body Part")
            elif disease=="Select":
                st.error("Select Disease")
            elif not d_no:
                st.error("Enter No/Count")
            elif d_duration=="Select":
                st.error("Select Duration")
            else:
                entry_text = f"Body Part: {body_part} + Disease: {disease} + Count: {d_no} + Duration: {d_duration}"
                if rq1 and rq1!="Select": entry_text += f" + {rq1}"
                if rq2 and rq2!="Select": entry_text += f" + {rq2}"
                if rq3 and rq3!="Select": entry_text += f" + {rq3}"
                st.session_state.patient_diseases.append({"text": entry_text})
                show_popup(f"Added: {disease}")
                st.rerun()
    
    # Added Diseases Display
    if st.session_state.patient_diseases:
        st.markdown("**Added Diseases:**")
        combined = " + ".join([d.get("text","") for d in st.session_state.patient_diseases])
        st.markdown(f'<div style="background:#FFFFFF;border:2px solid #2E7D5B;border-radius:10px;padding:10px;"><b>Combined:</b> {combined}</div>', unsafe_allow_html=True)
        for i, dd in enumerate(st.session_state.patient_diseases):
            c1, c2 = st.columns([4,1])
            with c1:
                st.write(f"{i+1}. {dd.get('text','')}")
            with c2:
                if st.button("Remove", key=f"v3_rem_{i}_{st.session_state.form_version}"):
                    st.session_state.patient_diseases.pop(i)
                    st.rerun()
    
    # Complaint, History, Diagnosis
    with st.container(border=True):
        st.markdown("#### Complaint, History, Diagnosis")
        b1, b2 = st.columns(2)
        with b1:
            history = st.text_area("Past History", height=100, key=f"v3_history_{st.session_state.form_version}")
            complaint = st.text_area("Complaint", height=100, placeholder="General Checkup if empty", key=f"v3_complaint_{st.session_state.form_version}")
        with b2:
            diagnosis = st.text_area("Diagnosis", height=100, key=f"v3_diag_{st.session_state.form_version}")
            treatment = st.text_area("Treatment", height=100, key=f"v3_treat_{st.session_state.form_version}")
    
    # Billing Complete
    with st.container(border=True):
        st.markdown("#### Billing")
        bill1, bill2, bill3, bill4 = st.columns(4)
        with bill1:
            fees = st.text_input("Consultation Fees", value="500", key=f"v3_fees_{st.session_state.form_version}")
        with bill2:
            med_charges = st.text_input("Medicine Charges", value="0", key=f"v3_med_{st.session_state.form_version}")
        with bill3:
            try:
                total_calc = float(fees or 0) + float(med_charges or 0)
            except:
                total_calc = 0
            total = st.text_input("Total", value=str(total_calc), key=f"v3_total_{st.session_state.form_version}")
        with bill4:
            paid = st.text_input("Paid", value=str(total_calc), key=f"v3_paid_{st.session_state.form_version}")
        
        bill5, bill6 = st.columns(2)
        with bill5:
            try:
                balance_calc = float(total or 0) - float(paid or 0)
            except:
                balance_calc = 0
            balance = st.text_input("Balance", value=str(balance_calc), key=f"v3_balance_{st.session_state.form_version}")
        with bill6:
            status = st.selectbox("Payment Status", ["Cash","Outstanding","Free"], key=f"v3_status_{st.session_state.form_version}")
            payment_method = st.selectbox("Payment Method", ["Select","Cash","Online","JazzCash","Free"], key=f"v3_pay_method_{st.session_state.form_version}")
        
        if st.button(f"Save Patient {disp_id} - Daily {daily_n}", type="primary", use_container_width=True, key=f"v3_save_new_{st.session_state.form_version}"):
            if not p_name.strip() or not p_phone.strip():
                st.error("Name & Phone required!")
            else:
                if not complaint.strip():
                    complaint = "General Checkup"
                disp_save, full_save, daily_save, cphone_save = calculate_next_ids_v3()
                diseases_text = " + ".join([d.get("text","") for d in st.session_state.patient_diseases]) if st.session_state.patient_diseases else ""
                data = {
                    "PatientID": full_save,
                    "OriginalPatientID": full_save,
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
                    "BP": bp,
                    "Pulse": pulse,
                    "Weight": weight.strip(),
                    "Height": height.strip(),
                    "Temperament": mizaj,
                    "Diseases": diseases_text,
                    "History": history.strip(),
                    "Complaint": complaint.strip(),
                    "Diagnosis": diagnosis.strip(),
                    "Treatment": treatment.strip(),
                    "Fees": fees.strip(),
                    "Status": status,
                    "Total": total,
                    "Paid": paid,
                    "Balance": balance,
                    "PaymentMethod": payment_method
                }
                with st.spinner(f"Saving {disp_save}..."):
                    if append_v3("New_patient", data):
                        show_popup(f"Saved! {disp_save} | Daily: {daily_save}")
                        st.session_state.personal_ok_v3 = False
                        st.session_state.patient_diseases = []
                        st.session_state.form_version += 1
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Save failed")

with tabs[1]:
    st.subheader("Revisit - Search Patient")
    # V206 Revisit Search Logic Full Imported - No dropdown, 4 fields
    df = read_sheet_v3("New_patient")
    
    # Fixed KeyError by checking columns exist
    if df.empty:
        st.info("No data yet")
        st.stop()
    
    # Ensure required columns exist to prevent KeyError
    for col in ["PatientID","OriginalPatientID","ClinicPhone","Date","Name","Phone","Address","FatherName"]:
        if col not in df.columns:
            df[col] = ""
    
    c1, c2 = st.columns(2)
    with c1:
        s_name = st.text_input("Patient Name", key="rev_name_v3", placeholder="Full or partial")
        s_date = st.text_input("Date (YYYY-MM-DD)", key="rev_date_v3", placeholder="e.g., 1 or 1-05 or 2026-05-01")
    with c2:
        s_phone = st.text_input("Phone Number", key="rev_phone_v3", placeholder="Full or partial")
        s_address = st.text_input("Address", key="rev_address_v3", placeholder="City or full address")
    
    if s_name or s_phone or s_date or s_address:
        filt = []
        is_date_search = bool(s_date and s_date.strip())
        parsed_date = parse_date_search(s_date) if is_date_search else None
        seen_ids = set()
        for _, r in df.iterrows():
            try:
                pid = str(r.get("PatientID","")).strip()
                match = False
                if s_name:
                    s_name_lower = str(s_name).strip().lower()
                    rec_name_lower = str(r.get("Name","")).lower()
                    if s_name_lower == rec_name_lower or s_name_lower in rec_name_lower:
                        match = True
                if s_phone:
                    s_phone_clean = str(s_phone).strip().replace(" ","").replace("-","")
                    rec_phone_clean = str(r.get("Phone","")).replace(" ","").replace("-","")
                    if s_phone_clean in rec_phone_clean:
                        match = True
                if s_date:
                    rec_date = str(r.get("Date","")).strip()
                    if parsed_date:
                        if match_date_record(rec_date, parsed_date):
                            match = True
                    else:
                        if str(s_date).strip().lower() in rec_date.lower():
                            match = True
                if s_address:
                    s_addr_lower = str(s_address).strip().lower()
                    rec_addr_lower = str(r.get("Address","")).lower()
                    if s_addr_lower in rec_addr_lower:
                        match = True
                if match:
                    if is_date_search and not s_name and not s_phone and not s_address:
                        filt.append(r)
                    else:
                        if pid and pid not in seen_ids:
                            filt.append(r)
                            seen_ids.add(pid)
                        elif not pid:
                            filt.append(r)
            except Exception as e:
                continue
        
        # Deduplicate
        if is_date_search and not s_name and not s_phone and not s_address:
            seen_combo = set()
            unique_filt = []
            for r in filt:
                try:
                    pid = str(r.get("PatientID","")).strip()
                    date_val = str(r.get("Date","")).strip()
                    combo_simple = f"{pid}_{date_val}"
                    if combo_simple not in seen_combo:
                        if not any(str(x.get("PatientID","")).strip() == pid and str(x.get("Date","")).strip() == date_val for x in unique_filt):
                            unique_filt.append(r)
                            seen_combo.add(combo_simple)
                except:
                    continue
            filt = unique_filt
            st.write(f"Found {len(filt)} visits")
        else:
            unique_by_id = {}
            for r in filt:
                try:
                    pid = str(r.get("PatientID","")).strip()
                    if pid not in unique_by_id:
                        unique_by_id[pid] = r
                    else:
                        try:
                            existing_date = str(unique_by_id[pid].get("Date",""))
                            new_date = str(r.get("Date",""))
                            if new_date > existing_date:
                                unique_by_id[pid] = r
                        except:
                            pass
                except:
                    continue
            filt = list(unique_by_id.values())
            st.write(f"Found {len(filt)} patients")
        
        for idx, r in enumerate(filt[:20]):
            try:
                with st.container(border=True):
                    st.write(f"{r.get('Name','')} | Date: {r.get('Date','')} | Address: {r.get('Address','')} | Phone: {r.get('Phone','')} | ID: {r.get('PatientID','')} | Balance: {r.get('Balance','0')}")
                    if st.button(f"Open {r.get('PatientID','')} - {r.get('Name','')}", key=f"rev_{r.get('PatientID','')}_{idx}_v3"):
                        st.session_state.revisit_data = r.to_dict() if hasattr(r, 'to_dict') else dict(r)
                        # History chain
                        try:
                            pid = str(r.get("PatientID","")).strip()
                            orig = str(r.get("OriginalPatientID", pid)).strip()
                            chain = df[(df["OriginalPatientID"].astype(str)==orig) | (df["PatientID"].astype(str)==pid) | (df["PatientID"].astype(str)==orig)]
                            st.session_state.revisit_history_chain = chain.sort_values("Date", ascending=False).to_dict('records') if not chain.empty else [r.to_dict() if hasattr(r, 'to_dict') else dict(r)]
                        except:
                            st.session_state.revisit_history_chain = [r.to_dict() if hasattr(r, 'to_dict') else dict(r)]
                        st.session_state.current_revisit_open = True
                        st.rerun()
            except Exception as e:
                continue
    else:
        st.info("Enter Name, Date, Phone, or Address to search")
        # Show recent to prevent KeyError
        try:
            recent = df.tail(10).sort_index(ascending=False)
            if not recent.empty:
                recent_display = recent.copy()
                recent_display["DisplayID"] = recent_display["PatientID"].astype(str).apply(lambda x: '_'.join(x.split('_')[:2]) if x.count('_')>=2 else x)
                st.dataframe(recent_display[["DisplayID","Date","Name","FatherName","Phone"]], use_container_width=True)
        except Exception as e:
            st.write(f"Recent data error: {e}")
    
    # Revisit Form if opened
    if st.session_state.get("current_revisit_open") and st.session_state.get("revisit_data"):
        r = st.session_state.revisit_data
        chain = st.session_state.get("revisit_history_chain", [r])
        st.markdown("---")
        st.subheader(f"Revisit Form - {r.get('Name','')} | {r.get('PatientID','')}")
        
        # History display per section (V206)
        if len(chain) > 1:
            with st.container(border=True):
                st.markdown("**Previous History - All Visits:**")
                for hist_r in chain[:3]:
                    st.write(f"{hist_r.get('Date','')} - {hist_r.get('Complaint','')[:50]} - {hist_r.get('Diagnosis','')[:50]}")
        
        # Edit form
        with st.form(f"revisit_edit_{r.get('PatientID','')}", clear_on_submit=False):
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                st.text_input("Original ID", value=str(r.get('OriginalPatientID', r.get('PatientID',''))), disabled=True, key=f"r_orig_{r.get('PatientID','')}")
            with rc2:
                st.text_input("This Visit ID", value=str(r.get('PatientID','')), disabled=True, key=f"r_visit_{r.get('PatientID','')}")
            with rc3:
                r_date = st.date_input("Visit Date", value=pd.to_datetime(r.get('Date', date.today())).date() if r.get('Date') else date.today(), key=f"r_date_{r.get('PatientID','')}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                r_name = st.text_input("Patient Name*", value=str(r.get('Name','')), key=f"r_name_{r.get('PatientID','')}")
                r_fname = st.text_input(FATHER_LABEL, value=str(r.get('FatherName','')), key=f"r_fname_{r.get('PatientID','')}")
                try:
                    age_val = int(str(r.get('Age','30')).split()[0]) if str(r.get('Age','')).split()[0].isdigit() else 30
                except:
                    age_val = 30
                r_age = st.number_input("Age*", min_value=0, max_value=120, value=age_val, key=f"r_age_{r.get('PatientID','')}")
            with c2:
                r_gender = st.selectbox("Gender*", ["Male","Female"], index=0 if "Male" in str(r.get('Gender','')) else 1, key=f"r_gender_{r.get('PatientID','')}")
                r_phone = st.text_input("Phone* (11 digits)", value=str(r.get('Phone','')), key=f"r_phone_{r.get('PatientID','')}")
                r_city = st.text_input("City", value=str(r.get('City','Bhai Pheru')), key=f"r_city_{r.get('PatientID','')}")
            with c3:
                r_address = st.text_area("Address*", value=str(r.get('Address','')), height=80, key=f"r_address_{r.get('PatientID','')}")
            
            # Vital with figure option
            rv1, rv2 = st.columns(2)
            with rv1:
                bp_opt = st.selectbox("BP", ["Select","High","Very high","Normal","Low","Very low","Other - Write figure"], key=f"r_bp_opt_{r.get('PatientID','')}")
                if bp_opt == "Other - Write figure":
                    r_bp = st.text_input("BP figure", value=str(r.get('BP','')), key=f"r_bp_fig_{r.get('PatientID','')}")
                else:
                    r_bp = bp_opt if bp_opt != "Select" else str(r.get('BP',''))
            with rv2:
                pulse_opt = st.selectbox("Pulse", ["Select","Fast","Very fast","Normal","Weak","Very weak","Other - Write figure"], key=f"r_pulse_opt_{r.get('PatientID','')}")
                if pulse_opt == "Other - Write figure":
                    r_pulse = st.text_input("Pulse figure", value=str(r.get('Pulse','')), key=f"r_pulse_fig_{r.get('PatientID','')}")
                else:
                    r_pulse = pulse_opt if pulse_opt != "Select" else str(r.get('Pulse',''))
            
            mizaj_opts = ["Select","Cold Dry","Dry Cold","Dry Hot","Hot Dry","Hot Wet","Wet Hot","Wet Cold","Cold Wet","Other - Write"]
            current_mizaj = str(r.get('Temperament',''))
            mizaj_idx = mizaj_opts.index(current_mizaj) if current_mizaj in mizaj_opts else 0
            mizaj_sel = st.selectbox("Mizaj", mizaj_opts, index=mizaj_idx, key=f"r_mizaj_{r.get('PatientID','')}")
            if mizaj_sel == "Other - Write":
                r_mizaj = st.text_input("Mizaj custom", value=current_mizaj, key=f"r_mizaj_custom_{r.get('PatientID','')}")
            else:
                r_mizaj = mizaj_sel if mizaj_sel != "Select" else current_mizaj
            
            rb1, rb2 = st.columns(2)
            with rb1:
                r_history = st.text_area("History", value=str(r.get('History','')), height=80, key=f"r_hist_{r.get('PatientID','')}")
                r_complaint = st.text_area("Complaint", value=str(r.get('Complaint','')), height=80, key=f"r_comp_{r.get('PatientID','')}")
            with rb2:
                r_diagnosis = st.text_area("Diagnosis", value=str(r.get('Diagnosis','')), height=80, key=f"r_diag_{r.get('PatientID','')}")
                r_treatment = st.text_area("Treatment", value=str(r.get('Treatment','')), height=80, key=f"r_treat_{r.get('PatientID','')}")
            
            rf1, rf2 = st.columns(2)
            with rf1:
                r_fees = st.text_input("Fees", value=str(r.get('Fees','500')), key=f"r_fees_{r.get('PatientID','')}")
            with rf2:
                r_status = st.selectbox("Payment Status", ["Cash","Outstanding","Free"], index=["Cash","Outstanding","Free"].index(str(r.get('Status','Cash'))) if str(r.get('Status','')) in ["Cash","Outstanding","Free"] else 0, key=f"r_status_{r.get('PatientID','')}")
            
            col_save, col_new = st.columns(2)
            with col_save:
                save_edit = st.form_submit_button(f"Update This Visit", type="primary", use_container_width=True)
            with col_new:
                save_new_visit = st.form_submit_button(f"Save as New Visit", use_container_width=True)
            
            if save_edit:
                update_data = {
                    "PatientID": r.get('PatientID',''),
                    "OriginalPatientID": r.get('OriginalPatientID', r.get('PatientID','')),
                    "ClinicPhone": clinic_phone,
                    "Date": str(r_date),
                    "Name": r_name.strip(),
                    "FatherName": r_fname.strip(),
                    "Age": r_age,
                    "Gender": r_gender,
                    "Phone": r_phone.strip(),
                    "Address": r_address.strip(),
                    "City": r_city.strip(),
                    "BP": r_bp,
                    "Pulse": r_pulse,
                    "Temperament": r_mizaj,
                    "History": r_history.strip(),
                    "Complaint": r_complaint.strip(),
                    "Diagnosis": r_diagnosis.strip(),
                    "Treatment": r_treatment.strip(),
                    "Fees": r_fees.strip(),
                    "Status": r_status
                }
                if update_v3("New_patient", r.get('PatientID',''), update_data):
                    show_popup(f"Updated {r.get('PatientID','')}")
                    time.sleep(1)
                    st.rerun()
            
            if save_new_visit:
                disp_new, full_new, daily_new, _ = calculate_next_ids_v3()
                original_id = r.get('OriginalPatientID', r.get('PatientID',''))
                new_data = {
                    "PatientID": full_new,
                    "OriginalPatientID": original_id,
                    "ClinicPhone": clinic_phone,
                    "DailyNumber": daily_new,
                    "Date": str(r_date),
                    "Name": r_name.strip(),
                    "FatherName": r_fname.strip(),
                    "Age": r_age,
                    "Gender": r_gender,
                    "Phone": r_phone.strip(),
                    "Address": r_address.strip(),
                    "City": r_city.strip(),
                    "BP": r_bp,
                    "Pulse": r_pulse,
                    "Temperament": r_mizaj,
                    "History": r_history.strip(),
                    "Complaint": r_complaint.strip(),
                    "Diagnosis": r_diagnosis.strip(),
                    "Treatment": r_treatment.strip(),
                    "Fees": r_fees.strip(),
                    "Status": r_status
                }
                if append_v3("New_patient", new_data):
                    show_popup(f"New Visit Saved! Original: {original_id} | New: {full_new}")
                    time.sleep(1)
                    st.rerun()
        
        if st.button("Close Revisit Form"):
            st.session_state.current_revisit_open = False
            st.rerun()
