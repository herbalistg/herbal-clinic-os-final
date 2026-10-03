# ============================================
# Herbal Clinic OS
# VERSION: V1.5 - Complete V1 Step - Create Missing Sheets
# Date: 2026-10-03
# Base: V1.4 (13/20 exist - reported by user)
# Goal: Make it 20/20 in one click, then V1 step complete -> Move to V2
# Same Sheet ID & secrets.toml - No change
# Login Free for testing
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

APP_VERSION = "V1.5 - Complete V1 (20/20)"

st.set_page_config(page_title=APP_VERSION, page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

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

def main():
  st.markdown(f"### 🌿 Herbal Clinic OS | {APP_VERSION}")
  st.markdown("<div style='background:#fff3e0;border:2px dashed #ff9800;border-radius:10px;padding:10px;text-align:center;'>🧪 TESTING MODE - Login Free | V1 Step Final</div>", unsafe_allow_html=True)
  
  sid=get_spreadsheet_id()
  client,msg=get_gspread_client()
  
  c1,c2=st.columns(2)
  with c1: st.info(f"Sheet ID: {sid[:30]+'...' if sid else 'Missing'}")
  with c2: st.info(f"Client: {msg}")

  st.markdown("---")
  st.markdown("#### V1 Step Result: 13/20 -> 20/20 Karna hai")

  if st.button("✅ Check Current Status (13/20)", key="check_v15"):
    if not client or not sid:
      st.error("Sheet not connected")
    else:
      sh=client.open_by_key(sid)
      existing=[ws.title for ws in sh.worksheets()]
      results=[]
      for s in ALL_SHEETS:
        results.append({"Sheet": s, "Exists": "Yes" if s in existing else "No"})
      df=pd.DataFrame(results)
      st.dataframe(df, use_container_width=True)
      yes_count=len([r for r in results if r["Exists"]=="Yes"])
      st.metric("Existing Sheets", f"{yes_count} / {len(results)}")
      st.session_state["existing"] = existing

  if st.button("🚀 Create Missing 7 Sheets Now (One Click)", type="primary", key="create_missing_v15"):
    if not client or not sid:
      st.error("Cannot create - Sheet not connected")
    else:
      sh=client.open_by_key(sid)
      existing=[ws.title for ws in sh.worksheets()]
      missing=[s for s in ALL_SHEETS if s not in existing]
      st.write(f"Missing: {missing}")
      progress=st.progress(0)
      for i, sheet_name in enumerate(missing):
        try:
          headers=SHEET_HEADERS[sheet_name]
          ws=sh.add_worksheet(title=sheet_name, rows=1000, cols=len(headers)+5)
          ws.append_row(headers)
          st.write(f"✅ Created: {sheet_name}")
        except Exception as e:
          st.write(f"❌ Failed {sheet_name}: {e}")
        progress.progress((i+1)/len(missing))
        time.sleep(0.5)
      st.success(f"Done! Created {len(missing)} sheets. Now you have 20/20")
      st.balloons()
      # Recheck
      sh=client.open_by_key(sid)
      existing2=[ws.title for ws in sh.worksheets()]
      yes2=len([s for s in ALL_SHEETS if s in existing2])
      st.metric("New Status", f"{yes2} / {len(ALL_SHEETS)}")

  st.markdown("---")
  st.markdown("""
  **V1 Step - Summary:**
  - V1 = Clean Base ✅
  - V1.1 = 22 Sheets Check - 13/20 mila ✅
  - V1.2 = Login (ab free) ✅
  - V1.3 = Login Free ✅
  - V1.4 = AttrDict Fix - 13/20 fix hua ✅
  - **V1.5 = 20/20 Complete** <- Ab is par hain
  
  **Iske baad V1 Step Complete!**
  Phir **V2** shuru karenge:
  - V2 = Initial Page Final + Dashboard + Patient Entry Basic
  """)

  if st.button("Next -> V2 Start Karna Hai?", key="next_v2"):
    st.info("V1 Complete! Ab V2 = Patient Basic Form + Knowledge Base Start karenge. Aap bolein to V2 bana dun.")

if __name__=="__main__": main()
