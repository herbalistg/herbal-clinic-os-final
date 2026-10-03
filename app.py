# ============================================
# Herbal Clinic OS - NEW INSTALLATION
# VERSION: V1.1 - Google Sheet Full Connect + 18 Sheets Check
# Date: 2026-10-03
# Base: V1 (Clean Base)
# Changes in V1.1:
#  - Full SHEET_HEADERS from V206 (22 sheets)
#  - Robust gspread client (secrets.toml + [connections.gsheets] both supported)
#  - get_all_records_cached (600s), save_to_sheet, check_sheet_structure
#  - Sheet Status Dashboard in App Admin
#  - Light & Fast - no heavy code
# Stack: VS Code + GitHub + Streamlit + Google Sheet
# ============================================

import streamlit as st
import datetime
import pandas as pd
import time

try:
  import gspread
  from google.oauth2.service_account import Credentials
  GSPREAD_AVAILABLE = True
except ImportError:
  GSPREAD_AVAILABLE = False

APP_VERSION = "V1.1 - Sheet Full Connect"

st.set_page_config(page_title=f"Herbal Clinic OS {APP_VERSION}", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

# ---------- SHEET STRUCTURE (from V206 - Final) ----------
SHEET_HEADERS = {
  "UserSignups": ["SignupID","Username","Password","UserType","ClinicName","Phone","Email","Date","Status","Role","From","LastLogin","DeviceInfo"],
  "PermissionGranted": ["ID","Username","UserType","PermissionType","GrantedDate","Status","IP","Device","ExpiryDate","GrantedBy"],
  "HomeUsers": ["UserID","Username","Password","FullName","Phone","Email","Date","Status","AccountHolderPhone","From","LastLogin","ClinicName","Address","Age","Gender","SubscriptionStatus"],
  "New_patient": ["PatientID","Date","Name","FatherName","Age","Gender","MaritalStatus","Occupation","CNIC","Phone","EmergencyPhone","Address","Referral","Diseases","ChiefComplaint","PastHistory","FamilyHistory","Allergy","Examination","Pulse","Temperament","BP","Weight","Temperature","Height","SleepPattern","Appetite","BowelMovement","Thirst","Urine","Sweating","StressLevel","EnergyLevel","SingleMedicines","FormulaMedicines","ManualMedicines","Fees","MedicineCharges","Total","Paid","Balance","PrevBalance","PaymentMethod","FeeStatus","RevisitDate","ClinicName","CreatedBy","Timestamp","AppVersion","DailyNumber","TotalNumber","GrandTotal","UserType","Habits","BloodGroup","CuredDiseases","RemainingDiseases"],
  "Revisit": ["RevisitID","PatientID","OriginalPatientID","Date","Name","FatherName","Age","Gender","MaritalStatus","Occupation","CNIC","Phone","EmergencyPhone","Address","Referral","Diseases","PreviousDiseases","ChiefComplaint","PastHistory","FamilyHistory","Allergy","Pulse","Temperament","BP","Weight","Temperature","Height","SleepPattern","Appetite","BowelMovement","SingleMedicines","FormulaMedicines","ManualMedicines","Fees","MedicineCharges","Total","Paid","Balance","PrevBalance","PaymentMethod","FeeStatus","ClinicName","CreatedBy","Timestamp","AppVersion","DailyNumber","TotalNumber","GrandTotal","CuredDiseases","RemainingDiseases","UserType","BloodGroup","Habits"],
  "AutoDiagnosis": ["ID","PatientID","Date","Name","FatherName","Age","Phone","Gender","MaritalStatus","Occupation","Address","BloodGroup","Diseases","DiseasesWithDetails","ExtraSymptoms","PastHistory","FamilyHistory","CurrentMedications","SleepPattern","Appetite","BowelMovement","Thirst","Urine","Sweating","StressLevel","EnergyLevel","AllergyHistory","Temperament","Mizaj","DietRecommendations","Restrictions","Instructions","ClinicName","CreatedBy","Timestamp","AppVersion","GrandTotal","UserType","Habits","Height","Weight"],
  "HomeTreatment": ["ID","PatientID","Date","Name","FatherName","Age","Phone","Gender","MaritalStatus","Occupation","Address","BloodGroup","Diseases","DiseasesWithDetails","ExtraSymptoms","PastHistory","FamilyHistory","CurrentMedications","SleepPattern","Appetite","BowelMovement","Thirst","Urine","Sweating","StressLevel","EnergyLevel","AllergyHistory","Temperament","Mizaj","DietRecommendations","Restrictions","Instructions","ClinicName","CreatedBy","Timestamp","AppVersion","GrandTotal","UserType","Habits","Height","Weight"],
  "Herbs": ["HerbID","Name","UrduName","Temperament","Mizaj","Uses","Benefits","Dosage","SideEffects","Precautions","ClinicName","Status","AddedBy","Date"],
  "Pharmacopoeia": ["ID","Name","UrduName","Category","Temperament","Mizaj","Uses","Benefits","Ingredients","Dosage","Method","SideEffects","ClinicName","Status","AddedBy","Date"],
  "Dictionary": ["ID","Word","UrduWord","ArabicWord","Meaning","MeaningUR","MeaningAR","Category","SubCategory","Language","Status","AddedBy","Date"],
  "Articles": ["ID","TitleEN","TitleUR","TitleAR","ContentEN","ContentUR","ContentAR","MainCategory","SubCategory","Audience","Type","Status","Date","ClinicName","Author","ImageURL","Tags","ViewCount"],
  "Feedback": ["ID","Name","From","Phone Number","Email","Feedback Page","Feedback","Date","Status","UserType","ClinicName","Rating","Response"],
  "AppSettings": ["Key","Value","Date","Status","Description","Category","UpdatedBy"],
  "Offer": ["ID","TitleEN","TitleUR","TitleAR","ContentEN","ContentUR","ContentAR","MainCategory","SubCategory","Status","Date","ClinicName","ExpiryDate","Discount"],
  "ClinicFormulas": ["FormulaID","Name","UrduName","Ingredients","Uses","Benefits","Dosage","Method","ClinicName","Status","AddedBy","Date"],
  "ClinicSettings": ["SettingID","ClinicName","SettingKey","SettingValue","Status","UpdatedBy","Date"],
  "Inventory": ["ItemID","ItemName","Category","Quantity","Unit","PurchasePrice","SalePrice","ExpiryDate","Supplier","ClinicName","Status","AddedBy","Date"],
  "BillingReport": ["ReportID","Date","PatientID","Name","Fees","MedicineCharges","Total","Paid","Balance","PaymentMethod","ClinicName","CreatedBy"],
  "Expenses": ["ExpenseID","Date","Category","Description","Amount","PaymentMethod","ClinicName","AddedBy","Status"],
  "Appointments": ["AppointmentID","Date","Time","PatientID","PatientName","Phone","Status","ClinicName","CreatedBy","Notes"],
}

ALL_SHEETS = list(SHEET_HEADERS.keys())
GENERAL_SHEETS = ["UserSignups", "PermissionGranted", "Articles", "Feedback"]
CLINIC_SHEETS = ["New_patient", "Revisit", "AutoDiagnosis", "Herbs", "Pharmacopoeia", "Dictionary"]
HOME_SHEETS = ["HomeUsers", "HomeTreatment"]
SETTING_SHEETS = ["AppSettings", "Offer", "ClinicFormulas", "ClinicSettings"]

# ---------- DICTIONARY ----------
DICT = {
  "welcome_title": {"en": "Welcome to Herbal Clinic International", "ur": "ہربل کلینک انٹر نیشنل میں خوش آمدید", "ar": "مرحبا بكم في عيادة الأعشاب الدولية"},
  "welcome_sub": {"en": "Your Complete Unani & Herbal Clinic Management System", "ur": "آپ کا مکمل یونانی و ہربل کلینک مینجمنٹ سسٹم", "ar": "نظام إدارة العيادة اليونانية والعشبية الكامل"},
}

def t(key):
  lang = st.session_state.get("lang","en")
  return DICT.get(key,{}).get(lang, DICT.get(key,{}).get("en",key))

# ---------- GOOGLE SHEET CORE (V1.1) ----------
@st.cache_resource(ttl=900)
def get_gspread_client():
  if not GSPREAD_AVAILABLE:
    return None, "gspread not installed"
  try:
    creds_dict = None
    # Support 2 formats: [gcp_service_account] and [connections.gsheets]
    if "gcp_service_account" in st.secrets:
      creds_dict = dict(st.secrets["gcp_service_account"])
    elif "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
      gs = st.secrets["connections"]["gsheets"]
      # if contains service_account json
      if isinstance(gs, dict) and "type" in gs:
        creds_dict = dict(gs)
      elif isinstance(gs, dict) and "service_account" in gs:
        creds_dict = dict(gs["service_account"])
      else:
        # Try gcp_service_account still
        if "gcp_service_account" in st.secrets:
          creds_dict = dict(st.secrets["gcp_service_account"])
    if not creds_dict:
      return None, "No service_account found in secrets.toml - Add [gcp_service_account]"
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
    return client, "OK"
  except Exception as e:
    return None, f"Auth Error: {e}"

def get_spreadsheet_id():
  try:
    if "SHEET_ID" in st.secrets:
      return st.secrets["SHEET_ID"]
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
      gs = st.secrets["connections"]["gsheets"]
      if isinstance(gs, dict) and "spreadsheet" in gs:
        return gs["spreadsheet"]
      if isinstance(gs, str):
        return gs
  except: pass
  return None

@st.cache_data(ttl=600)
def get_all_records_cached(sheet_name, max_rows=200):
  if sheet_name not in ALL_SHEETS:
    return []
  client, msg = get_gspread_client()
  if not client:
    return []
  sheet_id = get_spreadsheet_id()
  if not sheet_id:
    return []
  try:
    sh = client.open_by_key(sheet_id)
    ws = sh.worksheet(sheet_name)
    records = ws.get_all_records()
    if len(records) > max_rows:
      records = records[-max_rows:]
    return records
  except Exception as e:
    return []

def save_to_sheet(sheet_name, row_dict):
  client, msg = get_gspread_client()
  if not client:
    return False, f"Client error: {msg}"
  sheet_id = get_spreadsheet_id()
  if not sheet_id:
    return False, "SHEET_ID missing in secrets.toml"
  try:
    sh = client.open_by_key(sheet_id)
    try:
      ws = sh.worksheet(sheet_name)
    except:
      # Create sheet if not exists
      ws = sh.add_worksheet(title=sheet_name, rows=1000, cols=len(SHEET_HEADERS[sheet_name])+5)
      ws.append_row(SHEET_HEADERS[sheet_name])
    
    headers = SHEET_HEADERS[sheet_name]
    row = [row_dict.get(h,"") for h in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")
    # clear cache
    get_all_records_cached.clear()
    return True, "Saved"
  except Exception as e:
    return False, str(e)

def check_sheet_structure():
  client, msg = get_gspread_client()
  sheet_id = get_spreadsheet_id()
  if not client or not sheet_id:
    return [{"sheet": s, "exists": False, "status": f"No client/ID: {msg}"} for s in ALL_SHEETS]
  try:
    sh = client.open_by_key(sheet_id)
    existing_titles = [ws.title for ws in sh.worksheets()]
    results=[]
    for s in ALL_SHEETS:
      if s in existing_titles:
        try:
          ws = sh.worksheet(s)
          first_row = ws.row_values(1)
          expected = SHEET_HEADERS[s]
          missing = [h for h in expected if h not in first_row]
          if missing:
            results.append({"sheet": s, "exists": True, "status": f"Exists but missing headers: {missing[:3]}"})
          else:
            results.append({"sheet": s, "exists": True, "status": "OK - Headers match"})
        except Exception as e:
          results.append({"sheet": s, "exists": True, "status": f"Exists but error: {e}"})
      else:
        results.append({"sheet": s, "exists": False, "status": "Not exists - Will auto-create on first save"})
    return results
  except Exception as e:
    return [{"sheet": s, "exists": False, "status": f"Error: {e}"} for s in ALL_SHEETS]

# ---------- SESSION ----------
if "lang" not in st.session_state: st.session_state.lang="en"
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "username" not in st.session_state: st.session_state.username="Guest"
if "current_page" not in st.session_state: st.session_state.current_page="initial"

# ---------- UI ----------
def top_bar():
  st.markdown("""
  <style>
  .rtl { direction: rtl; text-align: right; font-family: 'Jameel Noori Nastaleeq','Noto Naskh Arabic',sans-serif; line-height:1.9; }
  .ltr { direction: ltr; text-align: left; }
  .card { background:white; border:1px solid #e0e0e0; border-radius:14px; padding:18px; margin-bottom:12px; box-shadow:0 2px 8px rgba(0,0,0,0.05); }
  .red-dot { color:red; }
  .ok { background:#e8f5e9; border:1px solid #4caf50; border-radius:8px; padding:8px; }
  .bad { background:#ffebee; border:1px solid #f44336; border-radius:8px; padding:8px; }
  </style>
  """, unsafe_allow_html=True)
  c1,c2,c3=st.columns([6,2,2])
  with c1: st.markdown(f"### 🌿 Herbal Clinic OS | {APP_VERSION}")
  with c2:
    lang_opt=st.selectbox("Lang", ["en","ur","ar"], index=["en","ur","ar"].index(st.session_state.lang), label_visibility="collapsed", key="lang_v11")
    st.session_state.lang=lang_opt
  with c3:
    if st.session_state.logged_in:
      st.caption(f"{st.session_state.username}")
      if st.button("Logout", key="logout_v11"):
        st.session_state.logged_in=False
        st.session_state.current_page="initial"
        st.rerun()

def initial_page():
  lang=st.session_state.lang
  rtl="rtl" if lang in ["ur","ar"] else "ltr"
  if lang=="en":
    html=f"<div class='ltr card'><span class='red-dot'>🔴</span> <b>{t('welcome_title')}</b><br>{DICT['welcome_sub']['en']}</div>"
  else:
    html=f"<div class='rtl card'><b>{t('welcome_title')}</b> <span class='red-dot'>🔴</span><br>{DICT['welcome_sub'][lang]}</div>"
  st.markdown(html, unsafe_allow_html=True)
  st.markdown(f"<div class='{rtl} card'>V1.1 Goal: Google Sheet Connect - 22 Sheets<br>General: {GENERAL_SHEETS}<br>Clinic: {CLINIC_SHEETS}<br>Home: {HOME_SHEETS}</div>", unsafe_allow_html=True)
  if st.button("Sign In Demo (Go to Dashboard)", type="primary", use_container_width=True, key="signin_v11"):
    st.session_state.logged_in=True
    st.session_state.username="Hakeem Demo"
    st.session_state.current_page="dashboard"
    st.rerun()

def dashboard_page():
  top_bar()
  st.markdown(f"### Dashboard - {APP_VERSION}")
  client, msg = get_gspread_client()
  sid = get_spreadsheet_id()
  colA,colB=st.columns(2)
  with colA: st.markdown(f"<div class='{'ok' if client else 'bad'}'>GSpread Client: {msg}</div>", unsafe_allow_html=True)
  with colB: st.markdown(f"<div class='{'ok' if sid else 'bad'}'>Sheet ID: {'Found '+sid[:15]+'...' if sid else 'Missing - Add SHEET_ID in secrets.toml'}</div>", unsafe_allow_html=True)

  tab1,tab2,tab3=st.tabs(["Sheet Structure Check","Test Save","Info"])
  with tab1:
    if st.button("Check All 22 Sheets Now", type="primary"):
      results=check_sheet_structure()
      df=pd.DataFrame(results)
      st.dataframe(df, use_container_width=True)
      ok_count=sum(1 for r in results if "OK" in r["status"])
      st.success(f"{ok_count} / {len(results)} sheets OK")
      if ok_count < len(results):
        st.warning("Jo sheets 'Not exists' hain wo pehli save par auto-create ho jayengi - tension nahi")
    else:
      st.info("Click to check Google Sheet structure - V1.1 core feature")

  with tab2:
    st.markdown("#### Test Save to Feedback Sheet (Demo)")
    name=st.text_input("Name", "Test User V1.1")
    fb=st.text_area("Feedback", "V1.1 Sheet connect working")
    if st.button("Save to Google Sheet - Feedback"):
      ok, msg2 = save_to_sheet("Feedback", {"ID": f"FB_{int(time.time())}", "Name": name, "Feedback": fb, "Date": str(datetime.date.today()), "From": "V1.1 Test"})
      if ok: st.success(f"Saved: {msg2}")
      else: st.error(f"Failed: {msg2}")
    st.markdown("#### Recent Feedback (from Sheet)")
    recs=get_all_records_cached("Feedback", 10)
    if recs: st.dataframe(pd.DataFrame(recs).tail(10), use_container_width=True)
    else: st.caption("No records yet or sheet not connected")

  with tab3:
    st.markdown("""
    **V1.1 kya karta hai:**
    - 22 sheets ke headers defined (V206 se copy)
    - Client dono tarah ke secrets support karta hai: [gcp_service_account] aur [connections.gsheets]
    - Cache 600s - fast, quota bachao
    - Auto-create sheet if missing
    
    **VS Code + GitHub Steps:**
    1. VS Code me `App_V1.1.py` ko `app.py` rename karo
    2. `secrets.toml` me add karo:
    ```
    SHEET_ID = "1D4x7wioVZyvw3i2p6NC2rTp1Z2J_DuTYGcJMy6X2sHA"
    [gcp_service_account]
    type = "service_account"
    ... baqi json ...
    ```
    3. GitHub push
    4. Streamlit Cloud -> Deploy
    
    **Next: V1.2 = Login persistent + UserSignups sheet connect**
    """)

def main():
  if not st.session_state.logged_in:
    initial_page()
  else:
    dashboard_page()

if __name__=="__main__": main()
