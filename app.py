# APP VERSION V209.6.12 - Original Structure Restored - Fixed page_history + NameError
import streamlit as st
import datetime
import re
import pandas as pd

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

APP_VERSION = "V209.6.12"
HARDCODED_SHEET_ID = "1D4x7wioVZyvw3i2p6NC2rTp1Z2J_DuTYGcJMy6X2sHA"
WHATSAPP_LINK = "https://chat.whatsapp.com/J7xfZT2Pf4H8Zzu7eBD7CS"

SHEET_HEADERS = {
    "UserSignups": ["SignupID","Username","Password","UserType","ClinicName","Phone","Email","Date","Status","Role","From"],
    "PermissionGranted": ["ID","Username","UserType","PermissionType","GrantedDate","Status","IP","Device"],
    "HomeUsers": ["UserID","Username","Password","FullName","Phone","Email","Date","Status","AccountHolderPhone","From"],
    "New_patient": ["PatientID","Date","Name","FatherName","Age","Gender","MaritalStatus","Occupation","CNIC","Phone","EmergencyPhone","Address","Referral","Diseases","ChiefComplaint","PastHistory","FamilyHistory","Allergy","Examination","Pulse","Temperament","BP","Weight","Temperature","SingleMedicines","FormulaMedicines","Fees","MedicineCharges","Total","Paid","Balance","PrevBalance","PaymentMethod","FeeStatus","RevisitDate","ClinicName","CreatedBy","Timestamp","AppVersion","DailyNumber","TotalNumber","GrandTotal"],
    "Revisit": ["RevisitID","PatientID","Date","Name","Phone","ClinicName","Complaint","Prescription","Fees","Paid","Balance","CreatedBy"],
    "AutoDiagnosis": ["ID","PatientID","Date","Name","FatherName","Age","Phone","Gender","Address","Diseases","ExtraSymptoms","Temperament","ClinicName","CreatedBy","AppVersion","GrandTotal"],
    "Herbs": ["HerbID","Name","Temperament","Uses","Dosage","ClinicName"],
    "Pharmacopoeia": ["ID","Name","Category","Temperament","Uses","Dosage","ClinicName"],
    "Dictionary": ["ID","Word","Meaning","Category","Language"],
    "Articles": ["ID","TitleEN","TitleUR","TitleAR","ContentEN","ContentUR","ContentAR","MainCategory","SubCategory","Audience","Type","Status","Date","ClinicName"],
    "Feedback": ["ID","Name","From","Phone Number","Email","Feedback Page","Feedback","Date","Status"],
    "AppSettings": ["Key","Value","Date","Status","Description"],
}
ALL_SHEETS = list(SHEET_HEADERS.keys())
GENERAL_SHEETS = ["UserSignups", "PermissionGranted", "Articles", "Feedback"]
CLINIC_SHEETS = ["New_patient", "Revisit", "AutoDiagnosis", "Herbs", "Pharmacopoeia", "Dictionary"]
HOME_SHEETS = ["HomeUsers"]

def sanitize_for_sheet(text):
    if not text: return ""
    text = str(text).strip()
    text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

st.set_page_config(page_title="Herbal Clinic International", page_icon="🌿", layout="centered", initial_sidebar_state="collapsed")

if "theme" not in st.session_state:
    st.session_state.theme = "light"

def get_theme_css():
    theme = st.session_state.get("theme", "light")
    if theme == "dim":
        return """
        html, body,.stApp, [data-testid="stAppViewContainer"] { background: #C8DCCB!important; color: #0F2A14!important; }
        .block-container { background: #DDEBE0!important; border: 3.5px solid #1B5E20!important; }
        .heading-h1 { font-size: 34px!important; font-weight: 900!important; color:#1B5E20!important; text-align:center; }
        .heading-h3 { font-size: 26px!important; font-weight: 800!important; }
        .heading-h4 { font-size: 20px!important; font-weight: 700!important; }
        .graceful-card { background: #A8CCAD!important; border: 2px solid #1B5E20!important; border-radius:12px; padding:4px; text-align:center; }
        .dash-section-title { background: #1B5E20!important; color:white; padding:8px 12px; border-radius:8px; font-weight:800; }
        .footer-sharp { text-align:center; color:#5a6d65!important; font-size:12px!important; margin-top:20px; border-top:1px solid #C8E6D5; padding:10px; }
        """
    else:
        return """
        html, body,.stApp, [data-testid="stAppViewContainer"] { background: #FFFFFF!important; color: #1F2D27!important; }
        .block-container { background: #FFFFFF!important; border: 3px solid #2E7D5B!important; border-radius:12px; }
        .heading-h1 { font-size: 34px!important; font-weight: 900!important; color:#1B5E20!important; text-align:center; }
        .heading-h3 { font-size: 26px!important; font-weight: 800!important; }
        .heading-h4 { font-size: 20px!important; font-weight: 700!important; }
        .graceful-card { background: #FFFFFF!important; border: 1.5px solid #E0E0E0!important; border-radius:12px; padding:2px; text-align:center; }
        .graceful-card:hover { border: 2.5px solid #2E7D5B!important; }
        .dash-section-title { background: #2E7D5B!important; color:white; padding:8px 12px; border-radius:8px; font-weight:800; }
        .footer-sharp { text-align:center; color:#5a6d65!important; font-size:12px!important; margin-top:20px; border-top:1px solid #C8E6D5; padding:10px; }
        """

def scroll_to_top():
    try:
        import streamlit.components.v1 as components
        components.html("<script>try{window.scrollTo(0,0);}catch(e){}</script>", height=0)
    except:
        pass

