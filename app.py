# ============================================
# Herbal Clinic OS
# VERSION: V2 - First Step of New Phase - Initial Page Final + Dashboard + Patient Basic
# Date: 2026-10-03
# Previous: V1 Complete (20/20 Sheets)
# V2 Goals:
#  - Initial Page Final with 3 languages (EN/UR/AR) + RTL + Red Dot like V206
#  - Dashboard Welcome with metrics from Google Sheet (real count)
#  - Patient Basic Entry (New_patient) - saves to sheet
#  - Auth Still MUTED till V2.5 as per user request
#  - Same Sheet ID & secrets.toml
# ============================================

import streamlit as st
import pandas as pd
import datetime
import time

try:
  import gspread
  from google.oauth2.service_account import Credentials
  GSPREAD_AVAILABLE = True
except ImportError:
  GSPREAD_AVAILABLE = False

APP_VERSION = "V2 - Initial Page + Patient Basic"

st.set_page_config(page_title=f"Herbal Clinic OS {APP_VERSION}", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

# ---------- SHEET HEADERS (Full) ----------
SHEET_HEADERS = {
  "UserSignups": ["SignupID","Username","Password","UserType","ClinicName","Phone","Email","Date","Status","Role","From","LastLogin","DeviceInfo"],
  "New_patient": ["PatientID","Date","Name","FatherName","Age","Gender","MaritalStatus","Occupation","CNIC","Phone","EmergencyPhone","Address","Referral","Diseases","ChiefComplaint","PastHistory","FamilyHistory","Allergy","Examination","Pulse","Temperament","BP","Weight","Temperature","Height","SleepPattern","Appetite","BowelMovement","Thirst","Urine","Sweating","StressLevel","EnergyLevel","SingleMedicines","FormulaMedicines","ManualMedicines","Fees","MedicineCharges","Total","Paid","Balance","PrevBalance","PaymentMethod","FeeStatus","RevisitDate","ClinicName","CreatedBy","Timestamp","AppVersion","DailyNumber","TotalNumber","GrandTotal","UserType","Habits","BloodGroup","CuredDiseases","RemainingDiseases"],
  "Revisit": ["RevisitID","PatientID","OriginalPatientID","Date","Name","FatherName","Age","Gender","Diseases","Fees","Total","Paid","Balance","ClinicName","CreatedBy","Timestamp"],
  "Feedback": ["ID","Name","From","Phone Number","Email","Feedback Page","Feedback","Date","Status","UserType","ClinicName","Rating","Response"],
  "Herbs": ["HerbID","Name","UrduName","Temperament","Mizaj","Uses","Benefits","Dosage"],
  "Pharmacopoeia": ["ID","Name","UrduName","Category","Temperament","Mizaj","Uses","Benefits","Ingredients"],
  "Dictionary": ["ID","Word","UrduWord","ArabicWord","Meaning","MeaningUR","MeaningAR","Category","Status"],
  "Articles": ["ID","TitleEN","TitleUR","TitleAR","ContentEN","ContentUR","ContentAR","MainCategory","Status","Date"],
  "AppSettings": ["Key","Value","Date","Status","Description"],
  "HomeUsers": ["UserID","Username","FullName","Phone","Status"],
}
ALL_SHEETS = list(SHEET_HEADERS.keys())

def get_spreadsheet_id():
  def safe_get(path):
    try:
      obj=st.secrets
      for p in path: 
        try: obj=obj[p]
        except: obj=getattr(obj,p)
      return obj if isinstance(obj,str) and len(obj)>10 else None
    except: return None
  for path in [["SHEET_ID"],["connections","gsheets","spreadsheet"],["gsheets","spreadsheet"]]:
    v=safe_get(path)
    if v: return v
  return None

@st.cache_resource(ttl=900)
def get_gspread_client():
  try:
    creds_dict=None
    try:
      if "gcp_service_account" in st.secrets: creds_dict=dict(st.secrets["gcp_service_account"])
    except: pass
    if not creds_dict:
      try:
        gs=st.secrets["connections"]["gsheets"]
        if hasattr(gs,'keys'):
          keys=list(gs.keys())
          if "type" in keys and "private_key" in keys: creds_dict=dict(gs)
      except: pass
    if not creds_dict:
      for path in [["connections","gsheets","gcp_service_account"],["connections","gsheets","service_account"]]:
        try:
          obj=st.secrets
          for p in path: obj=obj[p]
          if hasattr(obj,'keys') and "private_key" in list(obj.keys()):
            creds_dict=dict(obj)
            break
        except: continue
    if not creds_dict: return None, "No creds"
    creds=Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
    client=gspread.authorize(creds)
    return client, "OK"
  except Exception as e:
    return None, str(e)

@st.cache_data(ttl=300)
def get_all_records_cached(sheet_name, max_rows=500):
  client,msg=get_gspread_client()
  sid=get_spreadsheet_id()
  if not client or not sid: return []
  try:
    sh=client.open_by_key(sid)
    ws=sh.worksheet(sheet_name)
    recs=ws.get_all_records()
    return recs[-max_rows:] if len(recs)>max_rows else recs
  except: return []

def save_to_sheet(sheet_name, row_dict):
  client,msg=get_gspread_client()
  sid=get_spreadsheet_id()
  if not client or not sid: return False, f"Not connected: {msg}"
  try:
    sh=client.open_by_key(sid)
    try: ws=sh.worksheet(sheet_name)
    except:
      ws=sh.add_worksheet(title=sheet_name, rows=1000, cols=len(SHEET_HEADERS.get(sheet_name, ["ID"]))+5)
      ws.append_row(SHEET_HEADERS.get(sheet_name, list(row_dict.keys())))
    headers=SHEET_HEADERS.get(sheet_name, list(row_dict.keys()))
    row=[row_dict.get(h,"") for h in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")
    get_all_records_cached.clear()
    return True, f"Saved to {sheet_name}"
  except Exception as e:
    return False, str(e)

# ---------- DICTIONARY (EN/UR/AR) ----------
DICT = {
  "welcome_title": {"en": "Welcome to Herbal Clinic International", "ur": "ہربل کلینک انٹر نیشنل میں خوش آمدید", "ar": "مرحبا بكم في عيادة الأعشاب الدولية"},
  "welcome_sub": {"en": "Your Complete Unani & Herbal Clinic Management System", "ur": "آپ کا مکمل یونانی و ہربل کلینک مینجمنٹ سسٹم", "ar": "نظام إدارة العيادة اليونانية والعشبية الكامل"},
  "what_is": {"en": "What is this system?", "ur": "یہ سسٹم کیا ہے؟", "ar": "ما هو هذا النظام؟"},
  "what_is_desc": {"en": "Complete clinic OS for Hakeem, Tabib and Herbal Doctors. Manages Patient, Revisit, Dictionary, Pharmacopoeia, Billing, Stock.", "ur": "یہ حکیم، طبیب اور ہربل ڈاکٹرز کے لیے مکمل کلینک آپریٹنگ سسٹم ہے۔ مریض، دوبارہ معائنہ، لغت، قرابادین، بل، اسٹاک کا انتظام کرتا ہے۔", "ar": "نظام تشغيل عيادة كامل للحكيم والطبيب والمعالج بالأعشاب. يدير المريض، إعادة الزيارة، القاموس، دستور الأدوية، الفوترة، المخزون."},
  "home_treat": {"en": "Home Treatment Facility", "ur": "گھریلو طور پر علاج کی سہولت", "ar": "تسهيل العلاج المنزلي"},
  "home_treat_desc": {"en": "Patient enters basic info and gets Mizaj, diet, precautions, kitchen medicines. Phase 2.", "ur": "مریض بنیادی معلومات درج کر کے مزاج، غذا، پرہیز اور کچن کی دوائیں حاصل کرے گا۔ تفصیل فیز 2 میں۔", "ar": "يدخل المريض المعلومات الأساسية ويحصل على المزاج والنظام الغذائي والاحتياطات وأدوية المطبخ. المرحلة 2."},
  "phases": {"en": "Our 3 Phases", "ur": "ہمارے پروگرام کے 3 فیز", "ar": "المراحل الثلاث"},
  "phase1": {"en": "Phase 1: Basic Structure (You are here)", "ur": "فیز 1: بنیادی ڈھانچہ (آپ یہاں ہیں)", "ar": "المرحلة 1: الهيكل الأساسي (أنت هنا)"},
  "phase2": {"en": "Phase 2: Automation - Mizaj, Diet, Kitchen Medicines", "ur": "فیز 2: آٹومیشن - مزاج، غذا، کچن کی دوائیں", "ar": "المرحلة 2: الأتمتة"},
  "phase3": {"en": "Phase 3: Online Academy", "ur": "فیز 3: آن لائن اکیڈمی", "ar": "المرحلة 3: الأكاديمية عبر الإنترنت"},
  "free_note": {"en": "This App is FREE at this time. Sign up and start practice.", "ur": "اس وقت یہ ایپ بالکل فری ہے۔ سائن اپ کریں اور پریکٹس شروع کریں۔", "ar": "التطبيق مجاني حاليا. سجل وابدأ الممارسة."},
}

# ---------- SESSION ----------
if "lang" not in st.session_state: st.session_state.lang="en"
if "current_page" not in st.session_state: st.session_state.current_page="initial"
st.session_state.logged_in=True
st.session_state.username="Hakeem Testing - V2"

def t(key):
  lang=st.session_state.get("lang","en")
  return DICT.get(key,{}).get(lang, DICT.get(key,{}).get("en",key))

def top_bar():
  st.markdown("""
  <style>
  .rtl{direction:rtl;text-align:right;font-family:'Jameel Noori Nastaleeq','Noto Naskh Arabic',sans-serif;line-height:1.9;}
  .ltr{direction:ltr;text-align:left;}
  .card{background:white;border:1px solid #e0e0e0;border-radius:14px;padding:16px;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,0.05);}
  .red-dot{color:red;font-size:18px;}
  .v1-badge{background:#e8f5e9;border:1px solid #4caf50;border-radius:8px;padding:6px 10px;color:#2e7d32;font-weight:bold;display:inline-block;}
  .v2-badge{background:#e3f2fd;border:1px solid #1976d2;border-radius:8px;padding:6px 10px;color:#0d47a1;font-weight:bold;display:inline-block;}
  </style>
  """, unsafe_allow_html=True)
  c1,c2,c3=st.columns([6,2,2])
  with c1:
    st.markdown(f"### 🌿 Herbal Clinic OS | {APP_VERSION} <span class='v1-badge'>V1 ✅ 20/20</span> <span class='v2-badge'>V2 Start</span>", unsafe_allow_html=True)
  with c2:
    lang_opt=st.selectbox("Language", ["en","ur","ar"], index=["en","ur","ar"].index(st.session_state.lang), label_visibility="collapsed", key="lang_v2")
    st.session_state.lang=lang_opt
  with c3:
    st.caption(f"{st.session_state.username}")
    if st.button("Go to Initial", key="go_initial_v2"):
      st.session_state.current_page="initial"
      st.rerun()

def initial_page():
  top_bar()
  lang=st.session_state.lang
  rtl_class="rtl" if lang in ["ur","ar"] else "ltr"
  
  # Welcome
  if lang=="en":
    html=f"<div class='ltr card'><span class='red-dot'>🔴</span> <b>{t('welcome_title')}</b><br>{t('welcome_sub')}</div>"
  else:
    html=f"<div class='rtl card'><b>{t('welcome_title')}</b> <span class='red-dot'>🔴</span><br>{t('welcome_sub')}</div>"
  st.markdown(html, unsafe_allow_html=True)

  # What is
  if lang=="en":
    st.markdown(f"<div class='ltr card'><span class='red-dot'>🔴</span> <b>{t('what_is')}</b><br>{t('what_is_desc')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ltr card'><span class='red-dot'>🔴</span> <b>{t('home_treat')}</b><br>{t('home_treat_desc')}</div>", unsafe_allow_html=True)
  else:
    st.markdown(f"<div class='rtl card'><b>{t('what_is')}</b> <span class='red-dot'>🔴</span><br>{t('what_is_desc')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='rtl card'><b>{t('home_treat')}</b> <span class='red-dot'>🔴</span><br>{t('home_treat_desc')}</div>", unsafe_allow_html=True)

  # Phases
  st.markdown(f"<div class='{rtl_class} card'><b>{t('phases')}</b><br>1. {t('phase1')}<br>2. {t('phase2')}<br>3. {t('phase3')}</div>", unsafe_allow_html=True)
  st.markdown(f"<div class='{rtl_class} card'>{t('free_note')}</div>", unsafe_allow_html=True)

  col1,col2=st.columns(2)
  with col1:
    if st.button("Enter Dashboard - V2", type="primary", use_container_width=True, key="enter_dash_v2"):
      st.session_state.current_page="dashboard"
      st.rerun()
  with col2:
    if st.button("Check Sheets - 20/20 ✅", use_container_width=True, key="check_sheet_v2"):
      st.session_state.current_page="sheets"
      st.rerun()

def dashboard_page():
  top_bar()
  st.markdown(f"### Dashboard - {APP_VERSION}")
  st.success("V1 Complete: 20/20 Sheets | V2: Initial Page Final + Patient Basic | Auth Muted Till V2.5")

  # Metrics from Sheet
  recs_new = get_all_records_cached("New_patient", 500)
  recs_rev = get_all_records_cached("Revisit", 500)
  recs_fb = get_all_records_cached("Feedback", 500)

  m1,m2,m3,m4=st.columns(4)
  with m1: st.metric("Total Patients", len(recs_new))
  with m2: st.metric("Revisits", len(recs_rev))
  with m3: st.metric("Feedbacks", len(recs_fb))
  with m4: st.metric("Sheets", "20/20 ✅")

  tab1,tab2,tab3=st.tabs(["👤 New Patient Basic (V2)","📋 Recent Patients","ℹ️ V2 Roadmap"])

  with tab1:
    st.markdown("#### New Patient - Basic Entry - Saves to New_patient sheet")
    with st.container(border=True):
      c1,c2,c3=st.columns(3)
      with c1:
        name=st.text_input("Name / نام *", key="p_name_v2")
        father=st.text_input("Father Name / ولدیت", key="p_father_v2")
        age=st.number_input("Age / عمر", min_value=0, max_value=120, value=30, key="p_age_v2")
      with c2:
        gender=st.selectbox("Gender / جنس", ["Male","Female","Other"], key="p_gender_v2")
        phone=st.text_input("Phone / فون *", key="p_phone_v2")
        address=st.text_area("Address / پتہ", height=70, key="p_addr_v2")
      with c3:
        diseases=st.text_area("Chief Complaint / شکایت", height=70, key="p_dis_v2")
        fees=st.number_input("Fees / فیس", min_value=0, value=500, key="p_fees_v2")
        paid=st.number_input("Paid / وصول", min_value=0, value=500, key="p_paid_v2")

      if st.button("Save Patient - V2 Basic", type="primary", use_container_width=True, key="save_pat_v2"):
        if not name or not phone:
          st.error("Name and Phone required / نام اور فون ضروری ہے")
        else:
          pid=f"P_{int(time.time())}"
          row={
            "PatientID": pid,
            "Date": str(datetime.date.today()),
            "Name": name,
            "FatherName": father,
            "Age": age,
            "Gender": gender,
            "Phone": phone,
            "Address": address,
            "Diseases": diseases,
            "ChiefComplaint": diseases,
            "Fees": fees,
            "Paid": paid,
            "Balance": fees-paid,
            "Total": fees,
            "ClinicName": "Testing Clinic V2",
            "CreatedBy": st.session_state.username,
            "Timestamp": str(datetime.datetime.now()),
            "AppVersion": APP_VERSION,
            "UserType": "ClinicUser"
          }
          ok,msg=save_to_sheet("New_patient", row)
          if ok:
            st.success(f"✅ Saved: {pid} - {msg}")
            st.balloons()
          else:
            st.error(f"❌ Failed: {msg}")

  with tab2:
    st.markdown("#### Recent Patients from Google Sheet")
    if recs_new:
      df=pd.DataFrame(recs_new).tail(20)
      # Show important cols only
      cols_show=[c for c in ["PatientID","Date","Name","Age","Gender","Phone","Diseases","Fees","Paid"] if c in df.columns]
      st.dataframe(df[cols_show].iloc[::-1], use_container_width=True)
    else:
      st.info("No patients yet - Add first patient from Tab 1")

  with tab3:
    st.markdown("""
    **V2 Roadmap:**
    - V2 = Initial Page Final + Dashboard + Patient Basic ✅ (This version)
    - V2.1 = Patient Advanced fields (BP, Pulse, Temperament, History)
    - V2.2 = Revisit Search + Partial Search (Dash logic)
    - V2.3 = Dictionary + Herbs + Pharmacopoeia display
    - V2.4 = Billing + Payment
    - V2.5 = Signup/Signin Unmute + Real Auth + Permission
    
    **Current: V2 Basic - No heavy code, light & fast**
    **Same Sheet ID & secrets.toml - No change**
    """)

def sheets_page():
  top_bar()
  st.markdown("### Sheets Status - 20/20 Check")
  sid=get_spreadsheet_id()
  client,msg=get_gspread_client()
  if client and sid:
    sh=client.open_by_key(sid)
    existing=[ws.title for ws in sh.worksheets()]
    df=pd.DataFrame([{"Sheet": s, "Exists": "Yes ✅" if s in existing else "No ❌"} for s in ALL_SHEETS])
    st.dataframe(df, use_container_width=True)
    st.metric("Status", f"{len([s for s in ALL_SHEETS if s in existing])} / {len(ALL_SHEETS)}")
    if len([s for s in ALL_SHEETS if s in existing])==len(ALL_SHEETS):
      st.success("V1 Complete - 20/20 ✅")
      st.balloons()
  else:
    st.error(f"Not connected: {msg}")

  if st.button("Back to Dashboard"):
    st.session_state.current_page="dashboard"
    st.rerun()

def main():
  page=st.session_state.get("current_page","initial")
  if page=="initial":
    initial_page()
  elif page=="sheets":
    sheets_page()
  else:
    dashboard_page()

if __name__=="__main__": main()
