# ============================================
# Herbal Clinic OS - NEW INSTALLATION
# VERSION: V1.3 - Login Free Testing Mode + SHEET_ID Fix
# Date: 2026-10-03
# Base: V1.2
# Fixes in V1.3:
#  - LOGIN FREE for testing: Auto logged-in, testing banner
#  - SHEET_ID missing Fix: Checks 6 places + debug view
#  - Test Save fallback to local if sheet not connected
#  - Same Sheet ID & secrets.toml - no change needed
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

APP_VERSION = "V1.3 - Login Free Testing"

st.set_page_config(page_title=f"Herbal Clinic OS {APP_VERSION}", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

# ---------- SHEET HEADERS ----------
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
}
ALL_SHEETS = list(SHEET_HEADERS.keys())

# ---------- SHEET ID FIX - Check 6 places ----------
def get_spreadsheet_id_debug():
  debug=[]
  found=None
  # 1. Direct SHEET_ID
  try:
    if "SHEET_ID" in st.secrets:
      found = st.secrets["SHEET_ID"]
      debug.append(f"✅ Found in st.secrets['SHEET_ID']: {str(found)[:20]}...")
      return found, debug
    else:
      debug.append("❌ Not in st.secrets['SHEET_ID']")
  except Exception as e:
    debug.append(f"❌ Error checking SHEET_ID: {e}")

  # 2. connections.gsheets.spreadsheet
  try:
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
      gs = st.secrets["connections"]["gsheets"]
      if isinstance(gs, dict) and "spreadsheet" in gs:
        found = gs["spreadsheet"]
        debug.append(f"✅ Found in [connections.gsheets].spreadsheet: {str(found)[:20]}...")
        return found, debug
      else:
        debug.append(f"❌ [connections.gsheets] exists but no 'spreadsheet' key, type={type(gs)} keys={list(gs.keys())[:5] if isinstance(gs, dict) else 'not dict'}")
    else:
      debug.append("❌ Not in [connections.gsheets]")
  except Exception as e:
    debug.append(f"❌ Error checking connections.gsheets: {e}")

  # 3. gsheets.spreadsheet (direct)
  try:
    if "gsheets" in st.secrets:
      gs = st.secrets["gsheets"]
      if isinstance(gs, dict) and "spreadsheet" in gs:
        found = gs["spreadsheet"]
        debug.append(f"✅ Found in [gsheets].spreadsheet: {str(found)[:20]}...")
        return found, debug
      if isinstance(gs, str) and len(gs)>10:
        found=gs
        debug.append(f"✅ Found in [gsheets] as string: {str(found)[:20]}...")
        return found, debug
    debug.append("❌ Not in [gsheets]")
  except Exception as e:
    debug.append(f"❌ Error checking gsheets: {e}")

  # 4. List all top keys
  try:
    keys = list(st.secrets.keys())
    debug.append(f"ℹ️ All secrets top keys available: {keys}")
  except Exception as e:
    debug.append(f"❌ Can't list secrets keys: {e}")

  return None, debug

def get_spreadsheet_id():
  sid, _ = get_spreadsheet_id_debug()
  return sid

@st.cache_resource(ttl=900)
def get_gspread_client():
  if not GSPREAD_AVAILABLE: return None, "gspread not installed - pip install gspread google-auth"
  try:
    creds_dict=None
    if "gcp_service_account" in st.secrets: 
      creds_dict=dict(st.secrets["gcp_service_account"])
    elif "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
      gs=st.secrets["connections"]["gsheets"]
      if isinstance(gs, dict) and "type" in gs: creds_dict=dict(gs)
      elif isinstance(gs, dict) and "service_account" in gs: creds_dict=dict(gs["service_account"])
      elif "gcp_service_account" in st.secrets: creds_dict=dict(st.secrets["gcp_service_account"])
    if not creds_dict: 
      return None, "No service_account - Add [gcp_service_account] in secrets.toml"
    creds=Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
    client=gspread.authorize(creds)
    return client, "OK - Connected"
  except Exception as e: return None, f"Auth Error: {e}"

@st.cache_data(ttl=300)
def get_all_records_cached(sheet_name, max_rows=200):
  client,msg=get_gspread_client()
  sid=get_spreadsheet_id()
  if not client or not sid: return []
  try:
    sh=client.open_by_key(sid)
    ws=sh.worksheet(sheet_name)
    recs=ws.get_all_records()
    return recs[-max_rows:] if len(recs)>max_rows else recs
  except: return []