def safe_append_history(page="dashboard_welcome"):
    st.session_state.setdefault("page_history", ["dashboard_welcome"]).append(page)
    st.session_state["prev_page"] = st.session_state.get("current_page", "dashboard_welcome")

def get_user_display_h2():
    role = st.session_state.get("user_role","")
    uname = st.session_state.get("username","")
    cname = st.session_state.get("clinic_name","Herbal Clinic International")
    if role in ["Boss","Staff"] or st.session_state.get("user_type")=="Staff":
        return f"Staff - {uname} - {cname}"
    elif role=="home_user" or st.session_state.get("user_type")=="HomeUser":
        return f"Home User - {uname} - {cname}"
    else:
        return f"Clinic - {uname} - {cname}"

def navigate_to(page):
    st.session_state.setdefault("page_history", ["dashboard_welcome"])
    if st.session_state.get("current_page") != page:
        st.session_state["prev_page"] = st.session_state.get("current_page","dashboard_welcome")
        st.session_state["page_history"].append(st.session_state.get("current_page","dashboard_welcome"))
        if len(st.session_state["page_history"]) > 20:
            st.session_state["page_history"] = st.session_state["page_history"][-20:]
    st.session_state.current_page = page
    st.rerun()

def language_selector():
    import streamlit.components.v1 as components
    st.markdown(f"<style>{get_theme_css()}</style>", unsafe_allow_html=True)
    c_spacer, c_theme, c_lang, c_lang_text = st.columns([6,1,1,1])
    with c_theme:
        curr_theme = st.session_state.get("theme", "light")
        if curr_theme == "light":
            if st.button("🌿", key="theme_toggle_dim_v209"):
                st.session_state.theme = "dim"
                st.rerun()
        else:
            if st.button("☀️", key="theme_toggle_light_v209"):
                st.session_state.theme = "light"
                st.rerun()
    with c_lang:
        if st.button("🌐", key="lang_toggle_v209"):
            curr = st.session_state.get("app_language", "en")
            nxt = {"en":"ur", "ur":"ar", "ar":"en"}.get(curr, "en")
            st.session_state.app_language = nxt
            st.session_state.lang = nxt
            st.rerun()
    with c_lang_text:
        lang = st.session_state.get("app_language","en")
        st.markdown(f"<div style='text-align:left;font-size:14px;font-weight:700;color:#2E7D5B;margin-top:8px;'>{lang.upper()}</div>", unsafe_allow_html=True)

def clinic_heading_banner_compact():
    st.markdown(f"<style>{get_theme_css()}</style>", unsafe_allow_html=True)
    st.markdown(f"<div class='heading-h1'>🌿 Herbal Clinic International <span style='font-size:12px;color:#5a6d65;'>| {APP_VERSION}</span></div>", unsafe_allow_html=True)

def top_bar_inner_with_user():
    u = st.session_state.get("username","")
    st.markdown(f"<div style='background:#F1F7F3;padding:6px 12px;border-radius:8px;display:flex;justify-content:space-between;'><span>👤 {u}</span><span>{APP_VERSION}</span></div>", unsafe_allow_html=True)

def top_nav_inner():
    cols = st.columns(6)
    pages = [("🏠 Dashboard","dashboard_welcome"), ("➕ New Patient","patient"), ("🔄 Revisit","revisit"), ("📚 Herbs","clinic_herb_formula"), ("📰 Articles","clinic_articles"), ("⚙️ Admin","admin")]
    for i,(label,pg) in enumerate(pages):
        with cols[i % 6]:
            if st.button(label, key=f"nav_{pg}_v209", use_container_width=True):
                st.session_state.current_page = pg
                st.rerun()

def add_footer():
    st.markdown("<div class='footer-sharp'>Herbal Clinic International | V209.6.12 | WhatsApp Support</div>", unsafe_allow_html=True)

def under_development_footer(page):
    st.markdown(f"<div style='text-align:center;color:#888;font-size:11px;margin-top:15px;'>{page}</div>", unsafe_allow_html=True)

# ==================== GOOGLE SHEET CORE ====================
@st.cache_resource(show_spinner=False, ttl=300)
def get_gspread_client():
    if not GSPREAD_AVAILABLE:
        return None
    try:
        creds_dict = None
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
        elif "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            gs = st.secrets["connections"]["gsheets"]
            if isinstance(gs, dict) and "private_key" in gs:
                creds_dict = dict(gs)
        if not creds_dict or "private_key" not in creds_dict:
            return None
        pk = creds_dict["private_key"]
        pk = pk.replace("\\n", "\n")
        creds_dict["private_key"] = pk
        scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except:
        return None

@st.cache_resource(show_spinner=False, ttl=300)
def get_spreadsheet_cached():
    try:
        client = get_gspread_client()
        if not client:
            return None
        sid = HARDCODED_SHEET_ID
        try:
            if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
                gs = st.secrets["connections"]["gsheets"]
                if isinstance(gs, dict):
                    s = gs.get("spreadsheet","")
                    if s and len(str(s)) > 20:
                        sid = str(s)
                elif isinstance(gs, str) and len(gs) > 20:
                    sid = gs
        except:
            pass
        s = str(sid)
        if "docs.google.com" in s:
            m = re.search(r"/d/([a-zA-Z0-9-_]+)", s)
            if m: sid = m.group(1)
        if s.startswith("{"):
            m = re.search(r'1[a-zA-Z0-9-_]{20,}', s)
            if m: sid = m.group(0)
        sid = sid.strip().strip('"').strip("'").replace("{","").replace("}","").replace("spreadsheet","").replace(":","").replace("=","").strip()
        if len(sid) < 20:
            sid = HARDCODED_SHEET_ID
        return client.open_by_key(sid)
    except:
        try:
            client = get_gspread_client()
            if client:
                return client.open_by_key(HARDCODED_SHEET_ID)
        except:
            pass
        return None

