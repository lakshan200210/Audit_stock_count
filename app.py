import streamlit as st
import pandas as pd
import psycopg2
import psycopg2.extras
import hashlib
import io
import json
import base64
from datetime import datetime

st.set_page_config(
    page_title="Stock Count Pro",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
.stApp,section[data-testid="stMain"],div[data-testid="stAppViewContainer"],
div[data-testid="stMainBlockContainer"],div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"],div[data-testid="column"],
div[data-testid="stMarkdownContainer"],div[data-testid="stForm"],
div[data-testid="stWidgetLabel"],div[data-testid="stCaptionContainer"],
div[data-testid="stNumberInput"]>div,div[data-testid="stTextInput"]>div,
div[data-testid="stSelectbox"]>div,div[data-baseweb="tab-panel"],
div[data-baseweb="form-control-label"],div[data-baseweb="block"],
div[data-baseweb="card"],div.stTabs,div[data-testid="stTabsContent"]{
    background:transparent!important;box-shadow:none!important;border:none!important;}
html,body{color-scheme:light!important;}
.stApp{background-color:#F4F6FA!important;font-family:'DM Sans',sans-serif!important;color:#0D1B2A!important;}
.stApp *{color:#0D1B2A!important;}
.app-header *{color:#ffffff!important;}
.app-header .brand span{color:#5BC4FF!important;}
html,body,section[data-testid="stMain"],div[data-testid="stAppViewContainer"]{background-color:#F4F6FA!important;}
input,textarea,select{color:#0D1B2A!important;background-color:#F8FAFC!important;-webkit-text-fill-color:#0D1B2A!important;}
input::placeholder,textarea::placeholder{color:#A0AEC0!important;-webkit-text-fill-color:#A0AEC0!important;opacity:1!important;}
[data-baseweb="select"]*{color:#0D1B2A!important;}
[data-baseweb="menu"]{background-color:#fff!important;}
[data-baseweb="option"]{background-color:#fff!important;color:#0D1B2A!important;}
[data-baseweb="option"]:hover{background-color:#EEF2F7!important;}
.stTabs [data-baseweb="tab"]{color:#5A6A7A!important;}
.stTabs [aria-selected="true"]{color:#002855!important;}
section[data-testid="stSidebar"]{background-color:#ffffff!important;border-right:1px solid #E2E8F0!important;}
section[data-testid="stSidebar"] *{color:#0D1B2A!important;}
div[data-testid="stExpander"]{background-color:#ffffff!important;border:1px solid #E2E8F0!important;border-radius:10px!important;}
.stCheckbox label,.stCheckbox span{color:#0D1B2A!important;}
.stCaption,small{color:#8A9BAE!important;}
div[data-testid="stToast"]{background-color:#ffffff!important;border:1px solid #E2E8F0!important;}
div[data-testid="stAlert"]{background-color:transparent!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:2rem 1.5rem 4rem!important;max-width:720px!important;}
div[data-testid="stVerticalBlockBorderWrapper"]{background:#ffffff!important;border:1px solid #E2E8F0!important;border-radius:16px!important;box-shadow:0 2px 14px rgba(0,0,0,0.06)!important;padding:4px 0!important;margin-bottom:18px!important;}
div[data-testid="stVerticalBlockBorderWrapper"]>div{background:transparent!important;box-shadow:none!important;border:none!important;}
.app-header{background:linear-gradient(135deg,#002855 0%,#00509E 100%);border-radius:16px;padding:22px 28px;margin-bottom:24px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 4px 24px rgba(0,40,85,0.18);}
.app-header .brand{color:#fff;font-size:1.4rem;font-weight:700;letter-spacing:-0.5px;}
.app-header .brand span{color:#5BC4FF;}
.app-header .right{display:flex;align-items:center;gap:10px;}
.app-header .user-pill{background:rgba(255,255,255,0.14);border:1px solid rgba(255,255,255,0.28);border-radius:999px;padding:5px 14px;color:#fff;font-size:0.78rem;font-weight:500;font-family:'DM Mono',monospace;}
.admin-badge{display:inline-block;background:#FEF3C7;border:1px solid #FCD34D;border-radius:6px;padding:2px 8px;font-size:0.72rem;font-weight:700;color:#92400E!important;letter-spacing:0.5px;margin-left:8px;vertical-align:middle;}
.section-label{font-size:0.71rem;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;color:#8A9BAE;margin-bottom:14px;}
.stTextInput>div>div>input,.stNumberInput>div>div>input{border:1.5px solid #CBD5E0!important;border-radius:10px!important;padding:10px 14px!important;font-family:'DM Sans',sans-serif!important;font-size:0.95rem!important;background:#F8FAFC!important;color:#0D1B2A!important;}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus{border-color:#00509E!important;box-shadow:0 0 0 3px rgba(0,80,158,0.1)!important;outline:none!important;}
.stSelectbox>div>div>div{border:1.5px solid #CBD5E0!important;border-radius:10px!important;background:#F8FAFC!important;}
.stButton>button,.stDownloadButton>button{background:linear-gradient(135deg,#002855 0%,#00509E 100%)!important;color:#fff!important;border:none!important;border-radius:10px!important;font-family:'DM Sans',sans-serif!important;font-weight:600!important;font-size:0.88rem!important;height:46px!important;box-shadow:0 2px 8px rgba(0,80,158,0.22)!important;}
.stButton>button *,.stDownloadButton>button *{color:#fff!important;}
.stTabs [data-baseweb="tab-list"]{background:#EEF2F7!important;border-radius:10px!important;padding:4px!important;gap:4px!important;border-bottom:none!important;}
.stTabs [data-baseweb="tab"]{border-radius:8px!important;font-weight:600!important;font-size:0.88rem!important;color:#5A6A7A!important;padding:8px 20px!important;border:none!important;background:transparent!important;}
.stTabs [aria-selected="true"]{background:#fff!important;color:#002855!important;box-shadow:0 1px 6px rgba(0,0,0,0.1)!important;}
.sc-title{font-weight:700;font-size:0.92rem;color:#002855;}
.sc-meta{font-size:0.76rem;color:#8A9BAE;margin-top:2px;}
.user-row{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:#F8FAFC;border:1px solid #E8EDF3;border-radius:10px;margin-bottom:7px;}
.user-name{font-weight:600;font-size:0.88rem;}
.user-meta{font-size:0.76rem;color:#8A9BAE;margin-top:1px;}
[data-testid="stFileUploaderDropzone"]{border:2px dashed #CBD5E0!important;border-radius:12px!important;background:#F8FAFC!important;}
</style>
"""

# ─────────────────────────────────────────────
#  SECURITY
# ─────────────────────────────────────────────
def hash_pw(p): return hashlib.sha256(p.strip().encode()).hexdigest()


# ─────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner="Connecting…")
def get_db():
    conn = psycopg2.connect(st.secrets["DATABASE_URL"], connect_timeout=15)
    conn.autocommit = True
    return conn

def run(sql, params=(), fetch=None):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        st.cache_resource.clear()
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
    if fetch == "one": return cur.fetchone()
    if fetch == "all": return cur.fetchall()

def init_db():
    run("""CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE, created TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS stock_sessions (
            sid TEXT PRIMARY KEY, username TEXT NOT NULL,
            location TEXT, data TEXT, updated TEXT)""")
    if run("SELECT COUNT(*) as c FROM users", fetch="one")["c"] == 0:
        run("INSERT INTO users VALUES (%s,%s,%s,%s)",
            ("admin", hash_pw("admin123"), True, datetime.now().strftime("%Y-%m-%d")))

init_db()


# ─────────────────────────────────────────────
#  USER CRUD
# ─────────────────────────────────────────────
def get_user(u):
    return run("SELECT * FROM users WHERE username=%s", (u.strip().lower(),), fetch="one")
def get_all_users():
    rows = run("SELECT username,is_admin,created FROM users ORDER BY username", fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["username","is_admin","created"])
def create_user(u, p, admin=False):
    u = u.strip().lower()
    if not u or not p or get_user(u): return False
    run("INSERT INTO users VALUES (%s,%s,%s,%s)",
        (u, hash_pw(p), admin, datetime.now().strftime("%Y-%m-%d")))
    return True
def delete_user(u): run("DELETE FROM users WHERE username=%s", (u,))
def change_pw(u, p): run("UPDATE users SET password_hash=%s WHERE username=%s", (hash_pw(p), u))


# ─────────────────────────────────────────────
#  SESSION CRUD
# ─────────────────────────────────────────────
def df_to_json(df):
    cols = ["product code","product name","systems count","physical count","difference","last_updated"]
    return df[[c for c in cols if c in df.columns]].to_json(orient="records")

def json_to_df(j):
    df = pd.DataFrame(json.loads(j))
    if df.empty: return df
    df["physical count"] = pd.to_numeric(df.get("physical count", 0), errors="coerce").fillna(0).astype(int)
    df["difference"]     = pd.to_numeric(df.get("difference",     0), errors="coerce").fillna(0).astype(int)
    df["systems count"]  = pd.to_numeric(df.get("systems count",  0), errors="coerce").fillna(0)
    df["last_updated"]   = df.get("last_updated", pd.Series([""] * len(df))).fillna("").astype(str)
    df["product code"]   = df["product code"].astype(str)
    df["product name"]   = df["product name"].astype(str)
    return df

def save_session(sid, username, location, df):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    run("""INSERT INTO stock_sessions(sid,username,location,data,updated)
           VALUES(%s,%s,%s,%s,%s)
           ON CONFLICT(sid) DO UPDATE
           SET data=%s,location=%s,updated=%s""",
        (sid,username,location,df_to_json(df),ts,
         df_to_json(df),location,ts))

def load_session(sid):
    row = run("SELECT data FROM stock_sessions WHERE sid=%s", (sid,), fetch="one")
    return json_to_df(row["data"]) if row else None

def get_session_json(sid):
    row = run("SELECT data FROM stock_sessions WHERE sid=%s", (sid,), fetch="one")
    return row["data"] if row else "[]"

def get_my_sessions(username):
    rows = run("SELECT sid,location,updated FROM stock_sessions WHERE username=%s ORDER BY updated DESC",
               (username,), fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["sid","location","updated"])

def get_all_sessions():
    rows = run("SELECT sid,username,location,updated FROM stock_sessions ORDER BY updated DESC", fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["sid","username","location","updated"])


# ─────────────────────────────────────────────
#  EXCEL NORMALISE
# ─────────────────────────────────────────────
REQUIRED = {"product name","product code","systems count"}
def normalise(df):
    df.columns = [c.strip().lower() for c in df.columns]
    missing = REQUIRED - set(df.columns)
    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
        st.stop()
    df["product code"]   = df["product code"].astype(str).str.strip()
    df["product name"]   = df["product name"].astype(str).str.strip()
    df["systems count"]  = pd.to_numeric(df["systems count"], errors="coerce").fillna(0)
    df["physical count"] = 0
    df["difference"]     = 0
    df["last_updated"]   = ""
    return df


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def ui_header(username="", is_admin=False):
    badge = '<span class="admin-badge">ADMIN</span>' if is_admin else ""
    pill  = f'<span class="user-pill">👤 {username}{badge}</span>' if username else ""
    st.markdown(f"""
    <div class="app-header">
      <div class="brand">📦 Stock <span>Count Pro</span></div>
      <div class="right">{pill}</div>
    </div>""", unsafe_allow_html=True)

def section(t): st.markdown(f'<div class="section-label">{t}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  COUNTING PAGE — full screen HTML, no Streamlit
# ─────────────────────────────────────────────
def render_counting_page(sid, location, username, data_json):
    """
    Completely hides Streamlit and renders counting.html inline.
    Data is injected directly — no localStorage dependency on load.
    """
    # Escape data for safe JS embedding
    data_b64 = base64.b64encode(data_json.encode()).decode()
    sid_safe      = sid.replace("'", "\\'")
    location_safe = (location or "").replace("'", "\\'")
    username_safe = username.replace("'", "\\'")

    # Hide ALL Streamlit chrome, take over full viewport
    st.markdown("""
    <style>
    #MainMenu,footer,header,[data-testid="stToolbar"],
    [data-testid="stDecoration"],[data-testid="stStatusWidget"],
    section[data-testid="stSidebar"],[data-testid="stSidebarNav"],
    .stApp > header { display:none!important; }
    .block-container { padding:0!important; max-width:100%!important; }
    .stApp { background:#F4F6FA!important; }
    /* Kill the iframe border from components */
    iframe { border:none!important; }
    </style>
    """, unsafe_allow_html=True)

    # Back to dashboard button (outside the iframe)
    if st.button("← Back to Dashboard"):
        st.session_state.pop("counting_sid", None)
        st.session_state.pop("counting_data", None)
        st.rerun()

    # Load counting HTML
    import os
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "counting.html")
    try:
        with open(html_path) as f:
            counting_html = f.read()
    except FileNotFoundError:
        st.error("counting.html not found in repo root.")
        st.stop()

    # Inject session data right before </body> — no localStorage needed
    inject = f"""
    <script>
    // Data injected by Streamlit — available immediately, no localStorage wait
    window.__SC_SID__      = '{sid_safe}';
    window.__SC_LOCATION__ = '{location_safe}';
    window.__SC_USER__     = '{username_safe}';
    window.__SC_DATA__     = JSON.parse(atob('{data_b64}'));
    // Also write to localStorage for offline persistence
    localStorage.setItem('sc_sid',      window.__SC_SID__);
    localStorage.setItem('sc_location', window.__SC_LOCATION__);
    localStorage.setItem('sc_user',     window.__SC_USER__);
    localStorage.setItem('sc_data',     JSON.stringify(window.__SC_DATA__));
    localStorage.setItem('sc_streamlit_origin', window.location.origin);
    </script>
    """
    counting_html = counting_html.replace("</body>", inject + "\n</body>")

    # Also patch the init() function to use window.__SC_DATA__ if available
    patch = """
    <script>
    // Override init to use injected data instead of localStorage
    const _originalInit = init;
    function init() {
      if (window.__SC_DATA__ && window.__SC_DATA__.length > 0) {
        // Use injected data
        const sid      = window.__SC_SID__;
        const user     = window.__SC_USER__;
        const location = window.__SC_LOCATION__;
        saveCount_counter = parseInt(localStorage.getItem('sc_counter') || '0');

        document.getElementById('noDataState').style.display = 'none';
        document.getElementById('headerSid').textContent  = sid;
        document.getElementById('headerUser').textContent = user || '—';

        products = window.__SC_DATA__;
        products.forEach(p => {
          p['physical count'] = parseInt(p['physical count']) || 0;
          p['difference']     = parseInt(p['difference'])     || 0;
          p['systems count']  = parseFloat(p['systems count']) || 0;
          p['last_updated']   = p['last_updated'] || '';
          p['product code']   = String(p['product code'] || '');
          p['product name']   = String(p['product name'] || '');
        });
        updateSyncBar();
        renderApp();
      } else {
        _originalInit();
      }
    }
    </script>
    """
    counting_html = counting_html.replace("</head>", patch + "\n</head>")

    # Render full screen — height set to fill viewport
    st.components.v1.html(counting_html, height=900, scrolling=True)
    st.stop()


# ─────────────────────────────────────────────
#  SYNC HANDLER — counting page POSTs here
# ─────────────────────────────────────────────
qp = st.query_params
if qp.get("action") == "sync":
    sid_s  = qp.get("sid", "")
    data_s = qp.get("data", "")
    if sid_s and data_s:
        try:
            df_s = json_to_df(data_s)
            row  = run("SELECT username,location FROM stock_sessions WHERE sid=%s", (sid_s,), fetch="one")
            if row:
                save_session(sid_s, row["username"], row["location"] or "", df_s)
        except Exception:
            pass
    st.query_params.clear()
    st.rerun()


# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user     = None
    st.session_state.is_admin = False

if not st.session_state.user:
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    ui_header()
    with st.container(border=True):
        section("Sign In")
        st.markdown("#### Welcome to Stock Count Pro")
        u = st.text_input("Username", placeholder="your username")
        p = st.text_input("Password", type="password", placeholder="••••••••")
        if st.button("Sign In →", use_container_width=True):
            row = get_user(u)
            if row and row["password_hash"] == hash_pw(p):
                st.session_state.user     = row["username"]
                st.session_state.is_admin = bool(row["is_admin"])
                st.rerun()
            else:
                st.error("Incorrect username or password.")
    st.stop()

CU       = st.session_state.user
IS_ADMIN = st.session_state.is_admin


# ─────────────────────────────────────────────
#  IF COUNTING SESSION ACTIVE — show counting page
# ─────────────────────────────────────────────
if "counting_sid" in st.session_state:
    sid_c  = st.session_state.counting_sid
    data_c = st.session_state.counting_data
    loc_c  = st.session_state.get("counting_location", "")
    render_counting_page(sid_c, loc_c, CU, data_c)
    # render_counting_page calls st.stop() so nothing below runs


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────
st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"**Signed in as:** `{CU}`")
    st.markdown("**Role:** Admin 🔑" if IS_ADMIN else "**Role:** Counter 📦")
    st.divider()
    with st.expander("🔒 Change Password"):
        cp1 = st.text_input("New password", type="password", key="cp1")
        cp2 = st.text_input("Confirm",      type="password", key="cp2")
        if st.button("Update"):
            if not cp1: st.warning("Cannot be empty.")
            elif cp1 != cp2: st.error("Passwords do not match.")
            else: change_pw(CU, cp1); st.success("Updated!")
    st.divider()
    if st.button("🚪 Sign Out", use_container_width=True):
        for k in list(st.session_state.keys()): st.session_state.pop(k, None)
        st.rerun()

ui_header(username=CU, is_admin=IS_ADMIN)

tab_labels = (["  ✨  New Count  ","  📁  My Sessions  ","  ⚙️  Admin Panel  "]
              if IS_ADMIN else ["  ✨  New Count  ","  📁  My Sessions  "])
tabs   = st.tabs(tab_labels)
t_new  = tabs[0]
t_my   = tabs[1]


# ── NEW COUNT ──────────────────────────────────────────────
with t_new:
    with st.container(border=True):
        section("Start New Stock Count")
        sid_in  = st.text_input("Session ID",         placeholder="e.g. SC-2026-001")
        loc_in  = st.text_input("Warehouse / Location", placeholder="e.g. Main Warehouse")
        file_in = st.file_uploader("Upload Master Sheet (.xlsx)", type=["xlsx"])
        if file_in: st.caption(f"📎 {file_in.name} — ready")

        if st.button("🚀  Create & Start Counting", use_container_width=True):
            if not sid_in:
                st.warning("Please enter a Session ID.")
            elif not file_in:
                st.warning("Please upload a master sheet.")
            else:
                exists = run("SELECT 1 FROM stock_sessions WHERE sid=%s", (sid_in,), fetch="one")
                if exists:
                    st.error(f"Session **{sid_in}** already exists.")
                else:
                    try:
                        df = normalise(pd.read_excel(file_in))
                        save_session(sid_in, CU, loc_in, df)
                        st.session_state.counting_sid      = sid_in
                        st.session_state.counting_location = loc_in
                        st.session_state.counting_data     = df_to_json(df)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to read file: {e}")


# ── MY SESSIONS ────────────────────────────────────────────
with t_my:
    with st.container(border=True):
        section("My Stock Count Sessions")
        my = get_my_sessions(CU)

        if my.empty:
            st.info("No sessions yet. Create one in the New Count tab.")
        else:
            for _, row in my.iterrows():
                df_row  = load_session(row["sid"])
                total   = len(df_row) if df_row is not None else 0
                counted = int((df_row["last_updated"] != "").sum()) if df_row is not None else 0
                pct     = round(counted / total * 100) if total else 0
                n_vars  = int(((df_row["difference"] != 0) & (df_row["last_updated"] != "")).sum()) if df_row is not None else 0

                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"""
                        <div class="sc-title">{row['sid']}</div>
                        <div class="sc-meta">📍 {row['location'] or '—'} · 🕐 {row['updated'] or '—'}</div>
                        <div class="sc-meta" style="margin-top:4px">
                          {counted}/{total} counted · {pct}% ·
                          <span style="color:#DC2626">{n_vars} variances</span>
                        </div>""", unsafe_allow_html=True)
                    with c2:
                        if st.button("▶ Count", key=f"res_{row['sid']}", use_container_width=True):
                            # Pull latest data from DB (in case synced from phone)
                            data_json = get_session_json(row["sid"])
                            st.session_state.counting_sid      = row["sid"]
                            st.session_state.counting_location = row["location"] or ""
                            st.session_state.counting_data     = data_json
                            st.rerun()

                if df_row is not None:
                    e1, e2 = st.columns(2)
                    with e1:
                        out = io.BytesIO()
                        with pd.ExcelWriter(out, engine="openpyxl") as w:
                            df_row.to_excel(w, index=False, sheet_name="Stock Count")
                        st.download_button("📤 Export All", out.getvalue(),
                            file_name=f"{row['sid']}_StockCount_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True, key=f"exp_{row['sid']}")
                    with e2:
                        out2 = io.BytesIO()
                        with pd.ExcelWriter(out2, engine="openpyxl") as w:
                            df_row[df_row["difference"] != 0].to_excel(w, index=False, sheet_name="Variances")
                        st.download_button("⚠️ Variances Only", out2.getvalue(),
                            file_name=f"{row['sid']}_Variances_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True, key=f"var_{row['sid']}")


# ── ADMIN PANEL ────────────────────────────────────────────
if IS_ADMIN:
    t_admin = tabs[2]
    with t_admin:
        at1, at2, at3 = st.tabs(["  👥  Users  ","  📋  All Sessions  ","  ➕  Add User  "])

        with at1:
            with st.container(border=True):
                section("All Users")
                for _, u in get_all_users().iterrows():
                    uc1, uc2 = st.columns([4, 1])
                    with uc1:
                        role = "🔑 Admin" if u["is_admin"] else "📦 Counter"
                        st.markdown(f'<div class="user-row"><div><div class="user-name">{u["username"]}</div><div class="user-meta">{role} · {u["created"] or "—"}</div></div></div>', unsafe_allow_html=True)
                    with uc2:
                        if u["username"] != CU:
                            if st.button("Delete", key=f"del_{u['username']}", use_container_width=True):
                                delete_user(u["username"])
                                st.rerun()
                        else:
                            st.caption("(you)")

        with at2:
            with st.container(border=True):
                section("All Sessions")
                all_s = get_all_sessions()
                if all_s.empty:
                    st.info("No sessions found.")
                else:
                    for _, row in all_s.iterrows():
                        st.markdown(f"""
                        <div class="user-row">
                          <div>
                            <div class="user-name">{row['sid']}</div>
                            <div class="user-meta">👤 {row['username']} · 📍 {row['location'] or '—'} · 🕐 {row['updated'] or '—'}</div>
                          </div>
                        </div>""", unsafe_allow_html=True)

        with at3:
            with st.container(border=True):
                section("Create New User")
                nu  = st.text_input("Username", placeholder="e.g. john", key="nu")
                np_ = st.text_input("Password", type="password", key="np_")
                na  = st.checkbox("Grant admin access", key="na")
                if st.button("➕  Create User", use_container_width=True):
                    if not nu or not np_:
                        st.warning("Username and password required.")
                    else:
                        ok = create_user(nu, np_, na)
                        st.success(f"User **{nu.strip().lower()}** created!") if ok else st.error("Username already exists.")
