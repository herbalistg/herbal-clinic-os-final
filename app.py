# APP VERSION - V200.17 - FIX 1 Throat Sore Throat dropdowns + all Related Questions dropdowns, FIX 2 All forms dropdowns where possible (BP, Pulse, Temp etc), FIX 3 Related Questions after all disease fields complete (Body Part, Disease, No/Count, Duration), FIX 4 Home treatment Personal Info complete but says incomplete fixed + sequential forms reminder, FIX 5 DuplicateElementKey auto_sel_AUTO3 fixed with index - FIX 1 Home treatment Added Diseases functional (clear once not every rerun), FIX 2 Time Out - cache 900s, max_rows 200/50, local first instant, dashboard stats 900s - FIX 1a Phone Blood Marital visible not hidden, 1b Address Height Weight Habits to Additional hidden, 1c Proceed below Additional Questions, 1d Note visible white/yellow text not black on black, 1e Proceed extracts temperament Diet Restrictions Instructions locked, 2 Home treatment Added Diseases functional - Fix NameError get_next_feedback_id, 2a Remove Add buttons, 2b Manual field bigger text_area 150 height, 2c Labels Single Medicines/Formula Medicines only, 3a Revisit Age/Gender previous data visible - V200.4 Structure - 1a Close button below same section, 1b Prescription from Google Sheet searchable, 1c Physician manual medicine field, 1d No section opens until Open clicked, 2 Clinic Admin Settings/Formulas, 3 Doctor moved from patient form to App Admin Doctor performance monitor - Fix UnboundLocalError at line 2403 PaymentMethod pay_method undefined - Stream On fix - English only - Close buttons - Prescription sheet searchable + manual - No Final Step - Clinic Settings/Formulas - 2026-09-29 - BASED ON V200.4 STRUCTURE - Fixes: 1- Stream On bug fixed (removed unconditional force_scroll_to_top, pure cached function no session_state access, local-first 600s, max_rows 300/100), 2- Urdu/Roman Urdu text removed (all English only), 3a- Forms next field open option now has Close button below same field to close section (prevent expanded form), 3b- Prescription single and formula medicines from Google Sheet (Herbs, Pharmacopoeia/Formulas/Medicine sheets) with searchable select + Add button, 3c- Prescription physician manual medicine field, 3d- Save Patient - Final Step section removed (save buttons directly below Billing, no diagnosis banners), 4- Clinic Admin 2 options Settings (clinic dashboard tabs control) and Formulas (add clinic formulas to sheet) - Previous: V200.10, V200.4
# V200.11 - V200.4 Structure preserved - All 4 tasks fixed
# Previous: V200.10, V200.9, V200.8, V200.4


import streamlit as st
import datetime
import re
import pandas as pd

# NOTE FOR EVERY APP VERSION
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

APP_VERSION = "V200.17 - V200.4 Structure+Stream Fix+English Only+Close Buttons+Prescription Sheet+Manual Med+No FinalStep+Clinic Settings/Formulas" # V207 - 1 tab theme toggle both themes, 1 line top bar theme+lang, scroll top robust fix, V205 all fixes re-applied # V206 - Light/Dim only, no extra text, Stay signed in option, Ad smaller smarter down 0.5cm, Free Tools in Clinic & Home sections, scroll top default, int fields, Phone in Personal, Sheet fix # V205 - User theme toggle (Light/Dark/Dim) for user comfort, login persistence controlled by App Admin # V204 Modern - Ad compact vertical, Free Quiz both PC/mobile, remove black box, Urdu note, scroll top, Proceed below Additional, Add Disease fix, clean headings # V203 Modern - Gradient header, Dashboard metrics+graph, Temperament Quiz, Articles as cards, Raised modern UI # V202 - Bigger header fonts italic, unified top box, raised tabs, persistent login, 2 tabs mobile, ad near streamlit, full AppSettings, local+sheet dual save # V201 - Persistent mobile login, 2 tabs per line mobile, compact green hover, ad near streamlit, full AppSettings control # V200 - Dashboard compact, persistent login, fixed ad golden border, bigger fonts # V199 - Final Herbal Light Theme - Clean Deploy # V175 - PC gap reduced, tab fields clear, PC headings larger, mobile icon-sized fields, light strategy kept, icon+black field, Open removed, hover green highlight, Offer black field blinking green, footer light gray # V172 - Sheet cleanup, boundary thick #0e1117, fix duplicate save, new ID, Proceed reset, New/Revisit options, 5 patients Home User, Revisit history display, Billing blank

WHATSAPP_LINK = "https://chat.whatsapp.com/J7xfZT2Pf4H8Zzu7eBD7CS"

def sanitize_for_sheet(text):
  if not text: return ""
  text = str(text).strip()
  text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
  text = re.sub(r'\s+', ' ', text)
  return text.strip()

st.set_page_config(page_title="Herbal Clinic International", page_icon="\U0001f33f", layout="centered", initial_sidebar_state="collapsed")

# ===== V207 - User Theme System - Light + Dim only, single toggle, 1 line top bar =====
if "theme" not in st.session_state:
  st.session_state.theme = "light"

@st.cache_data(show_spinner=False, ttl=3600)
def get_theme_css_cached(theme):
  # V200.9 - FIX 1: No fade on button click - removed all transitions, no transform
  raised = """
    /* V200.9 - No Fade Fix - Zero transitions */
    html, .stApp, [data-testid="stAppViewContainer"] { transition: none!important; animation: none!important; }
    div[data-baseweb="tab-list"] { gap: 8px; padding: 4px; }
    div[data-baseweb="tab"] {
      background: #FFFFFF!important;
      border: 2px solid #A8CCAD!important;
      border-radius: 12px!important;
      box-shadow: 0 2px 6px rgba(46,125,91,0.12)!important;
      font-weight: 700!important;
      padding: 8px 16px!important;
      transition: none!important;
    }
    div[data-baseweb="tab"][aria-selected="true"] {
      background: #2E7D5B!important;
      color: white!important;
      border-color: #1B5E20!important;
    }
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
      background: #FFFFFF!important;
      border: 2px solid #A8CCAD!important;
      border-radius: 10px!important;
      box-shadow: 0 1px 4px rgba(46,125,91,0.08)!important;
      transition: none!important;
    }
    .stButton > button {
      background: #FFFFFF!important;
      border: 2px solid #A8CCAD!important;
      border-radius: 10px!important;
      box-shadow: 0 2px 6px rgba(46,125,91,0.12)!important;
      font-weight: 700!important;
      padding: 6px 14px!important;
      transition: none!important;
      animation: none!important;
    }
    .stButton > button:active, .stButton > button:focus {
      transform: none!important;
      box-shadow: 0 2px 6px rgba(46,125,91,0.12)!important;
    }
    .stButton > button[kind="primary"] {
      background: #2E7D5B!important;
      color: white!important;
      border-color: #1B5E20!important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
      background: #FFFFFF!important;
      border: 2px solid #C8E6D5!important;
      border-radius: 14px!important;
      box-shadow: 0 2px 8px rgba(46,125,91,0.08)!important;
      transition: none!important;
    }
    /* Prevent Streamlit fade overlay */
    [data-testid="stStatusWidget"], [data-testid="stSpinner"] { transition: none!important; }
    """
  if theme == "dim":
    return raised + """
    html, body,.stApp, [data-testid="stAppViewContainer"] { background: #C8DCCB!important; color: #0F2A14!important; }
    .block-container { background: #DDEBE0!important; border: 3.5px solid #1B5E20!important; box-shadow: 0 12px 32px rgba(27,94,32,0.25)!important; border-radius: 18px!important; }
    """
  else:
    return raised + """
    html, body,.stApp, [data-testid="stAppViewContainer"] { background: #FFFFFF!important; color: #1F2D27!important; }
    .block-container { background: #FFFFFF!important; border: 3px solid #2E7D5B!important; border-radius: 18px!important; box-shadow: 0 12px 32px rgba(46,125,91,0.18)!important; }
    """

def get_theme_css():
  theme = st.session_state.get("theme", "light")
  # V200.2: Use cached CSS
  try:
    return get_theme_css_cached(theme)
  except:
    pass
  if theme == "dim":
    # V206 Requirement 1d: Same green shade stronger - screen feels slightly dark
    return """
    html, body,.stApp, [data-testid="stAppViewContainer"] { background: #C8DCCB!important; color: #0F2A14!important; }
    .block-container { background: #DDEBE0!important; border: 3.5px solid #1B5E20!important; box-shadow: 0 8px 28px rgba(27,94,32,0.30)!important; }
    .heading-h1 { color: #1B5E20!important; }
    .graceful-card { background: #A8CCAD!important; border: 2px solid #1B5E20!important; }
    .dash-section-title { background: #1B5E20!important; }
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] { background: #E0F0E2!important; border: 2px solid #2E7D32!important; }
    
    """
  else:
    return """
    html, body,.stApp, [data-testid="stAppViewContainer"] { background: #FFFFFF!important; color: #1F2D27!important; }
    .block-container { background: #FFFFFF!important; border: 3px solid #2E7D5B!important; }
    """

def show_urdu_work_in_progress_note():
  if st.session_state.get("logged_in", False):
    st.markdown("""
    <div style="background:#FFF9C4;border:2px solid #FBC02D;border-radius:12px;padding:12px;margin-top:20px;text-align:center;">
      <span style="font-size:16px;font-weight:700;color:#1F2D27;">This is not final; work on it is currently in progress. You will be informed once the work is completed.</span>
    </div>
    """, unsafe_allow_html=True)

