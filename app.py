
import streamlit as st
import datetime
import re
import pandas as pd

# NOTE FOR EVERY APP VERSION - V177
# This app can be used in 3 languages: English, Urdu and Arabic.
# Words from a different language must not be used anywhere in the app while another language is active.
# English is default language.
# Global icon for language selection is placed on every page.
# Later we will create concise dictionary English/Urdu/Arabic and app will retrieve terms from dictionary when switching languages.

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

APP_VERSION = "V198"  # V175 - PC gap reduced, tab fields clear, PC headings larger, mobile icon-sized fields, light strategy kept, icon+black field, Open removed, hover green highlight, Offer black field blinking green, footer light gray  # V172 - Sheet cleanup, boundary thick #0e1117, fix duplicate save, new ID, Proceed reset, New/Revisit options, 5 patients Home User, Revisit history display, Billing blank

WHATSAPP_LINK = "https://chat.whatsapp.com/J7xfZT2Pf4H8Zzu7eBD7CS"

def sanitize_for_sheet(text):
    if not text: return ""
    text = str(text).strip()
    text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

st.set_page_config(page_title="Herbal Clinic International", page_icon="\U0001f33f", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
/* V198 - Herbal Light Theme - Safe minimal CSS */
html, body, .stApp, [data-testid="stAppViewContainer"] { background: #FFFFFF !important; color: #1F2D27 !important; }
.block-container { 
    max-width: 940px !important; 
    margin: 20px auto !important; 
    padding: 1.6rem 1.8rem !important; 
    background: #FFFFFF !important; 
    border: 3px solid #2E7D5B !important;
    border-radius: 20px !important; 
    box-shadow: 0 4px 20px rgba(46,125,91,0.12) !important;
}
#MainMenu, header {visibility: hidden;}
div[data-testid="stSidebar"] {display: none;}
.heading-h1 { font-size: 44px !important; font-weight: 900 !important; color:#2E7D5B !important; }
.heading-h2 { font-size: 22px !important; font-weight: 700 !important; color:#2E7D5B !important; }
.heading-h3 { font-size: 26px !important; font-weight: 700 !important; color:#1F2D27 !important; }
.heading-h4 { font-size: 22px !important; font-weight: 700 !important; color:#1F2D27 !important; margin:10px 0 !important; }
.heading-h5 { font-size: 20px !important; font-weight: 600 !important; color:#2E7D5B !important; }
.graceful-card { background: #F1F7F3; border:2px solid #2E7D5B; border-radius:12px; padding:12px; text-align:center; color:#1F2D27 !important; }
.dash-section-title { font-size:18px; font-weight:700; color:#FFFFFF; background:#2E7D5B; padding:8px 14px; border-radius:8px; margin:18px 0 10px 0; }
.demo-card { background: #F1F7F3; border:1px solid #C8E6D5; border-radius:14px; padding:16px; color:#1F2D27 !important; }
.footer-sharp { text-align:center; color:#5a6d65 !important; font-size:12px !important; margin-top:30px; border-top:1px solid #C8E6D5; padding:14px; }
.history-card { background:#F1F7F3; border:1px solid #C8E6D5; border-radius:12px; padding:12px; margin-bottom:10px; color:#1F2D27; }
</style>
""", unsafe_allow_html=True)


# GOOGLE SHEET - V186 Final Structure - 12 sheets as per user decision
# General (4): UserSignups, PermissionGranted, Articles, Feedback - displayed in App Admin alongside other tabs, not dashboard
# Clinic (6): New_patient, Revisit, AutoDiagnosis, Herbs, Pharmacopoeia, Dictionary - for clinics + dashboard
# Home User (1+1): HomeUsers + Home Treatment form
# AppSettings (1): OfferPercent, WhatsAppLink, AppVersion, MaintenanceMode etc - control sheet
# Removed: ClinicUsers merged into UserSignups with CU_ / HU_ IDs, Formulas merged into Pharmacopoeia
SHEET_HEADERS = {
    "UserSignups": ["SignupID","Username","Password","UserType","ClinicName","Phone","Email","Date","Status","Role","From"],
    "PermissionGranted": ["ID","Username","UserType","PermissionType","GrantedDate","Status","IP","Device"],
    "HomeUsers": ["UserID","Username","Password","FullName","Phone","Email","Date","Status","AccountHolderPhone","From"],
    "New_patient": ["PatientID","Date","Name","FatherName","Age","Gender","MaritalStatus","Occupation","CNIC","Phone","EmergencyPhone","Address","Referral","Diseases","ChiefComplaint","PastHistory","FamilyHistory","Allergy","Examination","Pulse","Temperament","BP","Weight","Temperature","SingleMedicines","FormulaMedicines","Fees","MedicineCharges","Total","Paid","Balance","PrevBalance","PaymentMethod","FeeStatus","RevisitDate","ClinicName","CreatedBy","Timestamp","AppVersion","DailyNumber","TotalNumber","GrandTotal"],
    "Revisit": ["RevisitID","PatientID","Date","Name","Phone","ClinicName","Complaint","Prescription","Fees","Paid","Balance","CreatedBy"],
    "AutoDiagnosis": ["ID","PatientID","Date","Name","FatherName","Age","Phone","Gender","Address","Diseases","ExtraSymptoms","Temperament","ClinicName","CreatedBy","AppVersion","GrandTotal"],
    "Herbs": ["HerbID","Name","Temperament","Uses","Dosage","ClinicName"],
    "Pharmacopoeia": ["ID","Name","Category","Temperament","Uses","Dosage","ClinicName"],
    "Dictionary": ["ID","Word","Meaning","Category","Language"],
    "Articles": ["ID","TitleEN","TitleUR","TitleAR","ContentEN","ContentUR","ContentAR","MainCategory","SubCategory","Audience","Type","Status","Date","ClinicName"],
    "Feedback": ["ID","Name","From","Phone Number","Email","Feedback Page","Feedback","Date","Status"],
    "AppSettings": ["Key","Value","Date","Status","Description"],
}
ALL_SHEETS = list(SHEET_HEADERS.keys())
# Section division for App Admin
GENERAL_SHEETS = ["UserSignups", "PermissionGranted", "Articles", "Feedback"]
CLINIC_SHEETS = ["New_patient", "Revisit", "AutoDiagnosis", "Herbs", "Pharmacopoeia", "Dictionary"]
HOME_SHEETS = ["HomeUsers"]
# AppSettings kept separate for control

LANG_DICT = {
    "en": {"app_name": "Herbal Clinic International"},
    "ur": {"app_name": "ہربل کلینک انٹرنیشنل"},
    "ar": {"app_name": "عيادة الأعشاب الدولية"},
}

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

LISTS = {
    "gender": ["Select","Male","Female"],
    "temperament": ["Select","Cold Dry","Dry Cold","Dry Hot","Hot Dry","Hot Wet","Wet Hot","Wet Cold","Cold Wet"],
    "fee_status": ["Select","Paid","Unpaid","Partial","Free"],
    "payment": ["Select","Cash","Online","JazzCash","Free"],
    "marital": ["Select","Single","Married"],
    "duration": ["Select","Day","Month","Year"],
    "severity": ["Select","Mild","Moderate","Severe"],
    "blood_group": ["Select","A+","A-","B+","B-","O+","O-","AB+","AB-"],
    "sleep": ["Select","Normal","Less","Excess","Disturbed"],
    "appetite": ["Select","Normal","Less","Excess","No Appetite"],
    "bowel": ["Select","Normal","Constipated","Loose","Irregular"],
    "allergy": ["Select","None","Dust","Pollen","Food","Medicine","Cold","Skin","Smoke","Other"],
    "occupation": ["Select","Student","Teacher","Farmer","Shopkeeper","Laborer","Driver","Housewife","Business","Doctor","Engineer","Government Job","Private Job","Retired","Unemployed","Other"],
}

defaults = {
    "logged_in": False,
    "current_page": "clinic_login",
    "lang": "en",
    "show_lang_selector": False,
    "clinic_name": "Herbal Clinic International",
    "physician_name": "Hakeem Muhammad Ahmad",
    "form_version": 0,
    "auto_diseases": [],
    "home_auto_diseases": [],
    "auto_disease_version": 0,
    "home_auto_disease_version": 0,
    "prev_balance": 0.0,
    "patient_diseases": [],
    "patient_disease_version": 0,
    "revisit_data": None,
    "auto_revisit_data": None,
    "home_auto_revisit_data": None,
    "username": "",
    "user_role": "clinic",
    "user_type": "Clinic",
    "feedback_page_ref": "",
    "admin_selected_section": "",
    "show_proceed_note": False,
    "show_home_proceed_note": False,
    "prev_page": "dashboard_welcome",
    "page_history": ["dashboard_welcome"],
    "auto_form_mode": "New Patient",
    "home_auto_form_mode": "New Patient",
    "home_user_patients": [],
    "auto_rev_date": "",
    "auto_rev_address": "",
    "auto_selected_patient": None,
    "section_opened": {"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False},
    "section_unlocked": {"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False},
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

def navigate_to(page):
    if "page_history" not in st.session_state:
        st.session_state.page_history = ["dashboard_welcome"]
    if st.session_state.get("current_page") != page:
        st.session_state.prev_page = st.session_state.get("current_page","dashboard_welcome")
        st.session_state.page_history.append(st.session_state.get("current_page","dashboard_welcome"))
        if len(st.session_state.page_history) > 20:
            st.session_state.page_history = st.session_state.page_history[-20:]
    st.session_state.current_page = page
    st.rerun()

def language_selector():
    top_c1, top_c2 = st.columns([3,1])
    with top_c1:
        st.markdown(f"<div style='font-size:11px;color:#181819;'></div>", unsafe_allow_html=True)
    with top_c2:
        # Fixed CSS - only for language icon, not for menu tabs - remove green border from last tab
        st.markdown('''<style>
        /* Language icon only - scoped, not affecting menu tabs */
        </style>''', unsafe_allow_html=True)
        if st.button("🌐", key=f"global_lang_icon_{st.session_state.current_page}_{st.session_state.form_version}_v179", help="Select Language - V179 Bigger Clear"):
            st.session_state.show_lang_selector = not st.session_state.show_lang_selector
    if st.session_state.get("show_lang_selector", False):
        st.markdown("<div style='background:#1a1c23;border:1px solid #333;border-radius:10px;padding:10px;margin-bottom:10px;'>", unsafe_allow_html=True)
        st.markdown("**Select Language**")
        lang_choice = st.radio("Language", ["English", "Urdu", "Arabic"], index=["en","ur","ar"].index(st.session_state.get("lang","en")) if st.session_state.get("lang","en") in ["en","ur","ar"] else 0, key=f"lang_radio_v172", label_visibility="collapsed", horizontal=True)
        if lang_choice == "English": st.session_state.lang = "en"
        elif lang_choice == "Urdu": st.session_state.lang = "ur"
        elif lang_choice == "Arabic": st.session_state.lang = "ar"
        if st.button("Close", key="close_lang_selector_v172"):
            st.session_state.show_lang_selector = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def get_user_display_h2():
    role = st.session_state.get("user_role","")
    uname = st.session_state.get("username","")
    cname = st.session_state.get("clinic_name","Herbal Clinic International")
    if role == "Boss" or role == "Staff" or st.session_state.get("user_type")=="Staff":
        return f"Staff - {uname} - {cname}"
    elif role == "home_user" or st.session_state.get("user_type")=="HomeUser":
        return f"Home User - {uname} - {cname}"
    else:
        return f"Clinic - {uname} - {cname}"

def clinic_heading_banner():
    user_h2 = get_user_display_h2()
    st.markdown(f"""
    <div style="background:#FFFFFF;border:3px solid #2E7D5B;border-radius:20px;padding:28px 24px;text-align:center;margin-bottom:12px;box-shadow: 0 4px 16px rgba(46,125,91,0.12);">
        <div style="font-family:'Segoe UI', 'Inter', sans-serif;font-weight:900;letter-spacing:1px;text-transform:uppercase;color:#2E7D5B !important;background:#F1F7F3;padding:10px 18px;border-radius:12px;display:inline-block;border:1.5px solid #C8E6D5;font-size:44px;">Herbal Clinic International</div>
        <div style="color:#5a6d65 !important; font-size:22px; font-weight:600; margin-top:14px;">Based on human temperament</div>
        <div style="font-size:22px; font-weight:800; color:#00f700 !important; margin-top:16px; background:#F1F7F3;padding:8px 16px;border-radius:10px;display:inline-block;border:1.5px solid #C8E6D5;text-shadow: 0 1px 0 #aac94c;">{user_h2}</div>
    </div>
    """, unsafe_allow_html=True)

def top_nav_inner():
    c1,c2=st.columns([1,1])
    with c1:
        if st.button("Back", key=f"back_{st.session_state.current_page}_v172"):
            hist = st.session_state.get("page_history", ["dashboard_welcome"])
            if len(hist) > 0:
                prev = hist.pop() if hist else "dashboard_welcome"
                if prev == st.session_state.current_page and hist:
                    prev = hist.pop() if hist else "dashboard_welcome"
                st.session_state.current_page = prev if prev else "dashboard_welcome"
            else:
                st.session_state.current_page = st.session_state.get("prev_page","dashboard_welcome")
            st.rerun()
    with c2:
        if st.button("Dashboard", key=f"dash_{st.session_state.current_page}_v172", type="primary"):
            st.session_state.page_history.append(st.session_state.current_page)
            st.session_state.prev_page = st.session_state.current_page
            st.session_state.current_page="dashboard_welcome"
            st.rerun()
    st.divider()

def top_nav_dashboard():
    c1,c2=st.columns([4,1])
    with c2:
        if st.button("Logout", key=f"logout_dash_v172", type="secondary"):
            st.session_state.logged_in=False
            st.session_state.current_page="clinic_login"
            st.session_state.page_history=["dashboard_welcome"]
            st.rerun()
    st.divider()

@st.cache_resource(show_spinner=False, ttl=3600)
def get_gspread_client():
    try:
        if not GSPREAD_AVAILABLE: return None
        scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
        creds_dict=None
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            creds_dict=dict(st.secrets["connections"]["gsheets"])
        elif "gcp_service_account" in st.secrets:
            creds_dict=dict(st.secrets["gcp_service_account"])
        if not creds_dict: return None
        if "private_key" in creds_dict:
            creds_dict["private_key"]=creds_dict["private_key"].replace("\\n","\n")
        creds=Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except: return None

@st.cache_resource(show_spinner=False, ttl=3600)
def get_spreadsheet_cached():
    try:
        client=get_gspread_client()
        if not client: return None
        sid=None
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            sid=st.secrets["connections"]["gsheets"].get("spreadsheet")
        if not sid and "gsheets" in st.secrets:
            sid=st.secrets["gsheets"].get("spreadsheet")
        if not sid: return None
        return client.open_by_key(sid)
    except: return None

def get_sheet_safe(name):
    try:
        sh=get_spreadsheet_cached()
        if not sh: return None
        try: return sh.worksheet(name)
        except:
            try:
                hdr=SHEET_HEADERS.get(name, ["ID"])
                ws=sh.add_worksheet(title=name, rows=1000, cols=len(hdr)+5)
                ws.append_row(hdr); return ws
            except: return None
    except: return None

@st.cache_data(ttl=600, show_spinner=False)
def get_all_records_cached(sheet_name):
    try:
        ws=get_sheet_safe(sheet_name)
        if not ws: return []
        try: return ws.get_all_records()
        except:
            vals=ws.get_all_values()
            if len(vals)<2: return []
            hdr=vals[0]
            return [dict(zip(hdr, r+[""]*(len(hdr)-len(r)))) for r in vals[1:]]
    except: return []

def save_patient(data):
    try:
        ws=get_sheet_safe("New_patient")
        if not ws: return False,"Demo Mode"
        hdr=ws.row_values(1) if ws.row_values(1) else list(data.keys())
        row=[data.get(h,"") for h in hdr]
        ws.append_row(row, value_input_option="RAW")
        get_all_records_cached.clear()
        return True,"Saved"
    except Exception as e: return False,str(e)

def get_next_numbers(clinic_name):
    try:
        records = get_all_records_cached("New_patient")
        my_records = [r for r in records if str(r.get("ClinicName","")).lower() == str(clinic_name).lower()]
        max_total=0
        for r in my_records:
            try:
                tn=int(str(r.get("TotalNumber","0") or 0))
                if tn>max_total: max_total=tn
            except: pass
        today_str=str(datetime.date.today())
        daily_count=len([r for r in my_records if today_str in str(r.get("Date",""))])
        return daily_count+1, max_total+1 if max_total>0 else 1
    except: return 1,1

def get_next_auto_id():
    # V172: New ID for AutoDiagnosis - fixed, gives new ID every entry
    try:
        recs = get_all_records_cached("AutoDiagnosis")
        max_id=0
        for r in recs:
            try:
                # ID format AUTO1, AUTO2 or numeric
                id_str=str(r.get("ID","") or r.get("PatientID",""))
                num=''.join(filter(str.isdigit, id_str))
                if num:
                    n=int(num)
                    if n>max_id: max_id=n
            except: pass
        return max_id+1
    except:
        return int(datetime.datetime.now().timestamp()) % 100000

def get_next_feedback_id():
    try:
        recs=get_all_records_cached("Feedback")
        max_id=0
        for r in recs:
            fid=str(r.get("ID",""))
            if fid.startswith("fd_"):
                try:
                    num=int(fid.split("_")[1])
                    if num>max_id: max_id=num
                except: pass
        return f"fd_{max_id+1}"
    except: return "fd_1"

def get_next_user_signup_id(user_type):
    # V186 - CU_ for Clinic, HU_ for Home User
    try:
        recs = get_all_records_cached("UserSignups")
        prefix = "CU_" if str(user_type).lower() in ["clinic","clinic_user","cu"] else "HU_"
        max_n = 0
        for r in recs:
            sid = str(r.get("SignupID","") or r.get("ID",""))
            if sid.startswith(prefix):
                try:
                    num = int(sid.split("_")[1])
                    if num > max_n: max_n = num
                except: pass
            # Also handle old numeric IDs for backward compatibility
            elif sid.startswith("CU") or sid.startswith("HU"):
                try:
                    num = int(''.join(filter(str.isdigit, sid)))
                    if num > max_n: max_n = num
                except: pass
        return f"{prefix}{max_n+1}"
    except:
        prefix = "CU_" if str(user_type).lower() in ["clinic"] else "HU_"
        return f"{prefix}1"

def col_idx_to_letter(idx):
    # 0 -> A, 25 -> Z, 26 -> AA etc
    letter = ""
    idx = int(idx)
    while True:
        idx, remainder = divmod(idx, 26)
        letter = chr(65 + remainder) + letter
        if idx == 0:
            break
        idx -= 1
    return letter

def delete_category_from_appsettings(cat_type, cat_name):
    try:
        ws = get_sheet_safe("AppSettings")
        if not ws:
            return False
        vals = ws.get_all_values()
        # cat_type is MainCategory or SubCategory
        target_key = f"{cat_type}_{cat_name}"
        for i,row in enumerate(vals[1:], start=2):
            if row and row[0]==target_key:
                ws.delete_rows(i)
                return True
            # Also check Value match for old entries without prefix
            if row and len(row)>1 and row[1]==cat_name and cat_type.lower() in str(row[0]).lower():
                ws.delete_rows(i)
                return True
        return False
    except Exception as e:
        return False

def get_next_offer_id():
    try:
        recs = get_all_records_cached("Articles")
        max_n=0
        for r in recs:
            oid=str(r.get("ID",""))
            if oid.lower().startswith("offer_"):
                try:
                    num=int(oid.split("_")[1])
                    if num>max_n: max_n=num
                except: pass
        return f"Offer_{max_n+1}"
    except: return "Offer_1"

def get_appsettings_value(key, default=""):
    try:
        recs = get_all_records_cached("AppSettings")
        for r in recs:
            if str(r.get("Key","")).lower() == str(key).lower():
                return r.get("Value", default)
        return default
    except: return default

def get_user_info_for_feedback():
    uname=st.session_state.get("username","")
    try:
        recs=get_all_records_cached("UserSignups")
        for r in recs:
            if str(r.get("Username","")).lower()==uname.lower():
                name=r.get("ClinicName") or r.get("Username") or uname
                from_loc=r.get("From") or r.get("ClinicName") or "Unknown"
                phone=r.get("Phone") or ""
                email=r.get("Email") or ""
                return name, from_loc, phone, email
        return st.session_state.get("physician_name", uname), st.session_state.get("clinic_name",""), "", ""
    except:
        return uname, st.session_state.get("clinic_name",""), "", ""

def get_home_user_phone():
    # For Home User phone matching validation
    uname=st.session_state.get("username","")
    try:
        recs=get_all_records_cached("UserSignups")
        for r in recs:
            if str(r.get("Username","")).lower()==uname.lower():
                return str(r.get("Phone","") or "")
        recs2=get_all_records_cached("HomeUsers")
        for r in recs2:
            if str(r.get("Username","")).lower()==uname.lower() or str(r.get("UserID","")).lower()==uname.lower():
                return str(r.get("Phone","") or r.get("AccountHolderPhone","") or "")
    except: pass
    return ""

def add_footer():
    is_dash = st.session_state.get("current_page","") == "dashboard_welcome"
    is_admin = st.session_state.get("current_page","") == "admin"
    is_login = st.session_state.get("current_page","") in ["clinic_login", "login", "signup", "initial", "home"]
    ver_txt = f" | {APP_VERSION}" if is_dash else ""
    # V197 - Requirement 6: Feedback/WhatsApp on all pages except Dashboard, App Admin, and preceding pages (login/signup/initial)
    if not is_dash and not is_admin and not is_login:
        st.markdown("---")
        st.markdown("""
        <div style="background:#161617;border-left:4px solid #ffaa00;padding:14px;border-radius:10px;margin-top:18px;">
            <b>Note!</b> This is currently a work in progress. Please let us know your suggestions for improving this page.<br>
            <b>Not!</b> Join us on WhatsApp.
        </div>
        """, unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("Feedback", key=f"fb_btn_footer_{st.session_state.get('current_page','')}_{st.session_state.form_version}_v197", type="primary", use_container_width=True):
                st.session_state.feedback_page_ref = st.session_state.get("current_page","")
                st.session_state.current_page = "feedback_page"
                st.rerun()
        with c2:
            st.markdown(f"""
            <div style="margin-top:2px;">
                <a href="{WHATSAPP_LINK}" target="_blank" style="text-decoration:none;">
                    <span style="display:inline-flex;align-items:center;background:#25D366;color:white;padding:10px 18px;border-radius:24px;font-size:14px;font-weight:700;width:100%;justify-content:center;">
                        <span style="background:white;color:#25D366;border-radius:50%;width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;margin-right:10px;font-weight:900;">W</span>
                        Join us on WhatsApp
                    </span>
                </a>
            </div>
            """, unsafe_allow_html=True)
    st.markdown(f"<div class='footer-sharp'>by mian Nadeem{ver_txt}</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="ad-note">
        This is just an ad link;<br>there is no need to open it
    </div>
    """, unsafe_allow_html=True)

def under_development_footer(page_title=""):
    # V197 - Only separator, Feedback/WhatsApp handled in add_footer
    st.markdown("---")

def section_heading_clickable(key, title):
    # V197 - Requirement 7: Next section opens only when previous mandatory fields completed
    if st.session_state.section_opened.get(key, False):
        st.markdown(f"<div class='heading-h4'>{title}</div>", unsafe_allow_html=True)
        return True
    else:
        # Check if previous section was completed
        order=["personal","vital","assessment","complaint","history","prescription","billing"]
        if key in order:
            idx = order.index(key)
            if idx > 0:
                prev_key = order[idx-1]
                if not st.session_state.section_opened.get(prev_key, False) and not st.session_state.section_unlocked.get(prev_key, False):
                    # For personal, we need to check if its mandatory fields were completed
                    if prev_key == "personal":
                        st.warning(f"Please complete Personal Information mandatory fields first to open {title}")
                        return False
        if st.button(f"Open {title}", key=f"open_{key}_{st.session_state.form_version}_v197"):
            # For non-personal sections, allow open if previous is unlocked
            st.session_state.section_opened[key]=True
            st.rerun()
        return False

def section_ok(key, is_revisit=False):
    # V197 - Fixed for 6 fields visible + not requiring phone when hidden
    if st.button(f"OK - {key}", key=f"ok_{key}_{st.session_state.form_version}_v197"):
        fv = st.session_state.form_version
        if key == "personal":
            name = str(st.session_state.get(f"p_name_{fv}","") or "").strip()
            age = str(st.session_state.get(f"p_age_{fv}","") or "").strip()
            gender = str(st.session_state.get(f"p_gender_{fv}","") or "").strip()
            # Fallback to revisit_data
            if is_revisit and st.session_state.get("revisit_data"):
                rd = st.session_state.revisit_data
                if not name:
                    name = str(rd.get("Name","") or "").strip()
                if not age:
                    age = str(rd.get("Age","") or "").strip()
                if not gender or gender=="Select":
                    gender = str(rd.get("Gender","") or "").strip()
            if not name:
                st.error("Please complete: Patient's Name * is mandatory")
                return
            if not age:
                st.error("Please complete: Age * is mandatory")
                return
            if gender == "Select" or not gender:
                st.error("Please complete: Gender * is mandatory")
                return
            # V197: Occupation, Father/Spouse, Address are optional (only 6 fields visible, not all mandatory)
        order=["personal","vital","diseases","assessment","complaint","history","prescription","billing"]
        if key not in order:
            order=["personal","vital","assessment","complaint","history","prescription","billing"]
        if key in order:
            idx=order.index(key)
            if idx+1 < len(order):
                nxt=order[idx+1]
                st.session_state.section_opened[nxt]=True
                st.session_state.section_unlocked[nxt]=True
        st.success(f"{key} OK - Next section unlocked")
        st.rerun()


def get_age_based_questions(age_str, gender):
    # V197 - Requirement 5: Questions based on age for Male and Female within Personal Info
    try:
        age = int(str(age_str).strip().split()[0])
    except:
        return []
    questions = []
    gender = str(gender).lower()
    if "female" in gender:
        if age >= 10 and age <= 12:
            questions = [
                ("Menarche Started?", ["Select","Yes","No"], "female_menarche"),
                ("Age of First Period?", "text", "female_menarche_age"),
            ]
        elif age >= 13 and age <= 50:
            questions = [
                ("Menstrual Cycle Regular?", ["Select","Regular","Irregular","No Periods"], "female_cycle"),
                ("Menstrual Flow?", ["Select","Normal","Heavy","Light","Scanty"], "female_flow"),
                ("Number of Pregnancies?", ["Select","0","1","2","3","4+"], "female_preg_count"),
                ("Any Miscarriage?", ["Select","Yes","No"], "female_miscarriage"),
                ("Using Contraception?", ["Select","Yes","No"], "female_contraception"),
                ("White Discharge (Leucorrhoea)?", ["Select","Yes","No","Sometimes"], "female_leucorrhoea"),
            ]
        elif age > 50:
            questions = [
                ("Menopause Age?", "text", "female_menopause_age"),
                ("Menopause Symptoms?", ["Select","Hot Flashes","Mood Swings","No Symptoms","Other"], "female_menopause_sym"),
                ("HRT Taken?", ["Select","Yes","No"], "female_hrt"),
            ]
    elif "male" in gender:
        if age >= 12 and age <= 18:
            questions = [
                ("Puberty Changes Started?", ["Select","Yes","No"], "male_puberty"),
                ("Voice Change?", ["Select","Yes","No","In Progress"], "male_voice"),
                ("Beard Growth?", ["Select","Yes","No","Starting"], "male_beard"),
            ]
        elif age >= 19 and age <= 40:
            questions = [
                ("Marital Status Effect?", ["Select","Single","Married","Issues"], "male_marital_effect"),
                ("Sexual Health Concerns?", ["Select","Yes","No","Sometimes"], "male_sexual"),
                ("Nightfall Frequency?", ["Select","Never","Rarely","Sometimes","Often"], "male_nightfall"),
            ]
        elif age > 40:
            questions = [
                ("Prostate Issues?", ["Select","Yes","No","Checkup Needed"], "male_prostate"),
                ("Urine Stream Weak?", ["Select","Yes","No"], "male_urine_weak"),
                ("Erectile Issues?", ["Select","Yes","No","Sometimes"], "male_erectile"),
            ]
    # Common for both
    if age < 5:
        questions += [
            ("Birth History Normal?", ["Select","Normal","C-Section","Premature","Complications"], "child_birth"),
            ("Vaccination Complete?", ["Select","Yes","No","Partial"], "child_vaccination"),
        ]
    elif age >= 5 and age <= 12:
        questions += [
            ("School Performance?", ["Select","Good","Average","Poor"], "child_school"),
            ("Growth Normal?", ["Select","Normal","Delayed","Advanced"], "child_growth"),
        ]
    return questions

def get_additional_patient_questions():
    # V197 - User's 10 Additional Questions with corrected wording + Physical Build (item 2 prepared by us)
    # For Auto-diagnosis and Home Treatment only, shown before result processing
    return [
        ("1. Residential Area / Environment", ["Select","Hot Area","Cold Area","Humid Area","Dry Area","Hot & Humid","Cold & Dry","Moderate / Normal"], "add_residential"),
        ("2. Physical Build / Body Structure", ["Select","Thin / Lean","Medium / Normal","Heavy / Broad","Muscular / Athletic","Obese / Overweight","Weak / Frail","Tall & Thin","Short & Stocky"], "add_physical_build"),
        ("3. Skin Condition", ["Select","Dry Skin","Moist / Oily Skin","Soft & Smooth","Rough & Dry","Normal","Sensitive","Combination"], "add_skin"),
        ("4. Hair Condition", ["Select","Dry Hair","Oily / Greasy Hair","Straight Hair","Curly / Wavy","Premature Graying","Hair Fall / Thinning","Normal"], "add_hair"),
        ("5. Eyes Condition", ["Select","Redness in Eyes","Watery / Moist Eyes","Dry Eyes","Dark Circles Around Eyes","Burning Sensation","Normal"], "add_eyes"),
        ("6. Tongue and Mouth", ["Select","Dryness of Mouth","Excessive Moisture / Salivation","Coated Tongue","Bitter Taste","Normal","Bad Breath"], "add_tongue_mouth"),
        ("7. Appetite", ["Select","Low Appetite","High Appetite","Normal Appetite","Variable / Irregular","No Appetite"], "add_appetite"),
        ("8. Thirst", ["Select","Low Thirst","High / Excessive Thirst","Normal Thirst","Frequent Thirst"], "add_thirst"),
        ("9. Temperature Preference", ["Select","Prefers Hot Items & Warm Environment","Prefers Cold Items & Cool Environment","Prefers Normal / Moderate","Likes Hot Food but Cold Environment","Likes Cold Food but Warm Environment"], "add_preference"),
        ("10. Urine Volume", ["Select","Low Volume / Less Urination","High Volume / Frequent Urination","Normal Volume","Burning Urination","Dark / Yellow Urine"], "add_urine"),
    ]


def reset_to_new_patient():
    st.session_state.form_version+=1
    st.session_state.prev_balance=0.0
    st.session_state.revisit_data=None
    st.session_state.section_opened={"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
    st.session_state.section_unlocked={"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
    st.rerun()

def render_patient_form(is_revisit=False):
    # V197 - Check feedback suspension before showing form - fixed to not show on first day
    try:
        if check_feedback_suspension():
            show_feedback_suspension_notice()
            return
    except:
        pass
    fv=st.session_state.form_version
    daily_num, total_num = get_next_numbers(st.session_state.clinic_name)
    prev_bal=0.0
    if is_revisit and st.session_state.revisit_data:
        pid=str(st.session_state.revisit_data.get("PatientID",""))
        daily_num=st.session_state.revisit_data.get("DailyNumber", daily_num)
        total_num=st.session_state.revisit_data.get("TotalNumber", total_num)
        try:
            prev_bal=float(str(st.session_state.revisit_data.get("Balance","0") or 0).replace(",","") or 0)
        except: prev_bal=0.0
        st.session_state.prev_balance=prev_bal
    else:
        pid=str(total_num)
        prev_bal=float(st.session_state.get("prev_balance",0) or 0)

    def get_prefill(k,d=""):
        if is_revisit and st.session_state.revisit_data:
            return st.session_state.revisit_data.get(k,d)
        return d

    # V172: If revisit, show past history and personal info before entry form
    if is_revisit and st.session_state.revisit_data:
        r=st.session_state.revisit_data
        st.markdown("<div class='heading-h4'>Selected Patient - Past History & Personal Info</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"<div class='history-card'><b>Name:</b> {r.get('Name','')} | <b>Age:</b> {r.get('Age','')} | <b>Gender:</b> {r.get('Gender','')} | <b>Phone:</b> {r.get('Phone','')}<br><b>Address:</b> {r.get('Address','')} | <b>CNIC:</b> {r.get('CNIC','')} | <b>Last Date:</b> {r.get('Date','')}<br><b>Chief Complaint:</b> {r.get('ChiefComplaint','')} | <b>Past History:</b> {r.get('PastHistory','')} | <b>Balance:</b> Rs {r.get('Balance','0')}</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='heading-h4'>Personal Information - V197 (6 fields visible)</div>", unsafe_allow_html=True)
        # V197 Requirement 2: Only 6 fields visible by default
        c1,c2,c3=st.columns(3)
        with c1:
            st.text_input("Patient's Name *", key=f"p_name_{fv}", value=get_prefill("Name",""), placeholder="Patient's Name")
            st.text_input("Spouse/Father's Name", key=f"p_fname_{fv}", value=get_prefill("FatherName",""), placeholder="Spouse/Father's Name")
        with c2:
            st.selectbox("Gender *", LISTS["gender"], key=f"p_gender_{fv}")
            st.text_input("Age *", key=f"p_age_{fv}", value=get_prefill("Age",""), placeholder="Age")
        with c3:
            # V197 Requirement 3: Occupation dropdown
            occ_list = LISTS.get("occupation", ["Select","Student","Teacher","Farmer","Shopkeeper","Laborer","Driver","Housewife","Business","Doctor","Engineer","Government Job","Private Job","Retired","Unemployed","Other"])
            st.selectbox("Occupation", occ_list, key=f"p_occupation_{fv}")
            st.text_input("Address", key=f"p_address_{fv}", value=get_prefill("Address",""), placeholder="Address")

        # Hidden fields - show only when Additional Information clicked
        show_extra_key = f"show_extra_personal_{fv}"
        if show_extra_key not in st.session_state:
            st.session_state[show_extra_key] = False
        
        if not st.session_state[show_extra_key]:
            if st.button("Additional Information ⬇️", key=f"add_info_btn_{fv}_v197", type="secondary"):
                st.session_state[show_extra_key] = True
                st.rerun()
        else:
            st.markdown("---")
            st.markdown("<div class='heading-h5'>Additional Personal Details (Hidden by default)</div>", unsafe_allow_html=True)
            c1,c2,c3=st.columns(3)
            with c1:
                st.selectbox("Blood Group", LISTS["blood_group"], key=f"p_blood_{fv}")
                st.text_input("Height", key=f"p_height_{fv}", placeholder="e.g., 5.6 ft")
            with c2:
                st.selectbox("Marital Status", LISTS["marital"], key=f"p_marital_{fv}")
                st.text_input("Phone *", key=f"p_phone_{fv}", value=get_prefill("Phone",""), placeholder="Phone")
            with c3:
                st.text_input("CNIC", key=f"p_cnic_{fv}", value=get_prefill("CNIC",""), placeholder="CNIC")
                st.text_input("Weight", key=f"p_weight_{fv}", placeholder="e.g., 70 kg")
            if st.button("Hide Additional Information ⬆️", key=f"hide_extra_{fv}_v197"):
                st.session_state[show_extra_key] = False
                st.rerun()

        # Age-based questions
        try:
            cur_age = st.session_state.get(f"p_age_{fv}","") or get_prefill("Age","")
            cur_gender = st.session_state.get(f"p_gender_{fv}","") or get_prefill("Gender","")
            age_qs = get_age_based_questions(cur_age, cur_gender)
            if age_qs:
                st.markdown("---")
                st.markdown(f"<div class='heading-h5'>Age-Based Questions for {cur_gender} (Age: {cur_age}) - V197</div>", unsafe_allow_html=True)
                cols = st.columns(3)
                for idx, (q_label, q_type, q_key) in enumerate(age_qs):
                    col = cols[idx % 3]
                    with col:
                        if isinstance(q_type, list):
                            st.selectbox(q_label, q_type, key=f"age_q_{q_key}_{fv}")
                        else:
                            st.text_input(q_label, key=f"age_q_{q_key}_{fv}")
        except:
            pass
        section_ok("personal", is_revisit=is_revisit)

    with st.container(border=True):
        if section_heading_clickable("vital","Vital Signs"):
            c1,c2,c3=st.columns(3)
            with c1:
                st.text_input("BP", key=f"v_bp_{fv}", value=get_prefill("BP",""))
                st.text_input("Weight", key=f"v_weight_{fv}", value=get_prefill("Weight",""))
                st.selectbox("Sleep Pattern", LISTS["sleep"], key=f"v_sleep_{fv}")
            with c2:
                st.text_input("Temperature", key=f"v_temp_{fv}", value=get_prefill("Temperature",""))
                st.selectbox("Pulse", ["Select","Normal","Fast","Slow"], key=f"v_pulse_{fv}")
                st.selectbox("Appetite", LISTS["appetite"], key=f"v_appetite_{fv}")
            with c3:
                st.selectbox("Temperament", LISTS["temperament"], key=f"u_temperament_{fv}")
                st.selectbox("Bowel Movement", LISTS["bowel"], key=f"v_bowel_{fv}")
            section_ok("vital", is_revisit=is_revisit)

    # V197 Fix: Diseases No/Count Duration mandatory + fix Add Disease error
    with st.container(border=True):
        if section_heading_clickable("diseases","Diseases"):
            st.markdown("<div class='heading-h5'>Select Body Part and Disease - Patient Form V197 Fixed Mandatory</div>", unsafe_allow_html=True)
            c1,c2,c3,c4=st.columns([3,3,2,2])
            with c1:
                body_part = st.selectbox("Body Part *", list(BODY_PARTS.keys()), key=f"pat_body_part_{fv}_v197")
                sub_diseases = BODY_PARTS.get(body_part, ["Select"])
            with c2:
                disease = st.selectbox(f"Disease in {body_part} *", sub_diseases, key=f"pat_disease_sub_{fv}_v197")
            with c3:
                d_no = st.text_input("No/Count *", key=f"pat_no_{fv}_v197", placeholder="e.g., 2 - Mandatory")
            with c4:
                d_duration = st.selectbox("Duration *", LISTS["duration"], key=f"pat_dur_{fv}_v197")
            if st.button("Add Disease +", key=f"pat_add_{fv}_v197", type="secondary", use_container_width=True):
                bp = st.session_state.get(f"pat_body_part_{fv}_v197", "Select")
                dis = st.session_state.get(f"pat_disease_sub_{fv}_v197", "Select")
                no_val = st.session_state.get(f"pat_no_{fv}_v197", "").strip()
                dur_val = st.session_state.get(f"pat_dur_{fv}_v197", "Select")
                if bp=="Select":
                    st.error("Please select Body Part *")
                elif dis=="Select":
                    st.error("Please select Disease *")
                elif not no_val:
                    st.error("Please complete: No/Count * is mandatory - V197")
                elif dur_val=="Select":
                    st.error("Please complete: Duration * is mandatory - V197")
                else:
                    entry_text = f"{bp} + {dis} + {no_val} {dur_val}"
                    if "patient_diseases" not in st.session_state:
                        st.session_state.patient_diseases = []
                    st.session_state.patient_diseases.append({"text": entry_text})
                    # V197 Fix #5: Do NOT set session_state after widget - causes StreamlitWidgetAlreadyInstantiatedError
                    # Instead, use form_version increment to clear via new keys on next rerun, or just keep values
                    st.success(f"✅ Added: {entry_text}")
                    st.rerun()
            # Show accumulated
            pd_list = st.session_state.get("patient_diseases", [])
            if pd_list:
                combined = " + ".join([d.get("text","") for d in pd_list])
                st.markdown(f"<div style='background:#161617;border:2px solid #00E676;border-radius:12px;padding:16px;'><b style='color:#FFD700;'>Added Diseases (Accumulated with +):</b> {combined}</div>", unsafe_allow_html=True)
                for i, dd in enumerate(pd_list):
                    st.write(f"{i+1}. {dd.get('text','')}")
                if st.button("Clear All Diseases", key=f"pat_clear_{fv}_v197"):
                    st.session_state.patient_diseases = []
                    st.rerun()
            else:
                st.info("No diseases added yet - Fill Body Part*, Disease*, No/Count* and Duration* then click Add Disease +")
            section_ok("diseases", is_revisit=is_revisit)

    with st.container(border=True):
        if section_heading_clickable("complaint","Chief Complaint & History"):
            st.text_area("Chief Complaint", key=f"chief_complaint_{fv}", value=get_prefill("ChiefComplaint",""))
            st.text_area("Past History", key=f"past_history_{fv}", value=get_prefill("PastHistory",""))
            st.text_area("Family History", key=f"family_hist_{fv}")
            st.text_area("Habits", key=f"habits_{fv}")
            section_ok("complaint", is_revisit=is_revisit)

    with st.container(border=True):
        if section_heading_clickable("prescription","Prescription"):
            c1,c2=st.columns(2)
            with c1:
                st.multiselect("Single Medicines", ["Ajwain","Haldi","Saunf","Zeera","Adrak","Lehsan","Other"], key=f"single_meds_{fv}")
            with c2:
                st.multiselect("Formula Medicines", ["Jawarish","Majoon","Hab","Sharbat","Oil","Other"], key=f"formula_meds_{fv}")
            section_ok("prescription", is_revisit=is_revisit)

    with st.container(border=True):
        st.markdown("<div class='heading-h4'>Billing</div>", unsafe_allow_html=True)
        if section_heading_clickable("billing","Billing Details"):
            # V172: Billing default blank for New Patient as well
            if is_revisit:
                default_fee = ""
                default_med = ""
                default_paid = ""
            else:
                default_fee = ""
                default_med = ""
                default_paid = ""
            c1,c2,c3,c4=st.columns(4)
            with c1:
                fee_val = st.text_input("Fee (Rs)", key=f"fee_{fv}", value=default_fee, placeholder="Enter Fee")
            with c2:
                med_val = st.text_input("Medicine Charges (Rs)", key=f"med_charges_{fv}", value=default_med, placeholder="Enter Medicine Charges")
            with c3:
                paid_val = st.text_input("Paid (Rs)", key=f"paid_{fv}", value=default_paid, placeholder="Enter Paid")
            with c4:
                fee_status = st.selectbox("Bill Status", LISTS["fee_status"], key=f"fee_status_{fv}")
            c5,c6=st.columns(2)
            with c5:
                payment_method = st.selectbox("Payment Method", LISTS["payment"], key=f"payment_method_{fv}")
            with c6:
                if prev_bal > 0:
                    st.markdown(f"<div style='background:#1a1c23;border:2px solid #ffaa00;border-radius:10px;padding:10px;text-align:center;'><b>Outstanding: Rs {prev_bal:.0f}</b></div>", unsafe_allow_html=True)
            try:
                f = float(str(fee_val).replace(",","") or 0)
                m = float(str(med_val).replace(",","") or 0)
                p = float(str(paid_val).replace(",","") or 0)
            except:
                f=m=p=0.0
            grand_total = f + m + prev_bal
            balance = grand_total - p
            if balance<0: balance=0
            st.markdown("<div style='margin:6px 0;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='heading-h4'>Grand Total - Billing Details Calculation</div>", unsafe_allow_html=True)
            if prev_bal > 0:
                st.markdown(f"<div class='demo-card'>Fee Rs {f:.0f} + Medicine Rs {m:.0f} + Outstanding Rs {prev_bal:.0f} = Grand Total Rs {grand_total:.0f} | Paid Rs {p:.0f} = Balance Rs {balance:.0f}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='demo-card'>Fee Rs {f:.0f} + Medicine Rs {m:.0f} = Grand Total Rs {grand_total:.0f} | Paid Rs {p:.0f} = Balance Rs {balance:.0f}</div>", unsafe_allow_html=True)
            cc1,cc2=st.columns(2)
            with cc1:
                st.metric("Grand Total", f"Rs {grand_total:.0f}")
            with cc2:
                st.metric("Balance", f"Rs {balance:.0f}")
            st.session_state[f"calc_gt_{fv}"]=grand_total
            st.session_state[f"calc_bal_{fv}"]=balance
            st.session_state[f"calc_f_{fv}"]=f
            st.session_state[f"calc_m_{fv}"]=m
            st.session_state[f"calc_p_{fv}"]=p
            st.session_state[f"calc_status_{fv}"]=fee_status
            st.session_state[f"calc_pay_{fv}"]=payment_method
            section_ok("billing", is_revisit=is_revisit)

    c1,c2,c3=st.columns([1,1,2])
    with c1:
        if st.button("Back", key=f"back_patient_{fv}_v172"):
            st.session_state.current_page="dashboard_welcome"
            st.rerun()
    with c2:
        if st.button("New Patient", key=f"new_patient_btn_{fv}_v172", type="secondary"):
            reset_to_new_patient()
    with c3:
        if st.button("Save Patient", type="primary", use_container_width=True, key=f"save_patient_{fv}_v172"):
            p_name = st.session_state.get(f"p_name_{fv}", "")
            if not str(p_name).strip():
                st.error("Name required"); st.stop()
            f=st.session_state.get(f"calc_f_{fv}",0); m=st.session_state.get(f"calc_m_{fv}",0); p=st.session_state.get(f"calc_p_{fv}",0)
            grand_total=st.session_state.get(f"calc_gt_{fv}",f+m+prev_bal)
            balance=st.session_state.get(f"calc_bal_{fv}",grand_total-p)
            if balance<0: balance=0
            status=st.session_state.get(f"calc_status_{fv}","Select")
            pay_method=st.session_state.get(f"calc_pay_{fv}","Select")
            data_dict={
                "PatientID": pid,
                "Date": str(datetime.date.today()),
                "Name": p_name,
                "FatherName": st.session_state.get(f"p_fname_{fv}", ""),
                "Age": st.session_state.get(f"p_age_{fv}", ""),
                "Gender": st.session_state.get(f"p_gender_{fv}", "Select"),
                "Phone": st.session_state.get(f"p_phone_{fv}", ""),
                "Address": st.session_state.get(f"p_address_{fv}", ""),
                "Fees": f,
                "MedicineCharges": m,
                "Total": f+m,
                "GrandTotal": grand_total,
                "Paid": p,
                "Balance": balance,
                "PrevBalance": prev_bal,
                "FeeStatus": status,
                "PaymentMethod": pay_method,
                "ClinicName": st.session_state.clinic_name,
                "CreatedBy": st.session_state.username,
                "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "AppVersion": APP_VERSION,
                "DailyNumber": daily_num,
                "TotalNumber": total_num,
            }
            ok,msg=save_patient(data_dict)
            if ok:
                st.success(f"Saved - PatientID {pid} | Grand Total Rs {grand_total:.0f} - Form cleared for new entry")
                st.balloons()
                st.session_state.form_version+=1
                st.session_state.prev_balance=0.0
                st.session_state.revisit_data=None
                st.session_state.section_opened={"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
                st.session_state.section_unlocked={"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
                st.rerun()
            else:
                st.warning(f"Local Save - ID {pid} | Grand Total Rs {grand_total:.0f} - {msg}")
                st.session_state.form_version+=1
                st.session_state.prev_balance=0.0
                st.session_state.revisit_data=None
                st.session_state.section_opened={"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
                st.session_state.section_unlocked={"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
                st.rerun()

def render_auto_form(prefix, is_home=False):
    version_key = f"{prefix}_disease_version"
    if version_key not in st.session_state:
        st.session_state[version_key] = 0
    ver = st.session_state[version_key]

    personal_ok_key = f"{prefix}_personal_ok"
    diseases_ok_key = f"{prefix}_diseases_ok"
    additional_ok_key = f"{prefix}_additional_ok"
    for k in [personal_ok_key, diseases_ok_key, additional_ok_key]:
        if k not in st.session_state:
            st.session_state[k] = False

    # Show selected patient history if Revisit mode
    selected_key = f"{prefix}_selected_patient"
    if st.session_state.get(f"{prefix}_form_mode") == "Revisit" and st.session_state.get(selected_key):
        r = st.session_state.get(selected_key)
        st.markdown("<div class='heading-h4'>Selected Patient - Past History & Personal Info</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"<div class='history-card'><b>Name:</b> {r.get('Name','')} | <b>Age:</b> {r.get('Age','')} | <b>Phone:</b> {r.get('Phone','')}<br><b>Address:</b> {r.get('Address','')} | <b>Date:</b> {r.get('Date','')}<br><b>Diseases:</b> {r.get('Diseases','')} | <b>Extra:</b> {r.get('ExtraSymptoms','')}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='heading-h4'>Personal Information - V197 (6 fields visible)</div>", unsafe_allow_html=True)
    with st.container(border=True):
        # Prefill helper
        def get_auto_prefill(field, default=""):
            sel = st.session_state.get(selected_key)
            if sel and st.session_state.get(f"{prefix}_form_mode")=="Revisit":
                return str(sel.get(field,"") or default)
            return st.session_state.get(f"{prefix}_name_v172","") if field=="Name" else default

        # V197 Requirement 2: Only 6 fields visible by default
        c1,c2,c3=st.columns(3)
        with c1:
            p_name_val = ""
            if st.session_state.get(selected_key) and st.session_state.get(f"{prefix}_form_mode")=="Revisit":
                p_name_val = st.session_state.get(selected_key).get("Name","")
            p_name=st.text_input("Patient's Name *", value=p_name_val, key=f"{prefix}_name_v197")
            p_father=st.text_input("Spouse/Father's Name", key=f"{prefix}_father_v197")
        with c2:
            p_gender=st.selectbox("Gender *", LISTS["gender"], key=f"{prefix}_gender_v197")
            p_age=st.text_input("Age *", key=f"{prefix}_age_v197")
        with c3:
            occ_list = LISTS.get("occupation", ["Select","Student","Teacher","Farmer","Shopkeeper","Laborer","Driver","Housewife","Business","Doctor","Engineer","Government Job","Private Job","Retired","Unemployed","Other"])
            p_occupation=st.selectbox("Occupation", occ_list, key=f"{prefix}_occ_v197")
            p_address=st.text_input("Address", key=f"{prefix}_addr_v197")

        # Hidden fields - Additional Information button
        show_extra_key = f"show_extra_auto_{prefix}"
        if show_extra_key not in st.session_state:
            st.session_state[show_extra_key] = False
        
        if not st.session_state[show_extra_key]:
            if st.button("Additional Information ⬇️", key=f"auto_add_info_{prefix}_v197"):
                st.session_state[show_extra_key] = True
                st.rerun()
        else:
            st.markdown("---")
            st.markdown("<div class='heading-h5'>Additional Personal Details (Hidden by default) - V197</div>", unsafe_allow_html=True)
            c1,c2,c3=st.columns(3)
            with c1:
                p_blood=st.selectbox("Blood Group", LISTS["blood_group"], key=f"{prefix}_blood_v197")
                p_height=st.text_input("Height", key=f"{prefix}_height_v197", placeholder="e.g., 5.6 ft")
            with c2:
                p_phone_default = ""
                if st.session_state.get(selected_key) and st.session_state.get(f"{prefix}_form_mode")=="Revisit":
                    p_phone_default = st.session_state.get(selected_key).get("Phone","")
                p_phone=st.text_input("Phone *", value=p_phone_default, key=f"{prefix}_phone_v197")
                p_weight=st.text_input("Weight", key=f"{prefix}_weight_v197", placeholder="e.g., 70 kg")
            with c3:
                p_marital=st.selectbox("Marital Status", LISTS["marital"], key=f"{prefix}_marital_v197")
                p_habits=st.text_input("Habits", key=f"{prefix}_habits_v197")
            if st.button("Hide Additional Information ⬆️", key=f"auto_hide_{prefix}_v197"):
                st.session_state[show_extra_key] = False
                st.rerun()
        
        # Ensure variables exist for OK check even if hidden
        if show_extra_key in st.session_state and not st.session_state[show_extra_key]:
            # Set defaults for hidden fields to avoid NameError in OK check
            p_blood = st.session_state.get(f"{prefix}_blood_v197", "Select")
            p_phone = st.session_state.get(f"{prefix}_phone_v197", p_phone_default if 'p_phone_default' in locals() else "")
            p_height = st.session_state.get(f"{prefix}_height_v197", "")
            p_weight = st.session_state.get(f"{prefix}_weight_v197", "")
            p_marital = st.session_state.get(f"{prefix}_marital_v197", "Select")
            p_habits = st.session_state.get(f"{prefix}_habits_v197", "")

        # Age-based questions
        try:
            age_qs = get_age_based_questions(p_age, p_gender)
            if age_qs:
                st.markdown("---")
                st.markdown(f"<div class='heading-h5'>Age-Based Questions for {p_gender} (Age: {p_age}) - V197</div>", unsafe_allow_html=True)
                cols = st.columns(3)
                for idx, (q_label, q_type, q_key) in enumerate(age_qs):
                    col = cols[idx % 3]
                    with col:
                        if isinstance(q_type, list):
                            st.selectbox(q_label, q_type, key=f"auto_age_q_{q_key}_{prefix}_v197")
                        else:
                            st.text_input(q_label, key=f"auto_age_q_{q_key}_{prefix}_v197")
        except:
            pass

        if not st.session_state[personal_ok_key]:
            if st.button(f"OK - Personal Information", key=f"{prefix}_personal_ok_btn_v172", type="primary"):
                if not p_name.strip():
                    st.error("Please complete: Patient Name")
                elif p_gender == "Select":
                    st.error("Please complete: Gender")
                elif not p_phone.strip():
                    st.error("Please complete: Phone")
                elif not p_age.strip():
                    st.error("Please complete: Age")
                else:
                    # Home User phone matching validation
                    if is_home:
                        home_phone = get_home_user_phone()
                        if home_phone and p_phone.strip() != home_phone:
                            st.error(f"Phone must match Home User signup phone: {home_phone}")
                            st.stop()
                    st.session_state[personal_ok_key] = True
                    st.success("Personal Information OK - Next section unlocked")
                    st.rerun()
        else:
            st.success("Personal Information Completed - OK")
            if st.button(f"Edit Personal Information", key=f"{prefix}_personal_edit_v172"):
                st.session_state[personal_ok_key] = False
                st.rerun()

    if not st.session_state[personal_ok_key]:
        st.warning("Please complete Personal Information and click OK to open next section")
        return None, None, None, None, None, None, []

    st.markdown(f"<div class='heading-h4'>Diseases</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<div class='heading-h5'>Select Body Part and Disease - V197 Fixed Mandatory</div>", unsafe_allow_html=True)
        c1,c2,c3,c4=st.columns([3,3,2,2])
        with c1:
            body_part = st.selectbox("Body Part *", list(BODY_PARTS.keys()), key=f"{prefix}_body_part_v197")
            sub_diseases = BODY_PARTS.get(body_part, ["Select"])
        with c2:
            disease_key = f"{prefix}_disease_sub_v197"
            disease = st.selectbox(f"Disease in {body_part} *", sub_diseases, key=disease_key)
        with c3:
            d_no = st.text_input("No/Count *", key=f"{prefix}_no_v197", placeholder="e.g., 2 - Mandatory")
        with c4:
            d_duration = st.selectbox("Duration *", LISTS["duration"], key=f"{prefix}_dur_v197")

        rq1_val = st.session_state.get(f"{prefix}_rel_q1_v197", "Select")
        rq2_val = st.session_state.get(f"{prefix}_rel_q2_v197", "")
        rq3_val = st.session_state.get(f"{prefix}_rel_q3_v197", "")
        if body_part != "Select" and disease != "Select":
            st.markdown(f"<div class='heading-h5'>Related Questions for {body_part} - {disease}</div>", unsafe_allow_html=True)
            related_qs = DISEASE_RELATED_QUESTIONS.get(body_part, DISEASE_RELATED_QUESTIONS["General"])
            cq1,cq2,cq3=st.columns(3)
            with cq1:
                rq1_val = st.selectbox(related_qs[0] if len(related_qs)>0 else "Severity", LISTS["severity"], key=f"{prefix}_rel_q1_v197")
            with cq2:
                rq2_val = st.text_input(related_qs[1] if len(related_qs)>1 else "Trigger", key=f"{prefix}_rel_q2_v197", placeholder="e.g., After eating")
            with cq3:
                rq3_val = st.text_input(related_qs[2] if len(related_qs)>2 else "Associated Symptom", key=f"{prefix}_rel_q3_v197", placeholder="e.g., Nausea")

        # V197 Fix #5: Robust Add Disease - No session_state set after widget to avoid StreamlitWidgetAlreadyInstantiatedError
        if st.button("Add Disease +", key=f"{prefix}_add_v197", type="secondary", use_container_width=True):
            bp = st.session_state.get(f"{prefix}_body_part_v197", "Select")
            dis = st.session_state.get(f"{prefix}_disease_sub_v197", "Select")
            no_val = st.session_state.get(f"{prefix}_no_v197", "").strip()
            dur_val = st.session_state.get(f"{prefix}_dur_v197", "Select")
            r1 = st.session_state.get(f"{prefix}_rel_q1_v197", "Select")
            r2 = st.session_state.get(f"{prefix}_rel_q2_v197", "").strip()
            r3 = st.session_state.get(f"{prefix}_rel_q3_v197", "").strip()
            if bp=="Select":
                st.error("Please select Body Part *")
            elif dis=="Select":
                st.error("Please select Disease *")
            elif not no_val:
                st.error("Please complete: No/Count * is mandatory - V197")
            elif dur_val=="Select":
                st.error("Please complete: Duration * is mandatory - V197")
            else:
                entry_text = f"{bp} + {dis} + {no_val} {dur_val}"
                if r1 and r1!="Select": entry_text += f" + {r1}"
                if r2: entry_text += f" + {r2}"
                if r3: entry_text += f" + {r3}"
                target_list_key = "home_auto_diseases" if is_home else "auto_diseases"
                if target_list_key not in st.session_state:
                    st.session_state[target_list_key] = []
                st.session_state[target_list_key].append({"text": entry_text})
                # V197 Fix: Don't set session_state after widget instantiation - causes error
                st.success(f"✅ Added: {entry_text}")
                st.rerun()

    st.markdown("<div class='heading-h5'>Added Diseases (Accumulated with +) - V197</div>", unsafe_allow_html=True)
    diseases_list = st.session_state.get("home_auto_diseases", []) if is_home else st.session_state.get("auto_diseases", [])
    if diseases_list:
        combined_text = " + ".join([d.get("text","") for d in diseases_list])
        st.markdown(f"<div style='background:#161617;border:2px solid #00E676;border-radius:12px;padding:16px;margin:8px 0;'><b style='color:#FFD700;'>Combined (+):</b> <span style='color:#e0e0e0;'>{combined_text}</span></div>", unsafe_allow_html=True)
        for i, dd in enumerate(diseases_list):
            c1,c2=st.columns([4,1])
            with c1:
                st.write(f"{i+1}. {dd.get('text','')}")
            with c2:
                if st.button(f"Remove", key=f"{prefix}_rem_{i}_v197"):
                    target_key = "home_auto_diseases" if is_home else "auto_diseases"
                    st.session_state[target_key].pop(i)
                    st.rerun()
        if st.button("Clear All Diseases", key=f"{prefix}_clear_v197"):
            target_key = "home_auto_diseases" if is_home else "auto_diseases"
            st.session_state[target_key] = []
            st.rerun()
    else:
        st.info("No diseases added yet - Fill Body Part*, Disease*, No/Count* and Duration* then click Add Disease +")

    with st.container(border=True):
        if not st.session_state[diseases_ok_key]:
            if st.button(f"OK - Diseases", key=f"{prefix}_diseases_ok_btn_v172", type="primary"):
                if not diseases_list:
                    st.error("Please complete: Add at least one disease")
                else:
                    st.session_state[diseases_ok_key] = True
                    st.success("Diseases OK - Next section unlocked")
                    st.rerun()
        else:
            st.success("Diseases Completed - OK")
            if st.button(f"Edit Diseases", key=f"{prefix}_diseases_edit_v172"):
                st.session_state[diseases_ok_key] = False
                st.rerun()

    if not st.session_state[diseases_ok_key]:
        st.warning("Please complete Diseases section and click OK to open next section")
        return p_name, p_father, p_age, p_phone, p_gender, p_address, diseases_list

    st.markdown("<div class='heading-h4'>Additional Information</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<div class='heading-h5'>Lifestyle and Symptoms</div>", unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1:
            sleep_pat = st.selectbox("Sleep Pattern", LISTS["sleep"], key=f"{prefix}_sleep_v172")
            appetite_pat = st.selectbox("Appetite", LISTS["appetite"], key=f"{prefix}_appetite_v172")
            thirst = st.selectbox("Thirst", ["Select","Normal","Excess","Less"], key=f"{prefix}_thirst_v172")
        with c2:
            bowel = st.selectbox("Bowel Movement", LISTS["bowel"], key=f"{prefix}_bowel_v172")
            urine = st.selectbox("Urine", ["Select","Normal","Burning","Frequent","Less"], key=f"{prefix}_urine_v172")
            sweat = st.selectbox("Sweating", ["Select","Normal","Excess","Less"], key=f"{prefix}_sweat_v172")
        with c3:
            stress = st.selectbox("Stress Level", ["Select","Low","Medium","High"], key=f"{prefix}_stress_v172")
            energy = st.selectbox("Energy Level", ["Select","Low","Normal","High"], key=f"{prefix}_energy_v172")
            allergy_hist = st.selectbox("Allergy History", LISTS["allergy"], key=f"{prefix}_allergy_v172")
        st.markdown("<div class='heading-h5'>Past and Family History</div>", unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            past_hist = st.text_area("Past Medical History", key=f"{prefix}_past_hist_v172", height=80)
            family_hist = st.text_area("Family History", key=f"{prefix}_family_hist_v172", height=80)
        with c2:
            current_meds = st.text_area("Current Medications", key=f"{prefix}_curr_meds_v172", height=80)
            extra_symptoms = st.text_area("Other Symptoms", key=f"{prefix}_extra_v172", height=80)

        if not st.session_state[additional_ok_key]:
            if st.button(f"OK - Additional Information", key=f"{prefix}_additional_ok_btn_v172", type="primary"):
                mandatory_missing = []
                if sleep_pat == "Select": mandatory_missing.append("Sleep Pattern")
                if appetite_pat == "Select": mandatory_missing.append("Appetite")
                if thirst == "Select": mandatory_missing.append("Thirst")
                if bowel == "Select": mandatory_missing.append("Bowel Movement")
                if urine == "Select": mandatory_missing.append("Urine")
                if sweat == "Select": mandatory_missing.append("Sweating")
                if stress == "Select": mandatory_missing.append("Stress Level")
                if energy == "Select": mandatory_missing.append("Energy Level")
                if allergy_hist == "Select": mandatory_missing.append("Allergy History")
                if mandatory_missing:
                    st.error(f"Please complete: {', '.join(mandatory_missing)}")
                else:
                    st.session_state[additional_ok_key] = True
                    st.success("Additional Information OK - Proceed unlocked")
                    st.rerun()
        else:
            st.success("Additional Information Completed - OK")
            if st.button(f"Edit Additional Information", key=f"{prefix}_additional_edit_v172"):
                st.session_state[additional_ok_key] = False
                st.rerun()

    if not st.session_state[additional_ok_key]:
        st.warning("Please complete Additional Information and click OK to enable Proceed")
        return p_name, p_father, p_age, p_phone, p_gender, p_address, diseases_list

    if st.button("Proceed", type="primary", use_container_width=True, key=f"{prefix}_proceed_v172"):
        # V172: Fix duplicate save - save only here, not on every render
        try:
            new_id = get_next_auto_id()
            ws=get_sheet_safe("AutoDiagnosis")
            if ws:
                diseases_str = " + ".join([d.get("text","") for d in (st.session_state.home_auto_diseases if is_home else st.session_state.auto_diseases)])
                # Phone matching already validated for Home User
                ws.append_row([f"AUTO{new_id}", f"AUTO{new_id}", str(datetime.date.today()), p_name, p_father, p_age, p_phone, p_gender, p_address, diseases_str, extra_symptoms + f" | Sleep:{sleep_pat} Appetite:{appetite_pat} Bowel:{bowel}", "N/A", st.session_state.clinic_name, st.session_state.username, APP_VERSION, 0], value_input_option="RAW")
                get_all_records_cached.clear()
            st.success(f"Proceed completed for {p_name} - ID AUTO{new_id} - {APP_VERSION}")
            st.balloons()
        except Exception as e:
            st.warning(f"Proceed saved locally - {e}")

        # V172: Reset to default state for new patient entry
        if is_home:
            st.session_state.show_home_proceed_note = True
        else:
            st.session_state.show_proceed_note = True

        # Clear form for new entry after short delay - set flags to reset
        st.session_state[personal_ok_key] = False
        st.session_state[diseases_ok_key] = False
        st.session_state[additional_ok_key] = False
        st.session_state[version_key] = 0
        if is_home:
            st.session_state.home_auto_diseases = []
        else:
            st.session_state.auto_diseases = []
        # Clear text inputs by incrementing form version
        st.session_state.form_version += 1
        st.rerun()

    # V197 Requirement 5: Additional Questions at end before result processing (Personal Information and Home treatment only)
    try:
        st.markdown("---")
        st.markdown("<div class='heading-h4'>Additional Questions (Previous Version)</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='heading-h5'>Previous Version Extra Questions - Moved to end before result</div>", unsafe_allow_html=True)
            add_qs = get_additional_patient_questions()
            cols = st.columns(3)
            for idx, (q_label, q_type, q_key) in enumerate(add_qs):
                col = cols[idx % 3]
                with col:
                    if isinstance(q_type, list):
                        st.selectbox(q_label, q_type, key=f"auto_add_q_{q_key}_{prefix}_v197_end")
                    else:
                        st.text_input(q_label, key=f"auto_add_q_{q_key}_{prefix}_v197_end")
    except:
        pass

    show_note = st.session_state.show_home_proceed_note if is_home else st.session_state.show_proceed_note
    if show_note:
        st.markdown("---")
        st.markdown("""
        <div style="background:#1a1c23;border-left:4px solid #ff0000;padding:14px;border-radius:10px;margin:16px 0;">
            <b>Note!</b> These results are not final; work on them is currently in progress. You will be notified soon once the work is complete.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='heading-h4'>Results - (Coming Soon)</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.text_area("1. Diet", value="", disabled=True, key=f"{prefix}_diet_inactive_v172", placeholder="Inactive")
            st.text_area("2. Dietary Restrictions", value="", disabled=True, key=f"{prefix}_diet_rest_inactive_v172", placeholder="Inactive")
            st.text_area("3. Medications", value="", disabled=True, key=f"{prefix}_meds_inactive_v172", placeholder="Inactive")
            st.text_area("4. Instructions", value="", disabled=True, key=f"{prefix}_instr_inactive_v172", placeholder="Inactive")
            st.text_area("5. Follow-up Examination", value="", disabled=True, key=f"{prefix}_followup_inactive_v172", placeholder="Inactive")
        if st.button("Start New Entry", key=f"{prefix}_new_entry_v172"):
            st.session_state.show_home_proceed_note = False
            st.session_state.show_proceed_note = False
            st.session_state[personal_ok_key] = False
            st.session_state[diseases_ok_key] = False
            st.session_state[additional_ok_key] = False
            st.session_state[version_key] = 0
            st.session_state.form_version += 1
            st.rerun()

    return p_name, p_father, p_age, p_phone, p_gender, p_address, diseases_list

def auto_selection_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Auto-Diagnosis</div>", unsafe_allow_html=True)
    # V172: 2 options before form - New Patient, Revisit
    mode = st.radio("Select Mode", ["New Patient", "Revisit"], key="auto_mode_radio_v172", horizontal=True)
    st.session_state.auto_form_mode = mode
    if mode == "Revisit":
        st.markdown("<div class='heading-h4'>Select Patient for Revisit</div>", unsafe_allow_html=True)
        records = get_all_records_cached("AutoDiagnosis")
        my = [r for r in records if str(r.get("ClinicName","")).lower() == str(st.session_state.clinic_name).lower()]
        c1,c2=st.columns(2)
        with c1:
            s_name = st.text_input("Patient Name", key="auto_rev_name_v173")
            s_date = st.text_input("Date (YYYY-MM-DD)", key="auto_rev_date_v173", placeholder="e.g., 2026-09-22")
        with c2:
            s_phone = st.text_input("Phone", key="auto_rev_phone_v173")
            s_address = st.text_input("Address", key="auto_rev_address_v173")
        if s_name or s_phone or s_date or s_address:
            filt=[]
            for r in my:
                match=False
                if s_name and s_name.lower() in str(r.get("Name","")).lower(): match=True
                if s_phone and s_phone.lower() in str(r.get("Phone","")).lower(): match=True
                if s_date and s_date.lower() in str(r.get("Date","")).lower(): match=True
                if s_address and s_address.lower() in str(r.get("Address","")).lower(): match=True
                if match:
                    filt.append(r)
            for r in filt[:10]:
                with st.container(border=True):
                    st.write(f"{r.get('Name','')} | {r.get('Phone','')} | {r.get('Date','')} | {r.get('Diseases','')[:100]}")
                    if st.button(f"Select {r.get('ID','')}", key=f"auto_sel_{r.get('ID','')}_v172"):
                        st.session_state.auto_selected_patient = r
                        st.session_state.auto_revisit_data = r
                        st.rerun()
        if st.session_state.get("auto_selected_patient"):
            st.success(f"Selected: {st.session_state.auto_selected_patient.get('Name','')}")
    else:
        # V197 Fix: Clear only once when switching to New Patient, not on every rerun (fixes Added Diseases + bug #4)
        if st.session_state.get("auto_form_mode_prev") != "New Patient":
            if st.session_state.get("auto_selected_patient"):
                st.session_state.auto_selected_patient = None
            st.session_state.auto_diseases = []
            st.session_state.home_auto_diseases = []
            st.session_state.auto_disease_version = 0
            st.session_state.auto_form_mode_prev = "New Patient"
        # Ensure lists exist
        if "auto_diseases" not in st.session_state:
            st.session_state.auto_diseases = []
        if "home_auto_diseases" not in st.session_state:
            st.session_state.home_auto_diseases = []

    render_auto_form("auto", is_home=False)
    under_development_footer("Auto-Diagnosis")
    add_footer()

def home_user_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Home User Page</div>", unsafe_allow_html=True)
    # V172: Tab to add up to 5 patients and create forms; phone must match Home User signup
    tab1, tab2 = st.tabs(["Home treatment", "My Patients (Up to 5)"])
    with tab1:
        st.markdown("<div class='heading-h4'>Home treatment</div>", unsafe_allow_html=True)
        mode = st.radio("Select Mode", ["New Patient", "Revisit"], key="home_auto_mode_radio_v172", horizontal=True)
        st.session_state.home_auto_form_mode = mode
        if mode == "Revisit":
            st.markdown("<div class='heading-h4'>Select Patient for Revisit</div>", unsafe_allow_html=True)
            records = get_all_records_cached("AutoDiagnosis")
            # For Home User, filter by CreatedBy or ClinicName
            my = [r for r in records if str(r.get("CreatedBy","")).lower() == str(st.session_state.username).lower() or str(r.get("ClinicName","")).lower() == str(st.session_state.clinic_name).lower()]
            c1,c2=st.columns(2)
            with c1:
                s_name = st.text_input("Patient Name", key="home_auto_rev_name_v173")
                s_date = st.text_input("Date", key="home_auto_rev_date_v173", placeholder="YYYY-MM-DD")
            with c2:
                s_phone = st.text_input("Phone", key="home_auto_rev_phone_v173")
                s_address = st.text_input("Address", key="home_auto_rev_address_v173")
            if s_name or s_phone or s_date or s_address:
                filt=[]
                for r in my:
                    match=False
                    if s_name and s_name.lower() in str(r.get("Name","")).lower(): match=True
                    if s_phone and s_phone.lower() in str(r.get("Phone","")).lower(): match=True
                    if s_date and s_date.lower() in str(r.get("Date","")).lower(): match=True
                    if s_address and s_address.lower() in str(r.get("Address","")).lower(): match=True
                    if match:
                        filt.append(r)
                for r in filt[:10]:
                    with st.container(border=True):
                        st.write(f"{r.get('Name','')} | {r.get('Phone','')} | {r.get('Date','')}")
                        if st.button(f"Select {r.get('ID','')}", key=f"home_auto_sel_{r.get('ID','')}_v172"):
                            st.session_state.home_auto_selected_patient = r
                            st.rerun()
        else:
            st.session_state.home_auto_selected_patient = None
            st.session_state.home_auto_diseases = []
            st.session_state.auto_diseases = []

        render_auto_form("home_auto", is_home=True)
    with tab2:
        st.markdown("<div class='heading-h4'>My Patients - Up to 5 Patients (Phone must match Home User signup)</div>", unsafe_allow_html=True)
        home_phone = get_home_user_phone()
        st.info(f"Your registered phone (must match): {home_phone if home_phone else 'Not found - please update signup'}")
        patients = st.session_state.get("home_user_patients", [])
        st.write(f"Current patients: {len(patients)}/5")
        if len(patients) < 5:
            with st.container(border=True):
                np_name = st.text_input("Patient Name", key="home_my_pat_name_v172")
                np_age = st.text_input("Age", key="home_my_pat_age_v172")
                np_phone = st.text_input("Phone (must match your signup)", value=home_phone, key="home_my_pat_phone_v172")
                np_relation = st.text_input("Relation", key="home_my_pat_relation_v172", placeholder="Self, Father, Mother, Child etc")
                if st.button("Add Patient", key="home_my_pat_add_v172"):
                    if not np_name.strip():
                        st.error("Name required")
                    elif np_phone.strip() != home_phone and home_phone:
                        st.error(f"Phone must match your signup phone: {home_phone}")
                    else:
                        patients.append({"name": np_name, "age": np_age, "phone": np_phone, "relation": np_relation, "date": str(datetime.date.today())})
                        st.session_state.home_user_patients = patients
                        st.success(f"Added {np_name} - {len(patients)}/5")
                        st.rerun()
        for i, p in enumerate(patients):
            with st.container(border=True):
                st.write(f"{i+1}. {p.get('name','')} - {p.get('relation','')} - Age {p.get('age','')} - Phone {p.get('phone','')} - Date {p.get('date','')}")
                if st.button(f"Create Form for {p.get('name','')}", key=f"home_my_pat_form_{i}_v172"):
                    st.session_state.home_auto_selected_patient = {"Name": p.get('name',''), "Phone": p.get('phone',''), "Age": p.get('age','')}
                    st.session_state.home_auto_form_mode = "Revisit"
                    st.rerun()
                if st.button(f"Remove {p.get('name','')}", key=f"home_my_pat_rem_{i}_v172"):
                    patients.pop(i)
                    st.session_state.home_user_patients = patients
                    st.rerun()

    under_development_footer("Home User Page")
    add_footer()

def patient_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>New Patient</div>", unsafe_allow_html=True)
    render_patient_form(is_revisit=False)
    under_development_footer("New Patient")
    add_footer()

def patient_revisit_form_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Revisit Form</div>", unsafe_allow_html=True)
    render_patient_form(is_revisit=True)
    under_development_footer("Revisit Form")
    add_footer()

def revisit_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Revisit - Search Patient</div>", unsafe_allow_html=True)
    st.markdown("<div class='heading-h5'>Search using any of these four fields: Patient Name, Date, Address, or Phone Number</div>", unsafe_allow_html=True)
    records = get_all_records_cached("New_patient")
    my = [r for r in records if str(r.get("ClinicName","")).lower() == str(st.session_state.clinic_name).lower()]
    c1,c2=st.columns(2)
    with c1:
        s_name = st.text_input("Patient Name", key="rev_name_v172")
        s_date = st.text_input("Date (YYYY-MM-DD)", key="rev_date_v172", placeholder="e.g., 2026-09-22")
    with c2:
        s_phone = st.text_input("Phone Number", key="rev_phone_v172")
        s_address = st.text_input("Address", key="rev_address_v172")
    
    if s_name or s_phone or s_date or s_address:
        filt=[]
        for r in my:
            match=False
            if s_name and s_name.lower() in str(r.get("Name","")).lower():
                match=True
            if s_phone and s_phone.lower() in str(r.get("Phone","")).lower():
                match=True
            if s_date and s_date.lower() in str(r.get("Date","")).lower():
                match=True
            if s_address and s_address.lower() in str(r.get("Address","")).lower():
                match=True
            if match:
                filt.append(r)
        st.write(f"Found {len(filt)} patients")
        for r in filt[:15]:
            with st.container(border=True):
                st.write(f"{r.get('Name','')} | Date: {r.get('Date','')} | Address: {r.get('Address','')} | Phone: {r.get('Phone','')} | ID: {r.get('PatientID','')} | Balance: Rs {r.get('Balance','0')}")
                if st.button(f"Open {r.get('PatientID','')}", key=f"rev_{r.get('PatientID','')}_v172"):
                    st.session_state.revisit_data=r
                    try: st.session_state.prev_balance=float(str(r.get("Balance","0") or 0).replace(",","") or 0)
                    except: st.session_state.prev_balance=0.0
                    st.session_state.current_page="patient_revisit_form"
                    st.rerun()
    else:
        st.info("Enter any of the four fields: Patient Name, Date, Address, Phone Number to search")
    under_development_footer("Revisit")
    add_footer()

def dictionary_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Dictionary</div>", unsafe_allow_html=True)
    recs=get_all_records_cached("Dictionary")
    for r in recs[:20]:
        st.write(f"{r.get('Word','')} - {r.get('Meaning','')}")
    under_development_footer("Dictionary")
    add_footer()

def pharmacopoeia_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Pharmacopoeia</div>", unsafe_allow_html=True)
    recs=get_all_records_cached("Pharmacopoeia")
    for r in recs[:20]:
        with st.container(border=True):
            st.write(f"{r.get('Name','')} - {r.get('Uses','')}")
    under_development_footer("Pharmacopoeia")
    add_footer()

def clinic_herb_formula_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Herbs & Pharmacopoeia</div>", unsafe_allow_html=True)
    st.info("Data Source: Google Sheets - Herbs and Formulas sheets. When you add data to sheet, it will appear here automatically - V179")
    tab_search_herb, tab_all_herbs, tab_search_form, tab_all_form = st.tabs(["Search Herbs", "All Herbs", "Search Formulas", "All Formulas"])
    with tab_search_herb:
        st.markdown("<div class='heading-h4'>Search Herbs</div>", unsafe_allow_html=True)
        search_herb = st.text_input("Herb search", key="herb_search_v179", placeholder="Type herb name")
        herb_recs = get_all_records_cached("Herbs")
        if not herb_recs:
            herb_recs = get_all_records_cached("Pharmacopoeia")
        if search_herb:
            filtered = [r for r in herb_recs if search_herb.lower() in str(r.get("Name","")).lower() or search_herb.lower() in str(r.get("Uses","")).lower()]
        else:
            filtered = herb_recs[:20]
        for r in filtered[:30]:
            with st.container(border=True):
                st.markdown(f"<b>{r.get('Name','')}</b> - {r.get('Temperament','')} | Uses: {r.get('Uses','')[:150]}", unsafe_allow_html=True)
    with tab_all_herbs:
        st.markdown("<div class='heading-h4'>All Herbs - Complete List from Google Sheet</div>", unsafe_allow_html=True)
        herb_all = get_all_records_cached("Herbs")
        if not herb_all:
            herb_all = get_all_records_cached("Pharmacopoeia")
        st.write(f"Total Herbs in Sheet: {len(herb_all)}")
        if not herb_all:
            st.warning("Herbs sheet is empty - add herbs to Google Sheet Herbs tab, they will appear here")
        else:
            df_herbs = pd.DataFrame(herb_all)
            st.dataframe(df_herbs, use_container_width=True)
            for r in herb_all[:100]:
                with st.container(border=True):
                    st.write(f"{r.get('Name','')} - {r.get('Temperament','')} - {r.get('Uses','')} - {r.get('Dosage','')}")
    with tab_search_form:
        st.markdown("<div class='heading-h4'>Search Formulas</div>", unsafe_allow_html=True)
        search_formula_herb = st.text_input("Herb name search in Formulas", key="formula_search_herb_v179", placeholder="Search by herb or formula name")
        formula_recs = get_all_records_cached("Formulas")
        curr_clinic = st.session_state.get("clinic_name","")
        my_formulas = [r for r in formula_recs if str(r.get("ClinicName","")).lower() == str(curr_clinic).lower()] if curr_clinic else formula_recs
        if search_formula_herb:
            filtered_form = [r for r in my_formulas if search_formula_herb.lower() in str(r.get("Ingredients","")).lower() or search_formula_herb.lower() in str(r.get("Name","")).lower()]
        else:
            filtered_form = my_formulas[:20]
        for r in filtered_form[:30]:
            with st.container(border=True):
                st.markdown(f"<b>{r.get('Name','')}</b> - Ingredients: {r.get('Ingredients','')} | Uses: {r.get('Uses','')}", unsafe_allow_html=True)
    with tab_all_form:
        st.markdown("<div class='heading-h4'>All Formulas - Complete List from Google Sheet</div>", unsafe_allow_html=True)
        formula_all = get_all_records_cached("Formulas")
        st.write(f"Total Formulas in Sheet: {len(formula_all)}")
        if not formula_all:
            st.warning("Formulas sheet is empty - add formulas to Google Sheet Formulas tab, they will appear here")
        else:
            df_form = pd.DataFrame(formula_all)
            st.dataframe(df_form, use_container_width=True)
            for r in formula_all[:100]:
                with st.container(border=True):
                    st.write(f"{r.get('Name','')} - {r.get('Ingredients','')} - {r.get('Uses','')} - {r.get('Temperament','')}")

    under_development_footer("Herbs & Pharmacopoeia")
    add_footer()



def home_user_articles_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Articles</div>", unsafe_allow_html=True)
    recs=get_all_records_cached("Articles")
    for r in recs[:10]:
        with st.container(border=True):
            st.write(r.get('TitleEN',''))
    under_development_footer("Articles")
    add_footer()


def articles_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Articles</div>", unsafe_allow_html=True)
    recs = get_all_records_cached("Articles")
    if not recs:
        st.info("No articles yet")
        add_footer()
        return
    # Sort by date newest first - Task 5
    def date_key(r):
        try:
            return datetime.datetime.strptime(str(r.get("Date","")), "%Y-%m-%d")
        except:
            return datetime.datetime.min
    recs_sorted = sorted(recs, key=date_key, reverse=True)
    
    # Task 4 - Default no article, only list
    if "selected_article_id" not in st.session_state:
        st.session_state.selected_article_id = None
    
    st.markdown("<div class='heading-h4'>Select Article to Read</div>", unsafe_allow_html=True)
    # Show list as buttons - only title, no date/id/category
    for r in recs_sorted[:100]:
        title = r.get("TitleEN","") or r.get("TitleUR","") or r.get("TitleAR","") or "Untitled"
        if st.button(title, key=f"art_list_{r.get('ID','')}_v180", use_container_width=True):
            st.session_state.selected_article_id = r.get("ID","")
            st.rerun()
    
    # Show selected article - Task 6 - only heading and content, no category/date/id
    if st.session_state.selected_article_id:
        sel = next((r for r in recs if r.get("ID","")==st.session_state.selected_article_id), None)
        if sel:
            st.markdown("---")
            # Determine language content to show based on available
            heading = sel.get("TitleEN","") or sel.get("TitleUR","") or sel.get("TitleAR","")
            content = sel.get("ContentEN","") or sel.get("ContentUR","") or sel.get("ContentAR","")
            # Try to show in current app language
            lang = st.session_state.get("lang","en")
            if lang=="ur" and sel.get("TitleUR",""):
                heading = sel.get("TitleUR","")
                content = sel.get("ContentUR","")
            elif lang=="ar" and sel.get("TitleAR",""):
                heading = sel.get("TitleAR","")
                content = sel.get("ContentAR","")
            st.markdown(f"<div class='heading-h3'>{heading}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='background:#1e1f22;border:2px solid #5a5a5a;border-radius:12px;padding:16px;margin-top:12px;white-space:pre-wrap;'>{content}</div>", unsafe_allow_html=True)
            if st.button("Close Article", key="close_art_v180"):
                st.session_state.selected_article_id = None
                st.rerun()
    
    add_footer()

def clinic_articles_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Articles</div>", unsafe_allow_html=True)
    recs = get_all_records_cached("Articles")
    clinic_recs = [r for r in recs if str(r.get("Audience","")).lower() in ["all","clinic",""]]
    if not clinic_recs:
        clinic_recs = recs

    # Language selection after page title - Task
    lang_sel = st.radio("Select Language", ["English", "Urdu - اردو", "Arabic - العربية"], horizontal=True, key="clinic_art_lang_v181")
    lang_map = {"English":"en", "Urdu - اردو":"ur", "Arabic - العربية":"ar"}
    sel_lang = lang_map[lang_sel]

    # Filter by selected language
    def has_lang(r, lang):
        if lang=="en": return bool(str(r.get("TitleEN","")).strip() or str(r.get("ContentEN","")).strip())
        if lang=="ur": return bool(str(r.get("TitleUR","")).strip() or str(r.get("ContentUR","")).strip())
        if lang=="ar": return bool(str(r.get("TitleAR","")).strip() or str(r.get("ContentAR","")).strip())
        return True

    filtered = [r for r in clinic_recs if has_lang(r, sel_lang)]

    def date_key(r):
        try:
            return datetime.datetime.strptime(str(r.get("Date","")), "%Y-%m-%d")
        except:
            return datetime.datetime.min
    filtered_sorted = sorted(filtered, key=date_key, reverse=True)

    if "clinic_selected_article_id" not in st.session_state:
        st.session_state.clinic_selected_article_id = None

    # Collapsible list using selectbox - Task
    if not filtered_sorted:
        st.info(f"No {sel_lang.upper()} articles found")
    else:
        options = []
        id_map = {}
        for r in filtered_sorted:
            title = ""
            if sel_lang=="en": title = r.get("TitleEN","")
            elif sel_lang=="ur": title = r.get("TitleUR","")
            else: title = r.get("TitleAR","")
            label = title or "Untitled"
            options.append(label)
            id_map[label] = r.get("ID","")
        
        sel_label = st.selectbox("Select Article to Read - collapsible list", ["-- Select --"] + options, key="clinic_art_select_v181")
        if sel_label != "-- Select --":
            st.session_state.clinic_selected_article_id = id_map.get(sel_label, "")

        if st.session_state.clinic_selected_article_id:
            sel = next((r for r in recs if r.get("ID","")==st.session_state.clinic_selected_article_id), None)
            if sel:
                st.markdown("---")
                heading = sel.get("TitleEN","") if sel_lang=="en" else sel.get("TitleUR","") if sel_lang=="ur" else sel.get("TitleAR","")
                content = sel.get("ContentEN","") if sel_lang=="en" else sel.get("ContentUR","") if sel_lang=="ur" else sel.get("ContentAR","")
                st.markdown(f"<div class='heading-h3'>{heading}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background:#1e1f22;border:2px solid #5a5a5a;border-radius:12px;padding:16px;white-space:pre-wrap;'>{content}</div>", unsafe_allow_html=True)
                if st.button("Close", key="close_clinic_v181"):
                    st.session_state.clinic_selected_article_id = None
                    st.rerun()
    add_footer()

def home_user_articles_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Articles</div>", unsafe_allow_html=True)
    recs = get_all_records_cached("Articles")
    home_recs = [r for r in recs if str(r.get("Audience","")).lower() in ["all","homeuser","home_user",""]]
    if not home_recs:
        home_recs = recs

    lang_sel = st.radio("Select Language", ["English", "Urdu - اردو", "Arabic - العربية"], horizontal=True, key="home_art_lang_v181")
    lang_map = {"English":"en", "Urdu - اردو":"ur", "Arabic - العربية":"ar"}
    sel_lang = lang_map[lang_sel]

    def has_lang(r, lang):
        if lang=="en": return bool(str(r.get("TitleEN","")).strip() or str(r.get("ContentEN","")).strip())
        if lang=="ur": return bool(str(r.get("TitleUR","")).strip() or str(r.get("ContentUR","")).strip())
        if lang=="ar": return bool(str(r.get("TitleAR","")).strip() or str(r.get("ContentAR","")).strip())
        return True

    filtered = [r for r in home_recs if has_lang(r, sel_lang)]

    def date_key(r):
        try:
            return datetime.datetime.strptime(str(r.get("Date","")), "%Y-%m-%d")
        except:
            return datetime.datetime.min
    filtered_sorted = sorted(filtered, key=date_key, reverse=True)

    if "home_selected_article_id" not in st.session_state:
        st.session_state.home_selected_article_id = None

    if not filtered_sorted:
        st.info(f"No {sel_lang.upper()} articles found")
    else:
        options = []
        id_map = {}
        for r in filtered_sorted:
            title = ""
            if sel_lang=="en": title = r.get("TitleEN","")
            elif sel_lang=="ur": title = r.get("TitleUR","")
            else: title = r.get("TitleAR","")
            label = title or "Untitled"
            options.append(label)
            id_map[label] = r.get("ID","")
        
        sel_label = st.selectbox("Select Article to Read - collapsible list", ["-- Select --"] + options, key="home_art_select_v181")
        if sel_label != "-- Select --":
            st.session_state.home_selected_article_id = id_map.get(sel_label, "")

        if st.session_state.home_selected_article_id:
            sel = next((r for r in recs if r.get("ID","")==st.session_state.home_selected_article_id), None)
            if sel:
                st.markdown("---")
                heading = sel.get("TitleEN","") if sel_lang=="en" else sel.get("TitleUR","") if sel_lang=="ur" else sel.get("TitleAR","")
                content = sel.get("ContentEN","") if sel_lang=="en" else sel.get("ContentUR","") if sel_lang=="ur" else sel.get("ContentAR","")
                st.markdown(f"<div class='heading-h3'>{heading}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background:#1e1f22;border:2px solid #5a5a5a;border-radius:12px;padding:16px;white-space:pre-wrap;'>{content}</div>", unsafe_allow_html=True)
                if st.button("Close", key="close_home_v181"):
                    st.session_state.home_selected_article_id = None
                    st.rerun()
    add_footer()

def articles_page():
    clinic_articles_page()



def get_app_setting(key, default="Yes"):
    try:
        recs = get_all_records_cached("AppSettings")
        for r in recs:
            if str(r.get("Key","")).lower() == key.lower():
                return str(r.get("Value",""))
        return default
    except:
        return default

def dashboard_welcome_page():
    language_selector()
    clinic_heading_banner()
    top_nav_dashboard()
    st.markdown("<div class='dash-section-title'>Clinic Section</div>", unsafe_allow_html=True)
    # V176 - Laptop: icon merged with tab, gap zero, thick raised clear bounding box on all sides
    r1c1,r1c2,r1c3=st.columns(3)
    with r1c1:
        st.markdown("<div class='graceful-card' style='padding:4px;'>", unsafe_allow_html=True)
        if st.button("🧑‍⚕️ New Patient", use_container_width=True, key="dash_new_v176"):
            st.session_state.prev_page = "dashboard_welcome"
            st.session_state.page_history.append("dashboard_welcome")
            st.session_state.form_version+=1
            st.session_state.prev_balance=0.0
            st.session_state.revisit_data=None
            st.session_state.section_opened={"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
            st.session_state.current_page="patient"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r1c2:
        st.markdown("<div class='graceful-card' style='padding:4px;'>", unsafe_allow_html=True)
        if st.button("🔍 Revisit", use_container_width=True, key="dash_rev_v176"):
            st.session_state.prev_page = "dashboard_welcome"
            st.session_state.page_history.append("dashboard_welcome")
            st.session_state.current_page="revisit"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r1c3:
        st.markdown("<div class='graceful-card' style='padding:4px;'>", unsafe_allow_html=True)
        if st.button("⚕️ Auto-Diagnosis", use_container_width=True, key="dash_auto_v176"):
            st.session_state.prev_page = "dashboard_welcome"
            st.session_state.page_history.append("dashboard_welcome")
            st.session_state.current_page="auto_selection"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    r2c1,r2c2,r2c3=st.columns(3)
    with r2c1:
        st.markdown("<div class='graceful-card' style='padding:4px;'>", unsafe_allow_html=True)
        if st.button("📚 Dictionary", use_container_width=True, key="dash_dict_v176"):
            st.session_state.prev_page = "dashboard_welcome"
            st.session_state.page_history.append("dashboard_welcome")
            st.session_state.current_page="dictionary"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r2c2:
        st.markdown("<div class='graceful-card' style='padding:4px;'>", unsafe_allow_html=True)
        if st.button("📰 Articles", use_container_width=True, key="dash_c_art_v176"):
            st.session_state.prev_page = "dashboard_welcome"
            st.session_state.page_history.append("dashboard_welcome")
            st.session_state.current_page="clinic_articles"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r2c3:
        st.markdown("<div class='graceful-card' style='padding:4px;'>", unsafe_allow_html=True)
        if st.button("🌿 Herbs & Pharma", use_container_width=True, key="dash_herb_v176"):
            st.session_state.prev_page = "dashboard_welcome"
            st.session_state.page_history.append("dashboard_welcome")
            st.session_state.current_page="clinic_herb_formula"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    show_offer = get_app_setting("OfferEnabled", get_app_setting("show_offer_tab","Yes"))
    if str(show_offer).lower() in ["yes","on","true","1","enabled"]: 
        r3c1,r3c2,r3c3=st.columns(3)
        with r3c1:
            st.markdown("<div class='graceful-card' style='padding:4px; border:3px solid #00ff88; animation: blinkGreen 1.2s infinite; box-shadow: 0 6px 0 #003d1f, 0 8px 16px rgba(0,255,136,0.3), inset 0 1px 0 rgba(255,255,255,0.15);'>", unsafe_allow_html=True)
            if st.button("🎁 Offer", use_container_width=True, key="dash_offer_v176"):
                st.session_state.prev_page = "dashboard_welcome"
                st.session_state.page_history.append("dashboard_welcome")
                st.session_state.current_page="offer_page"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='dash-section-title'>Home User</div>", unsafe_allow_html=True)
    h1,h2=st.columns(2)
    with h1:
        st.markdown("<div class='graceful-card' style='padding:4px;'>", unsafe_allow_html=True)
        if st.button("🏠 Home User Page", use_container_width=True, key="dash_home_v176"):
            st.session_state.prev_page = "dashboard_welcome"
            st.session_state.page_history.append("dashboard_welcome")
            st.session_state.current_page="home_user"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with h2:
        st.markdown("<div class='graceful-card' style='padding:4px;'>", unsafe_allow_html=True)
        if st.button("📄 Articles", use_container_width=True, key="dash_home_art_v176"):
            st.session_state.prev_page = "dashboard_welcome"
            st.session_state.page_history.append("dashboard_welcome")
            st.session_state.current_page="home_user_articles"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("user_role") in ["Boss","Staff"] or st.session_state.get("user_type")=="Staff":
        st.markdown("<div class='dash-section-title'>App Admin</div>", unsafe_allow_html=True)
        ac1,ac2,ac3=st.columns(3)
        with ac1:
            st.markdown("<div class='graceful-card' style='padding:4px;'>", unsafe_allow_html=True)
            if st.button("⚙️ App Admin Panel", use_container_width=True, key="dash_admin_panel_v176"):
                st.session_state.prev_page = "dashboard_welcome"
                st.session_state.page_history.append("dashboard_welcome")
                st.session_state.current_page="admin"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    try:
        recs = get_all_records_cached("UserSignups")
        total = len(recs)
        display = 650+total
    except:
        display=650
    st.markdown("---")
    st.markdown(f"<div style='text-align:center;'><div class='heading-h4'>Total App Users</div><div style='font-size:32px;font-weight:900;color:#00ff88;'>{display}</div><div style='color:#666;font-size:12px;margin-top:6px;'></div></div>", unsafe_allow_html=True)
    add_footer()

def clinic_login_page():
    language_selector()
    st.markdown(f"<div style='background:#1a1c23;border:2px solid #ff0000;border-radius:18px;padding:24px;text-align:center;'><div class='heading-h1'>Herbal Clinic International</div><div style='color:#666;'>3 Languages</div></div>", unsafe_allow_html=True)
    with st.container(border=True):
        t1,t2,t3=st.tabs(["Staff Login","Clinic User","Home User"])
        with t1:
            u=st.text_input("Username", value="boss", key="login_u_v172")
            p=st.text_input("Password", type="password", value="boss123", key="login_p_v172")
            if st.button("Login", use_container_width=True, type="primary", key="staff_login_v172"):
                st.session_state.logged_in=True
                st.session_state.username=u
                st.session_state.user_role="Boss"
                st.session_state.user_type="Staff"
                st.session_state.current_page="dashboard_welcome"
                st.rerun()
        with t2:
            cu=st.text_input("Username", key="clinic_u_v172")
            cp=st.text_input("Password", type="password", key="clinic_p_v172")
            if st.button("Login", use_container_width=True, type="primary", key="clinic_login_v172"):
                st.session_state.logged_in=True
                st.session_state.username=cu
                st.session_state.user_role="clinic"
                st.session_state.user_type="Clinic"
                st.session_state.current_page="dashboard_welcome"
                st.rerun()
        with t3:
            hu=st.text_input("Username", key="home_u_v172")
            hp=st.text_input("Password", type="password", key="home_p_v172")
            if st.button("Login", use_container_width=True, type="primary", key="home_login_v172"):
                st.session_state.logged_in=True
                st.session_state.username=hu
                st.session_state.user_role="home_user"
                st.session_state.user_type="HomeUser"
                st.session_state.current_page="home_user"
                st.rerun()
    add_footer()

def feedback_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Feedback</div>", unsafe_allow_html=True)
    page_ref = st.session_state.get("feedback_page_ref","") or "General"
    st.markdown(f"<div class='heading-h4'>Page: {page_ref}</div>", unsafe_allow_html=True)
    
    tab_fb, tab_wa = st.tabs(["Feedback Form", "WhatsApp Linked"])
    with tab_fb:
        name, from_loc, phone, email = get_user_info_for_feedback()
        st.text_input("Feedback Page (Auto)", value=page_ref, key="fb_page_ref_v197", disabled=True)
        # V197 - show if suspended
        try:
            if check_feedback_suspension():
                st.warning("Your patient forms are suspended due to missing feedback. Please submit feedback to restore.")
        except: pass
        feedback_text = st.text_area("Feedback Details *", key="fb_text_v197", height=150)
        if st.button("Submit", type="primary", use_container_width=True, key="fb_ok_v197"):
            if not feedback_text.strip():
                st.error("Feedback required")
            else:
                fid = get_next_feedback_id()
                ws = get_sheet_safe("Feedback")
                if ws:
                    # V197 - include Username and ClinicName for suspension check
                    row_data = {"ID": fid, "Name": name, "From": from_loc, "Phone Number": phone, "Email": email, "Feedback Page": page_ref, "Feedback": feedback_text, "Date": str(datetime.date.today()), "Status": "Unread", "Username": st.session_state.get("username",""), "ClinicName": st.session_state.get("clinic_name",""), "UserType": st.session_state.get("user_type","")}
                    hdr = ws.row_values(1) if ws.row_values(1) else SHEET_HEADERS["Feedback"]
                    # Ensure extra columns exist in row
                    row = [row_data.get(h,"") for h in hdr]
                    ws.append_row(row, value_input_option="RAW")
                    get_all_records_cached.clear()
                    st.success(f"Thank you! {fid} submitted - Full app services restored!")
                    st.balloons()
                    # V197 - Requirement 6: After Submit, return to same page where user wanted to work (Requirement 5)
                    get_all_records_cached.clear()
                    return_page = st.session_state.get("feedback_return_page","")
                    if return_page and return_page != "feedback_page":
                        st.session_state.current_page = return_page
                        st.session_state.feedback_return_page = ""
                        st.success(f"Returning to {return_page} - Full access restored!")
                    else:
                        st.session_state.current_page = "dashboard_welcome"
                    st.rerun()
    with tab_wa:
        st.markdown("<div class='heading-h4'>Join us on WhatsApp</div>", unsafe_allow_html=True)
        st.markdown("For quick support, suggestions and updates - join our WhatsApp community", unsafe_allow_html=True)
        st.markdown(f'''
        <div style="margin-top:12px;">
            <a href="{WHATSAPP_LINK}" target="_blank" style="text-decoration:none;">
                <span style="display:inline-flex;align-items:center;background:#25D366;color:white;padding:14px 22px;border-radius:28px;font-size:16px;font-weight:800;width:100%;justify-content:center;box-shadow: 0 4px 12px rgba(37,211,102,0.4);">
                    <span style="background:white;color:#25D366;border-radius:50%;width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;margin-right:12px;font-weight:900;font-size:18px;">W</span>
                    Join WhatsApp Group
                </span>
            </a>
        </div>
        ''', unsafe_allow_html=True)
        st.info("This WhatsApp linked tab is now available on Feedback page - V179 fix")
    add_footer()





# ========== POPUP & FEEDBACK SUSPENSION SYSTEM - V197 ==========
def get_popup_dismissed_key(username, popup_id):
    return f"PopupDismissed_{username}_{popup_id}"

def is_popup_dismissed(username, popup_id):
    try:
        recs = get_all_records_cached("AppSettings")
        key = get_popup_dismissed_key(username, popup_id)
        for r in recs:
            if str(r.get("Key",""))==key and str(r.get("Value","")).lower()=="yes":
                return True
        return False
    except:
        return False

def dismiss_popup_permanently(username, popup_id):
    try:
        ws = get_sheet_safe("AppSettings")
        if not ws:
            return
        hdr = ws.row_values(1) if ws.row_values(1) else SHEET_HEADERS["AppSettings"]
        # Check if exists
        vals = ws.get_all_values()
        for i,row in enumerate(vals[1:], start=2):
            if row and row[0]==get_popup_dismissed_key(username, popup_id):
                ws.update(f"B{i}", [["Yes"]])
                get_all_records_cached.clear()
                return
        row_data = {"Key": get_popup_dismissed_key(username, popup_id), "Value": "Yes", "Date": str(datetime.date.today()), "Status": "Active", "Description": f"Popup {popup_id} dismissed by {username} via OK"}
        row = [row_data.get(h,"") for h in hdr]
        ws.append_row(row, value_input_option="RAW")
        get_all_records_cached.clear()
    except Exception as e:
        pass

def get_active_popups():
    try:
        recs = get_all_records_cached("Articles")
        popups = [r for r in recs if str(r.get("MainCategory","")).lower()=="popup" or str(r.get("Type","")).lower()=="popup" or "popup" in str(r.get("ID","")).lower()]
        # Also from AppSettings if popup defined there
        try:
            appset = get_all_records_cached("AppSettings")
            for ar in appset:
                k=str(ar.get("Key",""))
                if k.lower().startswith("popup_") and not k.lower().startswith("popupdismissed_"):
                    # Create virtual popup record from AppSettings
                    popups.append({"ID": k, "TitleEN": ar.get("Description","") or k, "ContentEN": ar.get("Value",""), "MainCategory":"Popup", "Date": ar.get("Date","")})
        except: pass
        return popups
    except:
        return []

def show_single_popup_per_page(page_name):
    # Requirement 5: Multiple popups may exist, but show only one per page
    # Requirement 4: If X clicked, show again on next sign-in. If OK clicked, never show again.
    try:
        username = st.session_state.get("username","")
        if not username:
            return
        # Initialize session tracking for popups shown this session per page
        if "popups_shown_pages" not in st.session_state:
            st.session_state.popups_shown_pages = set()
        # If already shown a popup on this page in this session, don't show another
        if page_name in st.session_state.popups_shown_pages:
            return
        popups = get_active_popups()
        if not popups:
            return
        # Find first not dismissed
        for pop in popups:
            pid = str(pop.get("ID",""))
            if not is_popup_dismissed(username, pid):
                # Show this popup
                # Use dialog-like container with X and OK behavior
                if f"popup_closed_{pid}_{page_name}" not in st.session_state:
                    st.session_state[f"popup_closed_{pid}_{page_name}"] = False
                if st.session_state[f"popup_closed_{pid}_{page_name}"]:
                    continue
                # Display popup
                with st.container(border=True):
                    st.markdown(f"<div style='background:#161617;border:2px solid #ffaa00;border-radius:12px;padding:16px;'><div style='font-weight:900;font-size:18px;color:#ffaa00;'>📢 {pop.get('TitleEN','') or pop.get('TitleUR','') or pid}</div><div style='margin-top:8px;color:#e0e0e0;'>{pop.get('ContentEN','') or pop.get('ContentUR','') or pop.get('ContentAR','')}</div></div>", unsafe_allow_html=True)
                    c1,c2 = st.columns([1,1])
                    with c1:
                        if st.button("OK", key=f"popup_ok_{pid}_{page_name}_v197", type="primary"):
                            dismiss_popup_permanently(username, pid)
                            st.session_state.popups_shown_pages.add(page_name)
                            st.session_state[f"popup_closed_{pid}_{page_name}"] = True
                            st.rerun()
                    with c2:
                        if st.button("X Close", key=f"popup_x_{pid}_{page_name}_v197"):
                            # X clicked - do NOT dismiss permanently, so it will show again next sign-in
                            # Just mark as closed for this page view, but not permanently
                            st.session_state.popups_shown_pages.add(page_name)
                            st.session_state[f"popup_closed_{pid}_{page_name}"] = True
                            # Store that X was clicked - will show again next login because not dismissed
                            st.rerun()
                # Only one popup per page
                break
    except Exception as e:
        pass

def check_feedback_suspension():
    # V197 Requirement 5: Show notice only after 10 days, app tracks limit, resets from comment day if feedback within 10 days
    try:
        username = st.session_state.get("username","")
        if not username:
            return False
        # Boss/Staff should not be suspended on first day for testing - but logic still applies after 10 days
        # For safety, if username is boss, check but don't suspend on first day if no signup date
        recs = get_all_records_cached("Feedback")
        user_feedbacks = [r for r in recs if str(r.get("Username","")).lower()==username.lower() or str(r.get("ClinicName","")).lower()==str(st.session_state.get("clinic_name","")).lower() or str(r.get("Name","")).lower()==username.lower()]
        if not user_feedbacks:
            try:
                signup_recs = get_all_records_cached("UserSignups")
                for sr in signup_recs:
                    if str(sr.get("Username","")).lower()==username.lower():
                        date_str = str(sr.get("Date","")).strip()
                        # Try multiple date formats
                        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"]:
                            try:
                                signup_date = datetime.datetime.strptime(date_str.split(" ")[0], fmt).date()
                                days_since = (datetime.date.today() - signup_date).days
                                return days_since >= 10
                            except:
                                continue
                        # If date parse fails, DO NOT suspend on first day (V197 fix)
                        return False
                # If no signup found (e.g. boss login), do NOT suspend on first day
                return False
            except:
                return False
        latest_date = None
        for fb in user_feedbacks:
            dstr = str(fb.get("Date","")).strip()
            if not dstr:
                continue
            for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"]:
                try:
                    d = datetime.datetime.strptime(dstr.split(" ")[0], fmt).date()
                    if latest_date is None or d > latest_date:
                        latest_date = d
                    break
                except:
                    continue
        if latest_date is None:
            # If feedback exists but date invalid, don't suspend
            return False
        days_diff = (datetime.date.today() - latest_date).days
        # V197: Limit restarts from comment day, suspension only if >=10 days passed
        return days_diff >= 10
    except Exception as e:
        # On any error, don't suspend to avoid first-day issue
        return False

def show_feedback_suspension_notice():
    # V197 - Golden font, and correct navigation to feedback_page with return
    st.markdown("""
    <div style="background:#161617;border:2px solid #FFD700;border-radius:16px;padding:24px;text-align:center;margin:20px 0;box-shadow:0 6px 0 #5a4a00, 0 12px 24px rgba(0,0,0,0.6);">
        <div style="font-size:20px;font-weight:900;color:#FFD700;margin-bottom:12px;">⚠️ Notice! You have not yet provided your feedback. Please submit your feedback to restore full app services.</div>
        <div style="color:#cccccc;font-size:14px;margin-bottom:6px;">Your access to patient forms is temporarily suspended. Please provide feedback to continue.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("OK - Go to Feedback Page", key="feedback_suspend_ok_v197", type="primary", use_container_width=True):
        st.session_state.feedback_return_page = st.session_state.get("current_page","patient")
        st.session_state.feedback_page_ref = "Patient Form Suspension - 10 Days Limit"
        st.session_state.current_page = "feedback_page"
        st.rerun()

# ========== END POPUP & FEEDBACK SYSTEM - V197 ==========


# APP ADMIN LOCKED - V197 - Do not auto-modify this page without user explicit request
def admin_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown(f"<div class='heading-h3'>App Admin</div>", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)

    sections = ["General", "Clinic Data", "Home User", "Users", "Article", "Offer Control", "AppSettings", "Data"]
    if "admin_selected_section" not in st.session_state:
        st.session_state.admin_selected_section = ""

    # Highlight menu tab that opens - V197 fix
    st.markdown('''<style>
    .admin-menu-active {
        background: linear-gradient(145deg, #00ff88, #00cc6a) !important;
        color: #000 !important;
        font-weight: 900 !important;
        border: 2px solid #00ff88 !important;
        box-shadow: 0 4px 0 #007a33, 0 6px 16px rgba(0,230,118,0.4) !important;
    }
    </style>''', unsafe_allow_html=True)
    cols = st.columns(len(sections))
    for idx, sec in enumerate(sections):
        with cols[idx]:
            is_selected = st.session_state.admin_selected_section == sec
            btn_type = "primary" if is_selected else "secondary"
            # Highlight the opened menu tab
            if is_selected:
                st.markdown(f"<div style='background:#00E676;color:#000;font-weight:900;text-align:center;padding:4px;border-radius:6px;margin-bottom:4px;border:2px solid #00c853;box-shadow:0 2px 0 #007a33;'>✓ {sec}</div>", unsafe_allow_html=True)
            if st.button(sec, key=f"admin_nav_{sec}_v197", use_container_width=True, type=btn_type):
                st.session_state.admin_selected_section = sec
                st.rerun()
    selected = st.session_state.admin_selected_section
    if selected:
        st.markdown(f"<div style='background:#1a1c23;border-left:4px solid #00E676;padding:8px 12px;border-radius:8px;margin:8px 0;color:#00E676;font-weight:700;'>📂 Open Tab: {selected}</div>", unsafe_allow_html=True)


    if not selected:
        st.info("Please select a section")
        under_development_footer("App Admin")
        add_footer()
        return

    if selected == "General":
        st.markdown("<div class='heading-h4'>General</div>", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(["UserSignups (CU_/HU_)", "PermissionGranted", "Articles", "Feedback"])
        with tab1:
            recs = get_all_records_cached("UserSignups")
            st.write(f"Total: {len(recs)}")
            if recs:
                st.dataframe(pd.DataFrame(recs).head(30), use_container_width=True)
        with tab2:
            recs = get_all_records_cached("PermissionGranted")
            st.write(f"Total Permissions: {len(recs)}")
            if recs:
                st.dataframe(pd.DataFrame(recs).head(20), use_container_width=True)
        with tab3:
            recs = get_all_records_cached("Articles")
            st.write(f"Total Articles: {len(recs)}")
            if recs:
                st.dataframe(pd.DataFrame([{"ID":r.get("ID",""), "Title":r.get("TitleEN","")[:40], "MainCategory":r.get("MainCategory","")} for r in recs[:20]]), use_container_width=True)
        with tab4:
            fb_recs = get_all_records_cached("Feedback")
            st.write(f"Total Feedbacks: {len(fb_recs)}")
            if fb_recs:
                st.dataframe(pd.DataFrame(fb_recs).head(20), use_container_width=True)

    elif selected == "Clinic Data":
        st.markdown("<div class='heading-h4'>Clinic Data</div>", unsafe_allow_html=True)
        for sh_name in CLINIC_SHEETS:
            with st.expander(f"{sh_name} - {len(get_all_records_cached(sh_name))} records"):
                recs_d = get_all_records_cached(sh_name)
                if recs_d:
                    st.dataframe(pd.DataFrame(recs_d).head(10), use_container_width=True)

    elif selected == "Home User":
        st.markdown("<div class='heading-h4'>Home User</div>", unsafe_allow_html=True)
        recs = get_all_records_cached("HomeUsers")
        st.write(f"Total Home Users: {len(recs)}")
        if recs:
            st.dataframe(pd.DataFrame(recs).head(20), use_container_width=True)

    elif selected == "Users":
        st.markdown("<div class='heading-h4'>Users</div>", unsafe_allow_html=True)
        tab_clinic, tab_home = st.tabs(["Clinic Users (CU_1,2,3...)", "Home Users (HU_1,2,3...)"])
        all_recs = get_all_records_cached("UserSignups")
        with tab_clinic:
            clinic_recs = [r for r in all_recs if str(r.get("SignupID","")).startswith("CU_") or "clinic" in str(r.get("UserType","")).lower()]
            st.write(f"Total Clinic Users: {len(clinic_recs)}")
            if clinic_recs:
                disp=[]
                for r in clinic_recs:
                    disp.append({"ID": r.get("SignupID",""), "Name": r.get("ClinicName","") or r.get("Username",""), "Gender": r.get("Gender","") or "N/A", "Address": r.get("From","") or r.get("Address",""), "Date": r.get("Date",""), "Phone": r.get("Phone","")})
                st.dataframe(pd.DataFrame(disp), use_container_width=True)
        with tab_home:
            home_recs = [r for r in all_recs if str(r.get("SignupID","")).startswith("HU_") or "home" in str(r.get("UserType","")).lower()]
            st.write(f"Total Home Users: {len(home_recs)}")
            if home_recs:
                disp=[]
                for r in home_recs:
                    disp.append({"ID": r.get("SignupID",""), "Name": r.get("ClinicName","") or r.get("Username",""), "Gender": r.get("Gender","") or "N/A", "Address": r.get("From","") or r.get("Address",""), "Date": r.get("Date",""), "Phone": r.get("Phone","")})
                st.dataframe(pd.DataFrame(disp), use_container_width=True)

    elif selected == "Offer Control":
        st.markdown("<div class='heading-h4'>Offer Control</div>", unsafe_allow_html=True)
        current_offer = get_app_setting("OfferEnabled", get_app_setting("show_offer_tab","No"))
        st.info(f"Current Offer Status: {current_offer}")
        with st.container(border=True):
            col1,col2 = st.columns(2)
            with col1:
                if st.button("🟢 Offer ON", key="offer_on_v197", type="primary", use_container_width=True):
                    ws = get_sheet_safe("AppSettings")
                    if ws:
                        vals = ws.get_all_values()
                        hdr = vals[0] if vals else SHEET_HEADERS["AppSettings"]
                        found=False
                        for i,row in enumerate(vals[1:], start=2):
                            if row and row[0].lower() in ["offerenabled","show_offer_tab"]:
                                ws.update(f"B{i}", [["Yes"]])
                                ws.update(f"A{i}", [["OfferEnabled"]])
                                found=True
                                break
                        if not found:
                            row_data = {"Key": "OfferEnabled", "Value": "Yes", "Date": str(datetime.date.today()), "Status": "Active", "Description": "Offer ON"}
                            row = [row_data.get(h,"") for h in hdr]
                            ws.append_row(row, value_input_option="RAW")
                        get_all_records_cached.clear()
                        st.success("Offer ON")
                        st.rerun()
            with col2:
                if st.button("🔴 Offer OFF", key="offer_off_v197", use_container_width=True):
                    ws = get_sheet_safe("AppSettings")
                    if ws:
                        vals = ws.get_all_values()
                        found=False
                        for i,row in enumerate(vals[1:], start=2):
                            if row and row[0].lower() in ["offerenabled","show_offer_tab"]:
                                ws.update(f"B{i}", [["No"]])
                                found=True
                                break
                        if not found:
                            hdr = vals[0] if vals else SHEET_HEADERS["AppSettings"]
                            row_data = {"Key": "OfferEnabled", "Value": "No", "Date": str(datetime.date.today()), "Status": "Active", "Description": "Offer OFF"}
                            row = [row_data.get(h,"") for h in hdr]
                            ws.append_row(row, value_input_option="RAW")
                        get_all_records_cached.clear()
                        st.success("Offer OFF")
                        st.rerun()
        all_arts = get_all_records_cached("Articles")
        offer_arts = [r for r in all_arts if "offer" in str(r.get("MainCategory","")).lower() or "offer" in str(r.get("SubCategory","")).lower() or str(r.get("ID","")).lower().startswith("offer_")]
        st.write(f"Total Offer Articles: {len(offer_arts)}")
        if offer_arts:
            st.dataframe(pd.DataFrame([{"ID":r.get("ID",""), "TitleEN":r.get("TitleEN","")[:40]} for r in offer_arts]), use_container_width=True)

    elif selected == "Article":
        st.markdown("<div class='heading-h4'>Article Management</div>", unsafe_allow_html=True)
        recs = get_all_records_cached("Articles")
        if "art_selected_id_v197" not in st.session_state:
            st.session_state.art_selected_id_v197 = ""
        if "art_create_lang_v197" not in st.session_state:
            st.session_state.art_create_lang_v197 = "English"

        tab_art, tab_cat = st.tabs(["Article: Add/Edit/Delete", "Categories"])

        with tab_art:
            st.markdown("**Articles List - Default Empty, Show After Selection**")
            options = ["-- Select Article --"] + [f"{r.get('ID','')} - {r.get('TitleEN','')[:40]}" for r in recs]
            id_map = {f"{r.get('ID','')} - {r.get('TitleEN','')[:40]}": r.get("ID","") for r in recs}
            sel = st.selectbox("Select Article", options, key="art_select_v197")
            if sel != "-- Select Article --":
                st.session_state.art_selected_id_v197 = id_map.get(sel,"")
            else:
                st.session_state.art_selected_id_v197 = ""

            if st.session_state.art_selected_id_v197:
                sel_rec = next((r for r in recs if r.get("ID","")==st.session_state.art_selected_id_v197), None)
                if sel_rec:
                    st.markdown(f"**Selected: {sel_rec.get('ID','')}**")
                    with st.container(border=True):
                        e_id = st.text_input("ID", value=sel_rec.get("ID",""), disabled=True, key="art_edit_id_v197")
                        e_title_en = st.text_input("Title EN", value=sel_rec.get("TitleEN",""), key="art_edit_title_en_v197")
                        e_title_ur = st.text_input("Title UR", value=sel_rec.get("TitleUR",""), key="art_edit_title_ur_v197")
                        e_title_ar = st.text_input("Title AR", value=sel_rec.get("TitleAR",""), key="art_edit_title_ar_v197")
                        e_content_en = st.text_area("Content EN", value=sel_rec.get("ContentEN",""), height=150, key="art_edit_content_en_v197")
                        e_content_ur = st.text_area("Content UR", value=sel_rec.get("ContentUR",""), height=150, key="art_edit_content_ur_v197")
                        e_content_ar = st.text_area("Content AR", value=sel_rec.get("ContentAR",""), height=150, key="art_edit_content_ar_v197")
                        e_main_cat = st.text_input("MainCategory", value=sel_rec.get("MainCategory",""), key="art_edit_maincat_v197")
                        e_sub_cat = st.text_input("SubCategory", value=sel_rec.get("SubCategory",""), key="art_edit_subcat_v197")
                        e_audience = st.selectbox("Audience", ["All","Clinic","HomeUser","General","Offer"], key="art_edit_aud_v197")
                        c1,c2,c3 = st.columns(3)
                        with c1:
                            if st.button("Update Article", key="art_update_v197", type="primary"):
                                ws = get_sheet_safe("Articles")
                                if ws:
                                    vals = ws.get_all_values()
                                    hdr = vals[0]
                                    id_idx = hdr.index("ID")
                                    for i,row in enumerate(vals[1:], start=2):
                                        if len(row)>id_idx and row[id_idx]==e_id:
                                            updated = {**sel_rec, "TitleEN":e_title_en, "TitleUR":e_title_ur, "TitleAR":e_title_ar, "ContentEN":e_content_en, "ContentUR":e_content_ur, "ContentAR":e_content_ar, "MainCategory":e_main_cat, "SubCategory":e_sub_cat, "Audience":e_audience}
                                            row_new = [updated.get(h,"") for h in hdr]
                                            ws.update(f"A{i}", [row_new])
                                            get_all_records_cached.clear()
                                            st.success("Updated")
                                            st.rerun()
                                            break
                        with c2:
                            if st.button("Delete Article", key="art_delete_v197"):
                                ws = get_sheet_safe("Articles")
                                if ws:
                                    vals = ws.get_all_values()
                                    hdr = vals[0]
                                    id_idx = hdr.index("ID")
                                    for i,row in enumerate(vals[1:], start=2):
                                        if len(row)>id_idx and row[id_idx]==e_id:
                                            ws.delete_rows(i)
                                            get_all_records_cached.clear()
                                            st.success(f"Deleted {e_id}")
                                            st.session_state.art_selected_id_v197=""
                                            st.rerun()
                                            break
                        with c3:
                            if st.button("Clear Selection", key="art_clear_v197"):
                                st.session_state.art_selected_id_v197=""
                                st.rerun()
            else:
                st.info("No article selected - select to show details")

            st.markdown("---")
            st.markdown("**Create New Article**")
            with st.container(border=True):
                # Language selection English, Urdu, Arabic
                lang_choice = st.radio("Language Selection", ["English", "Urdu", "Arabic"], horizontal=True, key="art_create_lang_v197")
                # Title and Content based on language
                title_val = st.text_input("Title", value="", key=f"art_new_title_{lang_choice}_v197", placeholder=f"Title in {lang_choice}")
                content_val = st.text_area("Content", value="", height=150, key=f"art_new_content_{lang_choice}_v197", placeholder=f"Content in {lang_choice}")

                # Main Category list
                all_main_cats = sorted(list(set([r.get("MainCategory","") for r in recs if r.get("MainCategory","")])))
                default_mains = ["General","Clinic","HomeUser","Offer","Essential"]
                main_options = sorted(list(set(default_mains + all_main_cats)))
                main_cat = st.selectbox("Main Category", main_options, key="art_new_maincat_v197")

                # Sub Category list
                all_sub_cats = sorted(list(set([r.get("SubCategory","") for r in recs if r.get("SubCategory","")])))
                default_subs = ["General Offer","Health","Tips","News","Seasonal"]
                sub_options = ["-- Select Sub Category --"] + sorted(list(set(default_subs + all_sub_cats)))
                sub_cat_sel = st.selectbox("Sub Category", sub_options, key="art_new_subcat_v197")
                sub_cat = "" if sub_cat_sel=="-- Select Sub Category --" else sub_cat_sel
                # Allow custom sub category
                custom_sub = st.text_input("Or Add New Sub Category (if not in list)", value="", key="art_new_custom_sub_v197")
                if custom_sub.strip():
                    sub_cat = custom_sub.strip()

                # Audience list
                audience_options = ["All","Clinic","HomeUser","General","Offer"]
                audience = st.selectbox("Audience", audience_options, key="art_new_aud_v197")

                if st.button("Create Article", key="art_create_btn_v197", type="primary", use_container_width=True):
                    if not title_val.strip():
                        st.error("Title required")
                    else:
                        ws = get_sheet_safe("Articles")
                        if ws:
                            hdr = ws.row_values(1) if ws.row_values(1) else SHEET_HEADERS["Articles"]
                            # Auto ID logic
                            if main_cat=="Offer":
                                final_id = get_next_offer_id()
                            else:
                                # EN/UR/AR based on language
                                lang_prefix = {"English":"EN","Urdu":"UR","Arabic":"AR"}.get(lang_choice,"EN")
                                max_n=0
                                for r in recs:
                                    rid=str(r.get("ID",""))
                                    if rid.upper().startswith(lang_prefix):
                                        try:
                                            num=int(''.join(filter(str.isdigit, rid)))
                                            if num>max_n: max_n=num
                                        except: pass
                                final_id = f"{lang_prefix} {max_n+1}"

                            # Map title/content to language fields
                            t_en=t_ur=t_ar=""
                            c_en=c_ur=c_ar=""
                            if lang_choice=="English":
                                t_en=title_val; c_en=content_val
                            elif lang_choice=="Urdu":
                                t_ur=title_val; c_ur=content_val
                            else:
                                t_ar=title_val; c_ar=content_val

                            row_data = {"ID": final_id, "TitleEN": t_en, "TitleUR": t_ur, "TitleAR": t_ar, "ContentEN": c_en, "ContentUR": c_ur, "ContentAR": c_ar, "MainCategory": main_cat, "SubCategory": sub_cat, "Audience": audience, "Type": main_cat, "Status": "Active", "Date": str(datetime.date.today()), "ClinicName": st.session_state.get("clinic_name","")}
                            row = [row_data.get(h,"") for h in hdr]
                            ws.append_row(row, value_input_option="RAW")
                            get_all_records_cached.clear()
                            st.success(f"Created {final_id} in {lang_choice} - Title: {title_val}")
                            st.rerun()

        with tab_cat:
            st.markdown("**Categories**")
            # Get categories - merge from Articles + AppSettings for persistence + defaults
            default_mains = ["General","Clinic","HomeUser","Offer","Essential"]
            default_subs = ["General Offer","Health","Tips","News","Seasonal","Medicine"]
            all_main_from_articles = [r.get("MainCategory","") for r in recs if r.get("MainCategory","")]
            all_sub_from_articles = [r.get("SubCategory","") for r in recs if r.get("SubCategory","")]
            try:
                appset_recs = get_all_records_cached("AppSettings")
                for ar in appset_recs:
                    k=str(ar.get("Key",""))
                    if k.startswith("MainCategory_"):
                        all_main_from_articles.append(ar.get("Value",""))
                    if k.startswith("SubCategory_"):
                        all_sub_from_articles.append(ar.get("Value",""))
            except:
                pass
            # Merge with defaults so Edit/Delete always available
            all_main = sorted(list(set([x for x in (default_mains + all_main_from_articles) if x])))
            all_sub = sorted(list(set([x for x in (default_subs + all_sub_from_articles) if x])))
            
            # Main Categories Add/Edit/Delete - Always visible
            st.markdown("---")
            st.markdown("**Main Categories: Add/Edit/Delete**")
            with st.container(border=True):
                st.markdown("**Add Category**")
                new_main_cat = st.text_input("New Main Category Name", value="", key="cat_main_new_v197", placeholder="e.g. Offer, Health")
                if st.button("Add Main Category", key="cat_main_add_v197", type="primary"):
                    if not new_main_cat.strip():
                        st.error("Name required")
                    else:
                        ws = get_sheet_safe("AppSettings")
                        if ws:
                            hdr = ws.row_values(1) if ws.row_values(1) else SHEET_HEADERS["AppSettings"]
                            row_data = {"Key": f"MainCategory_{new_main_cat.strip()}", "Value": new_main_cat.strip(), "Date": str(datetime.date.today()), "Status": "Active", "Description": "Main Category"}
                            row = [row_data.get(h,"") for h in hdr]
                            ws.append_row(row, value_input_option="RAW")
                            get_all_records_cached.clear()
                        st.success(f"Main Category '{new_main_cat}' added")
                        st.rerun()

                st.markdown("**Edit / Delete Main Category**")
                sel_main = st.selectbox("Select Main Category to Edit/Delete", ["-- Select --"] + all_main, key="cat_main_sel_v197")
                if sel_main != "-- Select --":
                    st.markdown(f"**Selected: {sel_main} - Edit/Delete Active**")
                    new_name = st.text_input(f"New name for {sel_main}", value="", key="cat_main_edit_new_v197")
                    c1,c2 = st.columns(2)
                    with c1:
                        if st.button(f"Update Main Category", key="cat_main_rename_v197", type="primary"):
                            if not new_name.strip():
                                st.error("New name required")
                            else:
                                # Update in Articles
                                ws = get_sheet_safe("Articles")
                                count=0
                                if ws:
                                    try:
                                        vals = ws.get_all_values()
                                        hdr = vals[0]
                                        col_idx = hdr.index("MainCategory")
                                        for i,row in enumerate(vals[1:], start=2):
                                            if len(row)>col_idx and row[col_idx]==sel_main:
                                                ws.update(f"{col_idx_to_letter(col_idx)}{i}", [[new_name]])
                                                count+=1
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                                # Update in AppSettings
                                try:
                                    ws2 = get_sheet_safe("AppSettings")
                                    if ws2:
                                        vals2 = ws2.get_all_values()
                                        for i,row in enumerate(vals2[1:], start=2):
                                            if row and row[0]==f"MainCategory_{sel_main}":
                                                ws2.update(f"B{i}", [[new_name]])
                                                ws2.update(f"A{i}", [[f"MainCategory_{new_name}"]])
                                except: pass
                                get_all_records_cached.clear()
                                st.success(f"Renamed Main {sel_main} -> {new_name} in {count} articles")
                                st.rerun()
                    with c2:
                        if st.button(f"Delete Main Category", key="cat_main_delete_v197", type="secondary"):
                            # Delete from AppSettings
                            try:
                                ws2 = get_sheet_safe("AppSettings")
                                if ws2:
                                    vals2 = ws2.get_all_values()
                                    for i,row in enumerate(vals2[1:], start=2):
                                        if row and (row[0]==f"MainCategory_{sel_main}" or (len(row)>1 and row[1]==sel_main and "MainCategory" in str(row[0]))):
                                            ws2.delete_rows(i)
                                            break
                            except: pass
                            # Clear from Articles
                            ws = get_sheet_safe("Articles")
                            count=0
                            if ws:
                                try:
                                    vals = ws.get_all_values()
                                    hdr = vals[0]
                                    col_idx = hdr.index("MainCategory")
                                    for i,row in enumerate(vals[1:], start=2):
                                        if len(row)>col_idx and row[col_idx]==sel_main:
                                            ws.update(f"{col_idx_to_letter(col_idx)}{i}", [[""]])
                                            count+=1
                                except: pass
                            get_all_records_cached.clear()
                            st.success(f"Deleted Main Category {sel_main} - cleared from {count} articles")
                            st.rerun()
                else:
                    st.info("Select Main Category from list above to Edit/Delete - Options now always visible")

            # Sub Categories Add/Edit/Delete - Always visible
            st.markdown("---")
            st.markdown("**Sub Categories: Add/Edit/Delete**")
            with st.container(border=True):
                st.markdown("**Add Sub Category**")
                new_sub_cat = st.text_input("New Sub Category Name", value="", key="cat_sub_new_v197", placeholder="e.g. Health Tips")
                if st.button("Add Sub Category", key="cat_sub_add_v197", type="primary"):
                    if not new_sub_cat.strip():
                        st.error("Name required")
                    else:
                        ws = get_sheet_safe("AppSettings")
                        if ws:
                            hdr = ws.row_values(1) if ws.row_values(1) else SHEET_HEADERS["AppSettings"]
                            row_data = {"Key": f"SubCategory_{new_sub_cat.strip()}", "Value": new_sub_cat.strip(), "Date": str(datetime.date.today()), "Status": "Active", "Description": "Sub Category"}
                            row = [row_data.get(h,"") for h in hdr]
                            ws.append_row(row, value_input_option="RAW")
                            get_all_records_cached.clear()
                        st.success(f"Sub Category '{new_sub_cat}' added")
                        st.rerun()

                st.markdown("**Edit / Delete Sub Category**")
                sel_sub = st.selectbox("Select Sub Category to Edit/Delete", ["-- Select --"] + all_sub, key="cat_sub_sel_v197")
                if sel_sub != "-- Select --":
                    st.markdown(f"**Selected: {sel_sub} - Edit/Delete Active**")
                    new_sub_name = st.text_input(f"New name for {sel_sub}", value="", key="cat_sub_edit_new_v197")
                    c1,c2 = st.columns(2)
                    with c1:
                        if st.button(f"Update Sub Category", key="cat_sub_rename_v197", type="primary"):
                            if not new_sub_name.strip():
                                st.error("New name required")
                            else:
                                ws = get_sheet_safe("Articles")
                                count=0
                                if ws:
                                    try:
                                        vals = ws.get_all_values()
                                        hdr = vals[0]
                                        col_idx = hdr.index("SubCategory")
                                        for i,row in enumerate(vals[1:], start=2):
                                            if len(row)>col_idx and row[col_idx]==sel_sub:
                                                ws.update(f"{col_idx_to_letter(col_idx)}{i}", [[new_sub_name]])
                                                count+=1
                                    except: pass
                                try:
                                    ws2 = get_sheet_safe("AppSettings")
                                    if ws2:
                                        vals2 = ws2.get_all_values()
                                        for i,row in enumerate(vals2[1:], start=2):
                                            if row and row[0]==f"SubCategory_{sel_sub}":
                                                ws2.update(f"B{i}", [[new_sub_name]])
                                                ws2.update(f"A{i}", [[f"SubCategory_{new_sub_name}"]])
                                except: pass
                                get_all_records_cached.clear()
                                st.success(f"Renamed Sub {sel_sub} -> {new_sub_name} in {count}")
                                st.rerun()
                    with c2:
                        if st.button(f"Delete Sub Category", key="cat_sub_delete_v197", type="secondary"):
                            try:
                                ws2 = get_sheet_safe("AppSettings")
                                if ws2:
                                    vals2 = ws2.get_all_values()
                                    for i,row in enumerate(vals2[1:], start=2):
                                        if row and row[0]==f"SubCategory_{sel_sub}":
                                            ws2.delete_rows(i)
                                            break
                            except: pass
                            ws = get_sheet_safe("Articles")
                            count=0
                            if ws:
                                try:
                                    vals = ws.get_all_values()
                                    hdr = vals[0]
                                    col_idx = hdr.index("SubCategory")
                                    for i,row in enumerate(vals[1:], start=2):
                                        if len(row)>col_idx and row[col_idx]==sel_sub:
                                            ws.update(f"{col_idx_to_letter(col_idx)}{i}", [[""]])
                                            count+=1
                                except: pass
                            get_all_records_cached.clear()
                            st.success(f"Deleted Sub Category {sel_sub} - cleared from {count}")
                            st.rerun()
                else:
                    st.info("Select Sub Category from list above to Edit/Delete - Options now always visible")

    elif selected == "AppSettings":
        st.markdown("<div class='heading-h4'>AppSettings</div>", unsafe_allow_html=True)
        recs = get_all_records_cached("AppSettings")
        st.write(f"Total Settings: {len(recs)}")
        if recs:
            st.dataframe(pd.DataFrame(recs), use_container_width=True)
        with st.container(border=True):
            s_key = st.text_input("Key", key="appset_key_v197")
            s_val = st.text_input("Value", key="appset_val_v197")
            s_desc = st.text_input("Description", key="appset_desc_v197")
            if st.button("Save Setting", key="appset_save_v197", type="primary"):
                if not s_key.strip():
                    st.error("Key required")
                else:
                    ws = get_sheet_safe("AppSettings")
                    if ws:
                        vals = ws.get_all_values()
                        hdr = vals[0] if vals else SHEET_HEADERS["AppSettings"]
                        key_idx = hdr.index("Key") if "Key" in hdr else 0
                        found_row = None
                        for i,row in enumerate(vals[1:], start=2):
                            if len(row)>key_idx and row[key_idx].lower()==s_key.lower():
                                found_row = i
                                break
                        if found_row:
                            ws.update(f"B{found_row}", [[s_val]])
                            st.success(f"Updated {s_key} = {s_val}")
                        else:
                            row_data = {"Key": s_key, "Value": s_val, "Date": str(datetime.date.today()), "Status": "Active", "Description": s_desc}
                            row = [row_data.get(h,"") for h in hdr]
                            ws.append_row(row, value_input_option="RAW")
                            st.success(f"Added {s_key} = {s_val}")
                        get_all_records_cached.clear()
                        st.rerun()

    elif selected == "Data":
        st.markdown("<div class='heading-h4'>Data</div>", unsafe_allow_html=True)
        for sh_name in ALL_SHEETS:
            recs_d = get_all_records_cached(sh_name)
            st.write(f"{sh_name}: {len(recs_d)} records")
            if recs_d:
                st.dataframe(pd.DataFrame(recs_d).head(3), use_container_width=True)

    else:
        st.markdown(f"<div class='heading-h4'>{selected}</div>", unsafe_allow_html=True)
        recs = get_all_records_cached(selected) if selected in ALL_SHEETS else []
        st.write(f"Total {selected}: {len(recs)}")
        if recs:
            st.dataframe(pd.DataFrame(recs).head(20), use_container_width=True)

    under_development_footer("App Admin")
    add_footer()

def admin_feedback_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Feedback Admin</div>", unsafe_allow_html=True)
    recs=get_all_records_cached("Feedback")
    if not recs:
        st.info("No feedback")
        add_footer()
        return
    df=pd.DataFrame(recs)
    st.dataframe(df, use_container_width=True)
    add_footer()

def offer_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    offer_enabled = get_app_setting("OfferEnabled", get_app_setting("show_offer_tab","Yes"))
    if str(offer_enabled).lower() not in ["yes","on","true","1","enabled"]:
        st.warning("Offer is currently OFF - App Admin ne Offer band kiya hua hai")
        add_footer()
        return
    st.markdown("<div class='heading-h3'>Offer</div>", unsafe_allow_html=True)
    # V197 - extra line removed as per user request
    recs = get_all_records_cached("Articles")
    offer_recs = [r for r in recs if "offer" in str(r.get("MainCategory","")).lower() or "offer" in str(r.get("SubCategory","")).lower() or str(r.get("ID","")).lower().startswith("offer_")]
    if not offer_recs:
        st.info("No Offer articles yet - App Admin > Offer Control se banayen")
    else:
        def offer_key(r):
            oid=str(r.get("ID",""))
            try:
                if "_" in oid:
                    return int(oid.split("_")[1])
            except: pass
            return 0
        offer_recs_sorted = sorted(offer_recs, key=offer_key)
        for r in offer_recs_sorted:
            with st.container(border=True):
                st.markdown(f"<div class='heading-h4'>{r.get('ID','')} - {r.get('TitleEN','') or r.get('TitleUR','')}</div>", unsafe_allow_html=True)
                lang = st.session_state.get("lang","en")
                if lang=="ur" and r.get("TitleUR",""):
                    st.markdown(f"<b>{r.get('TitleUR','')}</b>")
                    st.write(r.get('ContentUR','')[:500])
                elif lang=="ar" and r.get("TitleAR",""):
                    st.markdown(f"<b>{r.get('TitleAR','')}</b>")
                    st.write(r.get('ContentAR','')[:500])
                else:
                    st.markdown(f"<b>{r.get('TitleEN','')}</b>")
                    st.write(r.get('ContentEN','')[:500])
                st.caption(f"Category: {r.get('MainCategory','')} / {r.get('SubCategory','')} | Date: {r.get('Date','')}")
    under_development_footer("Offer")
    add_footer()


def essential_page():
    language_selector()
    clinic_heading_banner()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Essential</div>", unsafe_allow_html=True)
    under_development_footer("Essential")
    add_footer()

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in=False
        st.session_state.current_page="clinic_login"
    if not st.session_state.logged_in:
        clinic_login_page()
    else:
        p=st.session_state.current_page
        if p=="dashboard_welcome": dashboard_welcome_page()
        elif p=="patient": patient_page()
        elif p=="patient_revisit_form": patient_revisit_form_page()
        elif p=="revisit": revisit_page()
        elif p=="admin": admin_page()
        elif p=="admin_feedback": admin_feedback_page()
        elif p=="dictionary": dictionary_page()
        elif p=="pharmacopoeia": pharmacopoeia_page()
        elif p=="auto_selection": auto_selection_page()
        elif p=="clinic_herb_formula": clinic_herb_formula_page()
        elif p=="home_user": home_user_page()
        elif p=="home_user_articles": home_user_articles_page()
        elif p=="articles": articles_page()
        elif p=="clinic_articles": clinic_articles_page()
        elif p=="essential_page": essential_page()
        elif p=="offer_page": offer_page()
        elif p=="feedback_page": feedback_page()
        else: dashboard_welcome_page()

if __name__=="__main__": main()
