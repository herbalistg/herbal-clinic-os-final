# ============================================
# Herbal Clinic OS
# VERSION: V2.3 - Father/Spouse Fix + Column Fix Retained
# Date: 2026-10-03
# Fixes in V2.3:
#  - Father Name -> Father Name / Spouse Name (باپ / سپاس) in all forms
#  - Column Mapping Fix from V2.2 retained
#  - Auth Muted
#  - Limit: 910/1024 -> Keep code compact
# ============================================

import streamlit as st
import pandas as pd
import datetime
import time

try:
  import gspread
  from google.oauth2.service_account import Credentials
  GSPREAD_AVAILABLE=True
except: GSPREAD_AVAILABLE=False

APP_VERSION="V2.3 - Father/Spouse + Column Fix"
st.set_page_config(page_title=APP_VERSION, page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

SHEET_HEADERS_STD={
  "New_patient": ["PatientID","Date","Name","FatherName","Age","Gender","MaritalStatus","Occupation","CNIC","Phone","EmergencyPhone","Address","Referral","Diseases","ChiefComplaint","PastHistory","FamilyHistory","Allergy","Examination","Pulse","Temperament","BP","Weight","Temperature","Height","SleepPattern","Appetite","BowelMovement","Thirst","Urine","Sweating","StressLevel","EnergyLevel","SingleMedicines","FormulaMedicines","ManualMedicines","Fees","MedicineCharges","Total","Paid","Balance","PrevBalance","PaymentMethod","FeeStatus","RevisitDate","ClinicName","CreatedBy","Timestamp","AppVersion","DailyNumber","TotalNumber","GrandTotal","UserType","Habits","BloodGroup","CuredDiseases","RemainingDiseases"],
  "Revisit": ["RevisitID","PatientID","OriginalPatientID","Date","Name","FatherName","Age","Gender","Diseases","Fees","Total","Paid","Balance","ClinicName","CreatedBy","Timestamp"],
  "Feedback": ["ID","Name","From","Phone Number","Email","Feedback Page","Feedback","Date","Status","UserType","ClinicName","Rating","Response"],
}

def get_sid():
  def safe_get(p):
    try:
      o=st.secrets
      for k in p:
        try: o=o[k]
        except: o=getattr(o,k)
      return o if isinstance(o,str) and len(o)>10 else None
    except: return None
  for path in [["SHEET_ID"],["connections","gsheets","spreadsheet"],["gsheets","spreadsheet"]]:
    v=safe_get(path)
    if v: return v
  return None

@st.cache_resource(ttl=900)
def get_client():
  try:
    cd=None
    try:
      if "gcp_service_account" in st.secrets: cd=dict(st.secrets["gcp_service_account"])
    except: pass
    if not cd:
      try:
        gs=st.secrets["connections"]["gsheets"]
        if hasattr(gs,'keys') and "private_key" in list(gs.keys()): cd=dict(gs)
      except: pass
    if not cd:
      for pa in [["connections","gsheets","gcp_service_account"],["connections","gsheets","service_account"]]:
        try:
          o=st.secrets
          for k in pa: o=o[k]
          if hasattr(o,'keys') and "private_key" in list(o.keys()): cd=dict(o); break
        except: continue
    if not cd: return None,"No creds"
    creds=Credentials.from_service_account_info(cd, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
    return gspread.authorize(creds),"OK"
  except Exception as e: return None,str(e)

def get_actual_headers(sheet):
  c,m=get_client(); sid=get_sid()
  if not c or not sid: return None,m
  try:
    sh=c.open_by_key(sid); ws=sh.worksheet(sheet)
    return ws.row_values(1),"OK"
  except Exception as e: return None,str(e)

@st.cache_data(ttl=300)
def get_records(sheet, n=200):
  c,m=get_client(); sid=get_sid()
  if not c or not sid: return []
  try:
    sh=c.open_by_key(sid); ws=sh.worksheet(sheet)
    recs=ws.get_all_records()
    return recs[-n:] if len(recs)>n else recs
  except: return []

def save_fixed(sheet, row_dict):
  c,m=get_client(); sid=get_sid()
  if not c or not sid: return False,f"Not connected: {m}"
  try:
    sh=c.open_by_key(sid); ws=sh.worksheet(sheet)
    actual=ws.row_values(1)
    if not actual:
      actual=SHEET_HEADERS_STD.get(sheet, list(row_dict.keys()))
      ws.append_row(actual)
    row=[row_dict.get(h,"") for h in actual]
    ws.append_row(row, value_input_option="USER_ENTERED")
    get_records.clear()
    return True,f"Saved to {sheet} ({len(actual)} cols) - Name:{row_dict.get('Name','')} Father/Spouse:{row_dict.get('FatherName','')}"
  except Exception as e: return False,str(e)

st.session_state.logged_in=True

def main():
  st.markdown(f"### 🌿 Herbal Clinic OS | {APP_VERSION}")
  st.markdown("<div style='background:#e8f5e9;border:2px solid #4caf50;border-radius:10px;padding:8px;text-align:center;'><b>V2.3 - Father Name / Spouse Name (باپ / سپاس) + Column Fix</b></div>", unsafe_allow_html=True)
  
  sid=get_sid(); client,msg=get_client()
  c1,c2=st.columns(2)
  with c1:
    if sid: st.success(f"SID: {sid[:25]}...")
    else: st.error("SID Missing")
  with c2:
    if client: st.success(f"Client: {msg}")
    else: st.error(msg)

  tab1,tab2,tab3=st.tabs(["👤 New Patient - Father/Spouse Fixed","🔍 Header Debug","📋 Recent"])

  with tab1:
    st.markdown("#### New Patient - Father Name / Spouse Name (باپ / سپاس)")
    st.info("Ab se har form me Father Name / Spouse Name - باپ / سپاس likha hoga | Column Fix retained from V2.2")

    with st.form("pat_v23_form", clear_on_submit=True):
      col1,col2,col3=st.columns(3)
      with col1:
        name=st.text_input("Name / نام *", key="n_v23")
        # CHANGED: Father/Spouse
        father_spouse=st.text_input("Father Name / Spouse Name / باپ / سپاس کا نام", key="f_v23", help="For male: Father Name, For female: Spouse Name")
        age=st.number_input("Age / عمر", 0,120,30, key="age_v23")
      with col2:
        gender=st.selectbox("Gender / جنس", ["Male","Female","Other"], key="g_v23")
        phone=st.text_input("Phone / فون *", key="ph_v23")
        address=st.text_area("Address / پتہ", height=70, key="ad_v23")
      with col3:
        diseases=st.text_area("Chief Complaint / شکایت", height=70, key="dis_v23")
        fees=st.number_input("Fees / فیس", 0,10000,500, key="fees_v23")
        paid=st.number_input("Paid / وصول", 0,10000,500, key="paid_v23")

      submitted=st.form_submit_button("Save Patient - V2.3", type="primary", use_container_width=True)

      if submitted:
        nc=name.strip(); pc=phone.strip(); fsc=father_spouse.strip()
        if not nc: st.error("Name required / نام ضروری")
        elif not pc: st.error("Phone required / فون ضروری")
        else:
          pid=f"P_{int(time.time())}"
          today=str(datetime.date.today())
          row={
            "PatientID": pid,
            "Date": today,
            "Name": nc,
            "FatherName": fsc,  # Same column, new label
            "Age": age,
            "Gender": gender,
            "Phone": pc,
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
            "ClinicName": "V2.3 Testing - Father/Spouse",
            "CreatedBy": "V2.3",
            "Timestamp": str(datetime.datetime.now()),
            "AppVersion": APP_VERSION,
            "UserType": "ClinicUser"
          }
          with st.spinner("Saving..."):
            ok,msg2=save_fixed("New_patient", row)
          if ok:
            st.success(f"✅ Saved: {pid} | Father/Spouse: {fsc}")
            st.success(msg2)
            st.balloons()
            time.sleep(0.8)
            st.rerun()
          else:
            st.error(f"❌ {msg2}")

  with tab2:
    st.markdown("#### Header Debug - Column Mapping Check")
    sheet=st.selectbox("Sheet", ["New_patient","Revisit"], key="sheet_v23")
    if st.button(f"Show {sheet} Headers", key="show_v23"):
      headers,hmsg=get_actual_headers(sheet)
      if headers:
        st.code(headers)
        st.write(f"Total cols: {len(headers)}")
        for field in ["Name","FatherName","Age","Date","DailyNumber","Phone"]:
          if field in headers:
            st.write(f"{field} -> pos {headers.index(field)}")
      else:
        st.error(hmsg)

  with tab3:
    st.markdown("#### Recent Patients - Check Father/Spouse Column")
    recs=get_records("New_patient",20)
    if recs:
      df=pd.DataFrame(recs).tail(15)
      cols_show=[c for c in ["PatientID","Date","Name","FatherName","Age","Gender","Phone","Diseases","Fees"] if c in df.columns]
      st.dataframe(df[cols_show].iloc[::-1], use_container_width=True)
      # Check mapping
      last=df.iloc[-1]
      st.write(f"Last: Name={last.get('Name','')} | Father/Spouse={last.get('FatherName','')} | Age={last.get('Age','')} | Date={last.get('Date','')} | DailyNumber={last.get('DailyNumber','')}")
      if str(last.get('Name','')).isdigit():
        st.error("🐛 BUG: Name is digit - Fix headers in Tab 2")
      else:
        st.success("✅ Mapping OK - Father/Spouse label fixed")
    else:
      st.info("No patients - Clean sheet as you said")

  st.markdown("---")
  st.caption("V2.3 - Father Name / Spouse Name (باپ / سپاس) applied to all future forms | Limit 940/1024 - Next chat V2.4 se")

if __name__=="__main__": main()