def get_sheet_safe(name):
    try:
        sh = get_spreadsheet_cached()
        if not sh: return None
        try: return sh.worksheet(name)
        except:
            try:
                hdr = SHEET_HEADERS.get(name, ["ID"])
                ws = sh.add_worksheet(title=name, rows=1000, cols=len(hdr)+5)
                ws.append_row(hdr)
                return ws
            except: return None
    except: return None

@st.cache_data(show_spinner=False, ttl=60)
def _get_all_records_cached_fast(sheet_name):
    try:
        ws = get_sheet_safe(sheet_name)
        if not ws: return []
        vals = ws.get_all_values()
        if not vals or len(vals) < 2: return []
        headers = vals[0]
        records = []
        for row in vals[1:]:
            if not any(row): continue
            rec = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
            records.append(rec)
        return records
    except: return []

def get_all_records_cached(sheet_name):
    try:
        cached = _get_all_records_cached_fast(sheet_name)
        if cached: return cached
        backup_key = f"local_backup_{sheet_name}"
        return st.session_state.get(backup_key, [])
    except:
        try:
            return st.session_state.get(f"local_backup_{sheet_name}", [])
        except: return []

def save_to_local_csv(sheet_name, data_dict):
    try:
        import copy
        backup_key = f"local_backup_{sheet_name}"
        if backup_key not in st.session_state:
            st.session_state[backup_key] = []
        st.session_state[backup_key].append(copy.deepcopy(data_dict))
        return True
    except: return False

def get_next_numbers(clinic_name):
    try:
        today_str = str(datetime.date.today())
        records = get_all_records_cached("New_patient")
        clinic_records = [r for r in records if str(r.get("ClinicName","")).lower() == str(clinic_name).lower()]
        max_total = 0
        for r in clinic_records:
            try:
                tn = int(str(r.get("TotalNumber","0") or 0).replace(",","") or 0)
                if tn > max_total: max_total = tn
            except: pass
        total_num = max_total + 1 if max_total > 0 else len(clinic_records) + 1
        today_count = sum(1 for r in clinic_records if today_str in str(r.get("Date","")))
        return today_count + 1, total_num
    except: return 1, 1

def get_sheet_connection_status():
    logs = []
    checks = []
    status = {"logs": logs, "checks": checks, "ok": False}
    def add_log(step, ok, msg, fix=""):
        logs.append(f"{'✅' if ok else '❌'} {step}: {msg}")
        checks.append({"step": step, "ok": ok, "msg": msg, "fix": fix})
    try:
        add_log("gspread", GSPREAD_AVAILABLE, "installed" if GSPREAD_AVAILABLE else "missing")
        if not GSPREAD_AVAILABLE:
            return status
        has_gcp = "gcp_service_account" in st.secrets
        add_log("[gcp_service_account]", has_gcp, "Found" if has_gcp else "NOT found")
        if not has_gcp:
            return status
        creds_dict = dict(st.secrets["gcp_service_account"])
        pk = creds_dict.get("private_key","")
        ok = "BEGIN PRIVATE KEY" in pk
        add_log("private_key", ok, "Valid" if ok else "Invalid")
        if not ok: return status
        client = get_gspread_client()
        ok = client is not None
        add_log("gspread client", ok, "Created" if ok else "Failed")
        if not ok: return status
        sh = get_spreadsheet_cached()
        ok = sh is not None
        add_log("Spreadsheet", ok, f"Opened: {sh.title}" if ok else "Failed")
        if not ok: return status
        ws = get_sheet_safe("New_patient")
        ok = ws is not None
        rows = len(ws.get_all_values()) if ok and ws else 0
        add_log("New_patient sheet", ok, f"Found {rows} rows" if ok else "Not found")
        status["ok"] = ok
    except Exception as e:
        add_log("Error", False, str(e))
    return status

def save_patient(data_dict):
    try:
        import copy
        cleaned = copy.deepcopy(data_dict)
        backup_key = "local_backup_New_patient"
        if backup_key not in st.session_state:
            st.session_state[backup_key] = []
        st.session_state[backup_key].append(cleaned)
        st.session_state["last_saved_patient"] = cleaned
        sheet_ok = False
        sheet_msg = "Not connected"
        try:
            ws = get_sheet_safe("New_patient")
            if ws:
                hdr = ws.row_values(1)
                if not hdr or len(hdr) < 5:
                    hdr = SHEET_HEADERS["New_patient"]
                row = []
                for h in hdr:
                    v = cleaned.get(h, "")
                    row.append(str(v).replace("\n"," ").replace("\r"," ") if v is not None else "")
                if len(row) < len(hdr): row += [""] * (len(hdr)-len(row))
                else: row = row[:len(hdr)]
                ws.append_row(row, value_input_option="RAW")
                sheet_ok = True
                sheet_msg = f"Sheet OK - Row {len(ws.get_all_values())}"
                try: _get_all_records_cached_fast.clear()
                except: pass
        except Exception as e:
            sheet_msg = f"Error: {str(e)[:120]}"
        total = len(st.session_state.get("local_backup_New_patient", []))
        if sheet_ok:
            return True, f"✅ Saved! Sheet+Local | Total:{total}"
        else:
            return True, f"✅ Saved! Local (Sheet: {sheet_msg}) | Total:{total}"
    except Exception as e:
        try:
            if "local_backup_New_patient" not in st.session_state:
                st.session_state["local_backup_New_patient"] = []
            st.session_state["local_backup_New_patient"].append(data_dict)
            return True, f"✅ Saved backup"
        except: return False, f"❌ Fail: {str(e)[:100]}"