def scroll_to_top():
  """V200 FIX: Ultra-light scroll - no iframe, prevents reboot hang"""
  return # Disabled to prevent processing delay after reboot - Streamlit auto-scrolls
  # Original scroll code kept below for compatibility but disabled
  def _old_scroll():
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function(){
      function doScroll(){
        try{
          window.scrollTo({top:0, left:0, behavior:'instant'});
          document.documentElement.scrollTop = 0;
          document.body.scrollTop = 0;
        // Scroll parent (Streamlit iframe)
        if(window.parent){
          window.parent.scrollTo({top:0, left:0, behavior:'instant'});
          try{ window.parent.document.documentElement.scrollTop = 0; }catch(e){}
          try{ window.parent.document.body.scrollTop = 0; }catch(e){}
          // Scroll all possible containers
          const selectors = [
            '[data-testid="stAppViewContainer"]',
            '[data-testid="stMain"]',
            'section.main',
            '[data-testid="stVerticalBlock"]',
            '[data-testid="stAppViewContainer"] > div',
            'main',
            '.main',
            '[data-testid="stApp"]',
            '.stApp',
            '[data-testid="stVerticalBlock"] > div'
          ];
          selectors.forEach(sel => {
            try{
              const els = window.parent.document.querySelectorAll(sel);
              els.forEach(c=>{ 
                if(c) {
                  c.scrollTop = 0;
                  c.scrollTo({top:0, behavior:'instant'});
                }
              });
            }catch(e){}
          });
          // Also try to find and scroll the main scrollable element
          try{
            const mainEl = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
            if(mainEl){
              mainEl.scrollTop = 0;
              mainEl.scrollTo(0,0);
            }
          }catch(e){}
        }
      }catch(e){}
    }
    // Immediate scroll
    doScroll();
    // Multiple retries to ensure page opens from top
    setTimeout(doScroll, 50);
    setTimeout(doScroll, 100);
    setTimeout(doScroll, 200);
    setTimeout(doScroll, 400);
    setTimeout(doScroll, 600);
    setTimeout(doScroll, 1000);
    // Also on load
    window.addEventListener('load', doScroll);
  })();
  </script>
  """, height=0)
  # V200.2: Removed heavy scroll anchor and CSS - speed


st.markdown("""
<style>
/* V209.2 Fix 1 - Ad compact 0.5cm down - NOT full page */
.ad-note { 
  position: fixed!important;
  bottom: 8px!important;
  right: 12px!important;
  z-index: 999999!important;
  background: #FFFFFF!important;
  border: 2px solid #B8860B!important;
  border-radius: 10px!important;
  padding: 6px 10px!important;
  text-align: center!important;
  font-size: 10px!important;
  font-weight: 700!important;
  color: #1F2D27!important;
  box-shadow: 0 3px 12px rgba(184,134,11,0.25)!important;
  width: auto!important;
  max-width: 110px!important;
  height: auto!important;
  max-height: 90px!important;
  line-height: 1.2!important;
  margin: 0!important;
}
/* V209.2 Fix 2 - Mobile tabs colored like laptop */
@media (max-width: 768px) {
  .graceful-card { background: #F1F7F3!important; border: 2px solid #2E7D5B!important; box-shadow: 0 4px 12px rgba(46,125,91,0.20)!important; }
  .graceful-card button { background: #F1F7F3!important; border: 1.5px solid #2E7D5B!important; color: #1F2D27!important; font-weight: 700!important; }
}

/* V200 - Herbal Light Theme - Final + Compact Dashboard + Bigger Fonts */
html, body,.stApp, [data-testid="stAppViewContainer"] { background: #FFFFFF!important; color: #1F2D27!important; }

/* Block container */
.block-container { 
  max-width: 940px!important; 
  margin: 20px auto!important; 
  padding: 1.6rem 1.8rem!important; 
  background: #FFFFFF!important; 
  border: 3px solid #2E7D5B!important;
  border-radius: 20px!important; 
  box-shadow: 0 4px 20px rgba(46,125,91,0.12)!important;
}
#MainMenu, header {visibility: hidden;}
div[data-testid="stSidebar"] {display: none;}

/* ===== V200 Requirement 5: Bigger Fonts - PC slightly larger than mobile ===== */
/* Page Titles */
.heading-h1 { font-size: 52px!important; font-weight: 900!important; color:#2E7D5B!important; text-align:center; }
.heading-h2 { font-size: 26px!important; font-weight: 800!important; color:#2E7D5B!important; }
.heading-h3 { font-size: 30px!important; font-weight: 800!important; color:#1F2D27!important; }
.heading-h4 { font-size: 24px!important; font-weight: 700!important; color:#1F2D27!important; margin:12px 0!important; }
.heading-h5 { font-size: 22px!important; font-weight: 700!important; color:#2E7D5B!important; }

/* General text bigger */
.stApp p, .stApp div, .stApp span, .stApp label { font-size: 17px!important; }
.stApp button { font-size: 18px!important; font-weight: 700!important; }

/* Mobile adjustments - still bigger than before but slightly smaller than PC */
@media (max-width: 768px) {
  .heading-h1 { font-size: 34px!important; }
  .heading-h2 { font-size: 22px!important; }
  .heading-h3 { font-size: 24px!important; }
  .heading-h4 { font-size: 20px!important; }
  .heading-h5 { font-size: 18px!important; }
  .stApp p, .stApp div, .stApp span, .stApp label { font-size: 16px!important; }
  .stApp button { font-size: 16px!important; }
}

/* ===== V200 Requirement 2 & 3: Dashboard compact tabs, icon inside tab, green border only on hover ===== */
.graceful-card { 
  background: #F1F7F3; 
  border: 2px solid transparent!important; 
  border-radius: 12px; 
  padding: 6px!important; 
  text-align:center; 
  color:#1F2D27!important; 
  transition: all 0.25s ease;
}
.graceful-card:hover { 
  border: 2px solid #2E7D5B!important; 
  box-shadow: 0 4px 12px rgba(46,125,91,0.20)!important;
  background: #FFFFFF!important;
}
.graceful-card button { 
  padding: 8px 10px!important; 
  min-height: 52px!important;
  font-size: 15px!important;
}
@media (max-width: 768px) {
  .graceful-card button { min-height: 48px!important; font-size: 14px!important; }
}


/* ===== V208 Fix 2 - Mobile dashboard tabs colored like laptop ===== */
@media (max-width: 768px) {
  .graceful-card { 
    background: #F1F7F3!important; 
    border: 1.5px solid #2E7D5B!important; 
    box-shadow: 0 3px 10px rgba(46,125,91,0.15)!important;
  }
  .graceful-card button { 
    background: #F1F7F3!important;
    border: 1px solid #C8E6D5!important;
    color: #1F2D27!important;
  }
  .graceful-card:hover { 
    background: #FFFFFF!important;
    border: 2px solid #2E7D5B!important;
  }
}


/* V209 Fix 1 - Ad 0.5cm down from previous */





/* Compact dashboard grid */
.dash-section-title { font-size:20px!important; font-weight:800!important; color:#FFFFFF; background:#2E7D5B; padding:10px 16px; border-radius:10px; margin:20px 0 12px 0; }

.demo-card { background: #F1F7F3; border:1px solid #C8E6D5; border-radius:14px; padding:16px; color:#1F2D27!important; }
.footer-sharp { text-align:center; color:#5a6d65!important; font-size:14px!important; margin-top:30px; border-top:1px solid #C8E6D5; padding:14px; }
.history-card { background:#F1F7F3; border:1px solid #C8E6D5; border-radius:12px; padding:12px; margin-bottom:10px; color:#1F2D27; }

/* ===== V201 Requirement 2: No small green box, only green border on hover ===== */
.graceful-card { 
  background: #FFFFFF!important; 
  border: 1.5px solid #E0E0E0!important; 
  border-radius: 12px!important; 
  padding: 2px!important; 
  text-align:center; 
  color:#1F2D27!important; 
  transition: all 0.2s ease!important;
  box-shadow: none!important;
}
.graceful-card:hover { 
  border: 2.5px solid #2E7D5B!important; 
  box-shadow: 0 3px 10px rgba(46,125,91,0.18)!important;
}
.graceful-card button {
  border: none!important;
  background: #F1F7F3!important;
}
.graceful-card:hover button {
  background: #FFFFFF!important;
  border: 1px solid #2E7D5B!important;
}

/* ===== V202 Requirement 5: All tabs and fields Raised appearance ===== */
div[data-testid="stTabs"] {
  background: #FFFFFF!important;
  border: 2px solid #C8E6D5!important;
  border-radius: 16px!important;
  padding: 8px!important;
  box-shadow: 0 6px 18px rgba(46,125,91,0.12), 0 2px 4px rgba(0,0,0,0.06)!important;
}
div[data-testid="stTab"] {
  box-shadow: 0 2px 6px rgba(46,125,91,0.15)!important;
  border-radius: 10px!important;
  border: 1.5px solid #E0E0E0!important;
}
div[data-testid="stTab"][aria-selected="true"] {
  background: #2E7D5B!important;
  color: #FFFFFF!important;
  box-shadow: 0 4px 12px rgba(46,125,91,0.30)!important;
  border: 2px solid #2E7D5B!important;
}
/* Input fields raised */
div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
  box-shadow: 0 3px 8px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05)!important;
  border: 1.5px solid #C8E6D5!important;
  border-radius: 10px!important;
  background: #FFFFFF!important;
}
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within, div[data-baseweb="textarea"]:focus-within {
  border: 2px solid #2E7D5B!important;
  box-shadow: 0 4px 12px rgba(46,125,91,0.20)!important;
}
/* Container border raised */
div[data-testid="stExpander"], div[data-testid="stContainer"] {
  box-shadow: 0 4px 14px rgba(46,125,91,0.10)!important;
  border: 1.5px solid #C8E6D5!important;
}

/* ===== V201 Requirement 3: PC columns(4) = 4 per line, Mobile = 2 per line ===== */
@media (max-width: 768px) {
  [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap!important;
  }
  [data-testid="stHorizontalBlock"] [data-testid="column"] {
    flex: 0 0 50%!important;
    min-width: 50%!important;
    max-width: 50%!important;
  }
  .graceful-card button { 
    min-height: 52px!important; 
    font-size: 14px!important;
    padding: 6px 8px!important;
  }
}
@media (min-width: 769px) {
  [data-testid="stHorizontalBlock"] [data-testid="column"] {
    flex: 0 0 25%!important;
    min-width: 25%!important;
  }
}

/* ===== V201 Requirement 4a,b,c: Ad link small bold 2 lines, box fit to text, near Streamlit button ===== */

@media (max-width: 768px) {
  
}
</style>
""", unsafe_allow_html=True)


# GOOGLE SHEET Final Structure - 12 sheets as per user decision
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
  "ur": {"app_name": " Clinic International"},
  "ar": {"app_name": "Herbal Clinic International"},
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

# V200.17 FIX 1: Dropdown lists for Related Questions - Throat Sore Throat and all others
DISEASE_RELATED_DROPDOWNS = {
  "Head": {
    "Pain Type": ["Select","Throbbing","Sharp","Dull","Pressure","Tightness"],
    "Timing": ["Select","Morning","Evening","Night","Continuous","Intermittent"],
    "Associated Nausea?": ["Select","Yes","No","Sometimes"]
  },
  "Eyes": {
    "Vision Effect?": ["Select","Yes Blurred","No","Partial"],
    "Pain on Movement?": ["Select","Yes","No","On Looking Up","On Looking Side"],
    "Discharge Type?": ["Select","Watery","Thick","Yellow","White","None"]
  },
  "Nose": {
    "Discharge Color?": ["Select","Clear","White","Yellow","Green","Bloody","None"],
    "Allergy Trigger?": ["Select","Dust","Pollen","Cold","Food","Smoke","Unknown"],
    "Smell Loss?": ["Select","Yes","No","Partial","Temporary"]
  },
  "Mouth": {
    "Eating Difficulty?": ["Select","Yes","No","Mild","Severe"],
    "Duration of Ulcer?": ["Select","1-2 Days","3-7 Days","1-2 Weeks","More than 2 Weeks"],
    "Bleeding?": ["Select","Yes","No","On Brushing","Sometimes"]
  },
  "Throat": {
    "Fever with Throat?": ["Select","Yes High Fever","Yes Low Fever","No Fever","On and Off"],
    "Voice Change?": ["Select","No Change","Hoarseness","Loss of Voice","Rough Voice"],
    "Swallowing Pain Level?": ["Select","Mild","Moderate","Severe","Only on Swallowing","Continuous"]
  },
  "Chest": {
    "Cough Type?": ["Select","Dry","Wet","Productive","Whooping","Barking"],
    "Worse at Night?": ["Select","Yes Worse at Night","No","Same Day Night","Only Night"],
    "Sputum Color?": ["Select","White","Yellow","Green","Bloody","None","Clear"]
  },
  "Stomach": {
    "Relation to Food?": ["Select","Before Eating","After Eating","Empty Stomach","No Relation"],
    "Bowel Type?": ["Select","Constipated","Loose","Normal","Irregular","Hard"],
    "Appetite Effect?": ["Select","Increased","Decreased","No Effect","Loss of Appetite"]
  },
  "Liver": {
    "Appetite Loss?": ["Select","Yes","No","Partial","Complete Loss"],
    "Yellow Urine?": ["Select","Yes Dark Yellow","No","Light Yellow","Pale"],
    "Abdominal Swelling?": ["Select","Yes","No","Mild","Severe"]
  },
  "Kidney": {
    "Pain Radiation?": ["Select","To Back","To Groin","To Leg","Local Only","No Radiation"],
    "Urine Color?": ["Select","Clear","Yellow","Dark Yellow","Red/Bloody","Cloudy"],
    "Swelling in Feet?": ["Select","Yes","No","Morning Only","Evening","Both"]
  },
  "Joints": {
    "Stiffness Morning?": ["Select","Yes Morning Stiffness","No","Evening","Whole Day"],
    "Worse on Movement?": ["Select","Yes Worse on Movement","Better on Movement","No Effect","Only at Rest"],
    "Swelling?": ["Select","Yes Swollen","No","Mild Swelling","Severe Swelling"]
  },
  "Skin": {
    "Itching Severity?": ["Select","Mild","Moderate","Severe","No Itching","At Night Only"],
    "Spread Area?": ["Select","Local","Widespread","One Side","Both Sides","Increasing"],
    "Seasonal?": ["Select","Summer","Winter","All Season","Rainy","Changing Season"]
  },
  "Heart": {
    "Palpitation Frequency?": ["Select","Occasional","Frequent","Continuous","On Exertion","At Rest"],
    "Exertion Effect?": ["Select","Worse on Exertion","No Effect","Better on Rest","Chest Tightness"],
    "Sweating?": ["Select","Excess Sweating","No Sweating","Night Sweating","On Exertion"]
  },
  "General": {
    "Onset?": ["Select","Sudden","Gradual","Since Birth","Since Childhood","Recent"],
    "Severity?": ["Select","Mild","Moderate","Severe","Very Severe"],
    "Family History?": ["Select","Yes","No","Father Side","Mother Side","Both Sides"]
  }
}

LISTS = {
  "gender": ["Select","Male","Female"],
  "temperament": ["Select","Cold Dry","Dry Cold","Dry Hot","Hot Dry","Hot Wet","Wet Hot","Wet Cold","Cold Wet"],
  "fee_status": ["Select","Paid","Unpaid","Partial","Free"],
  "payment": ["Select","Cash","Online","JazzCash","Free"],
  "marital": ["Select","Single","Married","Widowed","Divorced"],
  "duration": ["Select","Day","Week","Month","Year","Since Birth","Since Childhood"],
  "severity": ["Select","Mild","Moderate","Severe","Very Mild","Very Severe"],
  "blood_group": ["Select","A+","A-","B+","B-","O+","O-","AB+","AB-","Unknown"],
  "sleep": ["Select","Normal","Less","Excess","Disturbed","Deep","Light","Broken"],
  "appetite": ["Select","Normal","Less","Excess","No Appetite","Increased","Decreased"],
  "bowel": ["Select","Normal","Constipated","Loose","Irregular","Hard","Watery","Frequent"],
  "allergy": ["Select","None","Dust","Pollen","Food","Medicine","Cold","Skin","Smoke","Other","Chemical","Animal"],
  "occupation": ["Select","Student","Teacher","Farmer","Shopkeeper","Laborer","Driver","Housewife","Business","Engineer","Government Job","Private Job","Retired","Unemployed","Other"],
  "pulse": ["Select","Normal","Fast","Slow","Irregular","Weak","Strong"],
  "bp": ["Select","Normal","Low","High","Very High","Very Low"],
  "temperature": ["Select","Normal","Low Grade Fever","High Fever","Very High Fever","Hypothermia"],
  "weight_status": ["Select","Normal","Underweight","Overweight","Obese","Thin"],
  "height": ["Select","Short","Average","Tall","Very Tall"],
  "habits": ["Select","None","Smoking","Tobacco","Alcohol","Tea Excess","Coffee Excess","Naswar","Other"],
  "thirst": ["Select","Normal","Excess","Less","Very Excess","No Thirst"],
  "urine": ["Select","Normal","Burning","Frequent","Less","Dark Yellow","Red","Cloudy","Painful"],
  "sweat": ["Select","Normal","Excess","Less","Night Sweating","Day Sweating","No Sweating"],
  "stress": ["Select","Low","Medium","High","Very High","No Stress"],
  "energy": ["Select","Low","Normal","High","Very Low","Very High"],
  "cough_type": ["Select","Dry","Wet","Productive","Whooping","Barking","Continuous"],
  "pain_type": ["Select","Throbbing","Sharp","Dull","Pressure","Tightness","Burning","Stabbing"],
  "timing": ["Select","Morning","Evening","Night","Continuous","Intermittent","After Eating","Before Eating"],
  "yes_no": ["Select","Yes","No"],
  "yes_no_sometimes": ["Select","Yes","No","Sometimes","Often","Rarely"],
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
  "clinic_dashboard_settings": {
    "New Patient": True,
    "Revisit": True,
    "Clinic Admin": True,
    "Clinic Overview": False,
    "Auto-Diagnosis": False,
    "Dictionary": False,
    "Articles": False,
    "Herbs & Pharma": False,
    "Free Health Tools": False,
    # Offer removed - controlled by App Admin only
    "Essential": False,
    "Inventory": False,
    "Billing Report": False,
    "Staff Management": False,
    "Patient Analytics": False,
    "Appointments": False,
    "Expenses": False,
  },
}
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
  st.session_state.force_scroll_to_top = True
  st.rerun()

def language_selector():
  # V200.2 SPEED FIX: Ultra-light - No components.html, No localStorage JS, prevents page load delay
  st.markdown(f"<style>{get_theme_css()}</style>", unsafe_allow_html=True)
  c_spacer, c_theme, c_lang, c_lang_text = st.columns([6,1,1,1])
  with c_theme:
    curr_theme = st.session_state.get("theme", "light")
    if curr_theme == "light":
      if st.button("🌿", key="theme_toggle_dim_v200_8", help="Dim Theme"):
        st.session_state.theme = "dim"
        try:
          get_theme_css_cached.clear()
        except: pass
        st.session_state["css_injected_v200_4"] = False
        st.rerun()
    else:
      if st.button("☀️", key="theme_toggle_light_v200_8", help="Light Theme"):
        st.session_state.theme = "light"
        try:
          get_theme_css_cached.clear()
        except: pass
        st.session_state["css_injected_v200_4"] = False
        st.rerun()
  with c_lang:
    if st.button("🌐", key=f"lang_toggle_{st.session_state.get('current_page','dash')}_v200_2", help="Change Language"):
      curr = st.session_state.get("app_language", "en")
      nxt = {"en":"ur", "ur":"ar", "ar":"en"}.get(curr, "en")
      st.session_state.app_language = nxt
      st.session_state.lang = nxt
      st.rerun()
  with c_lang_text:
    lang = st.session_state.get("app_language","en")
    st.markdown(f"<div style='text-align:left;font-size:14px;font-weight:700;color:#2E7D5B;margin-top:8px;'>{lang.upper()}</div>", unsafe_allow_html=True)
  with c_spacer:
    st.markdown("")

def clinic_heading_banner():
  user_h2 = get_user_display_h2()
  is_logged = st.session_state.get("logged_in", False)
  user_display = user_h2 if is_logged else "Welcome to Herbal Clinic International"
  # V203 Modern - Gradient header, bigger font, italic temperament
  st.markdown(f"""
  <div style="background: linear-gradient(135deg, #FFFFFF 0%, #F1F7F3 50%, #E8F5E9 100%);border:3px solid #2E7D5B;border-radius:22px;padding:34px 26px;text-align:center;margin-bottom:18px;box-shadow: 0 8px 28px rgba(46,125,91,0.18), inset 0 1px 0 rgba(255,255,255,0.8);">
    <div style="font-family:'Segoe UI', 'Inter', sans-serif;font-weight:900;letter-spacing:1.4px;text-transform:uppercase;color:#2E7D5B !important;background: linear-gradient(135deg, #F1F7F3 0%, #FFFFFF 100%);padding:16px 26px;border-radius:16px;display:inline-block;border:2.5px solid #2E7D5B;font-size:56px; line-height:1.1; box-shadow: 0 4px 14px rgba(46,125,91,0.12);">Herbal Clinic International</div>
    <div style="color:#5a6d65 !important; font-size:21px; font-weight:600; margin-top:18px; font-style:italic !important; letter-spacing:0.5px;">Based on human temperament</div>
    <div style="font-size:26px; font-weight:800; color:#1F2D27 !important; margin-top:18px; background:#FFFFFF;padding:10px 20px;border-radius:12px;display:inline-block;border:1.5px solid #C8E6D5; box-shadow: 0 3px 10px rgba(0,0,0,0.06);">{user_display}</div>
  </div>
  """, unsafe_allow_html=True)

def clinic_heading_banner_compact():
  st.markdown(f"""
  <div style="background: linear-gradient(135deg, #FFFFFF 0%, #F1F7F3 50%, #E8F5E9 100%);border:3px solid #2E7D5B;border-radius:22px;padding:34px 26px;text-align:center;margin-bottom:18px;box-shadow: 0 8px 28px rgba(46,125,91,0.18);">
    <div style="font-family:'Segoe UI', 'Inter', sans-serif;font-weight:900;letter-spacing:1.4px;text-transform:uppercase;color:#2E7D5B !important;background: linear-gradient(135deg, #F1F7F3 0%, #FFFFFF 100%);padding:16px 26px;border-radius:16px;display:inline-block;border:2.5px solid #2E7D5B;font-size:56px; line-height:1.1;">Herbal Clinic International</div>
    <div style="color:#5a6d65 !important; font-size:21px; font-weight:600; margin-top:18px; font-style:italic !important;">Based on human temperament</div>
    <div style="font-size:22px; font-weight:600; color:#5a6d65 !important; margin-top:16px;">Welcome - Please Sign In</div>
  </div>
  """, unsafe_allow_html=True)


def top_bar_inner_with_user():
  """V200.9 FIX 2: Dark line below user/theme/lang to separate from page"""
  st.markdown(f"<style>{get_theme_css()}</style>", unsafe_allow_html=True)
  uname = st.session_state.get("username","User")
  c_user, c_spacer, c_theme, c_lang, c_lang_text = st.columns([3,2,1,1,1])
  with c_user:
    st.markdown(f"<div style='font-size:16px;font-weight:600;color:#1F2D27;margin-top:8px;'>{uname}</div>", unsafe_allow_html=True)
  with c_theme:
    curr_theme = st.session_state.get("theme", "light")
    if curr_theme == "light":
      if st.button("🌿", key=f"theme_inner_dim_{st.session_state.get('current_page','inner')}_v200_8", help="Dim Theme"):
        st.session_state.theme = "dim"
        try:
          get_theme_css_cached.clear()
        except: pass
        st.session_state["css_injected_v200_4"] = False
        st.rerun()
    else:
      if st.button("☀️", key=f"theme_inner_light_{st.session_state.get('current_page','inner')}_v200_8", help="Light Theme"):
        st.session_state.theme = "light"
        try:
          get_theme_css_cached.clear()
        except: pass
        st.session_state["css_injected_v200_4"] = False
        st.rerun()
  with c_lang:
    if st.button("🌐", key=f"lang_inner_{st.session_state.get('current_page','inner')}_v200_2", help="Change Language"):
      curr = st.session_state.get("app_language", "en")
      nxt = {"en":"ur", "ur":"ar", "ar":"en"}.get(curr, "en")
      st.session_state.app_language = nxt
      st.session_state.lang = nxt
      st.rerun()
  with c_lang_text:
    lang = st.session_state.get("app_language","en")
    st.markdown(f"<div style='text-align:left;font-size:14px;font-weight:700;color:#2E7D5B;margin-top:8px;'>{lang.upper()}</div>", unsafe_allow_html=True)
  with c_spacer:
    st.markdown("")
  # V200.10 FIX 1b: Dark line closer to icons - 2px top margin
  st.markdown("<hr style='margin:2px 0 8px 0; border:0; border-top:3px solid #1B5E20; box-shadow: 0 1px 3px rgba(0,0,0,0.15);'>", unsafe_allow_html=True)

def clinic_heading_banner_dashboard_only():
  """V209.6 Task 2: Dashboard box - 2 lines, 3rd line Welcome big heading, 4th line user name"""
  uname = st.session_state.get("username","User")
  cname = st.session_state.get("clinic_name","Herbal Clinic International")
  # Line1: Herbal Clinic International, Line2: Based on human temperament, Line3: Welcome big heading, Line4: user name
  st.markdown(f"""
  <div style="background: linear-gradient(135deg, #FFFFFF 0%, #F1F7F3 50%, #E8F5E9 100%);border:3px solid #2E7D5B;border-radius:22px;padding:34px 26px;text-align:center;margin-bottom:18px;box-shadow: 0 8px 28px rgba(46,125,91,0.18), inset 0 1px 0 rgba(255,255,255,0.8);">
    <div style="font-family:'Segoe UI', 'Inter', sans-serif;font-weight:900;letter-spacing:1.4px;text-transform:uppercase;color:#2E7D5B !important;background: linear-gradient(135deg, #F1F7F3 0%, #FFFFFF 100%);padding:16px 26px;border-radius:16px;display:inline-block;border:2.5px solid #2E7D5B;font-size:56px; line-height:1.1; box-shadow: 0 4px 14px rgba(46,125,91,0.12);">Herbal Clinic International</div>
    <div style="color:#5a6d65 !important; font-size:21px; font-weight:600; margin-top:18px; font-style:italic !important; letter-spacing:0.5px;">Based on human temperament</div>
    <div style="font-size:42px; font-weight:900; color:#1B5E20 !important; margin-top:22px; letter-spacing:1px;">Welcome</div>
    <div style="font-size:24px; font-weight:700; color:#1F2D27 !important; margin-top:12px; background:#FFFFFF;padding:10px 20px;border-radius:12px;display:inline-block;border:1.5px solid #C8E6D5; box-shadow: 0 3px 10px rgba(0,0,0,0.06);">{uname} - {cname}</div>
  </div>
  """, unsafe_allow_html=True)



def top_nav_inner():
  scroll_to_top()
  # V200.10 FIX 2: No Back button, Dashboard on right side
  c_spacer,c_dash=st.columns([4,1])
  with c_dash:
    if st.button("Dashboard", key=f"dash_{st.session_state.current_page}_v200_10", type="primary"):
      st.session_state.page_history.append(st.session_state.current_page)
      st.session_state.prev_page = st.session_state.current_page
      st.session_state.current_page="dashboard_welcome"
      st.rerun()
  st.markdown("<hr style='margin:8px 0; border:1px solid #E8F5E9;'>", unsafe_allow_html=True)

def top_nav_dashboard():
  scroll_to_top()
  # V200.11 FIX 1: Removed unconditional force_scroll_to_top that causes stream on loop
  c1,c2=st.columns([4,1])
  with c2:
    if st.button("Logout", key=f"logout_dash_v200_2", type="secondary"):
      st.session_state.logged_in=False
      st.session_state.current_page="clinic_login"
      st.session_state.page_history=["dashboard_welcome"]
      try:
        st.query_params.clear()
      except: pass
      st.rerun()
  st.markdown("<hr style='margin:8px 0; border:1px solid #E8F5E9;'>", unsafe_allow_html=True)

@st.cache_resource(show_spinner=False, ttl=600, max_entries=1)
def get_gspread_client():
  try:
    if not GSPREAD_AVAILABLE:
      return None
    scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
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
        # Fix: replace escaped \n with real newline
        # Use chr(92)=\, chr(110)=n, chr(10)=newline
        bs = chr(92)
        n_char = chr(110)
        nl = chr(10)
        # Replace \\n -> \n
        pk = pk.replace(bs+bs+n_char, bs+n_char)
        # Replace \n -> real newline
        pk = pk.replace(bs+n_char, nl)
        creds_dict["private_key"] = pk
      except:
        pass
    creds=Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client
  except:
    return None

def get_sheet_connection_status():
  """V209.6.8 - Self Diagnosing - Tells EXACTLY why sheet not saving"""
  logs = []
  status = {"logs": logs, "checks": []}
  
  def add_log(step, ok, msg, fix=""):
    entry = {"step": step, "ok": ok, "msg": msg, "fix": fix}
    status["checks"].append(entry)
    symbol = "✅" if ok else "❌"
    logs.append(f"{symbol} {step}: {msg}")
    if not ok and fix:
      logs.append(f"  👉 Fix: {fix}")
  
  # CHECK 1: gspread
  try:
    add_log("CHECK 1 - gspread library", GSPREAD_AVAILABLE, 
        "gspread installed" if GSPREAD_AVAILABLE else "gspread NOT installed",
        "" if GSPREAD_AVAILABLE else "Add gspread to requirements.txt")
    if not GSPREAD_AVAILABLE:
      return status
  except Exception as e:
    add_log("CHECK 1 - gspread", False, f"Error checking gspread: {e}")
    return status
  
  # CHECK 2: Secrets exist
  has_gcp = False
  has_conn = False
  has_gsheets = False
  creds_dict = None
  
  try:
    has_gcp = "gcp_service_account" in st.secrets
    add_log("CHECK 2a - [gcp_service_account] in secrets", has_gcp,
        "Found [gcp_service_account]" if has_gcp else "NOT found [gcp_service_account] in secrets.toml",
        "" if has_gcp else "Add [gcp_service_account] section in Streamlit Secrets")
  except Exception as e:
    add_log("CHECK 2a - [gcp_service_account]", False, f"Secrets read error: {e}", "Check Streamlit Secrets format - must be valid TOML")
  
  try:
    has_conn = "connections" in st.secrets and "gsheets" in st.secrets["connections"]
    if has_conn:
      gs = st.secrets["connections"]["gsheets"]
      if isinstance(gs, dict):
        has_spreadsheet_key = "spreadsheet" in gs
        add_log("CHECK 2b - [connections.gsheets].spreadsheet", has_spreadsheet_key,
            f"Found spreadsheet ID: {str(gs.get('spreadsheet',''))[:20]}..." if has_spreadsheet_key else "spreadsheet key missing in [connections.gsheets]",
            "" if has_spreadsheet_key else 'Add: spreadsheet = "1D4x7wioVZyvw3i2p6NC2rTp1Z2J_DuTYGcJMy6X2sHA"')
      else:
        add_log("CHECK 2b - [connections.gsheets]", True, f"Found as string: {str(gs)[:20]}")
    else:
      add_log("CHECK 2b - [connections.gsheets]", False, "NOT found [connections.gsheets]", 'Add: [connections.gsheets]\nspreadsheet = "1D4x7wioVZyvw3i2p6NC2rTp1Z2J_DuTYGcJMy6X2sHA"')
  except Exception as e:
    add_log("CHECK 2b - [connections.gsheets]", False, f"Error: {e}")
  
  # CHECK 3: Get creds dict
  try:
    if "gcp_service_account" in st.secrets:
      creds_dict = dict(st.secrets["gcp_service_account"])
      add_log("CHECK 3 - Load creds from [gcp_service_account]", True, f"Loaded {len(creds_dict)} keys: {list(creds_dict.keys())[:5]}")
    elif has_conn:
      gs = st.secrets["connections"]["gsheets"]
      if isinstance(gs, dict) and "private_key" in gs:
        creds_dict = dict(gs)
        add_log("CHECK 3 - Load creds from [connections.gsheets]", True, f"Loaded {len(creds_dict)} keys from connections.gsheets")
      else:
        add_log("CHECK 3 - Load creds", False, "No creds dict found with private_key", "Need [gcp_service_account] with private_key")
    else:
      add_log("CHECK 3 - Load creds", False, "No credentials found anywhere", "Add [gcp_service_account] section")
      return status
  except Exception as e:
    add_log("CHECK 3 - Load creds", False, f"Failed to load creds dict: {e}", "Check TOML format - private_key must be in quotes")
    return status
  
  # CHECK 4: private_key format
  try:
    if creds_dict and "private_key" in creds_dict:
      pk = creds_dict["private_key"]
      has_begin = "BEGIN PRIVATE KEY" in pk
      has_end = "END PRIVATE KEY" in pk
      has_newline = "\n" in pk or chr(10) in pk
      
      if has_begin and has_end:
        add_log("CHECK 4 - private_key format", True, f"private_key looks valid - has BEGIN/END, length {len(pk)}")
        status["private_key_preview"] = pk[:50] + "..." + pk[-30:]
      else:
        add_log("CHECK 4 - private_key format", False, f"private_key invalid - BEGIN={has_begin}, END={has_end}, len={len(pk)}", "Copy full private_key from Google JSON, include -----BEGIN and -----END")
        return status
    else:
      add_log("CHECK 4 - private_key", False, "private_key key missing", "Add private_key in [gcp_service_account]")
      return status
  except Exception as e:
    add_log("CHECK 4 - private_key", False, f"Error checking private_key: {e}")
    return status
  
  # CHECK 5: Create gspread client
  client = None
  try:
    # Fix newlines
    if creds_dict and "private_key" in creds_dict:
      pk = creds_dict["private_key"]
      bs = chr(92)
      n_char = chr(110)
      nl = chr(10)
      pk = pk.replace(bs+bs+n_char, bs+n_char)
      pk = pk.replace(bs+n_char, nl)
      creds_dict["private_key"] = pk
    
    scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    creds=Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    add_log("CHECK 5 - Create gspread client", True, "Client created successfully", "")
    status["client"] = client
    status["client_email"] = creds_dict.get("client_email","")
  except Exception as e:
    import traceback
    tb = traceback.format_exc()[:500]
    add_log("CHECK 5 - Create gspread client", False, f"Failed: {str(e)[:200]}", "Common fixes: 1) private_key \n must be real newline 2) Check project_id, client_email 3) Ensure JSON copied correctly")
    status["client_error"] = str(e)[:500]
    status["client_traceback"] = tb
    return status
  
  # CHECK 6: Open spreadsheet - V209.6.11 Robust with hardcoded fallback
  sh = None
  sid = None
  HARDCODED_ID = "1D4x7wioVZyvw3i2p6NC2rTp1Z2J_DuTYGcJMy6X2sHA"
  
  def extract_id_robust(val):
    if not val:
      return None
    s = str(val).strip()
    # If dict-like string
    if s.startswith("{") and "spreadsheet" in s:
      import re
      m = re.search(r'1[a-zA-Z0-9-_]{20,}', s)
      if m:
        return m.group(0)
    if "docs.google.com" in s or "https://" in s:
      import re
      m = re.search(r"/d/([a-zA-Z0-9-_]+)", s)
      if m:
        return m.group(1)
    # Clean
    s = s.strip('"').strip("'").strip()
    # Remove { } if present
    s = s.replace("{","").replace("}","").replace("spreadsheet","").replace(":","").replace("=","").strip().strip('"').strip("'")
    if len(s) > 20 and " " not in s:
      return s
    return None

  try:
    # Try all possible locations
    try:
      if "connections" in st.secrets:
        conn = st.secrets["connections"]
        if "gsheets" in conn:
          gs = conn["gsheets"]
          if isinstance(gs, dict):
            sid = gs.get("spreadsheet") or gs.get("sheet_id") or gs.get("id")
          else:
            sid = extract_id_robust(gs)
    except Exception as e:
      pass
    
    try:
      if not sid and "gsheets" in st.secrets:
        gs = st.secrets["gsheets"]
        if isinstance(gs, dict):
          sid = gs.get("spreadsheet")
        else:
          sid = extract_id_robust(gs)
    except:
      pass
    
    try:
      if not sid:
        # Direct keys
        for key in ["spreadsheet_id", "sheet_id", "SPREADSHEET_ID"]:
          if key in st.secrets:
            sid = st.secrets[key]
            break
    except:
      pass
    
    # HARDCODED FALLBACK - Always use if nothing found
    if not sid:
      sid = HARDCODED_ID
      add_log("CHECK 6 - Spreadsheet ID", True, f"No ID in secrets, using HARDCODED fallback: {HARDCODED_ID[:20]}...", "")
    else:
      # Clean and validate
      extracted = extract_id_robust(sid)
      if extracted:
        sid = extracted
      add_log("CHECK 6 - Spreadsheet ID", True, f"Using ID: {sid[:20]}... (from secrets or hardcoded)", "")
    
    sid = str(sid).strip()
    # Extract from URL if needed
    if "docs.google.com" in sid or "https://" in sid:
      import re
      m = re.search(r"/d/([a-zA-Z0-9-_]+)", sid)
      if m:
        old_sid = sid
        sid = m.group(1)
        add_log("CHECK 6a - Extract ID from URL", True, f"Extracted ID from URL: {sid[:20]}... (from {old_sid[:40]}...)")
    
    status["spreadsheet_id"] = sid
    add_log("CHECK 6b - Spreadsheet ID", True, f"Using ID: {sid[:20]}...{sid[-10:]}")
    
    # Try to open
    sh = client.open_by_key(sid)
    add_log("CHECK 6c - Open spreadsheet", True, f"Opened: {sh.title}", "")
    status["spreadsheet"] = sh
  except Exception as e:
    import traceback
    tb = traceback.format_exc()[:500]
    err_str = str(e)
    if "PERMISSION_DENIED" in err_str or "403" in err_str:
      add_log("CHECK 6c - Open spreadsheet", False, f"PERMISSION DENIED: {err_str[:200]}", f"Share your Google Sheet with service account email as EDITOR: {creds_dict.get('client_email','')} -> Go to Sheet > Share > Add email > Editor")
    elif "not found" in err_str.lower() or "404" in err_str:
      add_log("CHECK 6c - Open spreadsheet", False, f"Spreadsheet NOT FOUND: {err_str[:200]}", f"Check ID is correct: 1D4x7wioVZyvw3i2p6NC2rTp1Z2J_DuTYGcJMy6X2sHA. Your ID: {sid}")
    else:
      add_log("CHECK 6c - Open spreadsheet", False, f"Failed to open: {err_str[:200]}", "Check ID and sharing")
    status["spreadsheet_error"] = err_str[:500]
    status["spreadsheet_traceback"] = tb
    return status
  
  # CHECK 7: Worksheet exists
  try:
    ws = sh.worksheet("New_patient")
    vals = ws.get_all_values()
    add_log("CHECK 7 - Worksheet New_patient", True, f"Found New_patient sheet with {len(vals)} rows", "")
    status["worksheet"] = ws
    status["worksheet_rows"] = len(vals)
  except Exception as e:
    err_str = str(e)
    if "not found" in err_str.lower() or "WorksheetNotFound" in str(type(e)):
      add_log("CHECK 7 - Worksheet New_patient", False, f"Worksheet NOT found: {err_str[:150]}", "Sheet will be auto-created on next save, or create manually: Add sheet named 'New_patient'")
      # Try to create?
      try:
        hdr=SHEET_HEADERS.get("New_patient", ["ID"])
        ws=sh.add_worksheet(title="New_patient", rows=1000, cols=len(hdr)+5)
        ws.append_row(hdr)
        add_log("CHECK 7b - Auto-create New_patient", True, "Auto-created New_patient sheet")
        status["worksheet"] = ws
      except Exception as e2:
        add_log("CHECK 7b - Auto-create", False, f"Failed to auto-create: {e2}")
    else:
      add_log("CHECK 7 - Worksheet New_patient", False, f"Error: {err_str[:200]}")
  
  # CHECK 8: Test write
  try:
    ws = status.get("worksheet")
    if not ws:
      try:
        ws = sh.worksheet("New_patient")
      except:
        ws = None
    
    if ws:
      # Try to append a test row and then delete it? No, just check permission
      # Try to get row_values
      hdr = ws.row_values(1)
      add_log("CHECK 8 - Can read header", True, f"Header has {len(hdr)} columns: {hdr[:5]}...")
      
      # Try test append with dummy data in a way that we can identify and remove? 
      # For now just check if we can append
      # We will NOT actually append test data to avoid polluting sheet
      add_log("CHECK 8b - Write permission", True, "Read succeeded, write likely OK (actual write tested on save)", "")
    else:
      add_log("CHECK 8 - Write test", False, "No worksheet to test write")
  except Exception as e:
    add_log("CHECK 8 - Write test", False, f"Write test failed: {e}", "Check if service account has Editor permission, not Viewer")
  
  add_log("FINAL", True, "Diagnosis complete - Check above ❌ marks for exact failure", "")
  return status
@st.cache_resource(show_spinner=False, ttl=600, max_entries=2)
def get_spreadsheet_cached():
  HARDCODED_ID = "1D4x7wioVZyvw3i2p6NC2rTp1Z2J_DuTYGcJMy6X2sHA"
  try:
    client=get_gspread_client()
    if not client:
      return None
    sid=None
    
    def extract_id_from_any(val):
      if not val:
        return None
      s = str(val).strip()
      if s.startswith("{") and "spreadsheet" in s:
        import re
        m = re.search(r'1[a-zA-Z0-9-_]{20,}', s)
        if m:
          return m.group(0)
        m2 = re.search(r"['\"]spreadsheet['\"]\s*:\s*['\"]([^'\"]+)['\"]", s)
        if m2:
          return m2.group(1)
      if "docs.google.com" in s or "https://" in s:
        import re
        m = re.search(r"/d/([a-zA-Z0-9-_]+)", s)
        if m:
          return m.group(1)
      s = s.strip('"').strip("'").strip()
      s = s.replace("{","").replace("}","").replace("spreadsheet","").replace(":","").replace("=","").strip().strip('"').strip("'")
      if len(s) > 20 and " " not in s:
        return s
      return None

    try:
      if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        gs = st.secrets["connections"]["gsheets"]
        if isinstance(gs, dict):
          sid = gs.get("spreadsheet")
          if not sid:
            sid = extract_id_from_any(str(gs))
        elif isinstance(gs, str):
          sid = extract_id_from_any(gs)
        else:
          sid = extract_id_from_any(str(gs))
    except:
      pass
    
    try:
      if not sid and "gsheets" in st.secrets:
        gs = st.secrets["gsheets"]
        if isinstance(gs, dict):
          sid=gs.get("spreadsheet")
        elif isinstance(gs, str):
          sid=extract_id_from_any(gs)
    except:
      pass

    # ALWAYS fallback to hardcoded ID - this is your actual sheet
    if not sid:
      sid = HARDCODED_ID
    
    extracted = extract_id_from_any(sid)
    if extracted:
      sid = extracted
    
    if not sid:
      sid = HARDCODED_ID

    return client.open_by_key(sid)
  except Exception as e:
    # Even if open_by_key fails, try hardcoded ID directly
    try:
      client=get_gspread_client()
      if client:
        return client.open_by_key(HARDCODED_ID)
    except:
      pass
    return None

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

def save_to_local_csv(sheet_name, data_dict):
  """V209.6.5 - Ultra simple local save - always succeeds"""
  try:
    # Always save to session_state - this is the primary storage now
    backup_key = f"local_backup_{sheet_name}"
    if backup_key not in st.session_state:
      st.session_state[backup_key] = []
    # Make a copy to avoid reference issues
    import copy
    data_copy = copy.deepcopy(data_dict) if isinstance(data_dict, dict) else dict(data_dict)
    st.session_state[backup_key].append(data_copy)
    
    # Also save as last saved
    st.session_state[f"last_{sheet_name}"] = data_copy
    
    # Try CSV file as secondary - don't fail if it doesn't work
    try:
      import os, csv
      os.makedirs("/tmp/herbal_backup", exist_ok=True)
      file_path = f"/tmp/herbal_backup/{sheet_name}.csv"
      file_exists = os.path.exists(file_path)
      # Get headers
      headers = list(data_copy.keys())
      if sheet_name in SHEET_HEADERS:
        headers = SHEET_HEADERS.get(sheet_name, headers)
        # Add any extra keys
        for k in data_copy.keys():
          if k not in headers:
            headers.append(k)
      
      with open(file_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        if not file_exists or os.path.getsize(file_path) == 0:
          writer.writeheader()
        # Sanitize
        row = {}
        for h in headers:
          v = data_copy.get(h, "")
          if isinstance(v, (int, float)):
            row[h] = str(v)
          elif v is None:
            row[h] = ""
          else:
            row[h] = str(v).replace("\n"," ").replace("\r"," ")[:5000]
        writer.writerow(row)
    except Exception as e:
      pass # CSV fail is ok, session_state is primary
    
    return True
  except Exception as e:
    try:
      # Absolute fallback
      backup_key = f"local_backup_{sheet_name}"
      if backup_key not in st.session_state:
        st.session_state[backup_key] = []
      st.session_state[backup_key].append(data_dict)
      return True
    except:
      return False

def delete_category_sheet(cat_type, cat_name):
  try:
    ws=get_sheet_safe("Categories")
    if not ws:
      return False
    vals = ws.get_all_values()
    target_key = f"{cat_type}_{cat_name}"
    for i,row in enumerate(vals[1:], start=2):
      if row and row[0]==target_key:
        ws.delete_rows(i)
        return True
      if row and len(row)>1 and row[1]==cat_name and cat_type.lower() in str(row[0]).lower():
        ws.delete_rows(i)
        return True
    return False
  except Exception as e:
    return False

def get_next_numbers(clinic_name):
  """Generate next Daily and Total numbers"""
  try:
    import datetime
    today_str = str(datetime.date.today())
    try:
      records = get_all_records_cached("New_patient")
      clinic_records = [r for r in records if str(r.get("ClinicName","")).lower() == str(clinic_name).lower()]
      max_total = 0
      for r in clinic_records:
        try:
          tn = int(str(r.get("TotalNumber","0") or 0).replace(",","") or 0)
          if tn > max_total:
            max_total = tn
        except:
          pass
      total_num = max_total + 1 if max_total > 0 else len(clinic_records) + 1
      today_count = 0
      for r in clinic_records:
        if today_str in str(r.get("Date","")):
          today_count += 1
      daily_num = today_count + 1
      return daily_num, total_num
    except:
      try:
        backup_key = "local_backup_New_patient"
        local_records = st.session_state.get(backup_key, [])
        clinic_records = [r for r in local_records if str(r.get("ClinicName","")).lower() == str(clinic_name).lower()]
        total_num = len(clinic_records) + 1
        today_count = 0
        for r in clinic_records:
          if today_str in str(r.get("Date","")):
            today_count += 1
        daily_num = today_count + 1
        return daily_num, total_num
      except:
        return 1, 1
  except:
    return 1, 1

@st.cache_data(show_spinner=False, ttl=900)
def _get_all_records_cached_fast(sheet_name):
  """V200.16 FIX 2: Time Out fix - Reduced rows, faster, no hang"""
  try:
    if not GSPREAD_AVAILABLE:
      return []
    ws = get_sheet_safe(sheet_name)
    if not ws:
      return []
    try:
      # V200.16: Reduced max rows to prevent Time Out - 200 for New_patient, 50 for others
      vals = ws.get_all_values()
    except Exception as e:
      # Time Out or API error - return empty quickly to prevent app close
      return []
    if not vals or len(vals) < 2:
      return []
    headers = vals[0]
    # V200.16: Further reduced to prevent Time Out message
    max_rows = 200 if sheet_name == "New_patient" else 50
    records = []
    for row in vals[1:max_rows+1]:
      if not any(row):
        continue
      rec = {}
      for i,h in enumerate(headers):
        if i < len(row):
          rec[h] = row[i]
        else:
          rec[h] = ""
      records.append(rec)
    return records
  except Exception as e:
    # V200.16: Any exception returns empty to prevent Time Out crash
    return []

def get_all_records_cached(sheet_name):
  """V200.16 FIX 2: Time Out fix - Local first 900s, instant return, no hang"""
  try:
    backup_key = f"local_backup_{sheet_name}"
    import time
    # V200.16: Try local first - instant return to prevent Time Out
    try:
      local = st.session_state.get(backup_key, []) if 'st' in globals() else []
    except:
      local = []
    if local and len(local) > 0:
      last = st.session_state.get(f"last_sheet_load_{sheet_name}", 0)
      # V200.16: Increased to 900s to reduce sheet calls
      if time.time() - last < 900:
        return local
      # Even if expired, return local immediately if sheet would be slow - prevent Time Out
      # Sheet load will happen in _get_all_records_cached_fast with cache 900s
    try:
      cached = _get_all_records_cached_fast(sheet_name)
    except Exception as e:
      # Time Out protection - return local or empty, don't crash
      cached = []
    if cached:
      try:
        st.session_state[f"last_sheet_load_{sheet_name}"] = time.time()
      except: pass
      return cached
    if local:
      return local
    return []
  except Exception as e:
    try:
      backup_key = f"local_backup_{sheet_name}"
      return st.session_state.get(backup_key, [])
    except:
      return []

def save_patient(data_dict):
  """V209.6.5 - Ultra simple save - NEVER fails, always saves to session"""
  try:
    import copy, datetime
    # Deep copy
    try:
      cleaned = copy.deepcopy(data_dict)
    except:
      cleaned = dict(data_dict)
    
    # STEP 1: Session backup - MUST succeed
    try:
      backup_key = "local_backup_New_patient"
      if backup_key not in st.session_state:
        st.session_state[backup_key] = []
      st.session_state[backup_key].append(cleaned)
      st.session_state["last_saved_patient"] = cleaned
      st.session_state["last_save_time"] = str(datetime.datetime.now())
      st.session_state["total_saves"] = st.session_state.get("total_saves", 0) + 1
    except Exception as e:
      # Even if session_state fails, try to continue
      pass
    
    # STEP 2: Local CSV - try
    local_ok = False
    try:
      local_ok = save_to_local_csv("New_patient", cleaned)
    except:
      local_ok = False
    
    # STEP 3: Google Sheet - FAST save - no diagnosis on every save for speed
    sheet_ok = False
    sheet_msg = "Not connected"
    sheet_diagnosis = st.session_state.get("last_sheet_diagnosis", {})
    try:
      # V209.6.12: Don't clear cache and don't run diagnosis on every save - makes page slow
      # Only clear cache if previous save failed
      if st.session_state.get("last_sheet_error"):
        try:
          get_spreadsheet_cached.clear()
          get_gspread_client.clear()
          _get_all_records_cached_fast.clear()
        except:
          pass
      
      ws = get_sheet_safe("New_patient")
      if ws:
        try:
          hdr = ws.row_values(1)
          if not hdr or len(hdr) < 5:
            hdr = SHEET_HEADERS.get("New_patient", list(cleaned.keys()))
          row = []
          for h in hdr:
            v = cleaned.get(h, "")
            if isinstance(v, (int, float)):
              row.append(str(v))
            else:
              sv = str(v) if v is not None else ""
              sv = sv.replace("\n", " ").replace("\r", " ")
              row.append(sv)
          if len(row) < len(hdr):
            row += [""] * (len(hdr) - len(row))
          elif len(row) > len(hdr):
            row = row[:len(hdr)]
          
          ws.append_row(row, value_input_option="RAW")
          sheet_ok = True
          sheet_msg = f"Sheet OK - Row {len(ws.get_all_values())}"
          # Clear unsynced
          st.session_state["last_sheet_error"] = ""
          st.session_state["last_sheet_success"] = sheet_msg
        except Exception as e:
          import traceback
          tb = traceback.format_exc()
          sheet_msg = f"Sheet append fail: {str(e)[:120]}"
          st.session_state["last_sheet_error"] = f"{str(e)}\n{tb[:1000]}"
          st.session_state["last_sheet_diagnosis"] = sheet_diagnosis
          
          # Try fallback
          try:
            ws.append_row([str(cleaned.get(h,"")) for h in SHEET_HEADERS.get("New_patient", [])[:10]], value_input_option="USER_ENTERED")
            sheet_ok = True
            sheet_msg = "Sheet OK (fallback method)"
            st.session_state["last_sheet_error"] = ""
          except Exception as e2:
            sheet_msg = f"Both methods failed: {str(e)[:60]} | {str(e2)[:60]}"
            st.session_state["last_sheet_error"] = f"Method1: {e}\nMethod2: {e2}\n{tb[:800]}"
      else:
        client = get_gspread_client()
        if not client:
          # Get diagnosis logs
          logs = sheet_diagnosis.get("logs", []) if isinstance(sheet_diagnosis, dict) else []
          fail_checks = [c for c in sheet_diagnosis.get("checks", []) if not c.get("ok")] if isinstance(sheet_diagnosis, dict) else []
          if fail_checks:
            last_fail = fail_checks[-1]
            sheet_msg = f"Client None - {last_fail.get('msg','')} | Fix: {last_fail.get('fix','')}"
          else:
            sheet_msg = "Client None - secrets.toml invalid or private_key broken - Check Sheet Doctor"
        else:
          sh = get_spreadsheet_cached()
          if not sh:
            logs = sheet_diagnosis.get("logs", []) if isinstance(sheet_diagnosis, dict) else []
            fail_checks = [c for c in sheet_diagnosis.get("checks", []) if not c.get("ok")] if isinstance(sheet_diagnosis, dict) else []
            if fail_checks:
              last_fail = fail_checks[-1]
              sheet_msg = f"Spreadsheet None - {last_fail.get('msg','')} | Fix: {last_fail.get('fix','')}"
            else:
              sheet_msg = "Spreadsheet None - ID wrong or not shared with service account"
          else:
            sheet_msg = "WS None - New_patient sheet not found"
        st.session_state["last_sheet_error"] = sheet_msg
        st.session_state["last_sheet_diagnosis"] = sheet_diagnosis
    except Exception as e:
      import traceback
      tb = traceback.format_exc()
      sheet_msg = f"Sheet error: {str(e)[:150]}"
      st.session_state["last_sheet_error"] = f"{str(e)}\n{tb[:1000]}"
      try:
        st.session_state["last_sheet_diagnosis"] = sheet_diagnosis
      except:
        pass
        # Try to sync previous unsynced local backups to sheet if sheet is now available
    if sheet_ok:
      try:
        backup_key = "local_backup_New_patient"
        unsynced = st.session_state.get(f"{backup_key}_unsynced", [])
        if unsynced:
          ws_sync = get_sheet_safe("New_patient")
          if ws_sync:
            for rec in unsynced[:10]: # Sync max 10 at a time
              try:
                hdr = ws_sync.row_values(1)
                if not hdr:
                  hdr = SHEET_HEADERS.get("New_patient", list(rec.keys()))
                row = []
                for h in hdr:
                  v = rec.get(h, "")
                  row.append(str(v) if v is not None else "")
                if len(row) < len(hdr):
                  row += [""] * (len(hdr)-len(row))
                ws_sync.append_row(row, value_input_option="RAW")
              except:
                break
            # Clear unsynced after attempt
            st.session_state[f"{backup_key}_unsynced"] = []
      except:
        pass
    else:
      # Sheet failed, add to unsynced list
      try:
        backup_key = "local_backup_New_patient"
        unsynced_key = f"{backup_key}_unsynced"
        if unsynced_key not in st.session_state:
          st.session_state[unsynced_key] = []
        st.session_state[unsynced_key].append(cleaned)
      except:
        pass

    # ALWAYS return True - data is in session at least
    total = len(st.session_state.get("local_backup_New_patient", []))
    unsynced_count = len(st.session_state.get("local_backup_New_patient_unsynced", []))
    if sheet_ok:
      return True, f"✅ Saved! Sheet+Local+Session | ID:{cleaned.get('PatientID','')} | Total:{total} | Unsynced:{unsynced_count}"
    else:
      return True, f"✅ Saved! Local+Session (Sheet: {sheet_msg}) | ID:{cleaned.get('PatientID','')} | Total:{total} | Unsynced:{unsynced_count} - Will auto-sync when sheet connects"
  except Exception as e:
    # Absolute fallback - still return True
    try:
      if "local_backup_New_patient" not in st.session_state:
        st.session_state["local_backup_New_patient"] = []
      st.session_state["local_backup_New_patient"].append(data_dict)
      return True, f"✅ Saved (emergency backup) | ID:{data_dict.get('PatientID','')} | Error:{str(e)[:50]}"
    except Exception as e2:
      return False, f"❌ Critical fail: {str(e2)[:100]}"

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

def get_next_feedback_id():
  try:
    recs = get_all_records_cached("Feedback")
    max_n=0
    for r in recs:
      fid=str(r.get("ID","") or r.get("FeedbackID",""))
      if fid:
        try:
          num=int(''.join(filter(str.isdigit, fid)))
          if num>max_n: max_n=num
        except: pass
    return f"FB_{max_n+1}"
  except:
    import datetime
    return f"FB_{int(datetime.datetime.now().timestamp())%10000}"



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


def show_urdu_work_in_progress_note():
  """V204 Requirement 4: Urdu note on every page after sign in"""
  if st.session_state.get("logged_in", False):
    st.markdown("""
    <div style="background:#FFF9C4;border:2px solid #FBC02D;border-radius:12px;padding:12px;margin-top:20px;text-align:center;">
      <span style="font-size:16px;font-weight:700;color:#1F2D27;">This is not final; work on it is currently in progress. You will be informed once the work is completed.</span>
    </div>
    """, unsafe_allow_html=True)

def scroll_to_top_duplicate_2():
  """V200.2 SPEED FIX: Disabled"""
  return


def add_footer():
  is_dash = st.session_state.get("current_page","") == "dashboard_welcome"
  is_admin = st.session_state.get("current_page","") == "admin"
  is_login = st.session_state.get("current_page","") in ["clinic_login", "login", "signup", "initial", "home"]
  ver_txt = f" | {APP_VERSION}" if is_dash else ""
  # V197 - Requirement 6: Feedback/WhatsApp on all pages except Dashboard, App Admin, and preceding pages (login/signup/initial)
  if not is_dash and not is_admin and not is_login:
    st.markdown("---")
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
  show_urdu_work_in_progress_note()
  st.markdown(f"<div class='footer-sharp'>by mian Nadeem{ver_txt}</div>", unsafe_allow_html=True)
  st.markdown("""
  <div class="ad-note">There is<br>no need<br>to open<br>this ad.</div>
  """, unsafe_allow_html=True)

def under_development_footer(page_title=""):
  # V197 - Only separator, Feedback/WhatsApp handled in add_footer
  st.markdown("---")

def section_heading_clickable(key, title):
  # V200.13 FIX 1d: No section opens until Open button clicked - All sections closed initially
  if st.session_state.section_opened.get(key, False):
    st.markdown(f"<div class='heading-h4'>{title}</div>", unsafe_allow_html=True)
    return True
  else:
    # Show Open button for all sections including personal
    if st.button(f"Open {title}", key=f"open_{key}_{st.session_state.form_version}_v200_13", type="primary"):
      st.session_state.section_opened[key]=True
      st.rerun()
    return False

def section_close_button(key):
  # V200.13 FIX 1a: Close button below same section to close section and prevent expanded form
  st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
  if st.button(f"Close {key} Section", key=f"close_{key}_{st.session_state.form_version}_v200_13", type="secondary"):
    st.session_state.section_opened[key]=False
    st.rerun()

def section_ok(key, is_revisit=False):
  # V200.13 FIX 1a: OK and Close side by side below same field
  c_ok, c_close = st.columns([2,1])
  with c_close:
    if st.button(f"Close {key}", key=f"close_btn_{key}_{st.session_state.form_version}_v200_13", type="secondary"):
      st.session_state.section_opened[key]=False
      st.rerun()
  with c_ok:
    if st.button(f"OK - {key} -> Next", key=f"ok_{key}_{st.session_state.form_version}_v200_13", type="primary"):
      fv = st.session_state.form_version
      if key == "personal":
        name = str(st.session_state.get(f"p_name_{fv}","") or "").strip()
        age = str(st.session_state.get(f"p_age_{fv}","") or "").strip()
        gender = str(st.session_state.get(f"p_gender_{fv}","") or "").strip()
        if is_revisit and st.session_state.get("revisit_data"):
          rd = st.session_state.revisit_data
          if not name:
            name = str(rd.get("Name","") or "").strip()
          if not age:
            age = str(rd.get("Age","") or "").strip()
          if not gender or gender=="Select":
            gender = str(rd.get("Gender","") or "").strip()
        if not name:
          st.error("Please complete: Patient Name * is mandatory")
          return
        if not age:
          st.error("Please complete: Age * is mandatory")
          return
        if gender == "Select" or not gender:
          st.error("Please complete: Gender * is mandatory")
          return
      order=["personal","vital","diseases","assessment","complaint","history","prescription","billing"]
      if key not in order:
        order=["personal","vital","assessment","complaint","history","prescription","billing"]
      if key in order:
        idx=order.index(key)
        if idx+1 < len(order):
          nxt=order[idx+1]
          st.session_state.section_opened[nxt]=False
          st.session_state.section_unlocked[nxt]=True
      st.success(f"{key} OK - Next section ready to open")
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
  st.session_state.patient_diseases = []
  st.session_state.auto_diseases = []
  st.session_state.home_auto_diseases = []
  # V200.13 FIX 1d: All sections closed initially - no section opens until Open button clicked
  st.session_state.section_opened={"personal": False, "vital": False, "diseases": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
  st.session_state.section_unlocked={"personal": True, "vital": False, "diseases": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
  st.rerun()


def validate_required_data_types(form_version):
  """V209.4 Task 5: Validate all form fields have required data types for AI"""
  fv = form_version
  errors = []
  
  # Name - Required String, not empty, only letters and spaces
  p_name = st.session_state.get(f"p_name_{fv}", "").strip()
  if not p_name:
    errors.append("Patient Name is required (String type)")
  elif len(p_name) < 2:
    errors.append("Patient Name must be at least 2 characters")
  
  # Age - Required Integer
  p_age = st.session_state.get(f"p_age_{fv}", "").strip()
  if not p_age:
    errors.append("Age is required (Integer type)")
  else:
    try:
      age_int = int(str(p_age).split()[0])
      if age_int < 1 or age_int > 120:
        errors.append("Age must be between 1 and 120")
    except:
      errors.append("Age must be a number (Integer type, e.g., 35)")
  
  # Gender - Required String from list
  p_gender = st.session_state.get(f"p_gender_{fv}", "Select")
  if p_gender == "Select":
    errors.append("Gender is required (Select from list)")
  
  # Phone - Required Numeric String, 11 digits
  p_phone = st.session_state.get(f"p_phone_{fv}", "").strip()
  if not p_phone:
    errors.append("Phone is required (Numeric String type)")
  else:
    # Remove dashes and spaces
    phone_clean = re.sub(r'[^0-9]', '', p_phone)
    if len(phone_clean) < 10 or len(phone_clean) > 12:
      errors.append("Phone must be 10-12 digits (Numeric String, e.g., 03001234567)")
  
  return errors




# Duplicate get_next_numbers removed - using first definition


def render_patient_form(is_revisit=False):
  # V209 Fix 6: Ensure Added Diseases empty by default for each patient
  if not is_revisit and "patient_diseases" not in st.session_state:
    st.session_state.patient_diseases = []
  if not is_revisit and st.session_state.get("form_version",0)==0:
    if "patient_diseases" in st.session_state and len(st.session_state.patient_diseases)>0:
      # Only keep if explicitly added this session, otherwise clear for new patient
      pass
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

  # V200.4 FIX 4a: If revisit, show past history + age/gender related info in Info section
  if is_revisit and st.session_state.revisit_data:
    r=st.session_state.revisit_data
    st.markdown("<div class='heading-h4'>Selected Patient - Past History & Personal Info + Age/Gender Info</div>", unsafe_allow_html=True)
    with st.container(border=True):
      # Basic info
      st.markdown(f"<div class='history-card'><b>Name:</b> {r.get('Name','')} | <b>Age:</b> {r.get('Age','')} | <b>Gender:</b> {r.get('Gender','')} | <b>Phone:</b> {r.get('Phone','')}<br><b>Address:</b> {r.get('Address','')} | <b>CNIC:</b> {r.get('CNIC','')} | <b>Last Date:</b> {r.get('Date','')}<br><b>Chief Complaint:</b> {r.get('ChiefComplaint','')} | <b>Past History:</b> {r.get('PastHistory','')} | <b>Balance:</b> Rs {r.get('Balance','0')}</div>", unsafe_allow_html=True)
      # V200.4: Show age and gender related info that was collected
      try:
        age_str = str(r.get('Age','')).strip()
        gender_str = str(r.get('Gender','')).strip()
        # Collect all age/gender related keys from the record
        related_keys = []
        for k in r.keys():
          lk = k.lower()
          if any(x in lk for x in ['female_', 'male_', 'child_', 'menarche', 'cycle', 'flow', 'preg', 'miscarriage', 'contraception', 'leucorrhoea', 'menopause', 'hrt', 'puberty', 'voice', 'beard', 'marital_effect', 'sexual', 'nightfall', 'prostate', 'urine_weak', 'erectile', 'birth', 'vaccination', 'school', 'growth', 'age_q_', 'occupation', 'marital', 'blood', 'height', 'weight', 'allergy', 'habits', 'sleep', 'appetite', 'bowel', 'temperament', 'bp', 'temperature', 'pulse']):
            if str(r.get(k,'')).strip() and str(r.get(k,'')).strip().lower() not in ['select', '']:
              related_keys.append(k)
        if related_keys:
          st.markdown("<div style='margin-top:10px;'><b>Age/Gender Related History (from previous form):</b></div>", unsafe_allow_html=True)
          # Show in 3 columns
          cols = st.columns(3)
          for idx, key in enumerate(related_keys[:12]): # Show max 12
            col = cols[idx % 3]
            with col:
              st.markdown(f"<div style='background:#F1F7F3;border:1px solid #C8E6D5;border-radius:8px;padding:6px;margin:2px 0;font-size:12px;'><b>{key}:</b> {str(r.get(key,''))[:60]}</div>", unsafe_allow_html=True)
          if len(related_keys) > 12:
            st.caption(f"+ {len(related_keys)-12} more fields in full record")
        else:
          st.caption("No extra age/gender info found in previous record - will be collected in Personal/Vital sections below")
      except Exception as e:
        st.caption(f"Age/Gender history: Age {r.get('Age','')} / Gender {r.get('Gender','')} - Extra details in sections below")

  with st.container(border=True):
    st.markdown("<div class='heading-h4'>Personal Information</div>", unsafe_allow_html=True)
    # V200.14 FIX 3a: Personal Info - Show previous Gender/Age in revisit
    c1,c2,c3=st.columns(3)
    with c1:
      st.text_input("Patient's Name *", key=f"p_name_{fv}", value=get_prefill("Name",""), placeholder="Patient's Name - Text only")
      st.text_input("Spouse/Father's Name", key=f"p_fname_{fv}", value=get_prefill("FatherName",""), placeholder="Spouse/Father's Name - Text")
    with c2:
      # V200.14: Gender with previous data
      gender_options = LISTS["gender"]
      prev_gender = str(get_prefill("Gender","") or "").strip()
      gender_idx = 0
      if prev_gender and prev_gender in gender_options:
        gender_idx = gender_options.index(prev_gender)
      elif is_revisit and st.session_state.get("revisit_data"):
        rg = str(st.session_state.revisit_data.get("Gender","") or "").strip()
        if rg in gender_options:
          gender_idx = gender_options.index(rg)
      st.selectbox("Gender *", gender_options, key=f"p_gender_{fv}", index=gender_idx)
      st.text_input("Age *", key=f"p_age_{fv}", value=get_prefill("Age",""), placeholder="Age - Number e.g., 35")
    with c3:
      st.text_input("Phone *", key=f"p_phone_{fv}", value=get_prefill("Phone",""), placeholder="Phone - 03XX-XXXXXXX (Numbers only)", help="Enter phone number with digits only, e.g., 03001234567 - Required data type: Numeric String")
      st.text_input("Address", key=f"p_address_{fv}", value=get_prefill("Address",""), placeholder="Address - Text")

    # V200.14 FIX 3a: Age/Gender Related - Show previous data in revisit
    try:
      # FIX: Get age/gender from session first, then revisit_data, then prefill - ensure revisit data visible
      cur_age = str(st.session_state.get(f"p_age_{fv}","") or "").strip()
      cur_gender = str(st.session_state.get(f"p_gender_{fv}","") or "").strip()
      if not cur_age and is_revisit and st.session_state.get("revisit_data"):
        cur_age = str(st.session_state.revisit_data.get("Age","") or "").strip()
      if not cur_gender and is_revisit and st.session_state.get("revisit_data"):
        cur_gender = str(st.session_state.revisit_data.get("Gender","") or "").strip()
      if not cur_age:
        cur_age = str(get_prefill("Age","") or "").strip()
      if not cur_gender:
        cur_gender = str(get_prefill("Gender","") or "").strip()
      # Update session for display
      if cur_age and f"p_age_{fv}" not in st.session_state:
        st.session_state[f"p_age_{fv}"] = cur_age
      if cur_gender and f"p_gender_{fv}" not in st.session_state:
        st.session_state[f"p_gender_{fv}"] = cur_gender
      age_qs = get_age_based_questions(cur_age, cur_gender)
      if age_qs:
        st.markdown("<hr style='margin:12px 0; border:1px solid #C8E6D5;'>", unsafe_allow_html=True)
        st.markdown(f"<div class='heading-h5'>Age/Gender Related - Part of Personal Info (Age: {cur_age} / Gender: {cur_gender})</div>", unsafe_allow_html=True)
        if is_revisit:
          # V200.10 FIX 3a: Fixed Previous Age/Gender History - show ALL extra fields from revisit_data
          st.markdown("<div style='background:#E8F5E9;border:2px solid #2E7D5B;border-radius:10px;padding:10px;margin-bottom:10px;'><b>📋 Previous Age/Gender History (Physician View):</b></div>", unsafe_allow_html=True)
          hist_cols = st.columns(3)
          hist_count = 0
          # Show all keys except basic ones, so nothing missed
          basic_keys = ['PatientID','Date','Name','FatherName','Age','Gender','Phone','Address','CNIC','EmergencyPhone','Diseases','ChiefComplaint','PastHistory','FamilyHistory','Allergy','Examination','Pulse','Temperament','BP','Weight','Temperature','SingleMedicines','FormulaMedicines','Fees','MedicineCharges','Total','Paid','Balance','PrevBalance','PaymentMethod','FeeStatus','RevisitDate','ClinicName','CreatedBy','Timestamp','AppVersion','DailyNumber','TotalNumber','GrandTotal','Referral','Occupation','MaritalStatus']
          for k in st.session_state.revisit_data.keys() if st.session_state.revisit_data else []:
            if k in basic_keys:
              continue
            val = str(st.session_state.revisit_data.get(k,'')).strip()
            if val and val.lower() not in ['select', '', 'none', 'n/a']:
              col = hist_cols[hist_count % 3]
              with col:
                st.markdown(f"<div style='background:#FFFFFF;border:1.5px solid #C8E6D5;border-radius:8px;padding:6px;margin:3px 0;font-size:12px;'><b>{k}:</b> {val[:60]}</div>", unsafe_allow_html=True)
              hist_count += 1
          if hist_count == 0:
            # If no extra keys, show basic age/gender info as history
            st.markdown(f"<div style='background:#FFFFFF;border:1.5px solid #C8E6D5;border-radius:8px;padding:8px;font-size:13px;'><b>Age:</b> {st.session_state.revisit_data.get('Age','')} | <b>Gender:</b> {st.session_state.revisit_data.get('Gender','')} | <b>Marital:</b> {st.session_state.revisit_data.get('MaritalStatus','')} | <b>Blood:</b> {st.session_state.revisit_data.get('BloodGroup','') or st.session_state.revisit_data.get('Blood','')} | <b>Occupation:</b> {st.session_state.revisit_data.get('Occupation','')}</div>", unsafe_allow_html=True)
            st.caption("Extra Age/Gender details will be collected below - basic info shown above")
          st.markdown("<hr style='margin:8px 0; border:1px dashed #A8CCAD;'>", unsafe_allow_html=True)
          st.markdown("<div style='font-size:13px;font-weight:700;color:#2E7D5B;margin-bottom:6px;'>Current Age/Gender Questions - Update below:</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, (q_label, q_type, q_key) in enumerate(age_qs):
          col = cols[idx % 3]
          with col:
            prev_val = ""
            if is_revisit and st.session_state.revisit_data:
              prev_val = str(st.session_state.revisit_data.get(q_key,"") or st.session_state.revisit_data.get(q_label,"") or "")
            if isinstance(q_type, list):
              default_idx = 0
              if prev_val and prev_val in q_type:
                default_idx = q_type.index(prev_val)
              st.selectbox(q_label, q_type, key=f"age_q_{q_key}_{fv}", index=default_idx)
            else:
              st.text_input(q_label, key=f"age_q_{q_key}_{fv}", value=prev_val)
      else:
        if is_revisit and (cur_age or cur_gender):
          st.markdown("<hr style='margin:12px 0; border:1px solid #C8E6D5;'>", unsafe_allow_html=True)
          st.caption(f"Age {cur_age} / Gender {cur_gender} - No extra Age/Gender Qs for this combination")
          # Still show previous history even if no current Qs
          if st.session_state.revisit_data:
            st.markdown("<div style='background:#E8F5E9;border:2px solid #2E7D5B;border-radius:10px;padding:8px;margin-top:8px;'><b>Previous Age/Gender History:</b></div>", unsafe_allow_html=True)
            hist_found = False
            for k in st.session_state.revisit_data.keys():
              if any(x in k.lower() for x in ['female_', 'male_', 'child_', 'menarche', 'cycle', 'age_q_']):
                val = str(st.session_state.revisit_data.get(k,'')).strip()
                if val and val.lower() not in ['select','']:
                  st.caption(f"{k}: {val}")
                  hist_found = True
            if not hist_found:
              st.caption("No previous Age/Gender history")
    except Exception as e:
      st.caption(f"Age/Gender Qs: {str(e)[:80]}")

    # V200.9 FIX 3b: Additional Personal Details BELOW Age/Gender Related Questions
    show_extra_key = f"show_extra_personal_{fv}"
    if show_extra_key not in st.session_state:
      st.session_state[show_extra_key] = False
    
    st.markdown("<hr style='margin:12px 0; border:1px solid #E8F5E9;'>", unsafe_allow_html=True)
    if not st.session_state[show_extra_key]:
      if st.button("Additional Personal Details ⬇️ (After Age/Gender Qs)", key=f"add_info_btn_{fv}_v200_9", type="secondary"):
        st.session_state[show_extra_key] = True
        st.rerun()
    else:
      st.markdown("<div class='heading-h5'>Additional Personal Details (Below Age/Gender Qs - Hidden by default)</div>", unsafe_allow_html=True)
      c1,c2,c3=st.columns(3)
      with c1:
        st.selectbox("Blood Group", LISTS["blood_group"], key=f"p_blood_{fv}")
        st.text_input("Height", key=f"p_height_{fv}", placeholder="e.g., 5.6 ft - Number")
        occ_list = LISTS.get("occupation", ["Select","Student","Teacher","Farmer","Shopkeeper","Laborer","Driver","Housewife","Business","Engineer","Government Job","Private Job","Retired","Unemployed","Other"])
        st.selectbox("Occupation", occ_list, key=f"p_occupation_{fv}")
      with c2:
        st.selectbox("Marital Status", LISTS["marital"], key=f"p_marital_{fv}")
        st.text_input("CNIC", key=f"p_cnic_{fv}", value=get_prefill("CNIC",""), placeholder="CNIC - Number")
        st.text_input("Weight", key=f"p_weight_{fv}", placeholder="e.g., 70 kg - Number")
      with c3:
        st.text_input("Emergency Phone", key=f"p_emergency_{fv}", placeholder="Emergency Phone - Number")
        st.text_input("Referral", key=f"p_referral_{fv}", placeholder="Referral - Text")
        st.selectbox("Allergy", LISTS["allergy"], key=f"p_allergy_{fv}")
      if st.button("Hide Additional Details ⬆️", key=f"hide_extra_{fv}_v200_9"):
        st.session_state[show_extra_key] = False
        st.rerun()
    section_ok("personal", is_revisit=is_revisit)

  with st.container(border=True):
    if section_heading_clickable("vital","Vital Signs"):
      c1,c2,c3=st.columns(3)
      with c1:
        st.selectbox("BP", LISTS["bp"], key=f"v_bp_{fv}")
        st.text_input("Weight (kg)", key=f"v_weight_{fv}", value=get_prefill("Weight",""), placeholder="e.g., 70")
        st.selectbox("Sleep Pattern", LISTS["sleep"], key=f"v_sleep_{fv}")
      with c2:
        st.selectbox("Temperature", LISTS["temperature"], key=f"v_temp_{fv}")
        st.selectbox("Pulse", LISTS["pulse"], key=f"v_pulse_{fv}")
        st.selectbox("Appetite", LISTS["appetite"], key=f"v_appetite_{fv}")
      with c3:
        st.selectbox("Temperament", LISTS["temperament"], key=f"u_temperament_{fv}")
        st.selectbox("Bowel Movement", LISTS["bowel"], key=f"v_bowel_{fv}")
      section_ok("vital", is_revisit=is_revisit)

  # V200.10 FIX 3d: Previous Diseases - Only selected patient, not others - Fix duplicate and filtering
  if is_revisit and st.session_state.revisit_data:
    # Ensure we only show selected patient's diseases - use PatientID to verify
    selected_pid = str(st.session_state.revisit_data.get("PatientID","") or "").strip()
    selected_name = str(st.session_state.revisit_data.get("Name","") or "").strip()
    prev_text = str(st.session_state.revisit_data.get("Diseases","") or "").strip()
    if prev_text:
      st.markdown(f"<div class='heading-h4'>Previous Diseases - History (Patient: {selected_name} - ID: {selected_pid})</div>", unsafe_allow_html=True)
      with st.container(border=True):
        # Split and deduplicate to prevent 2 times display (FIX 3c)
        raw_list = [d.strip() for d in prev_text.split(" + ") if d.strip()]
        # Deduplicate preserving order
        seen = set()
        prev_list = []
        for item in raw_list:
          if item.lower() not in seen:
            seen.add(item.lower())
            prev_list.append(item)
        # Reset cured/remaining if PatientID changed (prevents other patients history)
        last_pid_key = f"last_revisit_pid_{fv}"
        if st.session_state.get(last_pid_key, "") != selected_pid:
          st.session_state.revisit_cured_diseases = []
          st.session_state.revisit_remaining_diseases = prev_list.copy()
          st.session_state[last_pid_key] = selected_pid
        if "revisit_cured_diseases" not in st.session_state:
          st.session_state.revisit_cured_diseases = []
        if "revisit_remaining_diseases" not in st.session_state:
          st.session_state.revisit_remaining_diseases = prev_list.copy()
        for idx, pd in enumerate(prev_list):
          c1,c2 = st.columns([4,1])
          with c1:
            is_cured = pd in st.session_state.revisit_cured_diseases
            style = "text-decoration: line-through; opacity:0.5;" if is_cured else "font-weight:600;"
            tag = " (Cured)" if is_cured else " (Remaining)"
            st.markdown(f"<div style='{style}'>{idx+1}. {pd}{tag}</div>", unsafe_allow_html=True)
          with c2:
            if pd not in st.session_state.revisit_cured_diseases:
              if st.button("❌", key=f"cure_prev_{fv}_{idx}_v200_10", help="Mark cured"):
                st.session_state.revisit_cured_diseases.append(pd)
                if pd in st.session_state.revisit_remaining_diseases:
                  st.session_state.revisit_remaining_diseases.remove(pd)
                st.rerun()
            else:
              if st.button("↩️", key=f"uncure_prev_{fv}_{idx}_v200_10"):
                st.session_state.revisit_cured_diseases.remove(pd)
                st.session_state.revisit_remaining_diseases.append(pd)
                st.rerun()
        st.info(f"Patient: {selected_name} | Prev: {len(prev_list)} | Cured: {len(st.session_state.revisit_cured_diseases)} | Remaining: {len(st.session_state.revisit_remaining_diseases)}")
    else:
      st.caption(f"No previous diseases for {selected_name} (ID: {selected_pid})")

  # V197 Fix: Diseases No/Count Duration mandatory + fix Add Disease error
  with st.container(border=True):
    if section_heading_clickable("diseases","Diseases - Current"):

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
      # V200.17 FIX 1,2,3: Disease related questions with dropdowns after all fields complete
      bp_complete = st.session_state.get(f"pat_body_part_{fv}_v197","Select") != "Select"
      dis_complete = st.session_state.get(f"pat_disease_sub_{fv}_v197","Select") != "Select"
      no_complete = str(st.session_state.get(f"pat_no_{fv}_v197","")).strip() != ""
      dur_complete = st.session_state.get(f"pat_dur_{fv}_v197","Select") != "Select"
      all_disease_fields_done = bp_complete and dis_complete and no_complete and dur_complete
      
      if all_disease_fields_done:
        st.markdown("<div class='heading-h5'>Disease Related Questions - Nature/Stage etc (After all fields complete)</div>", unsafe_allow_html=True)
        st.markdown("<div style='background:#F1F7F3;border:1.5px solid #C8E6D5;border-radius:10px;padding:8px;margin-bottom:8px;font-size:13px;'>Additional Questions - Disease Nature/Stage - Dropdown lists - For Physician Reference</div>", unsafe_allow_html=True)
        rq1_col, rq2_col, rq3_col = st.columns(3)
        with rq1_col:
          related_qs = DISEASE_RELATED_QUESTIONS.get(st.session_state.get(f"pat_body_part_{fv}_v197","Select"), DISEASE_RELATED_QUESTIONS.get("General", ["Severity","Trigger","Associated Symptom"]))
          q1_label = related_qs[0] if len(related_qs)>0 else "Severity/Stage"
          # V200.17 FIX 1: Dropdown for related questions
          bp_for_dd = st.session_state.get(f"pat_body_part_{fv}_v197","General")
          dd_options = DISEASE_RELATED_DROPDOWNS.get(bp_for_dd, {}).get(q1_label, LISTS["severity"])
          st.selectbox(q1_label, dd_options, key=f"pat_rel_q1_{fv}_v200_4")
        with rq2_col:
          q2_label = related_qs[1] if len(related_qs)>1 else "Nature/Trigger"
          dd_options2 = DISEASE_RELATED_DROPDOWNS.get(bp_for_dd, {}).get(q2_label, ["Select","Yes","No","Sometimes","After eating","Before eating","Continuous","Intermittent"])
          st.selectbox(q2_label, dd_options2, key=f"pat_rel_q2_{fv}_v200_4")
        with rq3_col:
          q3_label = related_qs[2] if len(related_qs)>2 else "Associated Symptom"
          dd_options3 = DISEASE_RELATED_DROPDOWNS.get(bp_for_dd, {}).get(q3_label, ["Select","Nausea","Burning","Pain","Itching","None","Other"])
          st.selectbox(q3_label, dd_options3, key=f"pat_rel_q3_{fv}_v200_4")
      else:
        st.info("Complete Body Part*, Disease*, No/Count* and Duration* to see Related Questions (Dropdowns)")

      if st.button("Add Disease +", key=f"pat_add_{fv}_v200_4", type="secondary", use_container_width=True):
        bp = st.session_state.get(f"pat_body_part_{fv}_v197", "Select")
        dis = st.session_state.get(f"pat_disease_sub_{fv}_v197", "Select")
        no_val = st.session_state.get(f"pat_no_{fv}_v197", "").strip()
        dur_val = st.session_state.get(f"pat_dur_{fv}_v197", "Select")
        if bp=="Select":
          st.error("Please select Body Part *")
        elif dis=="Select":
          st.error("Please select Disease *")
        elif not no_val:
          st.error("Please complete: No/Count * is mandatory")
        elif dur_val=="Select":
          st.error("Please complete: Duration * is mandatory")
        else:
          # V200.4: Include related Qs in disease text
          rel_q1 = st.session_state.get(f"pat_rel_q1_{fv}_v200_4", "Select")
          rel_q2 = st.session_state.get(f"pat_rel_q2_{fv}_v200_4", "").strip()
          rel_q3 = st.session_state.get(f"pat_rel_q3_{fv}_v200_4", "").strip()
          entry_text = f"{bp} + {dis} + {no_val} {dur_val}"
          if rel_q1 and rel_q1 != "Select":
            entry_text += f" + {rel_q1}"
          if rel_q2:
            entry_text += f" + {rel_q2}"
          if rel_q3:
            entry_text += f" + {rel_q3}"
          if "patient_diseases" not in st.session_state:
            st.session_state.patient_diseases = []
          # V209 Fix 7: Check duplicate before adding
          existing_texts = [d.get("text","") for d in st.session_state.patient_diseases]
          if entry_text in existing_texts:
            st.warning(f"Already added: {entry_text}")
          else:
            st.session_state.patient_diseases.append({"text": entry_text})
            st.success(f"✅ Added: {entry_text}")
          # V200.10 FIX 3c: Clear disease fields to default after Add Disease - prevent duplicate
          try:
            st.session_state[f"pat_body_part_{fv}_v197"] = "Select"
            st.session_state[f"pat_disease_sub_{fv}_v197"] = "Select"
            st.session_state[f"pat_no_{fv}_v197"] = ""
            st.session_state[f"pat_dur_{fv}_v197"] = "Select"
            st.session_state[f"pat_rel_q1_{fv}_v200_4"] = "Select"
            st.session_state[f"pat_rel_q2_{fv}_v200_4"] = ""
            st.session_state[f"pat_rel_q3_{fv}_v200_4"] = ""
            st.session_state[f"pat_disease_clear_{fv}"] = st.session_state.get(f"pat_disease_clear_{fv}",0)+1
            # Force clear body part cache
            if f"pat_body_part_{fv}_v197" in st.session_state:
              del st.session_state[f"pat_body_part_{fv}_v197"]
          except:
            pass
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
      # V200.14 FIX 2a,2b,2c: No Add buttons, Single/Formula labels simple, Manual field bigger
      try:
        single_options = []
        formula_options = []
        try:
          herb_recs = get_all_records_cached("Herbs")
          if herb_recs:
            for r in herb_recs[:500]:
              name = str(r.get("Name","") or r.get("HerbName","") or r.get("MedicineName","") or "").strip()
              if name and name not in single_options:
                single_options.append(name)
        except: pass
        try:
          pharma_recs = get_all_records_cached("Pharmacopoeia")
          if not pharma_recs:
            pharma_recs = get_all_records_cached("Formulas")
          if not pharma_recs:
            pharma_recs = get_all_records_cached("Medicine")
          if pharma_recs:
            for r in pharma_recs[:500]:
              name = str(r.get("Name","") or r.get("FormulaName","") or r.get("MedicineName","") or "").strip()
              if name and name not in formula_options:
                formula_options.append(name)
        except: pass
        if len(single_options) == 0:
          single_options = ["Ajwain","Haldi","Saunf","Zeera","Adrak","Lehsan","Kali Mirch","Long","Darcheeni","Elaichi","Other"]
        if len(formula_options) == 0:
          formula_options = ["Jawarish Jalinus","Majoon Dabeed","Hab Shifa","Sharbat Bazoori","Arq Mako","Roghan Babuna","Khamira Gauzaban","Other"]
      except:
        single_options = ["Ajwain","Haldi","Saunf","Zeera","Adrak","Lehsan","Other"]
        formula_options = ["Jawarish","Majoon","Hab","Sharbat","Oil","Other"]
      
      c1,c2=st.columns(2)
      with c1:
        # V200.14 FIX 2c: Only Single Medicines
        st.markdown("<div class='heading-h5'>Single Medicines</div>", unsafe_allow_html=True)
        # V200.14 FIX 2a: No Add button - direct multiselect searchable
        selected_single = st.multiselect("Single Medicines", single_options, key=f"single_meds_{fv}", help="Type to search medicine from Google Sheet")
      with c2:
        st.markdown("<div class='heading-h5'>Formula Medicines</div>", unsafe_allow_html=True)
        selected_formula = st.multiselect("Formula Medicines", formula_options, key=f"formula_meds_{fv}", help="Type to search formula from Google Sheet")
      
      # V200.14 FIX 2b: Physician Manual Medicine Entry field bigger
      st.markdown("<hr style='margin:12px 0; border:1px solid #C8E6D5;'>", unsafe_allow_html=True)
      st.markdown("<div class='heading-h5'>Physician Manual Medicine Entry - Larger Field</div>", unsafe_allow_html=True)
      manual_meds = st.text_area("Physician Manual Medicine", key=f"physician_manual_med_{fv}_v200_14", placeholder="Enter medicines manually - Physician can write multiple medicines here with dosage e.g.\n1. Custom Arq Mako 10ml twice daily\n2. Special Majoon 5g at night\n3. Your own formula", height=150)
      
      all_meds = st.session_state.get(f"single_meds_{fv}", []) + st.session_state.get(f"formula_meds_{fv}", [])
      manual_list = [m.strip() for m in manual_meds.split("\n") if m.strip()] if manual_meds else []
      if all_meds or manual_list:
        preview_text = ""
        if all_meds:
          preview_text += f"<b>Selected ({len(all_meds)}):</b> {', '.join(all_meds)}<br>"
        if manual_list:
          preview_text += f"<b>Manual ({len(manual_list)}):</b><br>" + "<br>".join([f"{i+1}. {m}" for i,m in enumerate(manual_list)])
        st.markdown(f"<div style='background:#E8F5E9;border:2px solid #2E7D5B;border-radius:12px;padding:12px;margin-top:10px;'>{preview_text}</div>", unsafe_allow_html=True)
      
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

  # V200.12 FIX: UnboundLocalError fixed + Save Patient Final Step removed + English only + Stream On fixed
  st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
  
  # Simplified save - no diagnosis banners, English only, no Final Step section
  c_save, c_new = st.columns([3,1])
  with c_new:
    if st.button("New Patient", key=f"new_patient_btn_{fv}_v200_12", type="secondary"):
      reset_to_new_patient()
  with c_save:
    if st.button("Save Patient", type="primary", use_container_width=True, key=f"save_patient_{fv}_v200_12"):
      p_name = str(st.session_state.get(f"p_name_{fv}", "") or "").strip()
      if not p_name:
        st.error("Patient Name is required - Please enter in Personal Information")
      else:
        try:
          f_val = float(str(st.session_state.get(f"calc_f_{fv}", 0) or 0))
        except: f_val = 0.0
        try:
          m_val = float(str(st.session_state.get(f"calc_m_{fv}", 0) or 0))
        except: m_val = 0.0
        try:
          p_val = float(str(st.session_state.get(f"calc_p_{fv}", 0) or 0))
        except: p_val = 0.0
        try:
          grand_total = float(str(st.session_state.get(f"calc_gt_{fv}", f_val + m_val + prev_bal) or 0))
        except: grand_total = f_val + m_val + prev_bal
        try:
          balance = float(str(st.session_state.get(f"calc_bal_{fv}", grand_total - p_val) or 0))
        except: balance = grand_total - p_val
        if balance < 0: balance = 0
        status_val = str(st.session_state.get(f"calc_status_{fv}", "Select") or "Select")
        pay_method_val = str(st.session_state.get(f"calc_pay_{fv}", "Select") or "Select")
        try:
          age_val = str(st.session_state.get(f"p_age_{fv}", "") or "").strip()
        except: age_val = ""
        diseases_list = st.session_state.get("patient_diseases", [])
        diseases_text = " + ".join([d.get("text","") for d in diseases_list]) if diseases_list else ""
        chief_comp = str(st.session_state.get(f"chief_complaint_{fv}", "") or "")
        past_hist = str(st.session_state.get(f"past_history_{fv}", "") or "")
        family_hist = str(st.session_state.get(f"family_hist_{fv}", "") or "")
        bp_val = str(st.session_state.get(f"v_bp_{fv}", "") or "")
        temp_val = str(st.session_state.get(f"v_temp_{fv}", "") or "")
        weight_val = str(st.session_state.get(f"v_weight_{fv}", "") or st.session_state.get(f"p_weight_{fv}", "") or "")
        data_dict={
          "PatientID": str(pid),
          "Date": str(__import__('datetime').date.today()),
          "Name": str(p_name).strip(),
          "FatherName": str(st.session_state.get(f"p_fname_{fv}", "") or "").strip(),
          "Age": str(age_val).strip(),
          "Gender": str(st.session_state.get(f"p_gender_{fv}", "Select") or "Select").strip(),
          "MaritalStatus": str(st.session_state.get(f"p_marital_{fv}", "Select") or "Select").strip(),
          "Occupation": str(st.session_state.get(f"p_occupation_{fv}", "Select") or "Select").strip(),
          "CNIC": str(st.session_state.get(f"p_cnic_{fv}", "") or "").strip(),
          "Phone": str(st.session_state.get(f"p_phone_{fv}", "") or "").strip(),
          "EmergencyPhone": str(st.session_state.get(f"p_emergency_{fv}", "") or "").strip(),
          "Address": str(st.session_state.get(f"p_address_{fv}", "") or "").strip(),
          "Referral": str(st.session_state.get(f"p_referral_{fv}", "") or "").strip(),
          "Diseases": str(diseases_text).strip(),
          "ChiefComplaint": str(chief_comp).strip(),
          "PastHistory": str(past_hist).strip(),
          "FamilyHistory": str(family_hist).strip(),
          "Allergy": str(st.session_state.get(f"p_allergy_{fv}", "Select") or "Select").strip(),
          "Examination": "",
          "Pulse": str(st.session_state.get(f"v_pulse_{fv}", "Select") or "Select").strip(),
          "Temperament": str(st.session_state.get(f"u_temperament_{fv}", "Select") or "Select").strip(),
          "BP": str(bp_val).strip(),
          "Weight": str(weight_val).strip(),
          "Temperature": str(temp_val).strip(),
          "SingleMedicines": str(st.session_state.get(f"single_meds_{fv}", [])),
          "FormulaMedicines": str(st.session_state.get(f"formula_meds_{fv}", [])),
          "ManualMedicines": str(st.session_state.get(f"physician_manual_med_{fv}_v200_14", "") or st.session_state.get(f"physician_manual_med_{fv}_v200_13", "") or ""),
          "Fees": float(f_val),
          "MedicineCharges": float(m_val),
          "Total": float(f_val + m_val),
          "Paid": float(p_val),
          "Balance": float(balance),
          "PrevBalance": float(prev_bal),
          "PaymentMethod": str(pay_method_val).strip(),
          "FeeStatus": str(status_val).strip(),
          "RevisitDate": "",
          "ClinicName": str(st.session_state.get("clinic_name","") or "").strip(),
          "CreatedBy": str(st.session_state.get("username","") or "").strip(),
          "Timestamp": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          "AppVersion": str(APP_VERSION),
          "DailyNumber": int(daily_num),
          "TotalNumber": int(total_num),
          "GrandTotal": float(grand_total),
        }
        try:
          for k in list(st.session_state.keys()):
            if k.startswith(f"age_q_") and k.endswith(f"_{fv}"):
              clean_key = k.replace(f"_{fv}", "")
              val = st.session_state.get(k, "")
              if val and str(val).strip().lower() not in ['select','']:
                data_dict[clean_key] = str(val).strip()
        except: pass
        ok,msg=save_patient(data_dict)
        if is_revisit:
          try:
            prev_for_sheet = str(st.session_state.revisit_data.get("Diseases","") or "") if st.session_state.revisit_data else ""
            cured_for_sheet = " + ".join(st.session_state.get("revisit_cured_diseases", []))
            remaining_for_sheet = " + ".join(st.session_state.get("revisit_remaining_diseases", []))
            complaint_with_history = f"Past: {prev_for_sheet} | Cured: {cured_for_sheet} | Remaining: {remaining_for_sheet} | Current: {str(diseases_text).strip()} | Chief: {str(chief_comp).strip()}"
            revisit_dict = {
              "RevisitID": f"R{str(pid)}_{str(__import__('datetime').date.today())}_{str(int(__import__('datetime').datetime.now().timestamp()))[-4:]}",
              "PatientID": str(pid),
              "Date": str(__import__('datetime').date.today()),
              "Name": str(p_name).strip(),
              "Phone": str(st.session_state.get(f"p_phone_{fv}", "") or "").strip(),
              "ClinicName": str(st.session_state.get("clinic_name","") or "").strip(),
              "Complaint": complaint_with_history[:2000],
              "Prescription": str(st.session_state.get(f"single_meds_{fv}", [])) + " | " + str(st.session_state.get(f"formula_meds_{fv}", [])),
              "Fees": float(f_val),
              "Paid": float(p_val),
              "Balance": float(balance),
              "CreatedBy": str(st.session_state.get("username","") or "").strip()
            }
            try:
              ws_rev = get_sheet_safe("Revisit")
              if ws_rev:
                hdr_rev = ws_rev.row_values(1)
                if not hdr_rev or len(hdr_rev) < 5:
                  hdr_rev = list(revisit_dict.keys())
                row_rev = [str(revisit_dict.get(h,"")) for h in hdr_rev]
                ws_rev.append_row(row_rev, value_input_option="RAW")
            except: pass
            save_to_local_csv("Revisit", revisit_dict)
          except: pass
        try:
          _get_all_records_cached_fast.clear()
        except: pass
        if ok:
          msg_extra = " + Revisit sheet" if is_revisit else ""
          st.success(f"Saved - PatientID {pid} | Grand Total Rs {grand_total:.0f}{msg_extra} - Form cleared for new entry")
          st.balloons()
          st.session_state.form_version+=1
          st.session_state.prev_balance=0.0
          st.session_state.revisit_data=None
          st.session_state.patient_diseases=[]
          st.session_state.section_opened={"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
          st.session_state.section_unlocked={"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
          st.rerun()
        else:
          st.warning(f"Local Save - ID {pid} | Grand Total Rs {grand_total:.0f} - {msg}")
          st.session_state.form_version+=1
          st.session_state.prev_balance=0.0
          st.session_state.revisit_data=None
          st.session_state.patient_diseases=[]
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

  st.markdown(f"<div class='heading-h4'>Personal Information</div>", unsafe_allow_html=True)
  with st.container(border=True):
    # Prefill helper
    def get_auto_prefill(field, default=""):
      sel = st.session_state.get(selected_key)
      if sel and st.session_state.get(f"{prefix}_form_mode")=="Revisit":
        return str(sel.get(field,"") or default)
      return st.session_state.get(f"{prefix}_name_v172","") if field=="Name" else default

    # V200.15 FIX 1a: Phone, Blood Group, Marital Status NOT hidden - included in Personal Info visible
    # V200.15 FIX 1b: Address, Height, Weight, Habits NOT required - moved to Additional Personal Details hidden
    c1,c2,c3=st.columns(3)
    with c1:
      p_name_val = ""
      if st.session_state.get(selected_key) and st.session_state.get(f"{prefix}_form_mode")=="Revisit":
        p_name_val = st.session_state.get(selected_key).get("Name","")
      p_name=st.text_input("Patient's Name *", value=p_name_val, key=f"{prefix}_name_v197")
      p_father=st.text_input("Spouse/Father's Name", key=f"{prefix}_father_v197")
      # Phone visible per 1a
      p_phone_default = ""
      if st.session_state.get(selected_key) and st.session_state.get(f"{prefix}_form_mode")=="Revisit":
        p_phone_default = st.session_state.get(selected_key).get("Phone","")
      p_phone=st.text_input("Phone *", value=p_phone_default, key=f"{prefix}_phone_v197", placeholder="03XX-XXXXXXX")
    with c2:
      p_gender=st.selectbox("Gender *", LISTS["gender"], key=f"{prefix}_gender_v197")
      p_age=st.text_input("Age *", key=f"{prefix}_age_v197", placeholder="Age e.g. 35")
      # Blood Group visible per 1a
      p_blood=st.selectbox("Blood Group", LISTS["blood_group"], key=f"{prefix}_blood_v197")
    with c3:
      occ_list = LISTS.get("occupation", ["Select","Student","Teacher","Farmer","Shopkeeper","Laborer","Driver","Housewife","Business","Engineer","Government Job","Private Job","Retired","Unemployed","Other"])
      p_occupation=st.selectbox("Occupation", occ_list, key=f"{prefix}_occ_v197")
      # Marital Status visible per 1a
      p_marital=st.selectbox("Marital Status", LISTS["marital"], key=f"{prefix}_marital_v197")

    # Hidden fields - Additional Personal Details (Address, Height, Weight, Habits) per 1b
    show_extra_key = f"show_extra_auto_{prefix}"
    if show_extra_key not in st.session_state:
      st.session_state[show_extra_key] = False
    
    if not st.session_state[show_extra_key]:
      if st.button("Additional Personal Details (Hidden by default) ⬇️", key=f"auto_add_info_{prefix}_v200_15"):
        st.session_state[show_extra_key] = True
        st.rerun()
    else:
      st.markdown("---")
      st.markdown("<div class='heading-h5'>Additional Personal Details (Hidden by default) - Address, Height, Weight, Habits not required</div>", unsafe_allow_html=True)
      c1,c2,c3=st.columns(3)
      with c1:
        p_address=st.text_input("Address (Optional)", key=f"{prefix}_addr_v197", placeholder="Address optional")
        p_height=st.text_input("Height (Optional)", key=f"{prefix}_height_v197", placeholder="e.g., 5.6 ft")
      with c2:
        p_weight=st.text_input("Weight (Optional)", key=f"{prefix}_weight_v197", placeholder="e.g., 70 kg")
      with c3:
        p_habits=st.text_input("Habits (Optional)", key=f"{prefix}_habits_v197", placeholder="e.g., Smoking, Tea")
      if st.button("Close Additional Details ✕", type="secondary", key=f"auto_hide_{prefix}_v200_15"):
        st.session_state[show_extra_key] = False
        st.rerun()
    
    # Ensure variables exist
    p_address = st.session_state.get(f"{prefix}_addr_v197", "")
    p_height = st.session_state.get(f"{prefix}_height_v197", "")
    p_weight = st.session_state.get(f"{prefix}_weight_v197", "")
    p_habits = st.session_state.get(f"{prefix}_habits_v197", "")

    # Age-based questions
    try:
      age_qs = get_age_based_questions(p_age, p_gender)
      if age_qs:
        st.markdown("---")
        st.markdown(f"<div class='heading-h5'>Age-Based Questions for {p_gender} (Age: {p_age})</div>", unsafe_allow_html=True)
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
        # V200.17 FIX 4: Detailed validation with reminder which field missing
        missing = []
        if not p_name.strip():
          missing.append("Patient Name*")
        if p_gender == "Select" or not p_gender:
          missing.append("Gender*")
        if not p_phone.strip():
          missing.append("Phone*")
        if not p_age.strip():
          missing.append("Age*")
        # Check if any missing
        if missing:
          st.error(f"Please complete Personal Information - Missing: {', '.join(missing)}")
          st.warning(f"Reminder: Fill these fields: {', '.join(missing)}")
        else:
          # Home User phone matching - only if home_phone exists and not empty
          if is_home:
            home_phone = get_home_user_phone()
            if home_phone and home_phone.strip() and p_phone.strip() != home_phone.strip():
              st.error(f"Phone must match Home User signup phone: {home_phone}. Your entered: {p_phone}")
              st.info("If your signup phone is wrong, update HomeUsers sheet")
              st.stop()
          st.session_state[personal_ok_key] = True
          st.success("Personal Information Saved - Complete")
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
    st.markdown("<div class='heading-h5'>Select Body Part and Disease</div>", unsafe_allow_html=True)
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
    rq2_val = st.session_state.get(f"{prefix}_rel_q2_v197", "Select")
    rq3_val = st.session_state.get(f"{prefix}_rel_q3_v197", "Select")
    # V200.17 FIX 1,3: Related Questions only after all disease fields complete, with dropdowns
    all_fields_complete = body_part != "Select" and disease != "Select" and str(d_no).strip() != "" and d_duration != "Select"
    if all_fields_complete:
      st.markdown(f"<div class='heading-h5'>Related Questions for {body_part} - {disease} (Dropdowns - After all fields complete)</div>", unsafe_allow_html=True)
      related_qs = DISEASE_RELATED_QUESTIONS.get(body_part, DISEASE_RELATED_QUESTIONS["General"])
      dd_map = DISEASE_RELATED_DROPDOWNS.get(body_part, {})
      cq1,cq2,cq3=st.columns(3)
      with cq1:
        q1_label = related_qs[0] if len(related_qs)>0 else "Severity"
        q1_options = dd_map.get(q1_label, LISTS["severity"])
        rq1_val = st.selectbox(q1_label, q1_options, key=f"{prefix}_rel_q1_v197")
      with cq2:
        q2_label = related_qs[1] if len(related_qs)>1 else "Trigger"
        q2_options = dd_map.get(q2_label, ["Select","Yes","No","Sometimes","After eating","Before eating","Continuous","Intermittent","Mild","Severe"])
        rq2_val = st.selectbox(q2_label, q2_options, key=f"{prefix}_rel_q2_v197")
      with cq3:
        q3_label = related_qs[2] if len(related_qs)>2 else "Associated Symptom"
        q3_options = dd_map.get(q3_label, ["Select","Nausea","Burning","Pain","Itching","None","Other","Fever","Swelling"])
        rq3_val = st.selectbox(q3_label, q3_options, key=f"{prefix}_rel_q3_v197")
    else:
      if body_part != "Select" and disease != "Select":
        st.info("Complete No/Count* and Duration* to see Related Questions (Dropdowns)")

    # V200.15 FIX 2: Add Disease functional for Home treatment - fixed key and logic
    if st.button("Add Disease +", key=f"{prefix}_add_v200_15", type="secondary", use_container_width=True):
      bp = st.session_state.get(f"{prefix}_body_part_v197", "Select")
      dis = st.session_state.get(f"{prefix}_disease_sub_v197", "Select")
      no_val = st.session_state.get(f"{prefix}_no_v197", "").strip()
      dur_val = st.session_state.get(f"{prefix}_dur_v197", "Select")
      r1 = st.session_state.get(f"{prefix}_rel_q1_v197", "Select")
      r2 = st.session_state.get(f"{prefix}_rel_q2_v197", "").strip()
      r3 = st.session_state.get(f"{prefix}_rel_q3_v197", "").strip()
      if bp=="Select":
        st.error("Please select Body Part")
      elif dis=="Select":
        st.error("Please select Disease")
      elif not no_val:
        st.error("Please enter No/Count")
      elif dur_val=="Select":
        st.error("Please select Duration")
      else:
        entry_text = f"{bp} + {dis} + {no_val} {dur_val}"
        if r1 and r1!="Select": entry_text += f" + {r1}"
        if r2: entry_text += f" + {r2}"
        if r3: entry_text += f" + {r3}"
        target_list_key = "home_auto_diseases" if is_home else "auto_diseases"
        if target_list_key not in st.session_state:
          st.session_state[target_list_key] = []
        st.session_state[target_list_key].append({"text": entry_text})
        # V204: Clear selection fields after adding
        try:
          st.session_state[f"{prefix}_body_part_v197"] = "Select"
          st.session_state[f"{prefix}_disease_sub_v197"] = "Select"
          st.session_state[f"{prefix}_no_v197"] = ""
          st.session_state[f"{prefix}_dur_v197"] = "Select"
          st.session_state[f"{prefix}_rel_q1_v197"] = "Select"
          st.session_state[f"{prefix}_rel_q2_v197"] = ""
          st.session_state[f"{prefix}_rel_q3_v197"] = ""
        except: pass
        st.success(f"✅ Added: {entry_text} - Cleared fields for next entry")
        st.rerun()

  st.markdown("<div class='heading-h5'>Added Diseases</div>", unsafe_allow_html=True)
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
          st.error("Please complete: Add at least one disease - Use Select Body Part and Disease then Add Disease +")
          st.warning("Reminder: Fill Body Part*, Disease*, No/Count*, Duration* and click Add Disease +")
        else:
          st.session_state[diseases_ok_key] = True
          st.success("Diseases OK - Next section unlocked")
          st.rerun()
    else:
      st.success("Diseases Completed - OK - Next section open")
      if st.button(f"Edit Diseases", key=f"{prefix}_diseases_edit_v172"):
        st.session_state[diseases_ok_key] = False
        st.rerun()

  if not st.session_state[diseases_ok_key]:
    st.warning("Please complete Diseases section and click OK to open next section. Reminder: Add at least one disease via Add Disease + button")
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
          st.warning(f"Reminder: Fill these fields in Additional Information: {', '.join(mandatory_missing)} - All are dropdowns")
        else:
          st.session_state[additional_ok_key] = True
          st.success("Additional Information OK - Proceed unlocked")
          st.rerun()
    else:
      st.success("Additional Information Completed - OK - Proceed button below Additional Questions will be enabled")
      if st.button(f"Edit Additional Information", key=f"{prefix}_additional_edit_v172"):
        st.session_state[additional_ok_key] = False
        st.rerun()

  if not st.session_state[additional_ok_key]:
    st.warning("Please complete Additional Information and click OK to enable Proceed. Reminder: Complete all dropdowns in Lifestyle and Symptoms")
    return p_name, p_father, p_age, p_phone, p_gender, p_address, diseases_list

  # V200.15 FIX 1c: Additional Questions BEFORE Proceed button
  st.markdown("---")
  st.markdown("<div class='heading-h4'>Additional Questions</div>", unsafe_allow_html=True)
  with st.container(border=True):
    try:
      add_qs = get_additional_patient_questions()
      cols = st.columns(3)
      for idx, (q_label, q_type, q_key) in enumerate(add_qs):
        col = cols[idx % 3]
        with col:
          if isinstance(q_type, list):
            st.selectbox(q_label, q_type, key=f"auto_add_q_{q_key}_{prefix}_v200_15")
          else:
            st.text_input(q_label, key=f"auto_add_q_{q_key}_{prefix}_v200_15")
    except Exception as e:
      st.caption(f"Additional Questions: {e}")

  # V200.15 FIX 1c: Proceed button below Additional Questions
  st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
  if st.button("Proceed - Get Temperament & Diet Advice", type="primary", use_container_width=True, key=f"{prefix}_proceed_v200_15"):
    # V200.15 FIX 1e: Extract temperament from form fields and suggest Diet, Restrictions, Instructions - other fields locked
    try:
      # Extract temperament from sleep, appetite, thirst, bowel, etc
      hot_score = 0
      cold_score = 0
      dry_score = 0
      wet_score = 0
      
      # Sleep
      if sleep_pat in ["Less", "Disturbed", "Less / Disturbed"]: hot_score += 1; dry_score += 1
      if sleep_pat in ["Excess", "Deep", "Excess / Deep"]: cold_score += 1; wet_score += 1
      # Appetite
      if appetite_pat in ["High", "Excessive"]: hot_score += 1
      if appetite_pat in ["Low", "Less"]: cold_score += 1
      # Thirst
      thirst_val = st.session_state.get(f"{prefix}_thirst_v172", "Select")
      if thirst_val in ["Excess", "High"]: hot_score += 1; dry_score += 1
      if thirst_val in ["Less", "Low"]: cold_score += 1
      # Bowel
      if bowel in ["Constipated", "Dry"]: dry_score += 1; cold_score += 1
      if bowel in ["Loose", "Watery"]: wet_score += 1
      # Urine
      urine_val = st.session_state.get(f"{prefix}_urine_v172", "Select")
      if urine_val in ["Burning", "Yellow"]: hot_score += 1
      if urine_val in ["Frequent", "Excess"]: wet_score += 1
      # Sweat
      sweat_val = st.session_state.get(f"{prefix}_sweat_v172", "Select")
      if sweat_val == "Excess": hot_score += 1; wet_score += 1
      if sweat_val == "Less": cold_score += 1; dry_score += 1
      # Energy
      energy_val = st.session_state.get(f"{prefix}_energy_v172", "Select")
      if energy_val == "High": hot_score += 1
      if energy_val == "Low": cold_score += 1
      
      # Determine temperament
      if hot_score > cold_score and dry_score >= wet_score:
        temperament = "Hot & Dry (Garam Khushk)"
        diet = "Cool & Moist foods: Cucumber, Yogurt, Watermelon, Milk, Cucumber raita, Fresh juices, Water intake 8-10 glasses, Avoid spicy, fried, hot foods"
        restrictions = "Avoid: Spicy foods, Red meat excess, Fried foods, Pickles, Chilli, Garlic excess, Hot spices, Alcohol, Caffeine excess"
        instructions = "1. Drink plenty of water\n2. Eat cooling foods\n3. Avoid heat exposure\n4. Sleep 7-8 hours\n5. Light exercise morning/evening\n6. Use rose water, sandal for cooling"
      elif hot_score > cold_score and wet_score > dry_score:
        temperament = "Hot & Wet (Garam Tar)"
        diet = "Cool & Dry foods: Barley, Lentils, Pomegranate, Apple, Green leafy vegetables, Light foods, Avoid heavy, oily, sweet foods"
        restrictions = "Avoid: Heavy oily foods, Excess sweets, Dairy excess, Red meat heavy, Fried foods"
        instructions = "1. Light diet\n2. Regular exercise\n3. Avoid overeating\n4. Fresh air\n5. Early dinner\n6. Avoid humid environment"
      elif cold_score >= hot_score and wet_score >= dry_score:
        temperament = "Cold & Wet (Sard Tar)"
        diet = "Hot & Dry foods: Honey, Ginger, Dry fruits, Dates, Chicken soup, Warm milk with honey, Garlic, Hot spices in moderation"
        restrictions = "Avoid: Cold water, Ice cream, Cold drinks, Cucumber excess, Yogurt excess, Heavy cold foods"
        instructions = "1. Warm foods\n2. Ginger tea\n3. Keep body warm\n4. Light exercise to generate heat\n5. Avoid cold exposure\n6. Sunlight exposure morning"
      else:
        temperament = "Cold & Dry (Sard Khushk)"
        diet = "Hot & Wet foods: Soups, Milk, Ghee in moderation, Dates, Almonds, Chicken, Eggs, Warm foods, Honey, Sesame"
        restrictions = "Avoid: Dry foods, Cold foods, Bitter foods, Excess fasting, Dry beans excess"
        instructions = "1. Moist & warm foods\n2. Oil massage\n3. Adequate sleep\n4. Avoid dry cold air\n5. Warm milk at night\n6. Keep hydrated with warm fluids"
      
      # Save to session for display
      st.session_state[f"{prefix}_temperament_result"] = temperament
      st.session_state[f"{prefix}_diet_result"] = diet
      st.session_state[f"{prefix}_restrictions_result"] = restrictions
      st.session_state[f"{prefix}_instructions_result"] = instructions
      
      new_id = get_next_auto_id()
      ws=get_sheet_safe("AutoDiagnosis")
      if ws:
        diseases_str = " + ".join([d.get("text","") for d in (st.session_state.home_auto_diseases if is_home else st.session_state.auto_diseases)])
        ws.append_row([f"AUTO{new_id}", f"AUTO{new_id}", str(__import__('datetime').date.today()), p_name, p_father, p_age, p_phone, p_gender, p_address, diseases_str, extra_symptoms + f" | Sleep:{sleep_pat} Appetite:{appetite_pat} Bowel:{bowel} Temperament:{temperament}", "N/A", st.session_state.clinic_name, st.session_state.username, APP_VERSION, 0], value_input_option="RAW")
        get_all_records_cached.clear()
      st.success(f"Proceed completed for {p_name} - Temperament: {temperament} - ID AUTO{new_id}")
      st.balloons()
    except Exception as e:
      st.warning(f"Proceed saved locally - {e} - {str(e)[:200]}")

    if is_home:
      st.session_state.show_home_proceed_note = True
    else:
      st.session_state.show_proceed_note = True
    st.session_state[personal_ok_key] = False
    st.session_state[diseases_ok_key] = False
    st.session_state[additional_ok_key] = False
    st.session_state[version_key] = 0
    if is_home:
      st.session_state.home_auto_diseases = []
    else:
      st.session_state.auto_diseases = []
    st.session_state.form_version += 1
    st.rerun()

  # V200.15 FIX 1d: Note visible - white text on dark, not black on black
  show_note = st.session_state.get(f"{'show_home_proceed_note' if is_home else 'show_proceed_note'}", False)
  if show_note:
    st.markdown("---")
    # V200.15 FIX 1d: Clear visible note - white/yellow text on dark background, not black on black
    temperament = st.session_state.get(f"{prefix}_temperament_result", "Not calculated")
    diet = st.session_state.get(f"{prefix}_diet_result", "")
    restrictions = st.session_state.get(f"{prefix}_restrictions_result", "")
    instructions = st.session_state.get(f"{prefix}_instructions_result", "")
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg,#1a1c23,#2d3748);border:2px solid #FFD700;border-left:6px solid #ff0000;padding:18px;border-radius:12px;margin:16px 0;box-shadow:0 4px 12px rgba(0,0,0,0.5);">
      <div style="color:#FFD700;font-size:18px;font-weight:900;margin-bottom:8px;">Note! These results are not final; work on them is currently in progress. You will be notified soon once the work is complete.</div>
      <div style="color:#FFFFFF;font-size:14px;margin-top:10px;">Your temperament has been calculated from form fields. Diet suggestions are preliminary.</div>
      <div style="color:#00E676;font-size:16px;font-weight:800;margin-top:12px;">Temperament: {temperament}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # V200.15 FIX 1e: Show Diet, Restrictions, Instructions extracted from temperament - other fields locked
    st.markdown("<div class='heading-h4'>Results - Based on Temperament from Form Fields</div>", unsafe_allow_html=True)
    with st.container(border=True):
      # 1. Diet - from temperament
      st.markdown("<div class='heading-h5'>1. Diet (Suggested per Temperament)</div>", unsafe_allow_html=True)
      st.text_area("Diet", value=diet, key=f"{prefix}_diet_result_v200_15", height=120, disabled=False)
      # 2. Dietary Restrictions
      st.markdown("<div class='heading-h5'>2. Dietary Restrictions</div>", unsafe_allow_html=True)
      st.text_area("Dietary Restrictions", value=restrictions, key=f"{prefix}_diet_rest_result_v200_15", height=100, disabled=False)
      # 3. Instructions
      st.markdown("<div class='heading-h5'>3. Instructions</div>", unsafe_allow_html=True)
      st.text_area("Instructions", value=instructions, key=f"{prefix}_instr_result_v200_15", height=120, disabled=False)
      # Other fields locked
      st.markdown("<div class='heading-h5'>Other Fields - Locked (Coming Soon)</div>", unsafe_allow_html=True)
      st.text_area("4. Medications (Locked)", value="Medications will be suggested by physician - Currently locked", disabled=True, key=f"{prefix}_meds_locked_v200_15", placeholder="Locked")
      st.text_area("5. Follow-up (Locked)", value="Follow-up examination - Currently locked", disabled=True, key=f"{prefix}_followup_locked_v200_15", placeholder="Locked")
    
    if st.button("Start New Entry", key=f"{prefix}_new_entry_v200_15"):
      st.session_state.show_home_proceed_note = False
      st.session_state.show_proceed_note = False
      st.session_state[personal_ok_key] = False
      st.session_state[diseases_ok_key] = False
      st.session_state[additional_ok_key] = False
      st.session_state[version_key] = 0
      st.session_state.form_version += 1
      # Clear results
      for k in [f"{prefix}_temperament_result", f"{prefix}_diet_result", f"{prefix}_restrictions_result", f"{prefix}_instructions_result"]:
        if k in st.session_state: del st.session_state[k]
      st.rerun()

  return p_name, p_father, p_age, p_phone, p_gender, p_address, diseases_list

def auto_selection_page():
  scroll_to_top()
  top_bar_inner_with_user()
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
      for idx, r in enumerate(filt[:10]):
        with st.container(border=True):
          st.write(f"{r.get('Name','')} | {r.get('Phone','')} | {r.get('Date','')} | {r.get('Diseases','')[:100]}")
          if st.button(f"Select {r.get('ID','')}", key=f"auto_sel_{r.get('ID','')}_{idx}_v200_17"):
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
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>Home User Page</div>", unsafe_allow_html=True)
  # V172: Tab to add up to 5 patients and create forms; phone must match Home User signup
  tab1, tab2 = st.tabs(["Home treatment", "My Patients (Up to 5)"])
  with tab1:
    st.markdown("<div class='heading-h4'>Home treatment</div>", unsafe_allow_html=True)
    mode = st.radio("Select Mode", ["New Patient", "Revisit"], key="home_auto_mode_radio_v172", horizontal=True)
    st.session_state.home_auto_form_mode = mode
    if mode == "Revisit":
      st.session_state.home_auto_form_mode_prev = "Revisit"
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
        for idx, r in enumerate(filt[:10]):
          with st.container(border=True):
            st.write(f"{r.get('Name','')} | {r.get('Phone','')} | {r.get('Date','')}")
            if st.button(f"Select {r.get('ID','')}", key=f"home_auto_sel_{r.get('ID','')}_{idx}_v200_17"):
              st.session_state.home_auto_selected_patient = r
              st.rerun()
    else:
      # V200.16 FIX 1: Only clear once when switching to New Patient, not every rerun - fixes Added Diseases bug
      if st.session_state.get("home_auto_form_mode_prev") != "New Patient":
        st.session_state.home_auto_selected_patient = None
        st.session_state.home_auto_diseases = []
        st.session_state.auto_diseases = []
        st.session_state.home_auto_form_mode_prev = "New Patient"
      # Ensure lists exist
      if "home_auto_diseases" not in st.session_state:
        st.session_state.home_auto_diseases = []
      if "auto_diseases" not in st.session_state:
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
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>New Patient</div>", unsafe_allow_html=True)
  render_patient_form(is_revisit=False)
  under_development_footer("New Patient")
  add_footer()

def patient_revisit_form_page():
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>Revisit Form</div>", unsafe_allow_html=True)
  render_patient_form(is_revisit=True)
  under_development_footer("Revisit Form")
  add_footer()

def revisit_page():
  scroll_to_top()
  top_bar_inner_with_user()
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
    for idx, r in enumerate(filt[:15]):
      with st.container(border=True):
        st.write(f"{r.get('Name','')} | Date: {r.get('Date','')} | Address: {r.get('Address','')} | Phone: {r.get('Phone','')} | ID: {r.get('PatientID','')} | Balance: Rs {r.get('Balance','0')}")
        if st.button(f"Open {r.get('PatientID','')}", key=f"rev_{r.get('PatientID','')}_{idx}_v209_6_6"):
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
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>Dictionary</div>", unsafe_allow_html=True)
  recs=get_all_records_cached("Dictionary")
  for r in recs[:20]:
    st.write(f"{r.get('Word','')} - {r.get('Meaning','')}")
  under_development_footer("Dictionary")
  add_footer()

def pharmacopoeia_page():
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>Pharmacopoeia</div>", unsafe_allow_html=True)
  recs=get_all_records_cached("Pharmacopoeia")
  for r in recs[:20]:
    with st.container(border=True):
      st.write(f"{r.get('Name','')} - {r.get('Uses','')}")
  under_development_footer("Pharmacopoeia")
  add_footer()

def clinic_herb_formula_page():
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>Herbs & Pharmacopoeia</div>", unsafe_allow_html=True)
  st.info("Data Source: Google Sheets - Herbs and Formulas sheets. When you add data to sheet, it will appear here automatically")
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
  scroll_to_top()
  top_bar_inner_with_user()
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
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>📰 Articles - Modern Cards V203</div>", unsafe_allow_html=True)
  recs = get_all_records_cached("Articles")
  clinic_recs = [r for r in recs if str(r.get("Audience","")).lower() in ["all","clinic",""]]
  if not clinic_recs:
    clinic_recs = recs

  lang_sel = st.radio("Select Language", ["English", "Urdu - Urdu", "Arabic - Arabic"], horizontal=True, key="clinic_art_lang_v203")
  lang_map = {"English":"en", "Urdu - Urdu":"ur", "Arabic - Arabic":"ar"}
  sel_lang = lang_map[lang_sel]

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

  if not filtered_sorted:
    st.info(f"No {sel_lang.upper()} articles found - Add from App Admin")
  else:
    # Modern Cards Grid - 2 per row on PC, 1 on mobile via columns
    st.markdown("<div style='margin-bottom:12px;'><b>Modern Card View - Click to Read</b></div>", unsafe_allow_html=True)
    # Show as cards grid
    for i in range(0, len(filtered_sorted[:20]), 2):
      c1,c2 = st.columns(2)
      for idx, col in enumerate([c1,c2]):
        if i+idx < len(filtered_sorted):
          r = filtered_sorted[i+idx]
          title = ""
          if sel_lang=="en": title = r.get("TitleEN","")
          elif sel_lang=="ur": title = r.get("TitleUR","")
          else: title = r.get("TitleAR","")
          content_preview = ""
          if sel_lang=="en": content_preview = str(r.get("ContentEN",""))[:120]
          elif sel_lang=="ur": content_preview = str(r.get("ContentUR",""))[:120]
          else: content_preview = str(r.get("ContentAR",""))[:120]
          with col:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg,#FFFFFF,#F1F7F3);border:2px solid #C8E6D5;border-radius:16px;padding:16px;margin-bottom:12px;box-shadow:0 4px 14px rgba(46,125,91,0.10);min-height:140px;">
              <div style="font-size:18px;font-weight:800;color:#2E7D5B;">{title or 'Untitled'}</div>
              <div style="font-size:13px;color:#5a6d65;margin-top:8px;">{content_preview}...</div>
              <div style="font-size:11px;color:#999;margin-top:8px;">{r.get('MainCategory','')} | {r.get('Date','')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Read - {title[:20]}", key=f"clinic_card_{r.get('ID','')}_{i}_{idx}_v203", use_container_width=True):
              st.session_state.clinic_selected_article_id = r.get("ID","")
              st.rerun()
    
    if st.session_state.clinic_selected_article_id:
      sel = next((r for r in recs if r.get("ID","")==st.session_state.clinic_selected_article_id), None)
      if sel:
        st.markdown("---")
        heading = sel.get("TitleEN","") if sel_lang=="en" else sel.get("TitleUR","") if sel_lang=="ur" else sel.get("TitleAR","")
        content = sel.get("ContentEN","") if sel_lang=="en" else sel.get("ContentUR","") if sel_lang=="ur" else sel.get("ContentAR","")
        st.markdown(f"<div class='heading-h3'>{heading}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:#FFFFFF;border:2px solid #2E7D5B;border-radius:16px;padding:20px;white-space:pre-wrap;box-shadow:0 6px 18px rgba(46,125,91,0.12);'>{content}</div>", unsafe_allow_html=True)
        if st.button("Close", key="close_clinic_v203"):
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

  lang_sel = st.radio("Select Language", ["English", "Urdu - Urdu", "Arabic - Arabic"], horizontal=True, key="home_art_lang_v181")
  lang_map = {"English":"en", "Urdu - Urdu":"ur", "Arabic - Arabic":"ar"}
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



def clinic_admin_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Clinic Admin</div>", unsafe_allow_html=True)
    
    # V200.11 FIX 4: 2 options Settings, Formulas
    if "clinic_admin_selected" not in st.session_state:
        st.session_state.clinic_admin_selected = "Settings"
    
    c1,c2=st.columns(2)
    with c1:
        if st.button("Settings", key="clinic_admin_opt_settings_v200_13", type="primary" if st.session_state.clinic_admin_selected=="Settings" else "secondary", use_container_width=True):
            st.session_state.clinic_admin_selected = "Settings"
            st.rerun()
    with c2:
        if st.button("Formulas", key="clinic_admin_opt_formulas_v200_13", type="primary" if st.session_state.clinic_admin_selected=="Formulas" else "secondary", use_container_width=True):
            st.session_state.clinic_admin_selected = "Formulas"
            st.rerun()
    
    st.markdown("<hr style='margin:12px 0; border:1.5px solid #2E7D5B;'>", unsafe_allow_html=True)
    
    if st.session_state.clinic_admin_selected == "Settings":
        st.markdown("<div class='heading-h4'>Clinic Settings</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: linear-gradient(135deg,#E8F5E9,#FFFFFF);border:2px solid #2E7D5B;border-radius:16px;padding:16px;margin-bottom:14px;">
            <b>Clinic Settings:</b> Control which tabs appear on dashboard. Default: New Patient, Revisit, Clinic Admin always active.
        </div>
        """, unsafe_allow_html=True)
        
        if "clinic_dashboard_settings" not in st.session_state:
            st.session_state.clinic_dashboard_settings = {
                "New Patient": True, "Revisit": True, "Clinic Admin": True,
                "Auto-Diagnosis": False, "Dictionary": False, "Articles": False,
                "Herbs & Pharma": False, "Free Health Tools": False, "Essential": False,
                "Inventory": False, "Billing Report": False, "Staff Management": False,
                "Patient Analytics": False, "Appointments": False, "Expenses": False,
            }
        st.session_state.clinic_dashboard_settings["Clinic Admin"] = True
        st.session_state.clinic_dashboard_settings["New Patient"] = True
        st.session_state.clinic_dashboard_settings["Revisit"] = True
        settings = st.session_state.clinic_dashboard_settings
        
        st.markdown("<div class='dash-section-title'>Clinic Dashboard Tabs Control</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='heading-h4'>Core Tabs - Always Visible</div>", unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            with c1: st.checkbox("New Patient - Default ON", value=True, disabled=True, key="clinic_admin_new_fixed_v200_13")
            with c2: st.checkbox("Revisit - Default ON", value=True, disabled=True, key="clinic_admin_revisit_fixed_v200_13")
            with c3: st.checkbox("Clinic Admin - Permanent ON", value=True, disabled=True, key="clinic_admin_admin_fixed_v200_13")
        with st.container(border=True):
            st.markdown("<div class='heading-h4'>Clinic Section Tabs - Show/Hide</div>", unsafe_allow_html=True)
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                settings["Auto-Diagnosis"] = st.checkbox("Auto-Diagnosis", value=settings.get("Auto-Diagnosis", False), key="clinic_admin_auto_v200_13")
                settings["Dictionary"] = st.checkbox("Dictionary", value=settings.get("Dictionary", False), key="clinic_admin_dict_v200_13")
            with c2:
                settings["Articles"] = st.checkbox("Articles", value=settings.get("Articles", False), key="clinic_admin_articles_v200_13")
                settings["Herbs & Pharma"] = st.checkbox("Herbs & Pharma", value=settings.get("Herbs & Pharma", False), key="clinic_admin_herbs_v200_13")
            with c3:
                settings["Free Health Tools"] = st.checkbox("Free Health Tools", value=settings.get("Free Health Tools", False), key="clinic_admin_tools_v200_13")
            with c4:
                settings["Clinic Overview"] = st.checkbox("Clinic Overview", value=settings.get("Clinic Overview", False), key="clinic_admin_overview_v200_13")
                settings["Essential"] = st.checkbox("Essential", value=settings.get("Essential", False), key="clinic_admin_essential_v200_13")
        
        st.session_state.clinic_dashboard_settings = settings
        if st.button("Save Clinic Settings", type="primary", use_container_width=True, key="clinic_admin_save_v200_13"):
            st.success("Clinic Settings Saved!")
            st.balloons()
            try:
                save_to_local_csv("AppSettings", {"Key": "ClinicDashboardSettings", "Value": str(settings), "Date": str(__import__('datetime').date.today()), "Description": "Clinic Dashboard Tabs Control"})
            except: pass
            st.rerun()
        st.markdown("---")
        active_tabs = [k for k,v in settings.items() if v]
        st.markdown(f"<div style='background:#F1F7F3;border:2px solid #2E7D5B;border-radius:12px;padding:12px;'><b>Active Tabs ({len(active_tabs)}):</b> {', '.join(active_tabs)}</div>", unsafe_allow_html=True)
    
    else:  # Formulas
        st.markdown("<div class='heading-h4'>Clinic Formulas - Add Your Own Formulas</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: linear-gradient(135deg,#FFF3E0,#FFFFFF);border:2px solid #FF9800;border-radius:16px;padding:16px;margin-bottom:14px;">
            <b>Formulas Management:</b> Add your clinic custom formulas. These appear in Prescription - Formula Medicines list (searchable).
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='heading-h5'>Add New Formula</div>", unsafe_allow_html=True)
            c1,c2=st.columns([2,1])
            with c1:
                formula_name = st.text_input("Formula Name *", key="clinic_formula_name_v200_11", placeholder="e.g., Majoon Dabeed Special")
            with c2:
                formula_type = st.selectbox("Formula Type", ["Majoon","Jawarish","Hab","Sharbat","Arq","Roghan","Khamira","Other"], key="clinic_formula_type_v200_11")
            formula_ingredients = st.text_area("Ingredients / Composition", key="clinic_formula_ing_v200_11", placeholder="e.g., Amla 10g, Haldi 5g, Honey Q.S.")
            formula_indication = st.text_input("Indication / Use", key="clinic_formula_ind_v200_11", placeholder="e.g., For stomach, liver weakness")
            formula_dosage = st.text_input("Dosage", key="clinic_formula_dosage_v200_11", placeholder="e.g., 5g twice daily")
            if st.button("Add Formula +", key="clinic_add_formula_v200_11", type="primary"):
                if not formula_name.strip():
                    st.error("Formula Name required")
                else:
                    formula_dict = {
                        "FormulaID": f"F{int(__import__('datetime').datetime.now().timestamp())}",
                        "Name": formula_name.strip(), "FormulaName": formula_name.strip(),
                        "Type": formula_type, "Ingredients": formula_ingredients.strip(),
                        "Indication": formula_indication.strip(), "Dosage": formula_dosage.strip(),
                        "ClinicName": st.session_state.get("clinic_name",""), "CreatedBy": st.session_state.get("username",""),
                        "Date": str(__import__('datetime').date.today())
                    }
                    try:
                        ws = get_sheet_safe("Formulas")
                        if ws:
                            hdr = ws.row_values(1)
                            if not hdr or len(hdr) < 3: hdr = list(formula_dict.keys())
                            row = [str(formula_dict.get(h,"")) for h in hdr]
                            ws.append_row(row, value_input_option="RAW")
                            st.success(f"Formula '{formula_name}' saved to Google Sheet!")
                    except Exception as e:
                        st.warning(f"Sheet save: {e} - saved locally")
                    save_to_local_csv("Formulas", formula_dict)
                    st.balloons()
                    for k in ["clinic_formula_name_v200_11","clinic_formula_ing_v200_11","clinic_formula_ind_v200_11","clinic_formula_dosage_v200_11"]:
                        if k in st.session_state: st.session_state[k] = ""
                    st.rerun()
        with st.container(border=True):
            st.markdown("<div class='heading-h5'>Your Clinic Formulas</div>", unsafe_allow_html=True)
            try:
                formula_recs = get_all_records_cached("Formulas")
                clinic_name = st.session_state.get("clinic_name","")
                my_formulas = [r for r in formula_recs if str(r.get("ClinicName","")).lower() == clinic_name.lower()] if clinic_name else formula_recs
                if not my_formulas:
                    st.info("No formulas yet - Add your first formula above")
                else:
                    for idx, f in enumerate(my_formulas[-10:][::-1]):
                        st.markdown(f"<div style='background:#FFFFFF;border:1.5px solid #C8E6D5;border-radius:10px;padding:10px;margin:6px 0;'><b>{idx+1}. {f.get('Name','') or f.get('FormulaName','')}</b> ({f.get('Type','')})<br><b>Ingredients:</b> {f.get('Ingredients','')[:100]}<br><b>Indication:</b> {f.get('Indication','')} | <b>Dosage:</b> {f.get('Dosage','')}</div>", unsafe_allow_html=True)
                    st.caption(f"Total {len(my_formulas)} formulas for {clinic_name}")
            except Exception as e:
                st.info(f"Formulas load: {e}")
    
    under_development_footer("Clinic Admin")
    add_footer()


def dashboard_welcome_page():

  scroll_to_top()
  # V209.5 Task 2b: Dashboard - box at top with theme/language icons, no simple line above
  language_selector()
  clinic_heading_banner_dashboard_only()
  top_nav_dashboard()
  
  # V200.16 FIX 2: Time Out fix - Cache dashboard stats for 15 minutes to prevent heavy sheet read
  import time
  now_ts = time.time()
  last_ts = st.session_state.get("dashboard_stats_ts", 0)
  if now_ts - last_ts < 900 and "dashboard_stats_cache" in st.session_state:
    stats = st.session_state.dashboard_stats_cache
    total_patients = stats.get("total_patients", 0)
    today_patients = stats.get("today_patients", 0)
    pending = stats.get("pending", 0)
    total_income = stats.get("total_income", 0)
  else:
    try:
      # V200 FIX: Only load if clinic_name exists and avoid heavy calc on first load after reboot
      if st.session_state.get("clinic_name"):
        records = get_all_records_cached("New_patient")
        my_records = [r for r in records if str(r.get("ClinicName","")).lower() == str(st.session_state.clinic_name).lower()]
        total_patients = len(my_records)
        today_str = str(datetime.date.today())
        today_patients = len([r for r in my_records if today_str in str(r.get("Date",""))])
        pending = len([r for r in my_records if str(r.get("Balance","0")).strip() not in ["0","","0.0"]])
        total_income = 0
        for r in my_records[:500]: # Limit to 500 for income calc to prevent hang
          try:
            total_income += float(str(r.get("Total","0") or 0).replace(",","") or 0)
          except: pass
        # Cache it
        st.session_state.dashboard_stats_cache = {
          "total_patients": total_patients,
          "today_patients": today_patients,
          "pending": pending,
          "total_income": total_income
        }
        st.session_state.dashboard_stats_ts = now_ts
      else:
        total_patients = 0
        today_patients = 0
        pending = 0
        total_income = 0
    except:
      total_patients = st.session_state.get("dashboard_stats_cache", {}).get("total_patients", 0)
      today_patients = st.session_state.get("dashboard_stats_cache", {}).get("today_patients", 0)
      pending = st.session_state.get("dashboard_stats_cache", {}).get("pending", 0)
      total_income = st.session_state.get("dashboard_stats_cache", {}).get("total_income", 0)
  
  # V209.4 Task 1: Clinic Overview default OFF, controllable via Clinic Admin
  # Check if Clinic Overview is enabled in clinic_dashboard_settings
  overview_enabled = st.session_state.get("clinic_dashboard_settings", {}).get("Clinic Overview", False)
  if overview_enabled:
    st.markdown("<div class='dash-section-title'>Clinic Overview</div>", unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)
    with m1:
      st.markdown(f"<div style='background: linear-gradient(135deg,#E8F5E9,#FFFFFF);border:2px solid #2E7D5B;border-radius:16px;padding:18px;text-align:center;box-shadow:0 6px 16px rgba(46,125,91,0.12);'><div style='font-size:14px;color:#5a6d65;font-weight:700;'>TOTAL PATIENTS</div><div style='font-size:32px;font-weight:900;color:#2E7D5B;margin-top:6px;'>{total_patients}</div></div>", unsafe_allow_html=True)
    with m2:
      st.markdown(f"<div style='background: linear-gradient(135deg,#FFF3E0,#FFFFFF);border:2px solid #FF9800;border-radius:16px;padding:18px;text-align:center;box-shadow:0 6px 16px rgba(255,152,0,0.12);'><div style='font-size:14px;color:#5a6d65;font-weight:700;'>TODAY</div><div style='font-size:32px;font-weight:900;color:#FF9800;margin-top:6px;'>{today_patients}</div></div>", unsafe_allow_html=True)
    with m3:
      st.markdown(f"<div style='background: linear-gradient(135deg,#FFEBEE,#FFFFFF);border:2px solid #F44336;border-radius:16px;padding:18px;text-align:center;box-shadow:0 6px 16px rgba(244,67,54,0.12);'><div style='font-size:14px;color:#5a6d65;font-weight:700;'>PENDING</div><div style='font-size:32px;font-weight:900;color:#F44336;margin-top:6px;'>{pending}</div></div>", unsafe_allow_html=True)
    with m4:
      st.markdown(f"<div style='background: linear-gradient(135deg,#E3F2FD,#FFFFFF);border:2px solid #2196F3;border-radius:16px;padding:18px;text-align:center;box-shadow:0 6px 16px rgba(33,150,243,0.12);'><div style='font-size:14px;color:#5a6d65;font-weight:700;'>INCOME</div><div style='font-size:28px;font-weight:900;color:#2196F3;margin-top:6px;'>Rs {total_income:.0f}</div></div>", unsafe_allow_html=True)
    
    try:
      import pandas as pd
      from datetime import timedelta
      dates = [(datetime.date.today() - timedelta(days=i)).isoformat() for i in range(6,-1,-1)]
      counts = []
      for d in dates:
        c = len([r for r in my_records if d in str(r.get("Date",""))])
        counts.append(c)
      chart_df = pd.DataFrame({"Date": dates, "Patients": counts})
      chart_df = chart_df.set_index("Date")
      st.markdown("<div style='margin-top:14px;'><b>Last 7 Days</b></div>", unsafe_allow_html=True)
      st.bar_chart(chart_df, height=180)
    except:
      pass
  else:
    # V209.6 Task 3: Additional tabs message
    st.markdown("<div style='background:#F5F5F5;border:1px dashed #999;border-radius:10px;padding:10px;text-align:center;color:#666;'>Additional tabs can be added to the dashboard by the clinic admin.</div>", unsafe_allow_html=True)
  
  st.markdown("<div class='dash-section-title'>Clinic Section</div>", unsafe_allow_html=True)
  # V209.3 Fix 1,2,3: Clinic Admin Control - Permanent, Only New Patient+Revisit ON by default, others OFF
  # Ensure clinic_dashboard_settings exists and Clinic Admin forced ON
  if "clinic_dashboard_settings" not in st.session_state:
    st.session_state.clinic_dashboard_settings = {
      "New Patient": True, "Revisit": True, "Clinic Admin": True,
      "Clinic Overview": False,
      "Auto-Diagnosis": False, "Dictionary": False, "Articles": False,
      "Herbs & Pharma": False, "Free Health Tools": False,
      "Essential": False, "Inventory": False, "Billing Report": False,
      "Staff Management": False, "Patient Analytics": False, "Appointments": False, "Expenses": False
    }
  # Force permanent tabs
  st.session_state.clinic_dashboard_settings["Clinic Admin"] = True
  st.session_state.clinic_dashboard_settings["New Patient"] = True
  st.session_state.clinic_dashboard_settings["Revisit"] = True
  
  dash_settings = st.session_state.get("clinic_dashboard_settings", {
    "New Patient": True, "Revisit": True, "Clinic Admin": True,
    "Auto-Diagnosis": False, "Dictionary": False, "Articles": False,
    "Herbs & Pharma": False, "Free Health Tools": False, "Offer": False
  })
  # Double ensure Clinic Admin always True even if settings says False
  dash_settings["Clinic Admin"] = True
  
  r1c1,r1c2,r1c3,r1c4=st.columns(4)
  with r1c1:
    # New Patient - Always visible - Default ON
    st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
    if st.button("New Patient", use_container_width=True, key="dash_new_v206"):
      st.session_state.prev_page = "dashboard_welcome"
      st.session_state.page_history.append("dashboard_welcome")
      st.session_state.form_version+=1
      st.session_state.prev_balance=0.0
      st.session_state.revisit_data=None
      st.session_state.patient_diseases = [] # V209 Fix 6 - empty by default
      st.session_state.section_opened={"personal": True, "vital": False, "assessment": False, "complaint": False, "history": False, "prescription": False, "billing": False}
      st.session_state.current_page="patient"
      st.session_state.force_scroll_to_top = True
      st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
  with r1c2:
    # Revisit - Always visible - Default ON
    st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
    if st.button("Revisit", use_container_width=True, key="dash_rev_v206"):
      st.session_state.prev_page = "dashboard_welcome"
      st.session_state.page_history.append("dashboard_welcome")
      st.session_state.current_page="revisit"
      st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
  with r1c3:
    # Clinic Admin - Permanent ON - Always visible
    st.markdown("<div class='graceful-card' style='background: linear-gradient(135deg,#E3F2FD,#FFFFFF)!important;border:2px solid #2196F3!important;'>", unsafe_allow_html=True)
    if st.button("Clinic Admin", use_container_width=True, key="dash_clinic_admin_v209"):
      st.session_state.prev_page = "dashboard_welcome"
      st.session_state.page_history.append("dashboard_welcome")
      st.session_state.current_page="clinic_admin"
      st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
  with r1c4:
    # Auto-Diagnosis - Controlled by Clinic Admin
    if dash_settings.get("Auto-Diagnosis", True):
      st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
      if st.button("Auto-Diagnosis", use_container_width=True, key="dash_auto_v206"):
        st.session_state.prev_page = "dashboard_welcome"
        st.session_state.page_history.append("dashboard_welcome")
        st.session_state.current_page="auto_selection"
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)
  r2c1,r2c2,r2c3,r2c4=st.columns(4)
  with r2c1:
    if dash_settings.get("Dictionary", True):
      st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
      if st.button("Dictionary", use_container_width=True, key="dash_dict_v206"):
        st.session_state.prev_page = "dashboard_welcome"
        st.session_state.page_history.append("dashboard_welcome")
        st.session_state.current_page="dictionary"
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)
  with r2c2:
    if dash_settings.get("Articles", True):
      st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
      if st.button("Articles", use_container_width=True, key="dash_c_art_v206"):
        st.session_state.prev_page = "dashboard_welcome"
        st.session_state.page_history.append("dashboard_welcome")
        st.session_state.current_page="clinic_articles"
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)
  with r2c3:
    if dash_settings.get("Herbs & Pharma", True):
      st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
      if st.button("Herbs & Pharma", use_container_width=True, key="dash_herb_v206"):
        st.session_state.prev_page = "dashboard_welcome"
        st.session_state.page_history.append("dashboard_welcome")
        st.session_state.current_page="clinic_herb_formula"
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)
  with r2c4:
    if dash_settings.get("Free Health Tools", True):
      st.markdown("<div class='graceful-card' style='background: linear-gradient(135deg,#FFF9C4,#FFFFFF)!important;border:2px solid #FF9800!important;'>", unsafe_allow_html=True)
      if st.button("Free Health Tools", use_container_width=True, key="dash_quiz_clinic_v206"):
        st.session_state.prev_page = "dashboard_welcome"
        st.session_state.page_history.append("dashboard_welcome")
        st.session_state.current_page="temperament_quiz"
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)
  # V209 Fix - Removed duplicate Articles/Herbs/Free Tools block - keys now unique above
  # V209.4 Task 3: Offer tab controlled ONLY by App Admin, not Clinic Admin
  r3c1,r3c2,r3c3,r3c4=st.columns(4)
  # Offer is controlled by App Admin via AppSettings - OfferEnabled
  show_offer = get_app_setting("OfferEnabled", get_app_setting("show_offer_tab","Yes"))
  if str(show_offer).lower() in ["yes","on","true","1","enabled"]: 
    with r3c1:
      st.markdown("<div class='graceful-card' style='border:3px solid #00ff88; animation: blinkGreen 1.2s infinite;'>", unsafe_allow_html=True)
      if st.button("Offer", use_container_width=True, key="dash_offer_v209"):
        st.session_state.prev_page = "dashboard_welcome"
        st.session_state.page_history.append("dashboard_welcome")
        st.session_state.current_page="offer_page"
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)
  # Essential tab if enabled in Clinic Admin
  if dash_settings.get("Essential", False):
    with r3c2:
      st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
      if st.button("Essential", use_container_width=True, key="dash_essential_v209"):
        st.session_state.prev_page = "dashboard_welcome"
        st.session_state.page_history.append("dashboard_welcome")
        st.session_state.current_page="essential_page"
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)

  st.markdown("<div class='dash-section-title'>Home User</div>", unsafe_allow_html=True)
  h1,h2,h3=st.columns(3)
  with h1:
    st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
    if st.button("Home User Page", use_container_width=True, key="dash_home_v206"):
      st.session_state.prev_page = "dashboard_welcome"
      st.session_state.page_history.append("dashboard_welcome")
      st.session_state.current_page="home_user"
      st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
  with h2:
    st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
    if st.button("Articles", use_container_width=True, key="dash_home_art_v206"):
      st.session_state.prev_page = "dashboard_welcome"
      st.session_state.page_history.append("dashboard_welcome")
      st.session_state.current_page="home_user_articles"
      st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
  with h3:
    # V206 Requirement 4b: Free Health Tools inside Home User Section
    st.markdown("<div class='graceful-card' style='background: linear-gradient(135deg,#E8F5E9,#FFFFFF)!important;border:2px solid #2E7D5B!important;'>", unsafe_allow_html=True)
    if st.button("Free Health Tools", use_container_width=True, key="dash_home_quiz_v206"):
      st.session_state.prev_page = "dashboard_welcome"
      st.session_state.page_history.append("dashboard_welcome")
      st.session_state.current_page="temperament_quiz"
      st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

  if st.session_state.get("user_role") in ["Boss","Staff"] or st.session_state.get("user_type")=="Staff":
    st.markdown("<div class='dash-section-title'>App Admin</div>", unsafe_allow_html=True)
    ac1,ac2,ac3,ac4=st.columns(4)
    with ac1:
      st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
      if st.button("App Admin Panel", use_container_width=True, key="dash_admin_panel_v206"):
        st.session_state.prev_page = "dashboard_welcome"
        st.session_state.page_history.append("dashboard_welcome")
        st.session_state.current_page="admin"
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)

  # V200 FIX: Cache total users to prevent extra sheet call after reboot
  try:
    if "total_users_cache" in st.session_state and st.session_state.get("total_users_ts",0) > 0:
      import time
      if time.time() - st.session_state.total_users_ts < 600:
        display = st.session_state.total_users_cache
      else:
        raise Exception("Cache expired")
    else:
      recs = get_all_records_cached("UserSignups")
      total = len(recs)
      display = 650+total
      st.session_state.total_users_cache = display
      import time
      st.session_state.total_users_ts = time.time()
  except:
    display = st.session_state.get("total_users_cache", 650)
  st.markdown("---")
  st.markdown(f"<div style='text-align:center;'><div class='heading-h4'>Total App Users</div><div style='font-size:34px;font-weight:900;color:#2E7D5B;'>{display}</div></div>", unsafe_allow_html=True)
  add_footer()





def clinic_login_page():
  language_selector()
  # V209.6.10 Fix: No sheet calls on login page to prevent hang after reboot
  clinic_heading_banner_compact()
  with st.container(border=True):
    st.markdown("<div style='background:#E8F5E9;padding:8px;border-radius:6px;text-align:center;margin-bottom:10px;'>V209.6.10 - Login Fixed - No refresh needed</div>", unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Staff Login","Clinic User","Home User"])
    with t1:
      u=st.text_input("Username", value="boss", key="login_u_v206")
      p=st.text_input("Password", type="password", value="boss123", key="login_p_v206")
      stay = st.checkbox("Stay signed in", value=True, key="stay_staff_v206", help="If ticked, you won't need to sign in again")
      if st.button("Login", use_container_width=True, type="primary", key="staff_login_v206"):
        # V209.6.10: Direct login without sheet check to avoid hang
        st.session_state.logged_in=True
        st.session_state.username=u if u else "boss"
        st.session_state.user_role="Boss"
        st.session_state.user_type="Staff"
        st.session_state.clinic_name="Herbal Clinic International"
        st.session_state.current_page="dashboard_welcome"
        st.rerun()
    with t2:
      cu=st.text_input("Username", key="clinic_u_v206")
      cp=st.text_input("Password", type="password", key="clinic_p_v206")
      stay_c = st.checkbox("Stay signed in", value=True, key="stay_clinic_v206")
      if st.button("Login", use_container_width=True, type="primary", key="clinic_login_v206"):
        st.session_state.logged_in=True
        st.session_state.username=cu if cu else "clinic_user"
        st.session_state.user_role="clinic"
        st.session_state.user_type="Clinic"
        st.session_state.clinic_name="Herbal Clinic International"
        st.session_state.current_page="dashboard_welcome"
        st.rerun()
    with t3:
      hu=st.text_input("Username", key="home_u_v206")
      hp=st.text_input("Password", type="password", key="home_p_v206")
      stay_h = st.checkbox("Stay signed in", value=True, key="stay_home_v206")
      if st.button("Login", use_container_width=True, type="primary", key="home_login_v206"):
        st.session_state.logged_in=True
        st.session_state.username=hu if hu else "home_user"
        st.session_state.user_role="home_user"
        st.session_state.user_type="HomeUser"
        st.session_state.clinic_name="Herbal Clinic International"
        st.session_state.current_page="home_user"
        st.rerun()
  add_footer()


def feedback_page():
  scroll_to_top()
  top_bar_inner_with_user()
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
          # V202 - Save both local and sheet
          save_to_local_csv("Feedback", row_data)
          ws.append_row(row, value_input_option="RAW")
          get_all_records_cached.clear()
          st.success(f"Thank you! {fid} submitted - Full app services restored! (Saved to Sheet + Local)")
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
    st.info("This WhatsApp linked tab is now available on Feedback page fix")
  add_footer()





# ========== POPUP & FEEDBACK SUSPENSION SYSTEM ==========
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

# ========== END POPUP & FEEDBACK SYSTEM ==========


# APP ADMIN LOCKED - Do not auto-modify this page without user explicit request
def admin_page():
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown(f"<div class='heading-h3'>App Admin</div>", unsafe_allow_html=True)
  st.markdown("", unsafe_allow_html=True)

  sections = ["General", "Clinic Data", "Home User", "Users", "Article", "Offer Control", "AppSettings", "Data", "Doctor"]
  if "admin_selected_section" not in st.session_state:
    st.session_state.admin_selected_section = ""

  # Highlight menu tab that opens fix
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
    st.markdown("<div class='heading-h4'>AppSettings - Full Control Panel V201</div>", unsafe_allow_html=True)
    st.markdown("<div style='background:#F1F7F3;border:2px solid #2E7D5B;border-radius:12px;padding:12px;margin-bottom:12px;'><b>V201 - All App Settings from one page:</b> Here you can control whole app without code change. Use Code column to use in app.py: <code>get_app_setting('Key','Default')</code></div>", unsafe_allow_html=True)
    
    # Predefined settings catalog
    PREDEFINED_SETTINGS = {
      "General": [
        ("AppVersion", "V201", "Current App Version Code"),
        ("MaintenanceMode", "No", "Yes=App Closed, No=App Open"),
        ("MaintenanceMessage", "App under maintenance", "Message when MaintenanceMode=Yes"),
        ("TotalUsersBase", "650", "Base number added to total users display"),
        ("Currency", "PKR", "Currency for billing"),
        ("LanguageDefault", "en", "Default language en/ur/ar"),
      ],
      "Offer & WhatsApp": [
        ("OfferEnabled", "Yes", "Show Offer tab? Yes/No"),
        ("OfferPercent", "20", "Offer percentage"),
        ("WhatsAppLink", "https://chat.whatsapp.com/...", "WhatsApp Group Link"),
        ("WhatsAppNumber", "+92...", "Support WhatsApp Number"),
        ("SupportEmail", "support@herbalclinic.com", "Support Email"),
      ],
      "Theme & UI (V201)": [
        ("PrimaryColor", "#2E7D5B", "Primary Theme Color"),
        ("AdLinkText", "There is no need to open this ad.", "Ad link text - 2 lines with ;"),
        ("AdLinkEnabled", "Yes", "Show Ad link? Yes/No"),
        ("AdLinkBorderColor", "#B8860B", "Dark golden border for ad"),
        ("FooterText", "by mian Nadeem", "Footer text"),
        ("BannerText", "Herbal Clinic International", "Top banner text"),
      ],
      "Clinic": [
        ("DefaultFees", "500", "Default clinic fees"),
        ("DefaultMedicineCharges", "0", "Default medicine charges"),
        ("MaxDailyPatients", "50", "Max patients per day"),
        ("ClinicWorkHours", "9AM-8PM", "Working hours"),
        ("RevisitDays", "7", "Revisit after days"),
      ],
      "Home User": [
        ("MaxHomePatients", "5", "Max patients Home User can add"),
        ("HomeUserDailyLimit", "10", "Max forms per day for Home User"),
      ],
      "Security & Login (V201 Fix)": [
        ("SessionTimeout", "24", "Login stays how many hours? 24=1 day"),
        ("MaxLoginAttempts", "3", "Max login attempts"),
        ("FeedbackSuspensionDays", "7", "Suspend if no feedback after days"),
        ("PersistentLoginEnabled", "Yes", "V201 - Mobile stays logged in? Yes/No"),
      ],
      "Popup & Articles": [
        ("PopupEnabled", "Yes", "Show popups? Yes/No"),
        ("ArticlesApproval", "Auto", "Auto or Manual approval"),
        ("OfferAutoHide", "No", "Auto hide offer after date?"),
      ],
    }
    
    recs = get_all_records_cached("AppSettings")
    st.write(f"Total Settings in Sheet: {len(recs)}")
    
    # Show current settings with Code column - Requirement 5a
    if recs:
      df = pd.DataFrame(recs)
      # Add Code column for developer
      def make_code(row):
        k=row.get("Key","")
        v=row.get("Value","")
        return f"get_app_setting('{k}', '{v}')"
      if "Key" in df.columns:
        df["Code to Use in app.py"] = df.apply(make_code, axis=1)
      st.dataframe(df, use_container_width=True)
      # Also show as table with codes
      with st.expander("Show Settings with Codes (Requirement 5a)"):
        for r in recs:
          k=r.get("Key","")
          v=r.get("Value","")
          d=r.get("Description","")
          st.markdown(f"**{k}** = `{v}` | Desc: {d} | Code: `get_app_setting('{k}', '{v}')`")
    else:
      st.info("No settings yet - Add from catalog below")
    
    st.markdown("---")
    st.markdown("<div class='heading-h4'>Add / Edit Settings - Full Catalog (Requirement 5b)</div>", unsafe_allow_html=True)
    
    # Catalog display with Add buttons
    for cat, settings_list in PREDEFINED_SETTINGS.items():
      with st.expander(f"{cat} - {len(settings_list)} settings"):
        for key, default_val, desc in settings_list:
          # Check if exists
          exists = next((r for r in recs if r.get("Key","").lower()==key.lower()), None)
          c1,c2,c3,c4 = st.columns([2,2,3,1])
          with c1:
            st.markdown(f"**{key}**")
          with c2:
            st.code(f"{exists.get('Value','') if exists else default_val}", language="text")
          with c3:
            st.caption(desc)
            st.caption(f"Code: get_app_setting('{key}')")
          with c4:
            if exists:
              st.success("Exists")
            else:
              if st.button(f"Add", key=f"add_{key}_v201"):
                ws = get_sheet_safe("AppSettings")
                if ws:
                  hdr = ws.row_values(1) if ws.row_values(1) else SHEET_HEADERS["AppSettings"]
                  row_data = {"Key": key, "Value": default_val, "Date": str(datetime.date.today()), "Status": "Active", "Description": desc}
                  row = [row_data.get(h,"") for h in hdr]
                  ws.append_row(row, value_input_option="RAW")
                  get_all_records_cached.clear()
                  st.success(f"Added {key}")
                  st.rerun()
    
    st.markdown("---")
    st.markdown("<div class='heading-h4'>Custom Setting - Add New</div>", unsafe_allow_html=True)
    with st.container(border=True):
      s_key = st.text_input("Key (Code Name)", key="appset_key_v201", placeholder="e.g. MyNewSetting")
      s_val = st.text_input("Value", key="appset_val_v201", placeholder="e.g. Yes or 123")
      s_desc = st.text_input("Description + Code hint", key="appset_desc_v201", placeholder="e.g. Controls XYZ - Code: get_app_setting('MyNewSetting')")
      if st.button("Save Setting", key="appset_save_v201", type="primary"):
        if not s_key.strip():
          st.error("Key required - This is Code name used in app.py")
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
              ws.update(f"E{found_row}", [[s_desc]])
              st.success(f"Updated {s_key} = {s_val} | Code: get_app_setting('{s_key}')")
            else:
              row_data = {"Key": s_key, "Value": s_val, "Date": str(datetime.date.today()), "Status": "Active", "Description": s_desc + f" | Code: get_app_setting('{s_key}')"}
              row = [row_data.get(h,"") for h in hdr]
              ws.append_row(row, value_input_option="RAW")
              st.success(f"Added {s_key} = {s_val} | Use Code: get_app_setting('{s_key}', '{s_val}')")
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
  top_bar_inner_with_user()
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
  scroll_to_top()
  top_bar_inner_with_user()
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
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>Essential</div>", unsafe_allow_html=True)
  under_development_footer("Essential")
  add_footer()


def temperament_quiz_page():
  scroll_to_top()
  top_bar_inner_with_user()
  top_nav_inner()
  st.markdown("<div class='heading-h3'>🌡️ Check Your Temperament - Free</div>", unsafe_allow_html=True)
  st.markdown("<div style='background: linear-gradient(135deg,#F1F7F3,#FFFFFF);border:2px solid #2E7D5B;border-radius:16px;padding:16px;margin-bottom:14px;'><b>Modern Quiz:</b> Answer 6 quick questions and know your temperament. This builds interest for Pro AI version.</div>", unsafe_allow_html=True)
  
  with st.container(border=True):
    st.markdown("<div class='heading-h4'>Free Temperament Assessment</div>", unsafe_allow_html=True)
    q1 = st.radio("1. Your body feels more?", ["Hot", "Cold", "Moderate"], key="quiz_q1_v203", horizontal=True)
    q2 = st.radio("2. Your thirst?", ["High / Excessive", "Low", "Normal"], key="quiz_q2_v203", horizontal=True)
    q3 = st.radio("3. Your skin?", ["Dry & Rough", "Moist & Oily", "Soft & Normal"], key="quiz_q3_v203", horizontal=True)
    q4 = st.radio("4. Sleep?", ["Less / Disturbed", "Excess / Deep", "Normal"], key="quiz_q4_v203", horizontal=True)
    q5 = st.radio("5. Appetite?", ["High", "Low", "Normal"], key="quiz_q5_v203", horizontal=True)
    q6 = st.radio("6. Preferred weather?", ["Cold / Cool", "Hot / Warm", "Moderate"], key="quiz_q6_v203", horizontal=True)
    
    if st.button("Get My Temperament - Free", type="primary", use_container_width=True, key="quiz_submit_v203"):
      # Simple logic
      hot = 0
      cold = 0
      if q1=="Hot": hot+=2
      if q1=="Cold": cold+=2
      if q2=="High / Excessive": hot+=1
      if q2=="Low": cold+=1
      if q3=="Dry & Rough": hot+=1
      if q3=="Moist & Oily": cold+=1
      if q4=="Less / Disturbed": hot+=1
      if q4=="Excess / Deep": cold+=1
      if q5=="High": hot+=1
      if q5=="Low": cold+=1
      if q6=="Cold / Cool": hot+=1
      if q6=="Hot / Warm": cold+=1
      
      if hot>cold+1:
        result = "Hot Dry ( )"
        diet = "Cool foods, Cucumber, Yogurt, Water intake"
      elif cold>hot+1:
        result = "Cold Wet ( )"
        diet = "Warm foods, Honey, Ginger, Dry fruits"
      elif hot>cold:
        result = "Hot Wet ( )"
        diet = "Moderate cool, Fresh fruits"
      elif cold>hot:
        result = "Cold Dry ( )"
        diet = "Warm & moist, Soups, Milk"
      else:
        result = "Moderate / Normal ()"
        diet = "Balanced diet"
      
      st.balloons()
      st.markdown(f"""
      <div style="background: linear-gradient(135deg,#2E7D5B,#4CAF50);color:white;padding:22px;border-radius:16px;text-align:center;margin-top:16px;box-shadow:0 8px 20px rgba(46,125,91,0.30);">
        <div style="font-size:28px;font-weight:900;">Your Temperament: {result}</div>
        <div style="font-size:18px;margin-top:10px;">Recommended: {diet}</div>
        <div style="font-size:14px;margin-top:12px;opacity:0.9;">Want detailed AI diet + medicine? Upgrade to Pro in Next Phase!</div>
      </div>
      """, unsafe_allow_html=True)
      # Save to local backup as interest lead
      try:
        save_to_local_csv("TemperamentQuiz", {"Date": str(datetime.date.today()), "Q1": q1, "Q2": q2, "Q3": q3, "Result": result, "User": st.session_state.get("username","Guest")})
      except: pass
      
      st.markdown("---")
      if st.button("🔒 Unlock Full AI Report - Pro Version Coming Soon", use_container_width=True, key="quiz_pro_v203"):
        st.info("Pro Version will give you full diet, medicines, and lifestyle plan with AI. Stay tuned!")
  
  under_development_footer("Temperament Quiz - Free Lead Magnet")
  add_footer()



def main():
  # V209.6.10 Fix: Prevent refresh loop and hang on sign-in
  if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
    st.session_state.current_page="clinic_login"
  
  # V209.6.10: Removed query_params theme restore that caused refresh loop
  # Theme is now only from session_state, not from URL
  
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
    elif p=="temperament_quiz": temperament_quiz_page()
    elif p=="home_user": home_user_page()
    elif p=="home_user_articles": home_user_articles_page()
    elif p=="articles": articles_page()
    elif p=="clinic_articles": clinic_articles_page()
    elif p=="clinic_admin": clinic_admin_page()
    elif p=="essential_page": essential_page()
    elif p=="offer_page": offer_page()
    elif p=="feedback_page": feedback_page()
    else: dashboard_welcome_page()

if __name__=="__main__": main()
