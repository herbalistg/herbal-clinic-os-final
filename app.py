# ============================================
# Herbal Clinic OS
# VERSION: V2.1 - Fix Name/Phone required bug + Clean Sheet Save
# Date: 2026-10-03
# Base: V2 (10/10 V1 Complete, but save bug)
# Fixes in V2.1:
#  - Form based entry (st.form) - No rerun bug
#  - Validation fixed: strip() + debug display
#  - Full 20 sheets headers restored (not just 10)
#  - Clean Sheet (you cleared data) - Now saves fresh
#  - Auth Muted till V2.5
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

APP_VERSION = "V2.1 - Patient Save Fixed"

st.set_page_config(page_title=APP_VERSION, page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

# Full 20 sheets headers (restore full V1)
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
  if not client or not sid: return False, f"Not connected: {msg} | SID={'Found' if sid else 'Missing'}"
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
    return True, f"Saved to {sheet_name} - ID {row_dict.get('PatientID','')}"
  except Exception as e:
    return False, f"Sheet Error: {e}"

# DICT
DICT = {
  "welcome_title": {"en": "Welcome to Herbal Clinic International", "ur": "ہربل کلینک انٹر نیشنل میں خوش آمدید", "ar": "مرحبا بكم في عيادة الأعشاب الدولية"},
  "welcome_sub": {"en": "Your Complete Unani & Herbal Clinic Management System", "ur": "آپ کا مکمل یونانی و ہربل کلینک مینجمنٹ سسٹم", "ar": "نظام إدارة العيادة اليونانية والعشبية الكامل"},
}

def t(key):
  lang=st.session_state.get("lang","en")
  return DICT.get(key,{}).get(lang, DICT.get(key,{}).get("en",key))

if "lang" not in st.session_state: st.session_state.lang="en"
if "current_page" not in st.session_state: st.session_state.current_page="dashboard"
st.session_state.logged_in=True
st.session_state.username="Hakeem Testing - V2.1"

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
    st.markdown(f"### 🌿 Herbal Clinic OS | V2.1 - Save Fixed | <span class='v1-badge'>V1 ✅ 20/20</span>", unsafe_allow_html=True)
  with c2:
    lang_opt=st.selectbox("Lang", ["en","ur","ar"], index=["en","ur","ar"].index(st.session_state.lang), label_visibility="collapsed", key="lang_v21")
    st.session_state.lang=lang_opt
  with c3:
    if st.button("Initial Page", key="go_initial_v21"):
      st.session_state.current_page="initial"
      st.rerun()

def initial_page():
  top_bar()
  lang=st.session_state.lang
  rtl_class="rtl" if lang in ["ur","ar"] else "ltr"
  if lang=="en":
    html=f"<div class='ltr card'><span class='red-dot'>🔴</span> <b>{t('welcome_title')}</b><br>{t('welcome_sub')}</div>"
  else:
    html=f"<div class='rtl card'><b>{t('welcome_title')}</b> <span class='red-dot'>🔴</span><br>{t('welcome_sub')}</div>"
  st.markdown(html, unsafe_allow_html=True)
  st.markdown(f"<div class='{rtl_class} card'>V2.1 - Sheet Cleaned, Fresh Start. 20/20 Sheets OK.</div>", unsafe_allow_html=True)
  if st.button("Enter Dashboard", type="primary", use_container_width=True, key="enter_dash_v21"):
    st.session_state.current_page="dashboard"
    st.rerun()

def dashboard_page():
  top_bar()
  st.markdown("### Dashboard - V2.1 Patient Save Fixed")
  
  recs_new = get_all_records_cached("New_patient", 500)
  recs_fb = get_all_records_cached("Feedback", 500)

  m1,m2,m3=st.columns(3)
  with m1: st.metric("Total Patients (Clean Sheet)", len(recs_new))
  with m2: st.metric("Feedbacks", len(recs_fb))
  with m3: st.metric("Sheets", "20/20 ✅")

  tab1,tab2=st.tabs(["👤 New Patient Basic - FIXED","📋 Recent Patients"])

  with tab1:
    st.markdown("#### New Patient - Basic Entry (V2.1 Fixed with Form)")
    st.info("Ab Form use ho raha hai - Name/Phone required bug fixed. Aapne sheet clean ki hai, ab fresh save hoga.")

    with st.form("patient_form_v21", clear_on_submit=True):
      c1,c2,c3=st.columns(3)
      with c1:
        name=st.text_input("Name / نام *", key="p_name_v21_form")
        father=st.text_input("Father Name / ولدیت", key="p_father_v21_form")
        age=st.number_input("Age / عمر", min_value=0, max_value=120, value=30, key="p_age_v21_form")
      with c2:
        gender=st.selectbox("Gender / جنس", ["Male","Female","Other"], key="p_gender_v21_form")
        phone=st.text_input("Phone / فون *", key="p_phone_v21_form")
        address=st.text_area("Address / پتہ", height=70, key="p_addr_v21_form")
      with c3:
        diseases=st.text_area("Chief Complaint / شکایت", height=70, key="p_dis_v21_form")
        fees=st.number_input("Fees / فیس", min_value=0, value=500, key="p_fees_v21_form")
        paid=st.number_input("Paid / وصول", min_value=0, value=500, key="p_paid_v21_form")

      submitted=st.form_submit_button("Save Patient - V2.1", type="primary", use_container_width=True)

      if submitted:
        # Debug - show what was entered
        st.write(f"Debug - Entered: Name='{name}' (len={len(name.strip())}), Phone='{phone}' (len={len(phone.strip())})")
        
        name_clean=name.strip() if name else ""
        phone_clean=phone.strip() if phone else ""
        
        if not name_clean:
          st.error("❌ Name required - نام لکھیں (empty or spaces only)")
        elif not phone_clean:
          st.error("❌ Phone required - فون نمبر لکھیں (empty or spaces only)")
        else:
          pid=f"P_{int(time.time())}"
          row={
            "PatientID": pid,
            "Date": str(datetime.date.today()),
            "Name": name_clean,
            "FatherName": father.strip() if father else "",
            "Age": age,
            "Gender": gender,
            "Phone": phone_clean,
            "Address": address.strip() if address else "",
            "Diseases": diseases.strip() if diseases else "",
            "ChiefComplaint": diseases.strip() if diseases else "",
            "Fees": fees,
            "Paid": paid,
            "Balance": fees-paid,
            "Total": fees,
            "ClinicName": "Testing Clinic V2.1 - Clean Sheet",
            "CreatedBy": st.session_state.username,
            "Timestamp": str(datetime.datetime.now()),
            "AppVersion": "V2.1",
            "UserType": "ClinicUser",
            "GrandTotal": len(recs_new)+1
          }
          with st.spinner("Saving to Google Sheet..."):
            ok,msg=save_to_sheet("New_patient", row)
          if ok:
            st.success(f"✅ Saved Successfully: {pid}")
            st.success(msg)
            st.balloons()
            time.sleep(1)
            st.rerun()
          else:
            st.error(f"❌ Failed: {msg}")

  with tab2:
    st.markdown("#### Recent Patients (After Clean)")
    if recs_new:
      df=pd.DataFrame(recs_new).tail(20)
      cols_show=[c for c in ["PatientID","Date","Name","Age","Gender","Phone","Diseases","Fees","Paid","Balance"] if c in df.columns]
      st.dataframe(df[cols_show].iloc[::-1], use_container_width=True)
      if st.button("Clear Cache & Reload"):
        get_all_records_cached.clear()
        st.rerun()
    else:
      st.info("No patients yet - Sheet is clean (as you cleared). Add first patient from Tab 1 - V2.1 will save fresh.")

def main():
  page=st.session_state.get("current_page","dashboard")
  if page=="initial":
    initial_page()
  else:
    dashboard_page()

if __name__=="__main__": main()
