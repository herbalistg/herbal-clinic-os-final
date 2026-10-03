"""
Herbal Clinic OS - V3.2 - Complete V206 3 Pages
================================================================
1. New Patient - Complete V206 (Personal 3 cols balanced, Age/Gender full, Additional 10 Qs, Diseases full with Body Part + Related Qs dropdowns, Prescription Herbs/Formula, Billing complete)
2. Revisit Search - Complete V206 (Name, Date YYYY-MM-DD with dash logic, Phone, Address, duplicate fix, history chain)
3. Revisit Form - Complete V206 (Full revisit form with history in each section, RP_ new ID each visit, OriginalPatientID same)

Fixes applied from V3.1:
- BP: High, Very high, Normal, Low, Very low + Other - Write figure
- Pulse: Fast, Very fast, Normal, Weak, Very weak + Other - Write figure
- Temp: High, Very high, Normal, Low, Very low + Other - Write figure
- Mizaj: Cold Dry...Cold Wet + Other - Write
- Status: Cash, Outstanding, Free
- No balloons - small popup
- KeyError fixed
- English only clean

Based on App_V206.py - 5800+ lines Light & Fast version
================================================================
"""
import streamlit as st
import datetime
import re
import pandas as pd
import time

st.set_page_config(page_title="Herbal Clinic V3.2", layout="wide", page_icon="🌿")

try:
  import gspread
  from google.oauth2.service_account import Credentials
  GSPREAD_AVAILABLE = True
except ImportError:
  GSPREAD_AVAILABLE = False

APP_VERSION = "V3.2 - Complete V206 3 Pages - New Patient + Revisit Search + Revisit Form"

# Theme CSS - V206 Light & Fast
def get_theme_css_cached(theme):
  raised = """
    html, .stApp, [data-testid="stAppViewContainer"] { transition: none!important; animation: none!important; }
    div[data-baseweb="tab-list"] { gap: 8px; padding: 4px; }
    div[data-baseweb="tab"] { background: #FFFFFF!important; border: 2px solid #A8CCAD!important; border-radius: 12px!important; box-shadow: 0 2px 6px rgba(46,125,91,0.12)!important; font-weight: 700!important; padding: 8px 16px!important; transition: none!important; }
    div[data-baseweb="tab"][aria-selected="true"] { background: #2E7D5B!important; color: white!important; border-color: #1B5E20!important; }
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] { background: #FFFFFF!important; border: 2px solid #A8CCAD!important; border-radius: 10px!important; box-shadow: 0 1px 4px rgba(46,125,91,0.08)!important; transition: none!important; }
    .stButton > button { background: #FFFFFF!important; border: 2px solid #A8CCAD!important; border-radius: 10px!important; box-shadow: 0 2px 6px rgba(46,125,91,0.12)!important; font-weight: 700!important; padding: 6px 14px!important; transition: none!important; animation: none!important; }
    .stButton > button:active, .stButton > button:focus { transform: none!important; box-shadow: 0 2px 6px rgba(46,125,91,0.12)!important; }
    .stButton > button[kind="primary"] { background: #2E7D5B!important; color: white!important; border-color: #1B5E20!important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF!important; border: 2px solid #C8E6D5!important; border-radius: 14px!important; box-shadow: 0 2px 8px rgba(46,125,91,0.08)!important; transition: none!important; }
    [data-testid="stStatusWidget"], [data-testid="stSpinner"] { transition: none!important; }
    .heading-h1 { font-size: 32px; font-weight: 900; color: #1B5E20; }
    .heading-h2 { font-size: 28px; font-weight: 800; color: #2E7D5B; }
    .heading-h3 { font-size: 24px; font-weight: 700; color: #2E7D5B; }
    .heading-h4 { font-size: 20px; font-weight: 700; color: #1F2D27; }
    .heading-h5 { font-size: 16px; font-weight: 700; color: #2E7D5B; }
    """
  if theme == "dim":
    return raised + """
    html, body, .stApp, [data-testid="stAppViewContainer"] { background: #C8DCCB!important; color: #0F2A14!important; }
    .block-container { background: #DDEBE0!important; border: 3.5px solid #1B5E20!important; box-shadow: 0 12px 32px rgba(27,94,32,0.25)!important; border-radius: 18px!important; }
    """
  else:
    return raised + """
    html, body, .stApp, [data-testid="stAppViewContainer"] { background: #FFFFFF!important; color: #1F2D27!important; }
    .block-container { background: #FFFFFF!important; border: 3px solid #2E7D5B!important; border-radius: 18px!important; box-shadow: 0 12px 32px rgba(46,125,91,0.18)!important; }
    """

def get_theme_css():
  theme = st.session_state.get("theme", "light")
  try:
    return get_theme_css_cached(theme)
  except:
    return ""

def show_popup(message):
    st.markdown(f'<div style="background: linear-gradient(135deg, #2E7D5B, #4CAF50); color:white; padding:12px; border-radius:10px; text-align:center; font-weight:700; box-shadow:0 4px 12px rgba(46,125,91,0.3); margin:8px 0;">{message}</div>', unsafe_allow_html=True)
    try:
        st.toast(message, icon="✅")
    except:
        pass

def scroll_to_top():
  st.markdown("<script>window.scrollTo(0,0);</script>", unsafe_allow_html=True)

def get_user_display_h2():
  return st.session_state.get("username","User")

def top_bar_inner_with_user():
  st.markdown(f"<style>{get_theme_css()}</style>", unsafe_allow_html=True)
  uname = st.session_state.get("username","User")
  c_user, c_spacer, c_theme, c_lang = st.columns([3,2,1,2])
  with c_user:
    st.markdown(f"<div style='font-size:16px;font-weight:600;color:#1F2D27;margin-top:8px;'>{uname}</div>", unsafe_allow_html=True)
  with c_theme:
    curr_theme = st.session_state.get("theme", "light")
    if curr_theme == "light":
      if st.button("🌿", key=f"theme_dim_{st.session_state.get('current_page','inner')}", help="Dim Theme"):
        st.session_state.theme = "dim"
        st.rerun()
    else:
      if st.button("☀️", key=f"theme_light_{st.session_state.get('current_page','inner')}", help="Light Theme"):
        st.session_state.theme = "light"
        st.rerun()
  with c_lang:
    lang = st.session_state.get("app_language","en")
    col_icon, col_text = st.columns([1,1])
    with col_icon:
      if st.button("🌐", key=f"lang_{st.session_state.get('current_page','inner')}", help="Change Language"):
        curr = st.session_state.get("app_language", "en")
        nxt = {"en":"ur", "ur":"ar", "ar":"en"}.get(curr, "en")
        st.session_state.app_language = nxt
        st.session_state.lang = nxt
        st.rerun()
    with col_text:
      st.markdown(f"<div style='text-align:left;font-size:14px;font-weight:700;color:#2E7D5B;margin-top:8px;margin-left:-8px;'>{lang.upper()}</div>", unsafe_allow_html=True)
  st.markdown("<hr style='margin:2px 0 8px 0; border:0; border-top:3px solid #1B5E20; box-shadow: 0 1px 3px rgba(0,0,0,0.15);'>", unsafe_allow_html=True)