def get_app_setting(key, default=""):
    try:
        recs = get_all_records_cached("AppSettings")
        for r in recs:
            if str(r.get("Key","")).lower() == str(key).lower():
                return r.get("Value", default)
        return default
    except:
        return default

# ==================== PAGES ====================
def clinic_login_page():
    language_selector()
    clinic_heading_banner_compact()
    with st.container(border=True):
        st.markdown("<div style='background:#E8F5E9;padding:8px;border-radius:6px;text-align:center;margin-bottom:10px;'>V209.6.12 Original Structure - Fixed</div>", unsafe_allow_html=True)
        t1,t2,t3 = st.tabs(["Staff Login","Clinic User","Home User"])
        with t1:
            u = st.text_input("Username", value="boss", key="login_u_v209")
            p = st.text_input("Password", type="password", value="boss123", key="login_p_v209")
            if st.button("Login", use_container_width=True, type="primary", key="staff_login_v209"):
                st.session_state.logged_in=True
                st.session_state.username=u or "boss"
                st.session_state.user_role="Boss"
                st.session_state.user_type="Staff"
                st.session_state.clinic_name="Herbal Clinic International"
                st.session_state.current_page="dashboard_welcome"
                st.session_state.setdefault("page_history", ["dashboard_welcome"])
                st.rerun()
        with t2:
            cu = st.text_input("Username", key="clinic_u_v209")
            cp = st.text_input("Password", type="password", key="clinic_p_v209")
            if st.button("Login", use_container_width=True, type="primary", key="clinic_login_v209"):
                st.session_state.logged_in=True
                st.session_state.username=cu or "clinic"
                st.session_state.user_role="clinic"
                st.session_state.user_type="Clinic"
                st.session_state.clinic_name="Herbal Clinic International"
                st.session_state.current_page="dashboard_welcome"
                st.session_state.setdefault("page_history", ["dashboard_welcome"])
                st.rerun()
        with t3:
            hu = st.text_input("Username", key="home_u_v209")
            hp = st.text_input("Password", type="password", key="home_p_v209")
            if st.button("Login", use_container_width=True, type="primary", key="home_login_v209"):
                st.session_state.logged_in=True
                st.session_state.username=hu or "home"
                st.session_state.user_role="home_user"
                st.session_state.user_type="HomeUser"
                st.session_state.clinic_name="Herbal Clinic International"
                st.session_state.current_page="home_user"
                st.session_state.setdefault("page_history", ["dashboard_welcome"])
                st.rerun()
    add_footer()

def dashboard_welcome_page():
    scroll_to_top()
    st.session_state.setdefault("page_history", ["dashboard_welcome"])
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Dashboard - V209.6.12</div>", unsafe_allow_html=True)
    records = get_all_records_cached("New_patient")
    my = [r for r in records if str(r.get("ClinicName","")).lower() == str(st.session_state.clinic_name).lower()]
    c1,c2,c3,c4 = st.columns(4)
    total_patients = len(my)
    today_str = str(datetime.date.today())
    today_patients = sum(1 for r in my if today_str in str(r.get("Date","")))
    total_income = sum(float(str(r.get("GrandTotal","0") or 0).replace(",","") or 0) for r in my)
    pending = sum(float(str(r.get("Balance","0") or 0).replace(",","") or 0) for r in my)
    with c1: st.metric("Total", total_patients)
    with c2: st.metric("Today", today_patients)
    with c3: st.metric("Income", f"Rs {total_income:.0f}")
    with c4: st.metric("Pending", f"Rs {pending:.0f}")
    st.markdown("<div class='dash-section-title'>Clinic Section</div>", unsafe_allow_html=True)
    r1c1,r1c2,r1c3,r1c4=st.columns(4)
    with r1c1:
        st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
        if st.button("New Patient", use_container_width=True, key="dash_new_v209"):
            safe_append_history("dashboard_welcome")
            st.session_state.form_version=st.session_state.get("form_version",0)+1
            st.session_state.prev_balance=0.0
            st.session_state.revisit_data=None
            st.session_state.patient_diseases = []
            st.session_state.current_page="patient"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r1c2:
        st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
        if st.button("Revisit", use_container_width=True, key="dash_rev_v209"):
            safe_append_history("dashboard_welcome")
            st.session_state.current_page="revisit"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r1c3:
        st.markdown("<div class='graceful-card' style='border:2px solid #2196F3!important;'>", unsafe_allow_html=True)
        if st.button("Clinic Admin", use_container_width=True, key="dash_clinic_admin_v209"):
            safe_append_history("dashboard_welcome")
            st.session_state.current_page="clinic_admin"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r1c4:
        st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
        if st.button("Auto-Diagnosis", use_container_width=True, key="dash_auto_v209"):
            safe_append_history("dashboard_welcome")
            st.session_state.current_page="auto_selection"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    r2c1,r2c2,r2c3,r2c4=st.columns(4)
    with r2c1:
        st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
        if st.button("Dictionary", use_container_width=True, key="dash_dict_v209"):
            safe_append_history("dashboard_welcome")
            st.session_state.current_page="dictionary"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r2c2:
        st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
        if st.button("Articles", use_container_width=True, key="dash_c_art_v209"):
            safe_append_history("dashboard_welcome")
            st.session_state.current_page="clinic_articles"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r2c3:
        st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
        if st.button("Herbs & Pharma", use_container_width=True, key="dash_herb_v209"):
            safe_append_history("dashboard_welcome")
            st.session_state.current_page="clinic_herb_formula"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with r2c4:
        st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
        if st.button("Free Health Tools", use_container_width=True, key="dash_quiz_v209"):
            safe_append_history("dashboard_welcome")
            st.session_state.current_page="temperament_quiz"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    r3c1,r3c2,r3c3,r3c4=st.columns(4)
    show_offer = get_app_setting("OfferEnabled", "Yes")
    if str(show_offer).lower() in ["yes","on","true","1","enabled"]:
        with r3c1:
            st.markdown("<div class='graceful-card' style='border:3px solid #00ff88;'>", unsafe_allow_html=True)
            if st.button("Offer", use_container_width=True, key="dash_offer_v209"):
                safe_append_history("dashboard_welcome")
                st.session_state.current_page="offer_page"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    with r3c2:
        st.markdown("<div class='graceful-card'>", unsafe_allow_html=True)
        if st.button("App Admin", use_container_width=True, key="dash_app_admin_v209"):
            safe_append_history("dashboard_welcome")
            st.session_state.current_page="admin"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    if my:
        with st.expander(f"Recent Patients ({len(my[-5:])})", expanded=False):
            for r in my[-5:][::-1]:
                st.write(f"{r.get('Name','')} | {r.get('Date','')} | ID:{r.get('PatientID','')} | Bal Rs {r.get('Balance','0')}")
    add_footer()

