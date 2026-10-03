# ============================================
# Herbal Clinic OS - NEW INSTALLATION SYSTEM
# VERSION: V1 - Clean Base Structure
# Date: 2026-10-03
# Previous System: V206 Light & Fast (5900 lines - retired due to size)
# New System: V1, V1.1, V1.2... (per step correction), V2, V2.1...
# Stack: VS Code + GitHub + Streamlit + Google Sheet
# ============================================

import streamlit as st
import datetime
import pandas as pd

try:
  import gspread
  from google.oauth2.service_account import Credentials
  GSPREAD_AVAILABLE = True
except ImportError:
  GSPREAD_AVAILABLE = False

APP_VERSION = "V1 - New Clean Base"

# ---------- CONFIG ----------
st.set_page_config(
  page_title="Herbal Clinic OS - V1",
  page_icon="🌿",
  layout="wide",
  initial_sidebar_state="collapsed"
)

# ---------- DICTIONARY (EN/UR/AR) - V1 Base ----------
DICT = {
  "welcome_title": {
    "en": "Welcome to Herbal Clinic International",
    "ur": "ہربل کلینک انٹر نیشنل میں خوش آمدید",
    "ar": "مرحبا بكم في عيادة الأعشاب الدولية"
  },
  "welcome_sub": {
    "en": "Your Complete Unani & Herbal Clinic Management System",
    "ur": "آپ کا مکمل یونانی و ہربل کلینک مینجمنٹ سسٹم",
    "ar": "نظام إدارة العيادة اليونانية والعشبية الكامل الخاص بكم"
  },
  "what_is": {
    "en": "What is this system?",
    "ur": "یہ سسٹم کیا ہے؟",
    "ar": "ما هو هذا النظام؟"
  },
  "what_is_desc": {
    "en": "This is a complete clinic operating system for Hakeem, Tabib and Herbal Doctors. It manages Patient, Revisit, Dictionary, Pharmacopoeia, Billing, Stock.",
    "ur": "یہ حکیم، طبیب اور ہربل ڈاکٹرز کے لیے مکمل کلینک آپریٹنگ سسٹم ہے۔ یہ مریض، دوبارہ معائنہ، لغت، قرابادین، بل، اسٹاک کا انتظام کرتا ہے۔",
    "ar": "هذا نظام تشغيل عيادة كامل للحكيم والطبيب والمعالج بالأعشاب. يدير المريض، إعادة الزيارة، القاموس، دستور الأدوية، الفوترة، المخزون."
  },
  "home_treatment": {
    "en": "Home Treatment Facility",
    "ur": "گھریلو طور پر علاج کی سہولت",
    "ar": "تسهيل العلاج المنزلي"
  },
  "home_treatment_desc": {
    "en": "Patient enters basic info and gets Mizaj, suitable foods, precautions, and kitchen-based medicines. Details in Phase 2.",
    "ur": "مریض فارم میں ضروری معلومات درج کر کے مزاج، مناسب غذائیں، پرہیز اور کچن میں موجود ادویات حاصل کرے گا۔ تفصیل فیز 2 میں۔",
    "ar": "يدخل المريض المعلومات الأساسية ويحصل على المزاج والأطعمة المناسبة والاحتياطات وأدوية المطبخ. التفاصيل في المرحلة 2."
  },
  "phases": {
    "en": "Our 3 Phases",
    "ur": "ہمارے پروگرام کے 3 فیز",
    "ar": "المراحل الثلاث لبرنامجنا"
  },
  "phase1": {
    "en": "Phase 1: Basic Structure (You are here now)",
    "ur": "فیز 1: ایپ کا بنیادی ڈھانچہ (اس وقت آپ یہاں ہیں)",
    "ar": "المرحلة 1: الهيكل الأساسي (أنت هنا الآن)"
  },
  "phase2": {
    "en": "Phase 2: Automation - Mizaj, Diet, Kitchen Medicines",
    "ur": "فیز 2: آٹومیشن - مزاج، غذا، کچن کی دوائیں",
    "ar": "المرحلة 2: الأتمتة - المزاج والنظام الغذائي وأدوية المطبخ"
  },
  "phase3": {
    "en": "Phase 3: Online Academy",
    "ur": "فیز 3: آن لائن اکیڈمی",
    "ar": "المرحلة 3: الأكاديمية عبر الإنترنت"
  }
}

def t(key):
  lang = st.session_state.get("lang", "en")
  return DICT.get(key, {}).get(lang, DICT.get(key, {}).get("en", key))

# ---------- GOOGLE SHEET HELPERS (Light) ----------
@st.cache_resource
def get_gspread_client():
  if not GSPREAD_AVAILABLE:
    return None
  try:
    # Expects secrets.toml with [gcp_service_account]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
    return client
  except Exception as e:
    return None

def get_sheet(sheet_name):
  client = get_gspread_client()
  if not client:
    return None
  try:
    sheet_id = st.secrets.get("SHEET_ID", "")
    if not sheet_id:
      return None
    sh = client.open_by_key(sheet_id)
    ws = sh.worksheet(sheet_name)
    return ws
  except:
    return None

# ---------- SESSION STATE ----------
if "lang" not in st.session_state:
  st.session_state.lang = "en"
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "username" not in st.session_state:
  st.session_state.username = "Guest"

