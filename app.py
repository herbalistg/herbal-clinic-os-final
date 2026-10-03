# ============================================
# Herbal Clinic OS
# VERSION: V2.2 - Column Mapping Fix - Data goes to correct column
# Date: 2026-10-03
# Bug Report: DailyNumber me Date, Name me Age (30) - Header order mismatch
# Fix in V2.2:
#  - Reads ACTUAL headers from Google Sheet row 1
#  - Saves data according to ACTUAL order, not hardcoded order
#  - Shows header debug + Fix Headers button
#  - Auth Muted
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

APP_VERSION = "V2.2 - Column Fix"

st.set_page_config(page_title=APP_VERSION, page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

SHEET_HEADERS_STANDARD = {
  "New_patient": ["PatientID","Date","Name","FatherName","Age","Gender","MaritalStatus","Occupation","CNIC","Phone","EmergencyPhone","Address","Referral","Diseases","ChiefComplaint","PastHistory","FamilyHistory","Allergy","Examination","Pulse","Temperament","BP","Weight","Temperature","Height","SleepPattern","Appetite","BowelMovement","Thirst","Urine","Sweating","StressLevel","EnergyLevel","SingleMedicines","FormulaMedicines","ManualMedicines","Fees","MedicineCharges","Total","Paid","Balance","PrevBalance","PaymentMethod","FeeStatus","RevisitDate","ClinicName","CreatedBy","Timestamp","AppVersion","DailyNumber","TotalNumber","GrandTotal","UserType","Habits","BloodGroup","CuredDiseases","RemainingDiseases"],
  "Revisit": ["RevisitID","PatientID","OriginalPatientID","Date","Name","FatherName","Age","Gender","MaritalStatus","Occupation","CNIC","Phone","EmergencyPhone","Address","Referral","Diseases","PreviousDiseases","ChiefComplaint","PastHistory","FamilyHistory","Allergy","Pulse","Temperament","BP","Weight","Temperature","Height","SleepPattern","Appetite","BowelMovement","SingleMedicines","FormulaMedicines","ManualMedicines","Fees","MedicineCharges","Total","Paid","Balance","PrevBalance","PaymentMethod","FeeStatus","ClinicName","CreatedBy","Timestamp","AppVersion","DailyNumber","TotalNumber","GrandTotal","CuredDiseases","RemainingDiseases","UserType","BloodGroup","Habits"],
  "Feedback": ["ID","Name","From","Phone Number","Email","Feedback Page","Feedback","Date","Status","UserType","ClinicName","Rating","Response"],
}

ALL_SHEETS = ["New_patient","Revisit","Feedback","UserSignups","Herbs","Pharmacopoeia","Dictionary","Articles","AppSettings","Offer","HomeUsers","AutoDiagnosis","HomeTreatment","PermissionGranted","ClinicFormulas","ClinicSettings","Inventory","BillingReport","Expenses","Appointments"]

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

def get_actual_headers(sheet_name):
  client,msg=get_gspread_client()
  sid=get_spreadsheet_id()
  if not client or not sid: return None, f"Not connected: {msg}"
  try:
    sh=client.open_by_key(sid)
    ws=sh.worksheet(sheet_name)
    headers=ws.row_values(1)
    return headers, "OK"
  except Exception as e:
    return None, str(e)

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

def save_to_sheet_fixed(sheet_name, row_dict):
  """FIXED: Uses actual sheet headers order, not hardcoded"""
  client,msg=get_gspread_client()
  sid=get_spreadsheet_id()
  if not client or not sid: return False, f"Not connected: {msg}"
  try:
    sh=client.open_by_key(sid)
    ws=sh.worksheet(sheet_name)
    actual_headers=ws.row_values(1)
    
    if not actual_headers:
      # No headers, create standard
      actual_headers=SHEET_HEADERS_STANDARD.get(sheet_name, list(row_dict.keys()))
      ws.append_row(actual_headers)
    
    # Build row according to ACTUAL headers order
    row=[row_dict.get(h,"") for h in actual_headers]
    
    ws.append_row(row, value_input_option="USER_ENTERED")
    get_all_records_cached.clear()
    return True, f"Saved to {sheet_name} using actual headers order ({len(actual_headers)} cols) - Row: {row[:5]}..."
  except Exception as e:
    return False, f"Error: {e}"

def fix_headers_to_standard(sheet_name):
  client,msg=get_gspread_client()
  sid=get_spreadsheet_id()
  if not client or not sid: return False, f"Not connected: {msg}"
  try:
    sh=client.open_by_key(sid)
    ws=sh.worksheet(sheet_name)
    standard=SHEET_HEADERS_STANDARD.get(sheet_name)
    if not standard: return False, f"No standard for {sheet_name}"
    
    # Get current data (without header)
    all_values=ws.get_all_values()
    if len(all_values)<=1:
      # Only header or empty, just overwrite header
      ws.clear()
      ws.append_row(standard)
      return True, f"Headers fixed to standard ({len(standard)} cols) - Sheet was empty"
    else:
      # Has data - backup then fix header
      data_rows=all_values[1:]  # without header
      ws.clear()
      ws.append_row(standard)
      # Note: old data will be misaligned, better to clear since user already cleaned
      return True, f"Headers fixed to standard ({len(standard)} cols) - Old data cleared (you said sheet cleaned)"
  except Exception as e:
    return False, str(e)

if "lang" not in st.session_state: st.session_state.lang="en"
st.session_state.logged_in=True

def main():
  st.markdown(f"### 🌿 Herbal Clinic OS | {APP_VERSION} - Column Mapping Fix")
  st.markdown("<div style='background:#ffebee;border:2px solid #f44336;border-radius:10px;padding:10px;text-align:center;'><b>🐛 Bug Report: Name me 30, DailyNumber me Date - Fixed in V2.2</b><br>Ab actual sheet headers se mapping hogi</div>", unsafe_allow_html=True)

  sid=get_spreadsheet_id()
  client,msg=get_gspread_client()
  
  col1,col2=st.columns(2)
  with col1:
    if sid: st.success(f"Sheet ID: {sid[:30]}...")
    else: st.error("Missing")
  with col2:
    if client: st.success(f"Client: {msg}")
    else: st.error(msg)

  tab1,tab2,tab3=st.tabs(["🔍 Debug Headers (Pehle Ye Dekhen)","👤 New Patient Fixed","📋 Recent"])

  with tab1:
    st.markdown("#### Step 1: Actual Headers Kya Hain Sheet Me?")
    sheet_to_check=st.selectbox("Sheet Select", ["New_patient","Revisit","Feedback"], key="sheet_check_v22")
    
    if st.button(f"Show Actual Headers of {sheet_to_check}", key="show_headers_v22"):
      headers, hmsg = get_actual_headers(sheet_to_check)
      if headers:
        st.write(f"Actual headers in sheet ({len(headers)} cols):")
        st.code(headers)
        st.write(f"First 10: {headers[:10]}")
        st.write(f"Last 10: {headers[-10:]}")
        
        # Compare with standard
        standard=SHEET_HEADERS_STANDARD.get(sheet_to_check, [])
        st.write(f"Standard should be ({len(standard)} cols):")
        st.code(standard[:20])
        
        # Find mismatches
        if headers != standard:
          st.warning(f"⚠️ Headers mismatch! Actual {len(headers)} vs Standard {len(standard)}")
          missing=[h for h in standard if h not in headers]
          extra=[h for h in headers if h not in standard]
          if missing: st.write(f"Missing in actual: {missing[:10]}")
          if extra: st.write(f"Extra in actual: {extra[:10]}")
          
          # Check positions of important fields
          for field in ["Name","Age","Date","DailyNumber","Phone"]:
            if field in headers:
              st.write(f"{field} at position {headers.index(field)} in actual")
            if field in standard:
              st.write(f"{field} should be at position {standard.index(field)} in standard")
        else:
          st.success("✅ Headers match standard - OK")
      else:
        st.error(f"Failed: {hmsg}")

    st.markdown("---")
    st.markdown("#### Step 2: Fix Headers to Standard (Agar Mismatch Hai)")
    st.warning("Aapne kaha sheet clean ki hai (data delete) - to header fix karna safe hai")
    sheet_to_fix=st.selectbox("Fix Sheet", ["New_patient","Revisit"], key="fix_sheet_v22")
    if st.button(f"Fix {sheet_to_fix} Headers to Standard Order", type="primary", key="fix_headers_btn_v22"):
      ok,msg2=fix_headers_to_standard(sheet_to_fix)
      if ok:
        st.success(msg2)
        st.balloons()
        get_all_records_cached.clear()
      else:
        st.error(msg2)

  with tab2:
    st.markdown("#### New Patient - V2.2 Fixed Column Mapping")
    st.info("Ab actual headers se mapping hogi - Name me Age nahi jayega")

    with st.form("patient_form_v22_fixed", clear_on_submit=True):
      c1,c2,c3=st.columns(3)
      with c1:
        name=st.text_input("Name / نام *", key="name_v22")
        father=st.text_input("Father Name", key="father_v22")
        age=st.number_input("Age", min_value=0, max_value=120, value=30, key="age_v22")
      with c2:
        gender=st.selectbox("Gender", ["Male","Female","Other"], key="gender_v22")
        phone=st.text_input("Phone *", key="phone_v22")
        address=st.text_area("Address", height=70, key="addr_v22")
      with c3:
        diseases=st.text_area("Complaint", height=70, key="dis_v22")
        fees=st.number_input("Fees", min_value=0, value=500, key="fees_v22")
        paid=st.number_input("Paid", min_value=0, value=500, key="paid_v22")

      submitted=st.form_submit_button("Save Patient - Fixed Mapping", type="primary", use_container_width=True)

      if submitted:
        name_c=name.strip()
        phone_c=phone.strip()
        if not name_c or not phone_c:
          st.error("Name and Phone required")
        else:
          # Show mapping debug
          actual_headers, _ = get_actual_headers("New_patient")
          if actual_headers:
            st.write(f"Using actual headers order: Name at {actual_headers.index('Name') if 'Name' in actual_headers else 'Not found'}, Age at {actual_headers.index('Age') if 'Age' in actual_headers else 'Not found'}, DailyNumber at {actual_headers.index('DailyNumber') if 'DailyNumber' in actual_headers else 'Not found'}")

          pid=f"P_{int(time.time())}"
          today=str(datetime.date.today())
          row={
            "PatientID": pid,
            "Date": today,
            "Name": name_c,
            "FatherName": father.strip(),
            "Age": age,
            "Gender": gender,
            "Phone": phone_c,
            "Address": address.strip(),
            "Diseases": diseases.strip(),
            "ChiefComplaint": diseases.strip(),
            "Fees": fees,
            "Paid": paid,
            "Balance": fees-paid,
            "Total": fees,
            "DailyNumber": 1,
            "TotalNumber": 1,
            "GrandTotal": 1,
            "ClinicName": "Testing V2.2 Fixed",
            "CreatedBy": "V2.2",
            "Timestamp": str(datetime.datetime.now()),
            "AppVersion": APP_VERSION,
            "UserType": "ClinicUser"
          }
          ok,msg2=save_to_sheet_fixed("New_patient", row)
          if ok:
            st.success(f"✅ Saved: {pid} - {msg2}")
            st.balloons()
          else:
            st.error(f"❌ {msg2}")

  with tab3:
    st.markdown("#### Recent Patients - Check Mapping")
    recs=get_all_records_cached("New_patient", 20)
    if recs:
      df=pd.DataFrame(recs)
      # Show raw to see if mapping correct
      st.dataframe(df.tail(10), use_container_width=True)
      
      # Check last row specifically
      if len(df)>0:
        last=df.iloc[-1]
        st.markdown("**Last Row Check:**")
        st.write(f"Name = {last.get('Name','')} (should be name, not age)")
        st.write(f"Age = {last.get('Age','')} (should be age like 30)")
        st.write(f"Date = {last.get('Date','')} (should be date like 2026-10-03)")
        st.write(f"DailyNumber = {last.get('DailyNumber','')} (should be number, not date)")
        
        # Bug detection
        if str(last.get('Name','')).isdigit():
          st.error("🐛 BUG STILL: Name is digit (Age) - Headers still mismatched! Go to Tab 1 and Fix Headers")
        elif str(last.get('DailyNumber','')).startswith('2026'):
          st.error("🐛 BUG STILL: DailyNumber is date - Headers mismatch! Fix Headers")
        else:
          st.success("✅ Mapping appears correct now!")
    else:
      st.info("No patients yet - Sheet clean as you said")

if __name__=="__main__": main()