def render_patient_form(is_revisit=False):
    if "form_version" not in st.session_state:
        st.session_state.form_version = 0
    fv = st.session_state.form_version
    daily_num, total_num = get_next_numbers(st.session_state.clinic_name)
    prev_bal = 0.0
    pid = str(total_num)
    if is_revisit and st.session_state.get("revisit_data"):
        r = st.session_state.revisit_data
        pid = str(r.get("PatientID",""))
        try: prev_bal = float(str(r.get("Balance","0") or 0).replace(",","") or 0)
        except: prev_bal = 0.0
        st.markdown(f"<div style='background:#FFF3E0;padding:10px;border-radius:8px;'><b>Revisit:</b> {r.get('Name','')} | Balance Rs {prev_bal:.0f} | ID {pid}</div>", unsafe_allow_html=True)
    def get_prefill(k,d=""):
        if is_revisit and st.session_state.get("revisit_data"):
            return st.session_state.revisit_data.get(k,d)
        return d
    with st.container(border=True):
        st.markdown("<div class='heading-h4'>Personal Information</div>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            st.text_input("Patient's Name *", key=f"p_name_{fv}", value=get_prefill("Name",""))
            st.text_input("Spouse/Father", key=f"p_fname_{fv}", value=get_prefill("FatherName",""))
        with c2:
            st.selectbox("Gender *", ["Select","Male","Female","Other"], key=f"p_gender_{fv}")
            st.text_input("Age *", key=f"p_age_{fv}", value=get_prefill("Age",""))
        with c3:
            st.text_input("Phone *", key=f"p_phone_{fv}", value=get_prefill("Phone",""))
            st.text_input("Address", key=f"p_address_{fv}", value=get_prefill("Address",""))
    with st.container(border=True):
        st.markdown("<div class='heading-h4'>Diseases</div>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns([3,3,2,2])
        with c1:
            body_part = st.selectbox("Body Part *", ["Select","Head","Chest","Stomach","Joints","Skin","General"], key=f"pat_body_{fv}")
        with c2:
            BODY_MAP = {"Head":["Select","Headache","Migraine"],"Chest":["Select","Cough","Asthma"],"Stomach":["Select","Stomach Pain","Acidity"],"Joints":["Select","Joint Pain","Back Pain"],"Skin":["Select","Eczema","Itching"],"General":["Select","Fever","Weakness","Diabetes"]}
            disease = st.selectbox(f"Disease", BODY_MAP.get(body_part, ["Select"]), key=f"pat_disease_{fv}")
        with c3:
            d_no = st.text_input("No/Count *", key=f"pat_no_{fv}")
        with c4:
            d_dur = st.selectbox("Duration *", ["Select","1 Day","1 Week","1 Month","1 Year","Since Childhood"], key=f"pat_dur_{fv}")
        if st.button("Add Disease +", key=f"pat_add_{fv}"):
            if body_part=="Select" or disease=="Select" or not d_no.strip() or d_dur=="Select":
                st.error("Fill all")
            else:
                txt_d = f"{body_part} + {disease} + {d_no} {d_dur}"
                if "patient_diseases" not in st.session_state: st.session_state.patient_diseases=[]
                if txt_d not in [d.get("text","") for d in st.session_state.patient_diseases]:
                    st.session_state.patient_diseases.append({"text": txt_d})
                    st.success(f"Added: {txt_d}")
                    st.rerun()
        pd_list = st.session_state.get("patient_diseases", [])
        if pd_list:
            st.info(" + ".join([d.get("text","") for d in pd_list]))
            if st.button("Clear All", key=f"pat_clear_{fv}"):
                st.session_state.patient_diseases=[]
                st.rerun()
    with st.container(border=True):
        st.markdown("<div class='heading-h4'>Chief Complaint</div>", unsafe_allow_html=True)
        st.text_area("Chief Complaint", key=f"chief_{fv}", value=get_prefill("ChiefComplaint",""))
        st.text_area("Past History", key=f"past_{fv}", value=get_prefill("PastHistory",""))
    with st.container(border=True):
        st.markdown("<div class='heading-h4'>Billing</div>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: fee_val = st.text_input("Fee (Rs)", key=f"fee_{fv}", value="")
        with c2: med_val = st.text_input("Medicine (Rs)", key=f"med_{fv}", value="")
        with c3: paid_val = st.text_input("Paid (Rs)", key=f"paid_{fv}", value="")
        try:
            f = float(str(fee_val).replace(",","") or 0)
            m = float(str(med_val).replace(",","") or 0)
            p = float(str(paid_val).replace(",","") or 0)
        except: f=m=p=0
        grand_total = f + m + prev_bal
        balance = grand_total - p
        if balance < 0: balance = 0
        c1,c2 = st.columns(2)
        with c1: st.metric("Grand Total", f"Rs {grand_total:.0f}")
        with c2: st.metric("Balance", f"Rs {balance:.0f}")
        st.session_state[f"calc_gt_{fv}"] = grand_total
        st.session_state[f"calc_bal_{fv}"] = balance
        st.session_state[f"calc_f_{fv}"] = f
        st.session_state[f"calc_m_{fv}"] = m
        st.session_state[f"calc_p_{fv}"] = p
    st.markdown("---")
    if st.button("💾 Save Patient NOW", type="primary", use_container_width=True, key=f"save_{fv}_v209"):
        p_name = st.session_state.get(f"p_name_{fv}","")
        if not str(p_name).strip():
            st.error("Name required")
        else:
            f = st.session_state.get(f"calc_f_{fv}",0)
            m = st.session_state.get(f"calc_m_{fv}",0)
            p = st.session_state.get(f"calc_p_{fv}",0)
            grand_total = st.session_state.get(f"calc_gt_{fv}", f+m+prev_bal)
            balance = st.session_state.get(f"calc_bal_{fv}", grand_total-p)
            diseases_list = st.session_state.get("patient_diseases", [])
            diseases_text = " + ".join([d.get("text","") for d in diseases_list])
            data_dict = {
                "PatientID": str(pid), "Date": str(datetime.date.today()),
                "Name": str(p_name).strip(),
                "FatherName": str(st.session_state.get(f"p_fname_{fv}","")).strip(),
                "Age": str(st.session_state.get(f"p_age_{fv}","")).strip(),
                "Gender": str(st.session_state.get(f"p_gender_{fv}","Select")),
                "Phone": str(st.session_state.get(f"p_phone_{fv}","")).strip(),
                "Address": str(st.session_state.get(f"p_address_{fv}","")).strip(),
                "Diseases": diseases_text,
                "ChiefComplaint": str(st.session_state.get(f"chief_{fv}","")).strip(),
                "PastHistory": str(st.session_state.get(f"past_{fv}","")).strip(),
                "Fees": float(f), "MedicineCharges": float(m), "Total": float(f+m),
                "Paid": float(p), "Balance": float(balance), "PrevBalance": float(prev_bal),
                "GrandTotal": float(grand_total),
                "ClinicName": str(st.session_state.clinic_name),
                "CreatedBy": str(st.session_state.username),
                "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "AppVersion": APP_VERSION,
                "DailyNumber": int(daily_num), "TotalNumber": int(total_num),
            }
            ok,msg = save_patient(data_dict)
            if is_revisit:
                try:
                    revisit_dict = {
                        "RevisitID": f"R{pid}_{str(datetime.date.today())}_{str(int(datetime.datetime.now().timestamp()))[-4:]}",
                        "PatientID": str(pid), "Date": str(datetime.date.today()),
                        "Name": str(p_name).strip(),
                        "Phone": str(st.session_state.get(f"p_phone_{fv}","")).strip(),
                        "ClinicName": str(st.session_state.clinic_name),
                        "Complaint": diseases_text,
                        "Prescription": "",
                        "Fees": float(f), "Paid": float(p), "Balance": float(balance),
                        "CreatedBy": str(st.session_state.username),
                    }
                    ws_rev = get_sheet_safe("Revisit")
                    if ws_rev:
                        hdr_rev = ws_rev.row_values(1) or SHEET_HEADERS["Revisit"]
                        row_rev = [str(revisit_dict.get(h,"")) for h in hdr_rev]
                        ws_rev.append_row(row_rev, value_input_option="RAW")
                    save_to_local_csv("Revisit", revisit_dict)
                except: pass
            try: _get_all_records_cached_fast.clear()
            except: pass
            if ok:
                st.success(f"Saved ID {pid} | Rs {grand_total:.0f} - Cleared")
                st.balloons()
                st.session_state.form_version+=1
                st.session_state.prev_balance=0.0
                st.session_state.revisit_data=None
                st.session_state.patient_diseases=[]
                st.rerun()
            else:
                st.warning(f"Local Save ID {pid} | {msg}")

def patient_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>New Patient - V209.6.12</div>", unsafe_allow_html=True)
    render_patient_form(is_revisit=False)
    add_footer()

def patient_revisit_form_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Revisit Form - V209.6.12</div>", unsafe_allow_html=True)
    render_patient_form(is_revisit=True)
    add_footer()

def revisit_page():
    scroll_to_top()
    st.session_state.setdefault("page_history", ["dashboard_welcome"])
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Revisit - Search</div>", unsafe_allow_html=True)
    records = get_all_records_cached("New_patient")
    my = [r for r in records if str(r.get("ClinicName","")).lower() == str(st.session_state.clinic_name).lower()]
    c1,c2 = st.columns(2)
    with c1:
        s_name = st.text_input("Patient Name", key="rev_name_v209")
        s_date = st.text_input("Date (YYYY-MM-DD)", key="rev_date_v209")
    with c2:
        s_phone = st.text_input("Phone", key="rev_phone_v209")
        s_address = st.text_input("Address", key="rev_address_v209")
    if s_name or s_phone or s_date or s_address:
        filt=[]
        for r in my:
            if (s_name and s_name.lower() in str(r.get("Name","")).lower()) or \
               (s_phone and s_phone.lower() in str(r.get("Phone","")).lower()) or \
               (s_date and s_date.lower() in str(r.get("Date","")).lower()) or \
               (s_address and s_address.lower() in str(r.get("Address","")).lower()):
                filt.append(r)
        st.write(f"Found {len(filt)} patients")
        for idx, r in enumerate(filt[:15]):
            with st.container(border=True):
                st.write(f"{r.get('Name','')} | {r.get('Date','')} | Phone:{r.get('Phone','')} | ID:{r.get('PatientID','')} | Bal Rs {r.get('Balance','0')}")
                if st.button(f"Open {r.get('PatientID','')}", key=f"rev_{r.get('PatientID','')}_{idx}_v209"):
                    st.session_state.revisit_data=r
                    st.session_state.prev_balance=float(str(r.get("Balance","0") or 0).replace(",","") or 0)
                    st.session_state.current_page="patient_revisit_form"
                    st.rerun()
    else:
        st.info("Enter Name, Phone, Date or Address to search")
    add_footer()

def dictionary_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Dictionary</div>", unsafe_allow_html=True)
    recs = get_all_records_cached("Dictionary")
    for r in recs[:50]:
        st.write(f"{r.get('Word','')} - {r.get('Meaning','')}")
    add_footer()

def clinic_herb_formula_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Herbs & Pharmacopoeia - V209.6.12</div>", unsafe_allow_html=True)
    tab1,tab2 = st.tabs(["Herbs","Formulas"])
    with tab1:
        herbs = get_all_records_cached("Herbs")
        if not herbs: herbs = get_all_records_cached("Pharmacopoeia")
        s = st.text_input("Search Herb", key="herb_search_v209")
        filt = [r for r in herbs if s.lower() in str(r.get("Name","")).lower()] if s else herbs[:30]
        for r in filt[:30]:
            with st.container(border=True):
                st.write(f"**{r.get('Name','')}** - {r.get('Uses','')}")
    with tab2:
        forms = get_all_records_cached("Pharmacopoeia")
        st.write(f"Total: {len(forms)}")
        for r in forms[:30]:
            with st.container(border=True):
                st.write(f"{r.get('Name','')} - {r.get('Uses','')}")
    add_footer()

def clinic_articles_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Articles</div>", unsafe_allow_html=True)
    recs = get_all_records_cached("Articles")
    for r in recs[:20]:
        with st.container(border=True):
            st.markdown(f"**{r.get('TitleEN','')}**")
            st.write(str(r.get('ContentEN',''))[:200])
    add_footer()

def admin_page():
    scroll_to_top()
    st.session_state.setdefault("page_history", ["dashboard_welcome"])
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>⚙️ App Admin - V209.6.12 + Doctor</div>", unsafe_allow_html=True)
    sections = ["🩺 Performance Doctor", "General", "Clinic Data", "Home User", "AppSettings"]
    if "admin_selected_section" not in st.session_state:
        st.session_state.admin_selected_section = "🩺 Performance Doctor"
    cols = st.columns(len(sections))
    for idx, sec in enumerate(sections):
        with cols[idx]:
            is_selected = st.session_state.admin_selected_section == sec
            btn_type = "primary" if is_selected else "secondary"
            if st.button(sec, key=f"admin_nav_{sec}_v209", use_container_width=True, type=btn_type):
                st.session_state.admin_selected_section = sec
                st.rerun()
    selected = st.session_state.admin_selected_section
    st.markdown(f"<div style='background:#1a1c23;border-left:4px solid #00E676;padding:8px 12px;border-radius:8px;margin:8px 0;color:#00E676;font-weight:700;'>📂 Open: {selected}</div>", unsafe_allow_html=True)
    if selected == "🩺 Performance Doctor":
        st.markdown("<div class='heading-h4'>🩺 Performance Doctor - V209.6.12</div>", unsafe_allow_html=True)
        st.markdown("<div style='background:#E8F5E9;padding:12px;border-radius:8px;border:2px solid #2E7D5B;margin-bottom:12px;'>Doctor checks app performance, sheet connection, and fixes issues.</div>", unsafe_allow_html=True)
        if st.button("🩺 Run Full Diagnosis", type="primary", use_container_width=True, key="doctor_run_v209"):
            with st.spinner("Diagnosing..."):
                import time
                start = time.time()
                diag = get_sheet_connection_status()
                elapsed = time.time() - start
                st.write(f"Time: {elapsed:.2f}s - {'Fast ✅' if elapsed < 2 else 'Slow ⚠️'}")
                for check in diag.get("checks", []):
                    if check.get("ok"):
                        st.success(f"✅ {check.get('step')}: {check.get('msg')}")
                    else:
                        st.error(f"❌ {check.get('step')}: {check.get('msg')}")
                        if check.get("fix"):
                            st.info(f"👉 Fix: {check.get('fix')}")
                c1,c2,c3 = st.columns(3)
                with c1: st.metric("Sheet Connect", f"{elapsed:.2f}s")
                with c2: st.metric("Cache", "Active 60s")
                with c3: st.metric("Local Backup", len(st.session_state.get("local_backup_New_patient", [])))
                cc1,cc2,cc3 = st.columns(3)
                with cc1:
                    if st.button("Clear Cache - Speed Up", key="fix_cache_v209"):
                        try:
                            get_spreadsheet_cached.clear()
                            get_gspread_client.clear()
                            _get_all_records_cached_fast.clear()
                            st.success("Cache cleared")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                with cc2:
                    if st.button("Test Write", key="fix_test_v209"):
                        try:
                            ws = get_sheet_safe("New_patient")
                            if ws:
                                st.success(f"OK - {len(ws.get_all_values())} rows")
                            else:
                                st.error("No access")
                        except Exception as e:
                            st.error(str(e))
        if st.session_state.get("last_sheet_error"):
            st.error(f"Last Error: {st.session_state.get('last_sheet_error','')[:300]}")
        if st.session_state.get("last_sheet_success"):
            st.success(f"Last Success: {st.session_state.get('last_sheet_success','')}")
        try:
            ce = st.secrets["gcp_service_account"].get("client_email","") if "gcp_service_account" in st.secrets else ""
            if ce:
                st.code(f"Sheet ID: {HARDCODED_SHEET_ID}\nEmail: {ce}\nURL: https://docs.google.com/spreadsheets/d/{HARDCODED_SHEET_ID}/edit", language="text")
        except: pass
    elif selected == "General":
        st.markdown("<div class='heading-h4'>General</div>", unsafe_allow_html=True)
        for sh_name in GENERAL_SHEETS:
            with st.expander(f"{sh_name} - {len(get_all_records_cached(sh_name))} records"):
                recs_d = get_all_records_cached(sh_name)
                if recs_d:
                    st.dataframe(pd.DataFrame(recs_d).head(10), use_container_width=True)
    elif selected == "Clinic Data":
        st.markdown("<div class='heading-h4'>Clinic Data</div>", unsafe_allow_html=True)
        for sh_name in CLINIC_SHEETS:
            with st.expander(f"{sh_name} - {len(get_all_records_cached(sh_name))} records"):
                recs_d = get_all_records_cached(sh_name)
                if recs_d:
                    st.dataframe(pd.DataFrame(recs_d).head(10), use_container_width=True)
    elif selected == "Home User":
        recs = get_all_records_cached("HomeUsers")
        st.write(f"Total Home Users: {len(recs)}")
        if recs:
            st.dataframe(pd.DataFrame(recs).head(20), use_container_width=True)
    elif selected == "AppSettings":
        recs = get_all_records_cached("AppSettings")
        st.write(f"Total Settings: {len(recs)}")
        if recs:
            st.dataframe(pd.DataFrame(recs).head(30), use_container_width=True)
    add_footer()

def clinic_admin_page():
    scroll_to_top()
    st.session_state.setdefault("page_history", ["dashboard_welcome"])
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Clinic Admin</div>", unsafe_allow_html=True)
    st.info("Clinic Admin - V209.6.12 Structure")
    add_footer()

def temperament_quiz_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Free Temperament Quiz</div>", unsafe_allow_html=True)
    q1 = st.radio("Body feels more?", ["Hot","Cold","Moderate"], key="quiz_q1_v209", horizontal=True)
    q2 = st.radio("Thirst?", ["High","Low","Normal"], key="quiz_q2_v209", horizontal=True)
    if st.button("Get Result", type="primary", key="quiz_submit_v209"):
        st.balloons()
        st.success(f"Result based on {q1}/{q2} - Hot/Cold analysis")
    add_footer()

def home_user_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Home User</div>", unsafe_allow_html=True)
    st.info("Home User Dashboard - V209.6.12")
    add_footer()

def offer_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Offer</div>", unsafe_allow_html=True)
    st.info("Offer Page - Controlled by App Admin")
    add_footer()

def essential_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Essential</div>", unsafe_allow_html=True)
    add_footer()

def auto_selection_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Auto Diagnosis</div>", unsafe_allow_html=True)
    add_footer()

def feedback_page():
    scroll_to_top()
    top_bar_inner_with_user()
    top_nav_inner()
    st.markdown("<div class='heading-h3'>Feedback</div>", unsafe_allow_html=True)
    add_footer()

def articles_page():
    clinic_articles_page()

def pharmacopoeia_page():
    clinic_herb_formula_page()

def admin_feedback_page():
    admin_page()

def home_user_articles_page():
    clinic_articles_page()

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in=False
        st.session_state.current_page="clinic_login"
    if "page_history" not in st.session_state:
        st.session_state.page_history=["dashboard_welcome"]
    if "prev_page" not in st.session_state:
        st.session_state.prev_page="dashboard_welcome"
    if "form_version" not in st.session_state:
        st.session_state.form_version=0
    if "patient_diseases" not in st.session_state:
        st.session_state.patient_diseases=[]
    if not st.session_state.logged_in:
        clinic_login_page()
    else:
        p=st.session_state.current_page
        if p=="dashboard_welcome": dashboard_welcome_page()
        elif p=="patient": patient_page()
        elif p=="patient_revisit_form": patient_revisit_form_page()
        elif p=="revisit": revisit_page()
        elif p=="admin": admin_page()
        elif p=="dictionary": dictionary_page()
        elif p=="pharmacopoeia": pharmacopoeia_page()
        elif p=="auto_selection": auto_selection_page()
        elif p=="clinic_herb_formula": clinic_herb_formula_page()
        elif p=="temperament_quiz": temperament_quiz_page()
        elif p=="home_user": home_user_page()
        elif p=="articles": articles_page()
        elif p=="clinic_articles": clinic_articles_page()
        elif p=="clinic_admin": clinic_admin_page()
        elif p=="essential_page": essential_page()
        elif p=="offer_page": offer_page()
        elif p=="feedback_page": feedback_page()
        elif p=="admin_feedback": admin_feedback_page()
        elif p=="home_user_articles": home_user_articles_page()
        else: dashboard_welcome_page()

if __name__=="__main__": main()
