# ============================================
# Herbal Clinic OS
# VERSION: V1.7 - Error Fix for V1.6 (with col ternary bug)
# Date: 2026-10-03
# Fix: Line 121 - with col1: st.success() if else - syntax error
# Same as V1.6 but fixed
# Login Free - Auth Muted
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

APP_VERSION = "V1.7 - Error Fixed - Muted Auth"

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

# MUTED AUTH
st.session_state.logged_in=True
st.session_state.username="Testing Hakeem - Auth Muted"
st.session_state.testing_mode=True

def main():
  st.markdown("""
  <style>
  .card{background:white;border:1px solid #e0e0e0;border-radius:14px;padding:14px;margin-bottom:10px;}
  .test-banner{background:#e8f5e9;border:2px solid #4caf50;border-radius:10px;padding:12px;text-align:center;font-weight:bold;color:#2e7d32;}
  .muted-banner{background:#e3f2fd;border:2px solid #1976d2;border-radius:10px;padding:10px;text-align:center;}
  </style>
  <div class='test-banner'>🧪 V1.7 - Error Fixed | Auth Muted | 13/20 Fix</div>
  """, unsafe_allow_html=True)
  
  st.markdown(f"### 🌿 Herbal Clinic OS | {APP_VERSION}")
  
  sid=get_spreadsheet_id()
  client,msg=get_gspread_client()
  
  col1,col2=st.columns(2)
  with col1:
    if sid:
      st.success(f"Sheet ID: {sid[:30]}...")
    else:
      st.error("Sheet ID Missing")
  with col2:
    if client:
      st.success(f"Client: {msg}")
    else:
      st.error(f"Client: {msg}")

  st.markdown("---")
  tab1,tab2=st.tabs(["📊 13/20 -> 20/20 Fix","ℹ️ Info"])

  with tab1:
    st.markdown("#### Current: 13 / 20 - Ab 20/20 karte hain")
    
    if st.button("Check Konsi Sheets Missing Hain?", key="check_missing_v17"):
      if not client or not sid:
        st.error("Sheet not connected")
      else:
        try:
          sh=client.open_by_key(sid)
          existing=[ws.title for ws in sh.worksheets()]
          missing=[s for s in ALL_SHEETS if s not in existing]
          present=[s for s in ALL_SHEETS if s in existing]
          st.write(f"**Present ({len(present)}):** {present}")
          st.write(f"**Missing ({len(missing)}):** {missing}")
          st.session_state["missing"] = missing
          df=pd.DataFrame([{"Sheet": s, "Exists": "Yes" if s in existing else "No"} for s in ALL_SHEETS])
          st.dataframe(df, use_container_width=True)
          st.metric("Status", f"{len(present)} / {len(ALL_SHEETS)}")
        except Exception as e:
          st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("#### One By One Banao (Safe)")

    # Get missing list fresh
    missing=[]
    if client and sid:
      try:
        sh=client.open_by_key(sid)
        existing=[ws.title for ws in sh.worksheets()]
        missing=[s for s in ALL_SHEETS if s not in existing]
      except:
        pass

    if missing:
      st.warning(f"Missing {len(missing)} sheets")
      for sheet_name in missing:
        colA,colB=st.columns([3,1])
        with colA:
          st.write(f"• {sheet_name} - {len(SHEET_HEADERS[sheet_name])} cols")
        with colB:
          if st.button(f"Create {sheet_name}", key=f"create_{sheet_name}_v17"):
            try:
              sh=client.open_by_key(sid)
              headers=SHEET_HEADERS[sheet_name]
              existing_titles=[ws.title for ws in sh.worksheets()]
              if sheet_name in existing_titles:
                st.success(f"{sheet_name} already exists!")
              else:
                ws=sh.add_worksheet(title=sheet_name, rows=1000, cols=len(headers)+2)
                ws.append_row(headers)
                st.success(f"✅ Created: {sheet_name}")
                time.sleep(0.5)
                st.rerun()
            except Exception as e:
              st.error(f"❌ Failed {sheet_name}: {e}")
              if "permission" in str(e).lower() or "403" in str(e):
                st.error("Permission Error: Sheet -> Share -> Service Account Email ko Editor banayen")
    else:
      # Check if we have client
      if client and sid:
        try:
          sh=client.open_by_key(sid)
          existing=[ws.title for ws in sh.worksheets()]
          count=len([s for s in ALL_SHEETS if s in existing])
          if count>=20:
            st.success(f"All {count} / {len(ALL_SHEETS)} sheets exist! V1 Complete ✅")
            st.balloons()
          else:
            st.info(f"Status: {count} / {len(ALL_SHEETS)} - Press Check button")
        except Exception as e:
          st.write(f"Checking... {e}")
      else:
        st.info("Connect sheet first")

    st.markdown("---")
    if st.button("🚀 Create All Missing Together", type="primary", key="create_all_v17"):
      if not client or not sid:
        st.error("Sheet not connected")
      else:
        try:
          sh=client.open_by_key(sid)
          existing=[ws.title for ws in sh.worksheets()]
          missing=[s for s in ALL_SHEETS if s not in existing]
          if not missing:
            st.success("Already 20/20!")
          else:
            for sheet_name in missing:
              try:
                headers=SHEET_HEADERS[sheet_name]
                ws=sh.add_worksheet(title=sheet_name, rows=1000, cols=len(headers)+2)
                ws.append_row(headers)
                st.write(f"✅ {sheet_name}")
              except Exception as e:
                st.write(f"❌ {sheet_name}: {e}")
            st.success("Done! Press Check again")
            time.sleep(1)
            st.rerun()
        except Exception as e:
          st.error(f"Error: {e}")

  with tab2:
    st.markdown("""
    **V1.7 Fix:**
    - V1.6 me `with col1: st.success() if else` syntax error tha - Fixed
    - Ab error nahi aayega
    - Auth Muted still
    - Same Sheet ID & secrets.toml
    
    **Next: V1 Complete -> V2 Start**
    """)

if __name__=="__main__": main()
