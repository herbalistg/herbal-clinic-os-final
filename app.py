# ============================================
# Herbal Clinic OS - NEW INSTALLATION
# VERSION: V1.4 - SHEET_ID AttrDict Fix + Login Free
# Date: 2026-10-03
# Base: V1.3
# Fix in V1.4:
#  - AttrDict bug fix: connections.gsheets is AttrDict not dict in new Streamlit
#  - Now checks 8 places including AttrDict direct access
#  - Same Sheet ID & secrets.toml - No change needed
#  - Still Login Free for testing
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

APP_VERSION = "V1.4 - AttrDict Fix + Login Free"

st.set_page_config(page_title=f"Herbal Clinic OS {APP_VERSION}", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

SHEET_HEADERS = {
  "UserSignups": ["SignupID","Username","Password","UserType","ClinicName","Phone","Email","Date","Status","Role","From","LastLogin","DeviceInfo"],
  "Feedback": ["ID","Name","From","Phone Number","Email","Feedback Page","Feedback","Date","Status","UserType","ClinicName","Rating","Response"],
  "New_patient": ["PatientID","Date","Name","FatherName","Age","Gender","Phone","Address","Diseases","Fees","Total","Paid","Balance","ClinicName","CreatedBy","Timestamp"],
  "Revisit": ["RevisitID","PatientID","Date","Name","Diseases","Fees","Total","Paid","Balance","ClinicName"],
  "Herbs": ["HerbID","Name","UrduName","Temperament","Mizaj","Uses","Benefits"],
  "Pharmacopoeia": ["ID","Name","UrduName","Category","Temperament","Uses"],
  "Dictionary": ["ID","Word","UrduWord","ArabicWord","Meaning","Category"],
  "Articles": ["ID","TitleEN","TitleUR","TitleAR","ContentEN","MainCategory","Status","Date"],
  "AppSettings": ["Key","Value","Date","Status","Description"],
  "Offer": ["ID","TitleEN","TitleUR","ContentEN","Status","Date"],
  "HomeUsers": ["UserID","Username","FullName","Phone","Status"],
  "AutoDiagnosis": ["ID","PatientID","Date","Name","Age","Gender","Diseases","Temperament","Mizaj"],
  "HomeTreatment": ["ID","PatientID","Date","Name","Age","Gender","Diseases","Mizaj"],
  "PermissionGranted": ["ID","Username","UserType","PermissionType","Status"],
  "ClinicFormulas": ["FormulaID","Name","UrduName","Ingredients","Uses"],
  "ClinicSettings": ["SettingID","ClinicName","SettingKey","SettingValue"],
  "Inventory": ["ItemID","ItemName","Category","Quantity","Unit"],
  "BillingReport": ["ReportID","Date","PatientID","Name","Total","Paid","Balance"],
  "Expenses": ["ExpenseID","Date","Category","Amount","Description"],
  "Appointments": ["AppointmentID","Date","Time","PatientID","PatientName","Phone","Status"],
}
ALL_SHEETS = list(SHEET_HEADERS.keys())

# ---------- FIXED SHEET ID EXTRACTOR FOR NEW STREAMLIT AttrDict ----------
def get_spreadsheet_id_debug():
  debug=[]
  found=None
  
  # Helper to safely get from secrets (supports AttrDict)
  def safe_get(path_list):
    try:
      obj = st.secrets
      for p in path_list:
        # AttrDict supports both dict and attribute access
        if isinstance(obj, dict) or hasattr(obj, '__getitem__'):
          try:
            obj = obj[p]
          except:
            obj = getattr(obj, p)
        else:
          obj = getattr(obj, p)
      return obj
    except Exception as e:
      return None

  # 1. Direct SHEET_ID
  v = safe_get(["SHEET_ID"])
  if v and isinstance(v, str) and len(v)>10:
    debug.append(f"✅ Found st.secrets['SHEET_ID']: {str(v)[:25]}...")
    return v, debug
  else:
    debug.append("❌ Not in st.secrets['SHEET_ID']")

  # 2. connections.gsheets.spreadsheet - NEW STREAMLIT WAY (AttrDict)
  v = safe_get(["connections","gsheets","spreadsheet"])
  if v and isinstance(v, str) and len(v)>10:
    debug.append(f"✅ Found [connections.gsheets].spreadsheet (AttrDict fixed): {str(v)[:25]}...")
    return v, debug
  else:
    debug.append(f"❌ [connections.gsheets].spreadsheet not found via AttrDict - tried, got: {type(v)} {str(v)[:50] if v else 'None'}")

  # 3. Try connections.gsheets itself is string ID
  v = safe_get(["connections","gsheets"])
  if isinstance(v, str) and len(v)>10 and "1" in v:
    debug.append(f"✅ Found [connections.gsheets] as direct string ID: {str(v)[:25]}...")
    return v, debug
  # If it's AttrDict, list its keys
  try:
    obj = st.secrets["connections"]["gsheets"]
    # Try to convert to dict for keys
    try:
      keys = list(obj.keys()) if hasattr(obj, 'keys') else dir(obj)
      debug.append(f"ℹ️ [connections.gsheets] keys available: {keys[:10]}")
      # Try each key case-insensitive for spreadsheet
      for k in keys:
        if 'spread' in k.lower() or 'sheet' in k.lower() or 'id' in k.lower():
          val = safe_get(["connections","gsheets",k])
          debug.append(f"  -> Trying key '{k}' = {str(val)[:40] if val else 'None'}")
          if val and isinstance(val, str) and len(val)>10:
            debug.append(f"✅ Found via key '{k}': {str(val)[:25]}...")
            return val, debug
    except Exception as e:
      debug.append(f"ℹ️ Could not list keys of gsheets: {e}")
  except:
    debug.append("❌ Not in [connections.gsheets] at all")

  # 4. gsheets.spreadsheet
  v = safe_get(["gsheets","spreadsheet"])
  if v and isinstance(v, str) and len(v)>10:
    debug.append(f"✅ Found [gsheets].spreadsheet: {str(v)[:25]}...")
    return v, debug
  else:
    debug.append("❌ Not in [gsheets].spreadsheet")

  # 5. List top keys
  try:
    top_keys = list(st.secrets.keys())
    debug.append(f"ℹ️ All top secrets keys: {top_keys}")
    # Show connections keys if exists
    if "connections" in top_keys:
      try:
        conn_keys = list(st.secrets["connections"].keys()) if hasattr(st.secrets["connections"], 'keys') else []
        debug.append(f"ℹ️ [connections] sub-keys: {conn_keys}")
      except: pass
  except Exception as e:
    debug.append(f"❌ Can't list top keys: {e}")

  debug.append("⚠️ FINAL: No Sheet ID found in any location")
  return None, debug

def get_spreadsheet_id():
  sid,_ = get_spreadsheet_id_debug()
  return sid

@st.cache_resource(ttl=900)
def get_gspread_client():
  if not GSPREAD_AVAILABLE: return None, "gspread not installed"
  try:
    # Try multiple places for creds
    creds_dict=None
    # Method 1: gcp_service_account
    try:
      if "gcp_service_account" in st.secrets:
        creds_dict=dict(st.secrets["gcp_service_account"])
    except: pass
    # Method 2: connections.gsheets as service_account
    if not creds_dict:
      try:
        gs = st.secrets["connections"]["gsheets"]
        # Check if gs itself is service account dict (has type)
        if hasattr(gs, 'keys'):
          keys = list(gs.keys())
          if "type" in keys and "private_key" in keys:
            creds_dict=dict(gs)
        # Check nested gcp_service_account
        if "gcp_service_account" in str(type(gs)):
          pass
      except: pass
    # Method 3: connections.gsheets.gcp_service_account or service_account
    if not creds_dict:
      for path in [["connections","gsheets","gcp_service_account"], ["connections","gsheets","service_account"], ["gcp_service_account"]]:
        try:
          obj=st.secrets
          for p in path: obj=obj[p]
          if obj and hasattr(obj, 'keys') and "private_key" in list(obj.keys()):
            creds_dict=dict(obj)
            break
        except: continue

    if not creds_dict:
      return None, "No service_account found - Add [gcp_service_account] or [connections.gsheets] with private_key"
    
    creds=Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
    client=gspread.authorize(creds)
    return client, "OK - Connected"
  except Exception as e:
    return None, f"Auth Error: {e}"

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
    try:
      import os
      os.makedirs("/tmp/herbal_test", exist_ok=True)
      df=pd.DataFrame([row_dict])
      path=f"/tmp/herbal_test/{sheet_name}_local.csv"
      if os.path.exists(path):
        old=pd.read_csv(path)
        df=pd.concat([old, df], ignore_index=True)
      df.to_csv(path, index=False)
      return True, f"Local Save (Sheet not connected yet): {path}"
    except Exception as e:
      return False, f"Both failed: {msg} | {e}"
  try:
    sh=client.open_by_key(sid)
    try: ws=sh.worksheet(sheet_name)
    except:
      ws=sh.add_worksheet(title=sheet_name, rows=1000, cols=len(SHEET_HEADERS.get(sheet_name, ["ID"]))+5)
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
if "logged_in" not in st.session_state: st.session_state.logged_in=True
if "username" not in st.session_state: st.session_state.username="Testing Hakeem (Login Free)"
if "testing_mode" not in st.session_state: st.session_state.testing_mode=True

def top_bar():
  st.markdown("""<style>.card{background:white;border:1px solid #e0e0e0;border-radius:14px;padding:18px;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,0.05);} .ok{background:#e8f5e9;border:1px solid #4caf50;border-radius:8px;padding:8px;} .bad{background:#ffebee;border:1px solid #f44336;border-radius:8px;padding:8px;} .test-banner{background:#fff3e0;border:2px dashed #ff9800;border-radius:10px;padding:10px;margin-bottom:10px;text-align:center;font-weight:bold;}</style>""", unsafe_allow_html=True)
  st.markdown("<div class='test-banner'>🧪 TESTING MODE - Login Free | V1.4 AttrDict Fix</div>", unsafe_allow_html=True)
  c1,c2=st.columns([7,3])
  with c1: st.markdown(f"### 🌿 Herbal Clinic OS | {APP_VERSION} | Copy-Paste Workflow")
  with c2: st.caption("VS Code = Copy/Paste | Streamlit = View")

def main():
  top_bar()
  client, cmsg = get_gspread_client()
  sid, debug = get_spreadsheet_id_debug()

  col1,col2=st.columns(2)
  with col1: st.markdown(f"<div class='{'ok' if client else 'bad'}'>GSpread: {cmsg}</div>", unsafe_allow_html=True)
  with col2: st.markdown(f"<div class='{'ok' if sid else 'bad'}'>Sheet ID: {sid[:30]+'...' if sid else 'Missing - see debug below'}</div>", unsafe_allow_html=True)

  # Debug expander - OPEN by default if missing
  with st.expander("🔍 Debug - Aapke secrets.toml me kya hai? (Isko kholen)", expanded=not bool(sid)):
    for line in debug:
      st.write(line)
    st.markdown("---")
    st.markdown("""
    **Aapka secrets.toml aise hona chahiye (2 me se 1 format):**
    
    **Format 1 - Simple (Recommended for copy-paste):**
    ```toml
    SHEET_ID = "1D4x7wioVZyvw3i2p6NC2rTp1Z2J_DuTYGcJMy6X2sHA"
    
    [gcp_service_account]
    type = "service_account"
    project_id = "your-project"
    private_key_id = "..."
    private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
    client_email = "...@....iam.gserviceaccount.com"
    client_id = "..."
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://oauth2.googleapis.com/token"
    ```
    
    **Format 2 - connections.gsheets wala (aapka current):**
    ```toml
    [connections.gsheets]
    spreadsheet = "1D4x7wioVZyvw3i2p6NC2rTp1Z2J_DuTYGcJMy6X2sHA"
    
    [connections.gsheets.gcp_service_account]
    type = "service_account"
    ... baqi json ...
    ```
    Dono me `spreadsheet` ka naam exact `spreadsheet` hona chahiye, `spreadsheet_id` ya `sheet_id` nahi.
    """)
    if st.button("Re-check Secrets"):
      st.cache_data.clear()
      st.cache_resource.clear()
      st.rerun()

  tab1,tab2=st.tabs(["✅ 22 Sheets Check (V1.1 Result)","🧪 Test Save"])

  with tab1:
    if st.button("Check All 22 Sheets Now", type="primary"):
      if not client or not sid:
        st.error(f"Cannot check - {cmsg} | SID missing. Upar debug dekhen.")
      else:
        try:
          sh=client.open_by_key(sid)
          existing=[ws.title for ws in sh.worksheets()]
          results=[]
          for s in ALL_SHEETS:
            if s in existing:
              results.append({"Sheet": s, "Exists": "Yes", "Status": "OK"})
            else:
              results.append({"Sheet": s, "Exists": "No", "Status": "Will auto-create on save"})
          df=pd.DataFrame(results)
          st.dataframe(df, use_container_width=True)
          st.success(f"{len([r for r in results if r['Exists']=='Yes'])} / {len(results)} sheets exist")
          st.balloons()
        except Exception as e:
          st.error(f"Error: {e}")

  with tab2:
    st.markdown("#### Feedback Test Save")
    name=st.text_input("Name", "Hakeem V1.4 Test", key="fb_n")
    fb=st.text_area("Feedback", "Testing AttrDict fix", key="fb_t")
    if st.button("Save Now", type="primary"):
      ok,msg2=save_to_sheet_with_fallback("Feedback", {"ID": f"FB_{int(time.time())}", "Name": name, "Feedback": fb, "Date": str(datetime.date.today()), "From": "V1.4 Fix"})
      if ok: st.success(msg2)
      else: st.error(msg2)
    recs=get_all_records_cached("Feedback", 20)
    if recs:
      st.dataframe(pd.DataFrame(recs).tail(10), use_container_width=True)
    else:
      st.caption("No records from Sheet yet - Local fallback check:")
      try:
        import os
        p="/tmp/herbal_test/Feedback_local.csv"
        if os.path.exists(p):
          st.dataframe(pd.read_csv(p).tail(10), use_container_width=True)
      except: pass

if __name__=="__main__": main()