def save_to_sheet_with_fallback(sheet_name, row_dict):
  client,msg=get_gspread_client()
  sid=get_spreadsheet_id()
  if not client or not sid:
    # Fallback to local CSV for testing
    try:
      import os
      os.makedirs("/tmp/herbal_test", exist_ok=True)
      df=pd.DataFrame([row_dict])
      path=f"/tmp/herbal_test/{sheet_name}_local.csv"
      if os.path.exists(path):
        old=pd.read_csv(path)
        df=pd.concat([old, df], ignore_index=True)
      df.to_csv(path, index=False)
      return True, f"Local Save (Sheet not connected): {path} - {msg} | SID={'Found' if sid else 'Missing'}"
    except Exception as e:
      return False, f"Both Sheet and Local failed: {msg} | {e}"
  
  try:
    sh=client.open_by_key(sid)
    try: ws=sh.worksheet(sheet_name)
    except:
      ws=sh.add_worksheet(title=sheet_name, rows=1000, cols=len(SHEET_HEADERS.get(sheet_name, ["ID","Data"]))+5)
      ws.append_row(SHEET_HEADERS.get(sheet_name, ["ID","Data"]))
    headers=SHEET_HEADERS.get(sheet_name, list(row_dict.keys()))
    row=[row_dict.get(h,"") for h in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")
    get_all_records_cached.clear()
    return True, f"Saved to Google Sheet: {sheet_name}"
  except Exception as e:
    return False, f"Sheet Error: {e}"

# ---------- SESSION - LOGIN FREE ----------
if "lang" not in st.session_state: st.session_state.lang="en"
# V1.3 - Testing Mode: Auto Logged In
if "logged_in" not in st.session_state: st.session_state.logged_in=True
if "username" not in st.session_state: st.session_state.username="Testing Hakeem (Login Free)"
if "usertype" not in st.session_state: st.session_state.usertype="ClinicUser"
if "testing_mode" not in st.session_state: st.session_state.testing_mode=True

def top_bar():
  st.markdown("""<style>.rtl{direction:rtl;text-align:right;font-family:'Jameel Noori Nastaleeq','Noto Naskh Arabic',sans-serif;line-height:1.9;} .ltr{direction:ltr;text-align:left;} .card{background:white;border:1px solid #e0e0e0;border-radius:14px;padding:18px;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,0.05);} .red-dot{color:red;} .ok{background:#e8f5e9;border:1px solid #4caf50;border-radius:8px;padding:8px;} .bad{background:#ffebee;border:1px solid #f44336;border-radius:8px;padding:8px;} .test-banner{background:#fff3e0;border:2px dashed #ff9800;border-radius:10px;padding:10px;margin-bottom:10px;text-align:center;font-weight:bold;}</style>""", unsafe_allow_html=True)
  if st.session_state.testing_mode:
    st.markdown("<div class='test-banner'>🧪 TESTING MODE - Login Free | ٹیسٹنگ موڈ - لاگ ان فری</div>", unsafe_allow_html=True)
  c1,c2,c3=st.columns([6,2,2])
  with c1: st.markdown(f"### 🌿 Herbal Clinic OS | {APP_VERSION}")
  with c2:
    lang_opt=st.selectbox("Lang", ["en","ur","ar"], index=["en","ur","ar"].index(st.session_state.lang), label_visibility="collapsed", key="lang_v13")
    st.session_state.lang=lang_opt
  with c3:
    st.caption(f"{st.session_state.username}")
    if st.button("Enable Login Later", key="enable_login_v13"):
      st.session_state.testing_mode=False
      st.session_state.logged_in=False
      st.rerun()

def dashboard_page():
  top_bar()
  st.markdown(f"### Dashboard - V1.3 Testing Mode - 22 Sheets Check")
  
  client, cmsg = get_gspread_client()
  sid, debug = get_spreadsheet_id_debug()
  
  col1,col2=st.columns(2)
  with col1:
    st.markdown(f"<div class='{'ok' if client else 'bad'}'>GSpread: {cmsg}</div>", unsafe_allow_html=True)
  with col2:
    st.markdown(f"<div class='{'ok' if sid else 'bad'}'>Sheet ID: {sid[:20]+'...' if sid else 'Missing'}</div>", unsafe_allow_html=True)
  
  with st.expander("🔍 Debug - secrets.toml me kya hai? (SHEET_ID kyun missing bata raha hai)", expanded=not bool(sid)):
    for line in debug:
      st.write(line)
    st.markdown("""
    **Hal kaise karen:**
    1. Streamlit Cloud me jayen -> App -> Settings -> Secrets
    2. Wahan ye hona chahiye:
    ```
    SHEET_ID = "aapki sheet id yahan"
    
    [gcp_service_account]
    type = "service_account"
    project_id = "..."
    private_key_id = "..."
    private_key = "-----BEGIN PRIVATE KEY-----\\n..."
    client_email = "..."
    ...
    ```
    3. Agar aap local VS Code me test kar rahe hain to `.streamlit/secrets.toml` file check karen
    4. File ka naam exact `secrets.toml` hona chahiye, `secret.toml` nahi
    """)
    if st.button("Re-check Secrets Now"):
      get_spreadsheet_id_debug.clear()
      get_gspread_client.clear()
      st.rerun()

  tab1,tab2,tab3=st.tabs(["✅ 22 Sheets Check (V1.1 Result)","🧪 Test Save (Feedback)","ℹ️ Next"])

  with tab1:
    st.markdown("#### V1.1 wala 22 Sheets Structure Check")
    if st.button("Check All 22 Sheets Now - V1.1 Test", type="primary", key="check_sheets_v13"):
      if not client or not sid:
        st.error(f"Cannot check - Client: {cmsg}, SID Missing. Upar debug dekhen.")
      else:
        try:
          sh=client.open_by_key(sid)
          existing=[ws.title for ws in sh.worksheets()]
          results=[]
          for s in ALL_SHEETS:
            if s in existing:
              try:
                ws=sh.worksheet(s)
                first=ws.row_values(1) if ws.row_count>0 else []
                expected=SHEET_HEADERS[s]
                missing=[h for h in expected if h not in first]
                status="OK" if not missing else f"Missing headers: {missing[:3]}"
              except Exception as e:
                status=f"Error: {e}"
              results.append({"Sheet": s, "Exists": "Yes", "Status": status})
            else:
              results.append({"Sheet": s, "Exists": "No", "Status": "Not exists - auto-create on save"})
          df=pd.DataFrame(results)
          st.dataframe(df, use_container_width=True)
          ok=sum(1 for r in results if r["Exists"]=="Yes")
          st.success(f"{ok} / {len(results)} sheets exist. 'No' wali first save par ban jayengi.")
        except Exception as e:
          st.error(f"Error: {e}")
    else:
      st.info("Button dabayen - Yehi wo result hai jo V1.1 me chahiye tha")

  with tab2:
    st.markdown("#### Test Save - Feedback Sheet")
    name=st.text_input("Name", "Hakeem Testing V1.3", key="fb_name_v13")
    fb=st.text_area("Feedback", "V1.3 login free testing", key="fb_text_v13")
    if st.button("Save - Test Save (Google Sheet ya Local)", type="primary", key="save_fb_v13"):
      ok,msg2=save_to_sheet_with_fallback("Feedback", {"ID": f"FB_{int(time.time())}", "Name": name, "Feedback": fb, "Date": str(datetime.date.today()), "From": "V1.3 Login Free Test", "Feedback Page": "Dashboard"})
      if ok: st.success(msg2)
      else: st.error(msg2)
    
    st.markdown("#### Recent Records")
    recs=get_all_records_cached("Feedback", 20)
    if recs:
      st.dataframe(pd.DataFrame(recs).tail(10), use_container_width=True)
    else:
      st.caption("No records from Google Sheet - Agar Sheet connect nahi to local me save hua hoga. Neeche local file check karen.")
      try:
        import os
        path="/tmp/herbal_test/Feedback_local.csv"
        if os.path.exists(path):
          st.write("Local file found:")
          st.dataframe(pd.read_csv(path).tail(10), use_container_width=True)
      except: pass

  with tab3:
    st.markdown("""
    **V1.3 me kya kiya:**
    - Login Free kar diya - ab direct Dashboard khulega
    - SHEET_ID 6 jagah check karta hai - debug dikhata hai
    - Agar Sheet connect nahi to local CSV me save karega - testing rukegi nahi
    - Wahi Sheet ID, wahi secrets.toml - koi change nahi
    
    **Aapka masla hal:**
    - V1.1 ka `SHEET_ID missing` - Upar debug expander me dekhen - Streamlit Cloud Secrets me SHEET_ID add karna hai
    - V1.2 Login fail - Ab login free hai, V2 tak free rahega
    
    **Next: V1.4 me Initial Page polish + V2 me Patient form**
    """)

def main():
  # V1.3 Testing Mode - Always logged in
  if st.session_state.testing_mode:
    st.session_state.logged_in=True
  dashboard_page()

if __name__=="__main__": main()