# ---------- UI HELPERS ----------
def top_bar():
  col1, col2, col3 = st.columns([6,2,2])
  with col1:
    st.markdown(f"### 🌿 Herbal Clinic OS | {APP_VERSION}")
  with col2:
    lang_opt = st.selectbox("Language / زبان / اللغة", ["en","ur","ar"], 
                             index=["en","ur","ar"].index(st.session_state.lang),
                             label_visibility="collapsed", key="lang_select_v1")
    st.session_state.lang = lang_opt
  with col3:
    if st.session_state.logged_in:
      st.caption(f"User: {st.session_state.username}")
      if st.button("Logout", key="logout_v1"):
        st.session_state.logged_in = False
        st.rerun()

def initial_page():
  lang = st.session_state.lang
  rtl_class = "rtl" if lang in ["ur","ar"] else "ltr"
  
  # RTL CSS for Urdu/Arabic
  st.markdown("""
  <style>
  .rtl { direction: rtl; text-align: right; font-family: 'Jameel Noori Nastaleeq', 'Noto Naskh Arabic', sans-serif; line-height:1.9; }
  .ltr { direction: ltr; text-align: left; }
  .card { background:white; border:1px solid #e0e0e0; border-radius:14px; padding:18px; margin-bottom:12px; box-shadow:0 2px 8px rgba(0,0,0,0.05); }
  .red-dot { color:red; font-size:18px; }
  .phase-box { background: linear-gradient(135deg,#F1F7F3,#FFFFFF); border:2px solid #2E7D5B; border-radius:14px; padding:14px; }
  </style>
  """, unsafe_allow_html=True)

  if lang == "en":
    title_html = f"<div class='ltr card'><span class='red-dot'>🔴</span> <b>{t('welcome_title')}</b><br>{t('welcome_sub')}</div>"
  else:
    title_html = f"<div class='rtl card'><b>{t('welcome_title')}</b> <span class='red-dot'>🔴</span><br>{t('welcome_sub')}</div>"
  
  st.markdown(title_html, unsafe_allow_html=True)

  # What is
  if lang == "en":
    st.markdown(f"<div class='ltr card'><span class='red-dot'>🔴</span> <b>{t('what_is')}</b><br>{t('what_is_desc')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ltr card'><span class='red-dot'>🔴</span> <b>{t('home_treatment')}</b><br>{t('home_treatment_desc')}</div>", unsafe_allow_html=True)
  else:
    st.markdown(f"<div class='rtl card'><b>{t('what_is')}</b> <span class='red-dot'>🔴</span><br>{t('what_is_desc')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='rtl card'><b>{t('home_treatment')}</b> <span class='red-dot'>🔴</span><br>{t('home_treatment_desc')}</div>", unsafe_allow_html=True)

  # Phases
  st.markdown(f"<div class='{rtl_class} card'><b>{t('phases')}</b><br>1. {t('phase1')}<br>2. {t('phase2')}<br>3. {t('phase3')}</div>", unsafe_allow_html=True)

  st.markdown("---")
  st.markdown(f"<div class='{rtl_class}'>This App is FREE at this time. Sign up and start practice. | اس وقت یہ ایپ بالکل فری ہے۔ | التطبيق مجاني حاليا.</div>", unsafe_allow_html=True)

  if st.button("Sign Up / Sign In (Demo) - V1", type="primary", use_container_width=True):
    st.session_state.logged_in = True
    st.session_state.username = "Hakeem Guest"
    st.session_state.current_page = "dashboard"
    st.rerun()

def dashboard_page():
  top_bar()
  st.markdown(f"### Dashboard - {t('welcome_title')}")
  st.info(f"V1 Clean Base is working. Google Sheet Available: {GSPREAD_AVAILABLE}")
  
  c1,c2,c3 = st.columns(3)
  with c1:
    st.markdown("<div class='card'><b>Patient</b><br>New + Revisit</div>", unsafe_allow_html=True)
    if st.button("Open Patient", key="dash_pat_v1"): st.info("V2 میں فعال ہوگا")
  with c2:
    st.markdown("<div class='card'><b>Knowledge Base</b><br>Dictionary, Pharmacopoeia</div>", unsafe_allow_html=True)
    if st.button("Open KB", key="dash_kb_v1"): st.info("V2 میں فعال ہوگا")
  with c3:
    st.markdown("<div class='card'><b>Temperament Quiz</b><br>Free Lead Magnet</div>", unsafe_allow_html=True)
    if st.button("Open Quiz", key="dash_quiz_v1"):
      st.session_state.current_page = "quiz"
      st.rerun()

  st.markdown("---")
  st.caption("Next: V1.1 = Google Sheet full connect + 18 sheets check, V1.2 = Login persistent, V1.3 = Initial Page final language polish")

def quiz_page():
  top_bar()
  st.markdown("### 🌡️ Temperament Quiz - Free (V1 Demo)")
  q1 = st.radio("Body feels?", ["Hot","Cold","Moderate"], horizontal=True, key="q1_v1")
  q2 = st.radio("Thirst?", ["High","Low","Normal"], horizontal=True, key="q2_v1")
  if st.button("Get Result", type="primary"):
    if q1=="Hot": st.success("Result: Hot Dry - Cool foods recommended (Demo logic)")
    elif q1=="Cold": st.success("Result: Cold Wet - Warm foods recommended")
    else: st.success("Result: Moderate - Balanced diet")
  if st.button("Back to Dashboard"):
    st.session_state.current_page = "dashboard"
    st.rerun()

def main():
  if "current_page" not in st.session_state:
    st.session_state.current_page = "initial"
  
  if not st.session_state.logged_in:
    initial_page()
  else:
    if st.session_state.current_page == "quiz":
      quiz_page()
    else:
      dashboard_page()

if __name__ == "__main__":
  main()