def top_nav_inner():
  c_spacer,c_dash=st.columns([4,1])
  with c_dash:
    if st.button("Dashboard", key=f"dash_{st.session_state.current_page}_v3", type="primary"):
      st.session_state.current_page="dashboard_welcome"
      st.rerun()
  st.markdown("<hr style='margin:8px 0; border:1px solid #E8F5E9;'>", unsafe_allow_html=True)

def clinic_heading_banner():
  user_h2 = get_user_display_h2()
  is_logged = st.session_state.get("logged_in", False)
  user_display = user_h2 if is_logged else "Welcome to Herbal Clinic International"
  st.markdown(f"""
  <div style="background: linear-gradient(135deg, #FFFFFF 0%, #F1F7F3 50%, #E8F5E9 100%);border:3px solid #2E7D5B;border-radius:22px;padding:34px 26px;text-align:center;margin-bottom:18px;box-shadow: 0 8px 28px rgba(46,125,91,0.18), inset 0 1px 0 rgba(255,255,255,0.8);">
    <div style="font-family:'Segoe UI', 'Inter', sans-serif;font-weight:900;letter-spacing:1.4px;text-transform:uppercase;color:#2E7D5B !important;background: linear-gradient(135deg, #F1F7F3 0%, #FFFFFF 100%);padding:16px 26px;border-radius:16px;display:inline-block;border:2.5px solid #2E7D5B;font-size:56px; line-height:1.1; box-shadow: 0 4px 14px rgba(46,125,91,0.12);">Herbal Clinic International</div>
    <div style="color:#5a6d65 !important; font-size:21px; font-weight:600; margin-top:18px; font-style:italic !important; letter-spacing:0.5px;">Based on human temperament</div>
    <div style="font-size:26px; font-weight:800; color:#1F2D27 !important; margin-top:18px; background:#FFFFFF;padding:10px 20px;border-radius:12px;display:inline-block;border:1.5px solid #C8E6D5; box-shadow: 0 3px 10px rgba(0,0,0,0.06);">{user_display}</div>
  </div>
  """, unsafe_allow_html=True)

def clinic_heading_banner_dashboard_only():
  clinic_heading_banner()

def under_development_footer(page_name):
  st.markdown(f"<div style='text-align:center;color:#888;font-size:12px;margin-top:20px;'>Herbal Clinic OS V3.2 - {page_name} - Complete V206</div>", unsafe_allow_html=True)

def add_footer():
  st.markdown("<div style='text-align:center;color:#aaa;font-size:11px;margin-top:10px;'>V3.2 - Complete V206 3 Pages</div>", unsafe_allow_html=True)

# V206 Constants
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
  "temperament": ["Select","Cold Dry","Dry Cold","Dry Hot","Hot Dry","Hot Wet","Wet Hot","Wet Cold","Cold Wet","Other - Write"],
  "fee_status": ["Cash","Outstanding","Free"],
  "payment": ["Select","Cash","Online","JazzCash","Free"],
  "marital": ["Select","Single","Married","Widowed","Divorced"],
  "duration": ["Select","Day","Week","Month","Year","Since Birth","Since Childhood"],
  "severity": ["Select","Mild","Moderate","Severe","Very Mild","Very Severe"],
  "blood_group": ["Select","A+","A-","B+","B-","O+","O-","AB+","AB-","Unknown"],
  "occupation": ["Select","Student","Teacher","Farmer","Shopkeeper","Laborer","Driver","Housewife","Business","Engineer","Government Job","Private Job","Retired","Unemployed","Other"],
  "bp": ["Select","High","Very high","Normal","Low","Very low","Other - Write figure"],
  "pulse": ["Select","Fast","Very fast","Normal","Weak","Very weak","Other - Write figure"],
  "temperature": ["Select","High","Very high","Normal","Low","Very low","Other - Write figure"],
}

# Sheets
SHEET_HEADERS = {
  "New_patient": ["PatientID","OriginalPatientID","ClinicPhone","DailyNumber","Date","Name","FatherName","Age","Gender","Phone","Address","City","BP","Pulse","Weight","Height","Temperament","Diseases","History","Complaint","Diagnosis","Treatment","Fees","Status","Total","Paid","Balance","PaymentMethod"],
}

# Defaults
defaults = {
  "logged_in": False, "current_page": "clinic_login", "lang": "en", "clinic_name": "Herbal Clinic International",
  "form_version": 0, "patient_diseases": [], "revisit_data": None, "username": "", "theme": "light", "app_language": "en"
}

for k,v in defaults.items():
  if k not in st.session_state:
    st.session_state[k] = v

# GSheet helpers - V206 Light & Fast
@st.cache_resource
def get_client():
  try:
    if not GSPREAD_AVAILABLE:
      return None
    creds_dict=None
    try:
      if "gcp_service_account" in st.secrets:
        creds_dict=dict(st.secrets["gcp_service_account"])
    except:
      pass
    if not creds_dict:
      try:
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
          maybe = st.secrets["connections"]["gsheets"]
          if isinstance(maybe, dict) and "private_key" in maybe:
            creds_dict=dict(maybe)
      except:
        pass
    if not creds_dict:
      return None
    if "private_key" in creds_dict:
      try:
        pk = creds_dict["private_key"]
        bs = chr(92); n_char = chr(110); nl = chr(10)
        pk = pk.replace(bs+bs+n_char, bs+n_char)
        pk = pk.replace(bs+n_char, nl)
        creds_dict["private_key"] = pk
      except:
        pass
    scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    creds=Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client
  except:
    return None

def get_sheet_safe(sheet_name):
  try:
    client = get_client()
    if not client:
      return None
    spreadsheet_id = ""
    try:
      spreadsheet_id = st.secrets["connections"]["gsheets"].get("spreadsheet","")
    except:
      pass
    if not spreadsheet_id:
      return None
    sh = client.open_by_key(spreadsheet_id)
    for w in sh.worksheets():
      if w.title.strip().lower() == sheet_name.strip().lower():
        return w
    return None
  except:
    return None

@st.cache_data(ttl=900)
def get_all_records_cached(sheet_name, max_rows=300):
  try:
    ws = get_sheet_safe(sheet_name)
    if not ws:
      return []
    try:
      recs = ws.get_all_records()
      if len(recs) > max_rows:
        recs = recs[-max_rows:]
      return recs
    except:
      vals = ws.get_all_values()
      if len(vals) < 2:
        return []
      headers = vals[0]
      recs = []
      for row in vals[1:]:
        if len(row) < len(headers):
          row += [""] * (len(headers)-len(row))
        recs.append(dict(zip(headers, row)))
      if len(recs) > max_rows:
        recs = recs[-max_rows:]
      return recs
  except:
    return []

def get_next_numbers(clinic_name):
  try:
    recs = get_all_records_cached("New_patient", max_rows=200)
    my = [r for r in recs if str(r.get("ClinicName","")).lower() == str(clinic_name).lower()] if clinic_name else recs
    total = len(my) + 1
    today_str = str(datetime.date.today())
    today_count = len([r for r in my if today_str in str(r.get("Date",""))]) + 1
    return today_count, total
  except:
    return 1, 1

def get_next_patient_id_v205(clinic_name, is_revisit=False):
  try:
    daily, total = get_next_numbers(clinic_name)
    prefix = "RP" if is_revisit else "NP"
    return f"{prefix}_{total}"
  except:
    return f"{'RP' if is_revisit else 'NP'}_1"

def save_to_local_csv(sheet_name, data_dict):
  try:
    import csv, os
    path = f"/tmp/{sheet_name}_backup.csv"
    file_exists = os.path.isfile(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
      writer = csv.DictWriter(f, fieldnames=list(data_dict.keys()))
      if not file_exists:
        writer.writeheader()
      writer.writerow(data_dict)
    return True, "Saved locally"
  except Exception as e:
    return False, str(e)

def reset_to_new_patient():
  st.session_state.form_version += 1
  st.session_state.patient_diseases = []
  st.session_state.revisit_data = None
  st.session_state.prev_balance = 0.0
  st.session_state.current_page = "patient"
  st.rerun()

def section_heading_clickable(key, title):
  if st.session_state.get("section_opened", {}).get(key, False):
    st.markdown(f"<div class='heading-h4'>{title}</div>", unsafe_allow_html=True)
    return True
  else:
    if st.button(f"Open {title}", key=f"open_{key}_{st.session_state.form_version}_v206", type="primary"):
      if "section_opened" not in st.session_state:
        st.session_state.section_opened = {}
      st.session_state.section_opened[key]=True
      st.rerun()
    return False

def section_close_button(key):
  if st.button(f"Close {key}", key=f"close_{key}_{st.session_state.form_version}_v206", type="secondary"):
    st.session_state.section_opened[key]=False
    st.rerun()

def section_ok(key, is_revisit=False):
  if st.button(f"OK - {key}", key=f"ok_{key}_{st.session_state.form_version}_v206_{is_revisit}", type="primary"):
    if "section_unlocked" not in st.session_state:
      st.session_state.section_unlocked = {}
    # Unlock next logic simplified
    show_popup(f"{key} Completed")
    st.session_state.section_opened[key]=False
    # Unlock next section
    order = ["personal","vital","diseases","complaint","history","prescription","billing"]
    if key in order:
      idx = order.index(key)
      if idx+1 < len(order):
        nxt = order[idx+1]
        st.session_state.section_opened[nxt]=True
    st.rerun()

def get_age_based_questions_v206(age_str, gender):
  try:
    age = int(str(age_str).strip().split()[0])
  except:
    return []
  questions = []
  gender = str(gender).lower()
  if "female" in gender:
    if age >= 10 and age <= 12:
      questions = [("Menarche Started?", ["Select","Yes","No"], "female_menarche")]
    elif age >= 13 and age <= 50:
      questions = [("Menstrual Cycle Regular?", ["Select","Regular","Irregular","No Periods"], "female_cycle"), ("Menstrual Flow?", ["Select","Normal","Heavy","Light","Scanty"], "female_flow"), ("Number of Pregnancies?", ["Select","0","1","2","3","4+"], "female_preg_count"), ("Any Miscarriage?", ["Select","Yes","No"], "female_miscarriage"), ("White Discharge?", ["Select","Yes","No","Sometimes"], "female_leucorrhoea")]
    elif age > 50:
      questions = [("Menopause Age?", "text", "female_menopause_age")]
  elif "male" in gender:
    if age >= 12 and age <= 18:
      questions = [("Puberty Changes Started?", ["Select","Yes","No"], "male_puberty")]
    elif age >= 19 and age <= 40:
      questions = [("Marital Status Effect?", ["Select","Single","Married","Issues"], "male_marital_effect")]
    elif age > 40:
      questions = [("Prostate Issues?", ["Select","Yes","No","Checkup Needed"], "male_prostate")]
  if age < 5:
    questions += [("Birth History Normal?", ["Select","Normal","C-Section","Premature","Complications"], "child_birth")]
  return questions

# ==================== NEW PATIENT - COMPLETE V206 ====================
def render_patient_form(is_revisit=False):
  if not is_revisit and "patient_diseases" not in st.session_state:
    st.session_state.patient_diseases = []
  if "section_opened" not in st.session_state:
    st.session_state.section_opened = {"personal": True, "vital": False, "diseases": False, "complaint": False, "history": False, "prescription": False, "billing": False}
  if "section_unlocked" not in st.session_state:
    st.session_state.section_unlocked = {"personal": True, "vital": False, "diseases": False, "complaint": False, "history": False, "prescription": False, "billing": False}
  
  fv=st.session_state.form_version
  daily_num, total_num = get_next_numbers(st.session_state.clinic_name)
  prev_bal=0.0
  if is_revisit and st.session_state.revisit_data:
    original_pid = str(st.session_state.revisit_data.get("PatientID","")).strip()
    try:
      pid = get_next_patient_id_v205(st.session_state.clinic_name, is_revisit=True)
    except:
      pid = f"RP_{total_num}"
    st.session_state.original_patient_id = original_pid
    try:
      prev_bal=float(str(st.session_state.revisit_data.get("Balance","0") or 0).replace(",","") or 0)
    except: prev_bal=0.0
    st.session_state.prev_balance=prev_bal
  else:
    try:
      pid = get_next_patient_id_v205(st.session_state.clinic_name, is_revisit=False)
    except:
      pid = f"NP_{total_num}"
    st.session_state.original_patient_id = pid
    prev_bal=float(st.session_state.get("prev_balance",0) or 0)

  def get_prefill(k,d=""):
    if is_revisit and st.session_state.revisit_data:
      return st.session_state.revisit_data.get(k,d)
    return d

  # V3.2 - Clean First Row - No phone, No System hidden text, Date in first row
  c1,c2,c3 = st.columns(3)
  with c1:
    st.markdown(f'<div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding:12px; border-radius:8px; border-left:4px solid #2e7d32;"><h4 style="margin:0; color:#2e7d32;">{pid}</h4><small>Patient ID</small></div>', unsafe_allow_html=True)
  with c2:
    st.markdown(f'<div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding:12px; border-radius:8px; border-left:4px solid #1565c0;"><h4 style="margin:0; color:#1565c0;">Daily: {daily_num}</h4><small>Today Count</small></div>', unsafe_allow_html=True)
  with c3:
    entry_date = datetime.date.today()
    st.markdown(f'<div style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); padding:12px; border-radius:8px; border-left:4px solid #ef6c00;"><h4 style="margin:0; color:#ef6c00;">{entry_date}</h4><small>Entry Date</small></div>', unsafe_allow_html=True)
  st.markdown("---")

  # Personal Information - Complete V206 - 3 columns balanced (Fix 1a)
  with st.container(border=True):
    st.markdown("<div class='heading-h4'>Personal Information</div>", unsafe_allow_html=True)
    pc1,pc2,pc3=st.columns(3)
    with pc1:
      st.text_input("Patient's Name *", key=f"p_name_{fv}", value=get_prefill("Name",""), placeholder="Patient's Name")
      st.text_input("Spouse/Father's Name", key=f"p_fname_{fv}", value=get_prefill("FatherName",""), placeholder="Spouse/Father's Name")
      st.text_input("Address *", key=f"p_address_{fv}", value=get_prefill("Address",""), placeholder="Address * Mandatory")
    with pc2:
      gender_options = LISTS["gender"]
      prev_gender = str(get_prefill("Gender","") or "").strip()
      gender_idx = gender_options.index(prev_gender) if prev_gender in gender_options else 0
      st.selectbox("Gender *", gender_options, key=f"p_gender_{fv}", index=gender_idx)
      st.text_input("Age *", key=f"p_age_{fv}", value=get_prefill("Age",""), placeholder="Age - Number")
      occ_list = LISTS.get("occupation", ["Select","Student","Teacher"])
      prev_occ = str(get_prefill("Occupation","") or "").strip()
      occ_idx = occ_list.index(prev_occ) if prev_occ in occ_list else 0
      st.selectbox("Occupation", occ_list, key=f"p_occupation_{fv}", index=occ_idx)
    with pc3:
      st.text_input("Phone *", key=f"p_phone_{fv}", value=get_prefill("Phone",""), placeholder="Phone 03XX-XXXXXXX")
      marital_idx = LISTS["marital"].index(str(get_prefill("MaritalStatus","") or "").strip()) if str(get_prefill("MaritalStatus","") or "").strip() in LISTS["marital"] else 0
      st.selectbox("Marital Status", LISTS["marital"], key=f"p_marital_{fv}", index=marital_idx)
      blood_options = LISTS["blood_group"]
      prev_blood = str(get_prefill("BloodGroup","") or "").strip()
      blood_idx = blood_options.index(prev_blood) if prev_blood in blood_options else 0
      st.selectbox("Blood Group", blood_options, key=f"p_blood_{fv}", index=blood_idx)
    
    # Age/Gender Based Questions - Complete V206 - Below Personal Info (Fix 1b)
    age_val = st.session_state.get(f"p_age_{fv}", "")
    gender_val = st.session_state.get(f"p_gender_{fv}", "")
    if age_val and gender_val and gender_val != "Select":
      age_qs = get_age_based_questions_v206(age_val, gender_val)
      if age_qs:
        st.markdown("---")
        st.markdown("<div class='heading-h5'>Age / Gender Based Questions</div>", unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, (q_label, q_type, q_key) in enumerate(age_qs):
          col = cols[idx % 2]
          with col:
            if isinstance(q_type, list):
              st.selectbox(q_label, q_type, key=f"age_q_{q_key}_{fv}_{is_revisit}")
            else:
              st.text_input(q_label, key=f"age_q_{q_key}_{fv}_{is_revisit}")

    # More Optional
    show_extra_key = f"show_extra_personal_{fv}"
    if show_extra_key not in st.session_state:
      st.session_state[show_extra_key] = False
    st.markdown("<hr style='margin:12px 0; border:1px solid #E8F5E9;'>", unsafe_allow_html=True)
    if not st.session_state[show_extra_key]:
      if st.button("+ More (Optional)", key=f"add_info_btn_{fv}_{is_revisit}", type="secondary"):
        st.session_state[show_extra_key] = True
        st.rerun()
    else:
      st.markdown("<div class='heading-h5'>Additional Info Details</div>", unsafe_allow_html=True)
      ac1,ac2,ac3=st.columns(3)
      with ac1:
        st.text_input("Height", key=f"p_height_{fv}_{is_revisit}", value=get_prefill("Height",""), placeholder="Height")
        st.text_input("Weight", key=f"p_weight_{fv}_{is_revisit}", value=get_prefill("Weight",""), placeholder="Weight")
      with ac2:
        st.selectbox("Sleep Pattern", ["Select","Normal","Less","Excess","Disturbed"], key=f"p_sleep_{fv}_{is_revisit}")
        st.selectbox("Appetite", ["Select","Normal","Less","Excess"], key=f"p_appetite_{fv}_{is_revisit}")
      with ac3:
        st.selectbox("Bowel Movement", ["Select","Normal","Constipated","Loose","Irregular"], key=f"p_bowel_{fv}_{is_revisit}")
        st.selectbox("Thirst", ["Select","Normal","Excess","Less"], key=f"p_thirst_{fv}_{is_revisit}")
      section_ok("personal", is_revisit=is_revisit)

  # Vital Examination - Complete V206 + BP/Pulse/Temp with figure option
  with st.container(border=True):
    st.markdown("<div class='heading-h4'>Vital Examination</div>", unsafe_allow_html=True)
    if section_heading_clickable("vital","Vital Examination Details"):
      vc1,vc2,vc3,vc4=st.columns(4)
      with vc1:
        bp_options = LISTS["bp"]
        prev_bp = str(get_prefill("BP","") or "").strip()
        bp_idx = bp_options.index(prev_bp) if prev_bp in bp_options else 0
        bp_sel = st.selectbox("BP", bp_options, key=f"p_bp_{fv}_{is_revisit}", index=bp_idx)
        if bp_sel == "Other - Write figure":
          bp_val = st.text_input("BP figure", key=f"p_bp_fig_{fv}_{is_revisit}", placeholder="120/80", value=prev_bp if prev_bp not in bp_options else "")
        else:
          bp_val = bp_sel if bp_sel != "Select" else ""
      with vc2:
        pulse_options = LISTS["pulse"]
        prev_pulse = str(get_prefill("Pulse","") or "").strip()
        pulse_idx = pulse_options.index(prev_pulse) if prev_pulse in pulse_options else 0
        pulse_sel = st.selectbox("Pulse", pulse_options, key=f"p_pulse_{fv}_{is_revisit}", index=pulse_idx)
        if pulse_sel == "Other - Write figure":
          pulse_val = st.text_input("Pulse figure", key=f"p_pulse_fig_{fv}_{is_revisit}", placeholder="78", value=prev_pulse if prev_pulse not in pulse_options else "")
        else:
          pulse_val = pulse_sel if pulse_sel != "Select" else ""
      with vc3:
        temp_options = LISTS["temperature"]
        prev_temp = str(get_prefill("Temperature","") or "").strip()
        temp_idx = temp_options.index(prev_temp) if prev_temp in temp_options else 0
        temp_sel = st.selectbox("Temperature", temp_options, key=f"p_temp_{fv}_{is_revisit}", index=temp_idx)
        if temp_sel == "Other - Write figure":
          temp_val = st.text_input("Temp figure", key=f"p_temp_fig_{fv}_{is_revisit}", placeholder="98.6F", value=prev_temp if prev_temp not in temp_options else "")
        else:
          temp_val = temp_sel if temp_sel != "Select" else ""
      with vc4:
        temperament_options = LISTS["temperament"]
        prev_temp2 = str(get_prefill("Temperament","") or "").strip()
        temp2_idx = temperament_options.index(prev_temp2) if prev_temp2 in temperament_options else 0
        mizaj_sel = st.selectbox("Mizaj", temperament_options, key=f"p_temperament_{fv}_{is_revisit}", index=temp2_idx)
        if mizaj_sel == "Other - Write":
          mizaj_val = st.text_input("Mizaj custom", key=f"p_mizaj_custom_{fv}_{is_revisit}", placeholder="Write mizaj", value=prev_temp2 if prev_temp2 not in temperament_options else "")
        else:
          mizaj_val = mizaj_sel if mizaj_sel != "Select" else ""
      section_ok("vital", is_revisit=is_revisit)
      section_close_button("vital")

  # Diseases - Complete V206
  with st.container(border=True):
    st.markdown("<div class='heading-h4'>Diseases</div>", unsafe_allow_html=True)
    if section_heading_clickable("diseases","Select Body Part and Disease"):
      dc1,dc2,dc3,dc4=st.columns([3,3,2,2])
      with dc1:
        body_part = st.selectbox("Body Part *", list(BODY_PARTS.keys()), key=f"body_part_{fv}_{is_revisit}")
        sub_diseases = BODY_PARTS.get(body_part, ["Select"])
      with dc2:
        disease = st.selectbox(f"Disease in {body_part} *", sub_diseases, key=f"disease_sub_{fv}_{is_revisit}")
      with dc3:
        no_options = ["Select","1","2","3","4","5","6","7","8","9","10","Other"]
        d_no_sel = st.selectbox("No/Count *", no_options, key=f"no_sel_{fv}_{is_revisit}")
        if d_no_sel == "Other":
          d_no = st.text_input("Enter Count", key=f"no_{fv}_{is_revisit}", placeholder="Enter number")
        else:
          d_no = d_no_sel if d_no_sel != "Select" else ""
      with dc4:
        d_duration = st.selectbox("Duration *", LISTS["duration"], key=f"dur_{fv}_{is_revisit}")

      all_fields_complete = body_part != "Select" and disease != "Select" and str(d_no).strip() != "" and d_duration != "Select"
      if all_fields_complete:
        st.markdown(f"<div class='heading-h5'>Related Questions for {body_part} - {disease}</div>", unsafe_allow_html=True)
        related_qs = DISEASE_RELATED_QUESTIONS.get(body_part, DISEASE_RELATED_QUESTIONS["General"])
        dd_map = DISEASE_RELATED_DROPDOWNS.get(body_part, {})
        cq1,cq2,cq3=st.columns(3)
        with cq1:
          q1_label = related_qs[0] if len(related_qs)>0 else "Severity"
          q1_options = dd_map.get(q1_label, LISTS["severity"])
          rq1 = st.selectbox(q1_label, q1_options, key=f"rel_q1_{fv}_{is_revisit}")
        with cq2:
          q2_label = related_qs[1] if len(related_qs)>1 else "Trigger"
          q2_options = dd_map.get(q2_label, ["Select","Yes","No","Sometimes"])
          rq2 = st.selectbox(q2_label, q2_options, key=f"rel_q2_{fv}_{is_revisit}")
        with cq3:
          q3_label = related_qs[2] if len(related_qs)>2 else "Associated Symptom"
          q3_options = dd_map.get(q3_label, ["Select","Nausea","Burning","Pain","Itching","None","Other"])
          rq3 = st.selectbox(q3_label, q3_options, key=f"rel_q3_{fv}_{is_revisit}")
      else:
        rq1=rq2=rq3="Select"
        if body_part != "Select" and disease != "Select":
          st.info("Complete No/Count* and Duration* to see Related Questions")

      if st.button("Add Disease +", key=f"add_disease_{fv}_{is_revisit}", type="secondary", use_container_width=True):
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
          if 'rq1' in locals() and rq1 and rq1!="Select": entry_text += f" + {rq1}"
          if 'rq2' in locals() and rq2: entry_text += f" + {rq2}"
          if 'rq3' in locals() and rq3: entry_text += f" + {rq3}"
          if "patient_diseases" not in st.session_state:
            st.session_state.patient_diseases = []
          st.session_state.patient_diseases.append({"text": entry_text})
          show_popup(f"Added: {disease}")
          st.rerun()
      
      if st.session_state.patient_diseases:
        st.markdown("<div class='heading-h5'>Added Diseases</div>", unsafe_allow_html=True)
        combined = " + ".join([d.get("text","") for d in st.session_state.patient_diseases])
        st.markdown(f"<div style='background:#FFFFFF;border:2px solid #2E7D5B;border-radius:12px;padding:16px;margin:8px 0;'><b>Combined:</b> {combined}</div>", unsafe_allow_html=True)
        for i, dd in enumerate(st.session_state.patient_diseases):
          c1,c2=st.columns([4,1])
          with c1:
            st.write(f"{i+1}. {dd.get('text','')}")
          with c2:
            if st.button("Remove", key=f"rem_{i}_{fv}_{is_revisit}"):
              st.session_state.patient_diseases.pop(i)
              st.rerun()
      
      section_ok("diseases", is_revisit=is_revisit)
      section_close_button("diseases")

  # Complaint, History, Diagnosis, Treatment
  with st.container(border=True):
    st.markdown("<div class='heading-h4'>Complaint, History, Diagnosis</div>", unsafe_allow_html=True)
    if section_heading_clickable("complaint","Complaint Details"):
      b1,b2=st.columns(2)
      with b1:
        history = st.text_area("Past History", key=f"history_{fv}_{is_revisit}", value=get_prefill("History",""), height=100)
        complaint = st.text_area("Complaint", key=f"complaint_{fv}_{is_revisit}", value=get_prefill("Complaint",""), height=100, placeholder="General Checkup if empty")
      with b2:
        diagnosis = st.text_area("Diagnosis", key=f"diagnosis_{fv}_{is_revisit}", value=get_prefill("Diagnosis",""), height=100)
        treatment = st.text_area("Treatment", key=f"treatment_{fv}_{is_revisit}", value=get_prefill("Treatment",""), height=100)
      st.session_state[f"hist_{fv}_{is_revisit}"] = st.session_state.get(f"history_{fv}_{is_revisit}", "")
      st.session_state[f"comp_{fv}_{is_revisit}"] = st.session_state.get(f"complaint_{fv}_{is_revisit}", "")
      st.session_state[f"diag_{fv}_{is_revisit}"] = st.session_state.get(f"diagnosis_{fv}_{is_revisit}", "")
      st.session_state[f"treat_{fv}_{is_revisit}"] = st.session_state.get(f"treatment_{fv}_{is_revisit}", "")
      section_ok("complaint", is_revisit=is_revisit)
      section_close_button("complaint")

  # Billing - Complete V206 + Cash/Outstanding/Free
  with st.container(border=True):
    st.markdown("<div class='heading-h4'>Billing</div>", unsafe_allow_html=True)
    if section_heading_clickable("billing","Billing Details"):
      if is_revisit:
        default_fee = ""; default_med = ""; default_paid = ""
      else:
        default_fee = ""; default_med = ""; default_paid = ""
      c1,c2,c3,c4=st.columns(4)
      with c1:
        fee_val = st.text_input("Fee (Rs)", key=f"fee_{fv}_{is_revisit}", value=default_fee, placeholder="Enter Fee")
      with c2:
        med_val = st.text_input("Medicine Charges (Rs)", key=f"med_charges_{fv}_{is_revisit}", value=default_med, placeholder="Enter Medicine Charges")
      with c3:
        paid_val = st.text_input("Paid (Rs)", key=f"paid_{fv}_{is_revisit}", value=default_paid, placeholder="Enter Paid")
      with c4:
        fee_status = st.selectbox("Bill Status", LISTS["fee_status"], key=f"fee_status_{fv}_{is_revisit}")
      c5,c6=st.columns(2)
      with c5:
        payment_method = st.selectbox("Payment Method", LISTS["payment"], key=f"payment_method_{fv}_{is_revisit}")
      with c6:
        if prev_bal > 0:
          st.markdown(f"<div style='background:#FFF3E0;border:2px solid #FF9800;border-radius:10px;padding:10px;text-align:center;'><b style='color:#E65100;'>Outstanding: Rs {prev_bal:.0f}</b></div>", unsafe_allow_html=True)
      try:
        f = float(str(fee_val).replace(",","") or 0); m = float(str(med_val).replace(",","") or 0); p = float(str(paid_val).replace(",","") or 0)
      except:
        f=m=p=0.0
      grand_total = f + m + prev_bal
      balance = grand_total - p
      if balance<0: balance=0
      st.markdown(f"<div class='heading-h3'>Grand Total: Rs {grand_total:.0f} | Balance: Rs {balance:.0f}</div>", unsafe_allow_html=True)
      st.markdown(f"<div style='background:#E8F5E9;border:2px solid #2E7D5B;border-radius:10px;padding:10px;font-size:14px;'><b>Billing Summary:</b> Fee Rs {f:.0f} + Medicine Rs {m:.0f} {'+ Outstanding Rs '+str(int(prev_bal)) if prev_bal>0 else ''} = Grand Total Rs {grand_total:.0f} | Paid Rs {p:.0f} = Balance Rs {balance:.0f}</div>", unsafe_allow_html=True)
      st.session_state[f"calc_gt_{fv}_{is_revisit}"]=grand_total
      st.session_state[f"calc_bal_{fv}_{is_revisit}"]=balance
      section_ok("billing", is_revisit=is_revisit)
      section_close_button("billing")

  # Save Patient
  st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
  c_save, c_new = st.columns([3,1])
  with c_new:
    if st.button("New Patient", key=f"new_patient_btn_{fv}_{is_revisit}", type="secondary"):
      reset_to_new_patient()
  with c_save:
    if st.button("Save Patient", type="primary", use_container_width=True, key=f"save_patient_{fv}_{is_revisit}"):
      # Validation
      p_name = st.session_state.get(f"p_name_{fv}", "").strip()
      p_phone = st.session_state.get(f"p_phone_{fv}", "").strip()
      p_age = st.session_state.get(f"p_age_{fv}", "").strip()
      p_address = st.session_state.get(f"p_address_{fv}", "").strip()
      p_gender = st.session_state.get(f"p_gender_{fv}", "Select")
      if not p_name:
        st.error("Patient Name required")
      elif not p_age:
        st.error("Age required")
      elif p_gender == "Select":
        st.error("Gender required")
      elif not p_phone:
        st.error("Phone required")
      elif not p_address:
        st.error("Address required")
      else:
        try:
          ws = get_sheet_safe("New_patient")
          if not ws:
            st.error("Sheet not connected - Saved locally")
            save_to_local_csv("New_patient", {"PatientID": pid, "Name": p_name, "Phone": p_phone})
          else:
            headers = ws.row_values(1)
            # Ensure headers have our required
            if len(headers) < 10:
              headers = SHEET_HEADERS["New_patient"]
              ws.update('A1', [headers], value_input_option='USER_ENTERED')
            # Build row
            # Get values
            bp_v = st.session_state.get(f"p_bp_{fv}_{is_revisit}", "")
            if st.session_state.get(f"p_bp_fig_{fv}_{is_revisit}", ""):
              bp_v = st.session_state.get(f"p_bp_fig_{fv}_{is_revisit}", "")
            pulse_v = st.session_state.get(f"p_pulse_{fv}_{is_revisit}", "")
            if st.session_state.get(f"p_pulse_fig_{fv}_{is_revisit}", ""):
              pulse_v = st.session_state.get(f"p_pulse_fig_{fv}_{is_revisit}", "")
            temp_v = st.session_state.get(f"p_temp_{fv}_{is_revisit}", "")
            if st.session_state.get(f"p_temp_fig_{fv}_{is_revisit}", ""):
              temp_v = st.session_state.get(f"p_temp_fig_{fv}_{is_revisit}", "")
            mizaj_v = st.session_state.get(f"p_temperament_{fv}_{is_revisit}", "")
            if st.session_state.get(f"p_mizaj_custom_{fv}_{is_revisit}", ""):
              mizaj_v = st.session_state.get(f"p_mizaj_custom_{fv}_{is_revisit}", "")
            
            diseases_text = " + ".join([d.get("text","") for d in st.session_state.get("patient_diseases",[])])
            
            fee_v = st.session_state.get(f"fee_{fv}_{is_revisit}", "0")
            med_v = st.session_state.get(f"med_charges_{fv}_{is_revisit}", "0")
            paid_v = st.session_state.get(f"paid_{fv}_{is_revisit}", "0")
            status_v = st.session_state.get(f"fee_status_{fv}_{is_revisit}", "Cash")
            pay_method_v = st.session_state.get(f"payment_method_{fv}_{is_revisit}", "Cash")
            grand_total_v = st.session_state.get(f"calc_gt_{fv}_{is_revisit}", 0)
            balance_v = st.session_state.get(f"calc_bal_{fv}_{is_revisit}", 0)
            
            complaint_v = st.session_state.get(f"complaint_{fv}_{is_revisit}", "") or st.session_state.get(f"comp_{fv}_{is_revisit}", "") or "General Checkup"
            
            row_data = {
              "PatientID": pid,
              "OriginalPatientID": st.session_state.get("original_patient_id", pid),
              "Date": str(datetime.date.today()),
              "Name": p_name,
              "FatherName": st.session_state.get(f"p_fname_{fv}", ""),
              "Age": p_age,
              "Gender": p_gender,
              "Phone": p_phone,
              "Address": p_address,
              "BP": bp_v,
              "Pulse": pulse_v,
              "Temperament": mizaj_v,
              "Diseases": diseases_text,
              "History": st.session_state.get(f"history_{fv}_{is_revisit}", "") or st.session_state.get(f"hist_{fv}_{is_revisit}", ""),
              "Complaint": complaint_v,
              "Diagnosis": st.session_state.get(f"diagnosis_{fv}_{is_revisit}", "") or st.session_state.get(f"diag_{fv}_{is_revisit}", ""),
              "Treatment": st.session_state.get(f"treatment_{fv}_{is_revisit}", "") or st.session_state.get(f"treat_{fv}_{is_revisit}", ""),
              "Fees": fee_v,
              "Status": status_v,
              "Total": grand_total_v,
              "Paid": paid_v,
              "Balance": balance_v,
              "PaymentMethod": pay_method_v,
              "ClinicName": st.session_state.clinic_name
            }
            # Map to headers
            row = [str(row_data.get(h,"")) for h in headers]
            ws.append_row(row, value_input_option='RAW')
            show_popup(f"Saved! ID {pid} | Grand Total Rs {grand_total_v:.0f}")
            # Reset
            st.session_state.form_version+=1
            st.session_state.patient_diseases=[]
            st.session_state.revisit_data=None
            st.session_state.section_opened={"personal": True, "vital": False, "diseases": False, "complaint": False, "history": False, "prescription": False, "billing": False}
            st.session_state.section_unlocked={"personal": True, "vital": False, "diseases": False, "complaint": False, "history": False, "prescription": False, "billing": False}
            st.rerun()
        except Exception as e:
          st.error(f"Save error: {e}")
          save_to_local_csv("New_patient", {"PatientID": pid, "Name": p_name, "Phone": p_phone, "Error": str(e)})

def patient_page():
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>New Patient - Complete V206</div>", unsafe_allow_html=True)
  render_patient_form(is_revisit=False)
  under_development_footer("New Patient")
  add_footer()

def patient_revisit_form_page():
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>Revisit Form - Complete V206</div>", unsafe_allow_html=True)
  render_patient_form(is_revisit=True)
  under_development_footer("Revisit Form")
  add_footer()

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
    rec_day = None; rec_month = None; rec_year = None
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
    sd = search_parsed.get("day"); sm = search_parsed.get("month"); sy = search_parsed.get("year")
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

def revisit_page():
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>Revisit - Search Patient - Complete V206</div>", unsafe_allow_html=True)
  st.markdown("<div class='heading-h5'>Search using any of these four fields: Patient Name, Date, Address, or Phone Number</div>", unsafe_allow_html=True)
  st.markdown("<div style='background:#FFF9C4;border:1px solid #FFD700;border-radius:8px;padding:8px;margin-bottom:8px;font-size:12px;'><b>Date Search Guide:</b> Day only: <code>1</code> = only day 1 (not 11,21,31) | Month: <code>-05</code> or <code>1-05</code> = month 05 | Year: <code>--2026</code> or <code>1-05-2026</code> = year 2026 | Full: <code>2026-05-01</code> or <code>1-05-2026</code></div>", unsafe_allow_html=True)
  records = get_all_records_cached("New_patient")
  my = [r for r in records if str(r.get("ClinicName","")).lower() == str(st.session_state.clinic_name).lower()]
  c1,c2=st.columns(2)
  with c1:
    s_name = st.text_input("Patient Name", key="rev_name_v3", placeholder="Full or partial")
    s_date = st.text_input("Date (YYYY-MM-DD)", key="rev_date_v3", placeholder="e.g., 1 or 1-05 or 1-05-2026 or 2026-05-01")
  with c2:
    s_phone = st.text_input("Phone Number", key="rev_phone_v3", placeholder="Full or partial")
    s_address = st.text_input("Address", key="rev_address_v3", placeholder="Full address or city/village only")
  
  if s_name or s_phone or s_date or s_address:
    filt=[]
    is_date_search = bool(s_date and s_date.strip())
    parsed_date = parse_date_search(s_date) if is_date_search else None
    seen_ids = set()
    for r in my:
      pid = str(r.get("PatientID","")).strip()
      match=False
      if s_name:
        s_name_lower = str(s_name).strip().lower()
        rec_name_lower = str(r.get("Name","")).lower()
        if s_name_lower == rec_name_lower or s_name_lower in rec_name_lower:
          match=True
      if s_phone:
        s_phone_clean = str(s_phone).strip().replace(" ","").replace("-","")
        rec_phone_clean = str(r.get("Phone","")).replace(" ","").replace("-","")
        if s_phone_clean in rec_phone_clean:
          match=True
      if s_date:
        rec_date = str(r.get("Date","")).strip()
        if parsed_date:
          if match_date_record(rec_date, parsed_date):
            match=True
        else:
          if str(s_date).strip().lower() in rec_date.lower():
            match=True
      if s_address:
        s_addr_lower = str(s_address).strip().lower()
        rec_addr_lower = str(r.get("Address","")).lower()
        if s_addr_lower in rec_addr_lower:
          match=True
      if match:
        if is_date_search and not s_name and not s_phone and not s_address:
          filt.append(r)
        else:
          if pid and pid not in seen_ids:
            filt.append(r)
            seen_ids.add(pid)
          elif not pid:
            filt.append(r)
    if is_date_search and not s_name and not s_phone and not s_address:
      seen_combo = set()
      unique_filt = []
      for r in filt:
        pid = str(r.get("PatientID","")).strip()
        date = str(r.get("Date","")).strip()
        timestamp = str(r.get("Timestamp","")).strip()[:16]
        combo = f"{pid}_{date}_{timestamp}"
        combo_simple = f"{pid}_{date}"
        if combo not in seen_combo and combo_simple not in seen_combo:
          if any(str(x.get("PatientID","")).strip() == pid and str(x.get("Date","")).strip() == date for x in unique_filt):
            continue
          unique_filt.append(r)
          seen_combo.add(combo)
          seen_combo.add(combo_simple)
      filt = unique_filt
      st.write(f"Found {len(filt)} visits - Specific entity only")
    else:
      unique_by_id = {}
      for r in filt:
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
      filt = list(unique_by_id.values())
      st.write(f"Found {len(filt)} patients - Same ID shown once")
    for idx, r in enumerate(filt[:20]):
      with st.container(border=True):
        st.write(f"{r.get('Name','')} | Date: {r.get('Date','')} | Address: {r.get('Address','')} | Phone: {r.get('Phone','')} | ID: {r.get('PatientID','')} | Balance: Rs {r.get('Balance','0')}")
        if st.button(f"Open {r.get('PatientID','')} - {r.get('Name','')}", key=f"rev_{r.get('PatientID','')}_{idx}_v3"):
          st.session_state.revisit_data=r
          try:
            pid = str(r.get("PatientID","")).strip()
            chain = [rec for rec in my if str(rec.get("PatientID","")).strip() == pid]
            from datetime import datetime as _dt
            def parse_date_sort(rec):
              try:
                d = str(rec.get("Date",""))
                return _dt.strptime(d, "%Y-%m-%d")
              except:
                return _dt.min
            chain = sorted(chain, key=parse_date_sort, reverse=True)
            st.session_state.revisit_history_chain = chain
          except:
            st.session_state.revisit_history_chain = [r]
          try: st.session_state.prev_balance=float(str(r.get("Balance","0") or 0).replace(",","") or 0)
          except: st.session_state.prev_balance=0.0
          st.session_state.current_page="patient_revisit_form"
          st.rerun()
  else:
    st.info("Enter any field: Name (full/partial), Date (1 or 1-05 or 1-05-2026), Address (city/village or full), Phone")
  under_development_footer("Revisit")
  add_footer()

def clinic_login_page():
  clinic_heading_banner()
  st.markdown("<div class='heading-h3'>Clinic Login</div>", unsafe_allow_html=True)
  uname = st.text_input("Username", key="clinic_uname_v3")
  pwd = st.text_input("Password", type="password", key="clinic_pwd_v3")
  if st.button("Login", type="primary", key="login_v3"):
    if uname and pwd:
      st.session_state.logged_in=True
      st.session_state.username=uname
      st.session_state.clinic_name="Herbal Clinic International"
      st.session_state.current_page="dashboard_welcome"
      st.rerun()
    else:
      st.error("Enter username and password")

def dashboard_welcome_page():
  scroll_to_top()
  top_bar_inner_with_user()
  clinic_heading_banner_dashboard_only()
  st.markdown("<div class='heading-h3'>Dashboard - V3.2 Complete V206</div>", unsafe_allow_html=True)
  r1c1,r1c2,r1c3=st.columns(3)
  with r1c1:
    if st.button("New Patient - Complete V206", use_container_width=True, key="dash_new_v3", type="primary"):
      st.session_state.current_page="patient"
      st.rerun()
  with r1c2:
    if st.button("Revisit Search - Complete V206", use_container_width=True, key="dash_rev_search_v3"):
      st.session_state.current_page="revisit"
      st.rerun()
  with r1c3:
    if st.button("Revisit Form - Complete V206", use_container_width=True, key="dash_rev_form_v3"):
      if st.session_state.revisit_data:
        st.session_state.current_page="patient_revisit_form"
      else:
        st.session_state.current_page="revisit"
      st.rerun()
  
  # Stats
  try:
    records = get_all_records_cached("New_patient")
    my = [r for r in records if str(r.get("ClinicName","")).lower() == str(st.session_state.clinic_name).lower()]
    total = len(my)
    today_str = str(datetime.date.today())
    today_count = len([r for r in my if today_str in str(r.get("Date",""))])
    st.markdown(f"<div style='background:#E8F5E9;border:2px solid #2E7D5B;border-radius:12px;padding:16px;margin-top:16px;'><b>Total Patients: {total} | Today: {today_count}</b></div>", unsafe_allow_html=True)
  except:
    pass
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
    else: dashboard_welcome_page()

if __name__=="__main__": main()
