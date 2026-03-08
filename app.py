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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

.stApp,
section[data-testid="stMain"],
div[data-testid="stAppViewContainer"],
div[data-testid="stMainBlockContainer"],
div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"],
div[data-testid="column"],
div[data-testid="stMarkdownContainer"],
div[data-testid="stForm"],
div[data-testid="stWidgetLabel"],
div[data-testid="stCaptionContainer"],
div[data-testid="stNumberInput"] > div,
div[data-testid="stTextInput"] > div,
div[data-testid="stSelectbox"] > div,
div[data-baseweb="tab-panel"],
div[data-baseweb="form-control-label"],
div[data-baseweb="block"],
div[data-baseweb="card"],
div.stTabs,
div[data-testid="stTabsContent"] {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

html, body { color-scheme: light !important; }
.stApp {
    background-color: #F4F6FA !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #0D1B2A !important;
    color-scheme: light !important;
}
.stApp * { color: #0D1B2A !important; }
.app-header * { color: #ffffff !important; }
.app-header .brand span { color: #5BC4FF !important; }
.app-header .admin-badge { color: #92400E !important; }

html, body,
section[data-testid="stMain"],
div[data-testid="stAppViewContainer"] { background-color: #F4F6FA !important; }

input, textarea, select {
    color: #0D1B2A !important;
    background-color: #F8FAFC !important;
    -webkit-text-fill-color: #0D1B2A !important;
}
input::placeholder, textarea::placeholder {
    color: #A0AEC0 !important;
    -webkit-text-fill-color: #A0AEC0 !important;
    opacity: 1 !important;
}
[data-baseweb="select"] * { color: #0D1B2A !important; }
[data-baseweb="menu"]       { background-color: #fff !important; }
[data-baseweb="option"]     { background-color: #fff !important; color: #0D1B2A !important; }
[data-baseweb="option"]:hover { background-color: #EEF2F7 !important; }
.stTabs [data-baseweb="tab"] { color: #5A6A7A !important; }
.stTabs [aria-selected="true"] { color: #002855 !important; }
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #E2E8F0 !important;
}
section[data-testid="stSidebar"] * { color: #0D1B2A !important; }
div[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
}
.stCheckbox label, .stCheckbox span { color: #0D1B2A !important; }
.stCaption, small { color: #8A9BAE !important; }
div[data-testid="stToast"] { background-color: #ffffff !important; border: 1px solid #E2E8F0 !important; }
div[data-testid="stAlert"] { background-color: transparent !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1.5rem 4rem !important; max-width: 720px !important; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 14px rgba(0,0,0,0.06) !important;
    padding: 4px 0 !important;
    margin-bottom: 18px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

.app-header {
    background: linear-gradient(135deg, #002855 0%, #00509E 100%);
    border-radius: 16px; padding: 22px 28px; margin-bottom: 24px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 4px 24px rgba(0,40,85,0.18);
}
.app-header .brand { color: #fff; font-size: 1.4rem; font-weight: 700; letter-spacing: -0.5px; }
.app-header .brand span { color: #5BC4FF; }
.app-header .right { display: flex; align-items: center; gap: 10px; }
.app-header .user-pill {
    background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.28);
    border-radius: 999px; padding: 5px 14px; color: #fff;
    font-size: 0.78rem; font-weight: 500; font-family: 'DM Mono', monospace;
}
.app-header .session-pill {
    background: rgba(91,196,255,0.18); border: 1px solid rgba(91,196,255,0.4);
    border-radius: 999px; padding: 5px 14px; color: #5BC4FF;
    font-size: 0.78rem; font-weight: 500; font-family: 'DM Mono', monospace;
}
.admin-badge {
    display: inline-block; background: #FEF3C7; border: 1px solid #FCD34D;
    border-radius: 6px; padding: 2px 8px; font-size: 0.72rem;
    font-weight: 700; color: #92400E !important; letter-spacing: 0.5px;
    margin-left: 8px; vertical-align: middle;
}
.section-label {
    font-size: 0.71rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.2px; color: #8A9BAE; margin-bottom: 14px;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    border: 1.5px solid #CBD5E0 !important; border-radius: 10px !important;
    padding: 10px 14px !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important; background: #F8FAFC !important; color: #0D1B2A !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #00509E !important; box-shadow: 0 0 0 3px rgba(0,80,158,0.1) !important;
    outline: none !important;
}
.stSelectbox > div > div > div {
    border: 1.5px solid #CBD5E0 !important; border-radius: 10px !important; background: #F8FAFC !important;
}
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, #002855 0%, #00509E 100%) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    font-size: 0.88rem !important; height: 46px !important;
    box-shadow: 0 2px 8px rgba(0,80,158,0.22) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px) !important; box-shadow: 0 4px 16px rgba(0,80,158,0.3) !important;
}
.stButton > button *, .stDownloadButton > button * { color: #fff !important; }
.stTabs [data-baseweb="tab-list"] {
    background: #EEF2F7 !important; border-radius: 10px !important;
    padding: 4px !important; gap: 4px !important; border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.88rem !important;
    color: #5A6A7A !important; padding: 8px 20px !important;
    border: none !important; background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #fff !important; color: #002855 !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.1) !important;
}
.stat-box { background: #F4F6FA; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 10px; text-align: center; }
.stat-label { font-size: 0.69rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #8A9BAE; margin-bottom: 5px; }
.stat-value { font-size: 1.85rem; font-weight: 700; color: #002855; line-height: 1; }
.vbox { border-radius: 12px; padding: 14px 10px; text-align: center; }
.vbox.neutral  { background: #F4F6FA; border: 1px solid #E2E8F0; }
.vbox.positive { background: #ECFDF5; border: 1px solid #6EE7B7; }
.vbox.negative { background: #FEF2F2; border: 1px solid #FCA5A5; }
.vbox-label { font-size: 0.69rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #8A9BAE; margin-bottom: 5px; }
.vbox-value { font-size: 1.85rem; font-weight: 700; line-height: 1; }
.vbox.neutral  .vbox-value { color: #0D1B2A; }
.vbox.positive .vbox-value { color: #059669; }
.vbox.negative .vbox-value { color: #DC2626; }
.prog-wrap { margin-top: 16px; }
.prog-head { display: flex; justify-content: space-between; font-size: 0.77rem; color: #8A9BAE; margin-bottom: 6px; }
.prog-track { background: #E2E8F0; border-radius: 999px; height: 7px; overflow: hidden; }
.prog-fill  { background: linear-gradient(90deg, #002855, #5BC4FF); height: 100%; border-radius: 999px; }
.log-row { display: flex; align-items: center; justify-content: space-between; padding: 11px 14px; background: #F8FAFC; border: 1px solid #E8EDF3; border-radius: 10px; margin-bottom: 7px; }
.log-name { font-weight: 600; font-size: 0.88rem; color: #0D1B2A; }
.log-meta  { font-size: 0.76rem; color: #8A9BAE; margin-top: 1px; }
.badge-pos  { background: #D1FAE5; color: #065F46 !important; border-radius: 6px; padding: 2px 9px; font-size: 0.79rem; font-weight: 700; font-family: 'DM Mono', monospace; }
.badge-neg  { background: #FEE2E2; color: #991B1B !important; border-radius: 6px; padding: 2px 9px; font-size: 0.79rem; font-weight: 700; font-family: 'DM Mono', monospace; }
.badge-zero { background: #E2E8F0; color: #374151 !important; border-radius: 6px; padding: 2px 9px; font-size: 0.79rem; font-weight: 700; font-family: 'DM Mono', monospace; }
.user-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: #F8FAFC; border: 1px solid #E8EDF3; border-radius: 10px; margin-bottom: 7px; }
.user-name { font-weight: 600; font-size: 0.88rem; color: #0D1B2A; }
.user-meta { font-size: 0.76rem; color: #8A9BAE; margin-top: 1px; }
.divider { border: none; border-top: 1px solid #E2E8F0; margin: 18px 0; }
.sync-bar {
    background: #EEF2F7; border: 1px solid #E2E8F0; border-radius: 10px;
    padding: 10px 16px; display: flex; align-items: center;
    justify-content: space-between; margin-bottom: 14px; font-size: 0.82rem;
}
.sync-dot-ok  { width:8px; height:8px; border-radius:50%; background:#10B981; display:inline-block; margin-right:6px; }
.sync-dot-pending { width:8px; height:8px; border-radius:50%; background:#F59E0B; display:inline-block; margin-right:6px; }
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed #CBD5E0 !important; border-radius: 12px !important; background: #F8FAFC !important;
}

/* ── FIX 1: product result buttons wrap to 2 lines on mobile ── */
.stButton > button {
    height: auto !important;
    min-height: 46px !important;
    white-space: normal !important;
    word-break: break-word !important;
    text-align: left !important;
    line-height: 1.4 !important;
    padding-top: 10px !important;
    padding-bottom: 10px !important;
}
/* Selected product display card */
.product-card {
    background: #EEF5FF;
    border: 2px solid #00509E;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 14px;
}
.product-card .pc-code {
    font-family: 'DM Mono', monospace;
    font-size: 0.76rem;
    color: #5A6A7A;
    margin-bottom: 4px;
}
.product-card .pc-name {
    font-size: 0.98rem;
    font-weight: 700;
    color: #002855;
    line-height: 1.35;
    word-break: break-word;
    white-space: normal;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SECURITY
# ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode()).hexdigest()


# ─────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner="Connecting…")
def get_db():
    url = st.secrets["DATABASE_URL"]
    conn = psycopg2.connect(url, connect_timeout=15)
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
    run("""CREATE TABLE IF NOT EXISTS audit_sessions (
            sid TEXT PRIMARY KEY, username TEXT NOT NULL,
            client TEXT, data BYTEA, updated TEXT)""")
    row = run("SELECT COUNT(*) as c FROM users", fetch="one")
    if row and row["c"] == 0:
        run("INSERT INTO users VALUES (%s,%s,%s,%s)",
            ("admin", hash_password("admin123"), True, datetime.now().strftime("%Y-%m-%d")))

init_db()


# ─────────────────────────────────────────────
#  USER CRUD
# ─────────────────────────────────────────────
def get_user(username):
    return run("SELECT username, password_hash, is_admin FROM users WHERE username=%s",
               (username.strip().lower(),), fetch="one")

def get_all_users():
    rows = run("SELECT username, is_admin, created FROM users ORDER BY username", fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["username","is_admin","created"])

def create_user(username, password, is_admin=False):
    username = username.strip().lower()
    if not username or not password or get_user(username):
        return False
    run("INSERT INTO users VALUES (%s,%s,%s,%s)",
        (username, hash_password(password), is_admin, datetime.now().strftime("%Y-%m-%d")))
    return True

def delete_user(username):
    run("DELETE FROM users WHERE username=%s", (username,))

def change_password(username, new_password):
    run("UPDATE users SET password_hash=%s WHERE username=%s",
        (hash_password(new_password), username))


# ─────────────────────────────────────────────
#  AUDIT CRUD
# ─────────────────────────────────────────────
def df_to_bytes(df: pd.DataFrame) -> bytes:
    cols = ["product code","product name","systems count","physical count","difference","last_updated"]
    save_df = df[[c for c in cols if c in df.columns]]
    buf = io.BytesIO()
    save_df.to_pickle(buf, compression="gzip")
    return buf.getvalue()

def bytes_to_df(raw: bytes) -> pd.DataFrame:
    try:
        return pd.read_pickle(io.BytesIO(raw), compression="gzip")
    except Exception:
        return pd.read_pickle(io.BytesIO(raw))

def save_audit_db(sid, username, client, df):
    data = psycopg2.Binary(df_to_bytes(df))
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M")
    run("""INSERT INTO audit_sessions (sid,username,client,data,updated)
           VALUES (%s,%s,%s,%s,%s)
           ON CONFLICT (sid) DO UPDATE
           SET data=%s, client=%s, updated=%s""",
        (sid, username, client, data, ts, data, client, ts))

def load_audit_db(sid):
    row = run("SELECT data FROM audit_sessions WHERE sid=%s", (sid,), fetch="one")
    return bytes_to_df(bytes(row["data"])) if row else None

def get_user_sessions(username):
    rows = run("SELECT sid, client, updated FROM audit_sessions WHERE username=%s ORDER BY updated DESC",
               (username,), fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["sid","client","updated"])

def get_all_sessions_admin():
    rows = run("SELECT sid, username, client, updated FROM audit_sessions ORDER BY updated DESC", fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["sid","username","client","updated"])


# ─────────────────────────────────────────────
#  LOCAL STORAGE HELPERS
# ─────────────────────────────────────────────
def df_to_json(df: pd.DataFrame) -> str:
    return df.to_json(orient="records")

def json_to_df(json_str: str) -> pd.DataFrame:
    records = json.loads(json_str)
    df = pd.DataFrame(records)
    df["physical count"] = pd.to_numeric(df["physical count"], errors="coerce").fillna(0).astype(int)
    df["difference"]     = pd.to_numeric(df["difference"],     errors="coerce").fillna(0).astype(int)
    df["last_updated"]   = df["last_updated"].fillna("").astype(str)
    df["systems count"]  = pd.to_numeric(df["systems count"],  errors="coerce").fillna(0)
    df["product code"]   = df["product code"].astype(str)
    df["product name"]   = df["product name"].astype(str)
    return df

def set_local_storage(key: str, value: str):
    safe_value = value.replace("`", "\\`").replace("\\", "\\\\")
    st.components.v1.html(f"""
    <script>localStorage.setItem("{key}", `{safe_value}`);</script>
    """, height=0)

def clear_local_storage():
    st.components.v1.html("""
    <script>
    ["bdo_user","bdo_sid","bdo_client","bdo_df","bdo_counter"].forEach(k => localStorage.removeItem(k));
    </script>
    """, height=0)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
REQUIRED = {"product name", "product code", "systems count"}

def normalise_df(df):
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

def render_header(username="", session_id="", is_admin=False):
    admin_badge = '<span class="admin-badge">ADMIN</span>' if is_admin else ""
    user_pill   = f'<span class="user-pill">👤 {username}{admin_badge}</span>' if username else ""
    sess_pill   = f'<span class="session-pill">📍 {session_id}</span>' if session_id else ""
    st.markdown(f"""
    <div class="app-header">
        <div class="brand">📦 Stock <span>Count Pro</span></div>
        <div class="right">{sess_pill}{user_pill}</div>
    </div>""", unsafe_allow_html=True)

def section(label):
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)

def sync_status(counter: int):
    pending = counter % 10
    if pending == 0:
        st.markdown('<div class="sync-bar"><span><span class="sync-dot-ok"></span>All changes backed up</span></div>', unsafe_allow_html=True)
    else:
        left = 10 - pending
        st.markdown(f'<div class="sync-bar"><span><span class="sync-dot-pending"></span>{pending} unsaved counts · auto-backup in {left}</span></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
if "ls_checked" not in st.session_state:
    st.session_state.ls_checked      = False
    st.session_state.current_user    = None
    st.session_state.is_admin        = False
    st.session_state.active_sid      = None
    st.session_state.active_client   = None
    st.session_state.df              = None
    st.session_state.save_counter    = 0
    # FIX 2: track selected product index in session_state
    st.session_state.selected_idx    = None
    st.session_state.selected_code   = None

qp         = st.query_params
ls_user    = qp.get("ls_user",    "")
ls_sid     = qp.get("ls_sid",     "")
ls_client  = qp.get("ls_client",  "")
ls_counter = qp.get("ls_counter", "0")

if ls_user and not st.session_state.current_user:
    row = get_user(ls_user)
    if row:
        st.session_state.current_user = row["username"]
        st.session_state.is_admin     = bool(row["is_admin"])


# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────
if not st.session_state.current_user:
    render_header()

    st.components.v1.html("""
    <script>
    const u = localStorage.getItem("bdo_user");
    if (u) {
        const url = new URL(window.parent.location.href);
        url.searchParams.set("ls_user",    u);
        url.searchParams.set("ls_sid",     localStorage.getItem("bdo_sid")    || "");
        url.searchParams.set("ls_client",  localStorage.getItem("bdo_client") || "");
        url.searchParams.set("ls_counter", localStorage.getItem("bdo_counter")|| "0");
        window.parent.location.href = url.toString();
    }
    </script>
    """, height=0)

    with st.container(border=True):
        section("Sign In")
        st.markdown("#### Welcome to Stock Count Pro")
        username_input = st.text_input("Username", placeholder="your username")
        password_input = st.text_input("Password", type="password", placeholder="••••••••")
        if st.button("Sign In →", use_container_width=True):
            uname = username_input.strip().lower()
            row   = get_user(uname)
            if row and row["password_hash"] == hash_password(password_input):
                st.session_state.current_user = row["username"]
                st.session_state.is_admin     = bool(row["is_admin"])
                set_local_storage("bdo_user", row["username"])
                st.rerun()
            else:
                st.error("Incorrect username or password.")
    st.stop()


CU       = st.session_state.current_user
IS_ADMIN = st.session_state.is_admin


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**Signed in as:** `{CU}`")
    if IS_ADMIN:
        st.markdown("**Role:** Admin 🔑")
    st.divider()
    with st.expander("🔒 Change Password"):
        cp1 = st.text_input("New password",     type="password", key="cp1")
        cp2 = st.text_input("Confirm password", type="password", key="cp2")
        if st.button("Update Password"):
            if not cp1:
                st.warning("Password cannot be empty.")
            elif cp1 != cp2:
                st.error("Passwords do not match.")
            else:
                change_password(CU, cp1)
                st.success("Password updated!")
    st.divider()
    if st.button("🚪 Sign Out", use_container_width=True):
        clear_local_storage()
        for k in ["current_user","is_admin","active_sid","active_client",
                  "df","save_counter","selected_idx","selected_code"]:
            st.session_state.pop(k, None)
        st.query_params.clear()
        st.rerun()


# ─────────────────────────────────────────────
#  RESTORE ACTIVE SESSION FROM localStorage
# ─────────────────────────────────────────────
if not st.session_state.active_sid and ls_sid:
    st.components.v1.html("""
    <script>
    const sid    = localStorage.getItem("bdo_sid");
    const client = localStorage.getItem("bdo_client");
    const df     = localStorage.getItem("bdo_df");
    const ctr    = localStorage.getItem("bdo_counter") || "0";
    if (sid && df) {
        const url = new URL(window.parent.location.href);
        url.searchParams.set("ls_sid",     sid);
        url.searchParams.set("ls_client",  client || "");
        url.searchParams.set("ls_counter", ctr);
        url.searchParams.set("ls_df",      df);
        window.parent.location.href = url.toString();
    }
    </script>
    """, height=0)

ls_df = qp.get("ls_df", "")
if ls_df and st.session_state.active_sid is None and ls_sid:
    try:
        restored_df = json_to_df(ls_df)
        st.session_state.active_sid    = ls_sid
        st.session_state.active_client = ls_client
        st.session_state.df            = restored_df
        st.session_state.save_counter  = int(ls_counter)
    except Exception:
        pass


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────
if not st.session_state.active_sid:
    render_header(username=CU, is_admin=IS_ADMIN)

    tabs     = (["  ✨  New Count  ","  📁  My Sessions  ","  ⚙️  Admin Panel  "]
                if IS_ADMIN else
                ["  ✨  New Count  ","  📁  My Sessions  "])
    tab_objs = st.tabs(tabs)
    t1, t2   = tab_objs[0], tab_objs[1]

    with t1:
        with st.container(border=True):
            section("Start New Stock Count")
            sid_new    = st.text_input("Session ID", placeholder="e.g. SC-2026-001")
            client_new = st.text_input("Warehouse / Location", placeholder="e.g. Main Warehouse")
            file_new   = st.file_uploader("Upload Master Sheet (.xlsx)", type=["xlsx"])
            if file_new:
                st.caption(f"📎 {file_new.name} — ready")
            if st.button("🚀  Start Stock Count", use_container_width=True):
                if not sid_new:
                    st.warning("Please enter a Session ID.")
                elif not file_new:
                    st.warning("Please upload a master sheet.")
                else:
                    exists = run("SELECT 1 FROM audit_sessions WHERE sid=%s", (sid_new,), fetch="one")
                    if exists:
                        st.error(f"Session **{sid_new}** already taken.")
                    else:
                        try:
                            df = normalise_df(pd.read_excel(file_new))
                            st.session_state.active_sid    = sid_new
                            st.session_state.active_client = client_new
                            st.session_state.df            = df
                            st.session_state.save_counter  = 0
                            st.session_state.selected_idx  = None
                            st.session_state.selected_code = None
                            save_audit_db(sid_new, CU, client_new, df)
                            set_local_storage("bdo_sid",     sid_new)
                            set_local_storage("bdo_client",  client_new)
                            set_local_storage("bdo_df",      df_to_json(df))
                            set_local_storage("bdo_counter", "0")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to read file: {e}")

    with t2:
        with st.container(border=True):
            section("My Sessions")
            history = get_user_sessions(CU)
            if history.empty:
                st.info("No saved sessions yet.")
            else:
                for _, row in history.iterrows():
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"""
                        <div style="padding:4px 0">
                          <div style="font-weight:600;font-size:0.9rem">{row['sid']}</div>
                          <div style="font-size:0.77rem;color:#8A9BAE">{row['client'] or '—'} · {row['updated'] or '—'}</div>
                        </div>""", unsafe_allow_html=True)
                    with c2:
                        if st.button("Load", key=f"load_{row['sid']}", use_container_width=True):
                            loaded = load_audit_db(row["sid"])
                            if loaded is not None:
                                st.session_state.active_sid    = row["sid"]
                                st.session_state.active_client = row["client"]
                                st.session_state.df            = loaded
                                st.session_state.save_counter  = 0
                                st.session_state.selected_idx  = None
                                st.session_state.selected_code = None
                                set_local_storage("bdo_sid",     row["sid"])
                                set_local_storage("bdo_client",  row["client"] or "")
                                set_local_storage("bdo_df",      df_to_json(loaded))
                                set_local_storage("bdo_counter", "0")
                                st.rerun()
                            else:
                                st.error("Could not load session.")

    if IS_ADMIN:
        t3 = tab_objs[2]
        with t3:
            at1, at2, at3 = st.tabs(["  👥  Users  ","  📋  All Sessions  ","  ➕  Add User  "])
            with at1:
                with st.container(border=True):
                    section("All Users")
                    for _, u in get_all_users().iterrows():
                        uc1, uc2 = st.columns([4, 1])
                        with uc1:
                            role = "🔑 Admin" if u["is_admin"] else "👤 Counter"
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
                    all_sess = get_all_sessions_admin()
                    if all_sess.empty:
                        st.info("No sessions.")
                    else:
                        for _, row in all_sess.iterrows():
                            sc1, sc2 = st.columns([4, 1])
                            with sc1:
                                st.markdown(f"""
                                <div style="padding:4px 0">
                                  <div style="font-weight:600;font-size:0.9rem">{row['sid']}</div>
                                  <div style="font-size:0.77rem;color:#8A9BAE">👤 {row['username']} · {row['client'] or '—'} · {row['updated'] or '—'}</div>
                                </div>""", unsafe_allow_html=True)
                            with sc2:
                                if st.button("Load", key=f"aload_{row['sid']}", use_container_width=True):
                                    loaded = load_audit_db(row["sid"])
                                    if loaded is not None:
                                        st.session_state.active_sid    = row["sid"]
                                        st.session_state.active_client = row["client"]
                                        st.session_state.df            = loaded
                                        st.session_state.save_counter  = 0
                                        st.session_state.selected_idx  = None
                                        st.session_state.selected_code = None
                                        st.rerun()
            with at3:
                with st.container(border=True):
                    section("Create New User")
                    nu_user  = st.text_input("Username", placeholder="e.g. john", key="nu_user")
                    nu_pass  = st.text_input("Password", type="password", key="nu_pass")
                    nu_admin = st.checkbox("Grant admin access", key="nu_admin")
                    if st.button("➕  Create User", use_container_width=True):
                        if not nu_user or not nu_pass:
                            st.warning("Username and password are required.")
                        else:
                            ok = create_user(nu_user, nu_pass, nu_admin)
                            st.success(f"User **{nu_user.strip().lower()}** created!") if ok else st.error("Username already exists.")
    st.stop()


# ─────────────────────────────────────────────
#  COUNTING SCREEN
# ─────────────────────────────────────────────
# FIX 2: Always reference st.session_state.df directly — never assign to a
# local variable 'df' and mutate that, because Streamlit won't see the change.
sid = st.session_state.active_sid

updated_mask = st.session_state.df["last_updated"] != ""
pct     = round(updated_mask.sum() / len(st.session_state.df) * 100, 1) if len(st.session_state.df) else 0.0
total   = len(st.session_state.df)
counted = int(updated_mask.sum())
n_vars  = int(((st.session_state.df["difference"] != 0) & updated_mask).sum())

render_header(username=CU, session_id=sid, is_admin=IS_ADMIN)
sync_status(st.session_state.save_counter)

with st.container(border=True):
    section("Count Overview")
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="stat-box"><div class="stat-label">Total</div><div class="stat-value">{total}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="stat-box"><div class="stat-label">Counted</div><div class="stat-value">{counted}</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="stat-box"><div class="stat-label">Variances</div><div class="stat-value" style="color:#DC2626">{n_vars}</div></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="prog-wrap">
      <div class="prog-head"><span>Progress</span><span><b style="color:#002855">{pct}%</b></span></div>
      <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SEARCH — FIX 1: replaced selectbox with buttons
#  so product names wrap to 2 lines on mobile
#  instead of being cut off with "..."
# ─────────────────────────────────────────────
with st.container(border=True):
    section("Enter Count")
    search = st.text_input("Search", placeholder="🔍  Product name or code…",
                           label_visibility="collapsed", key="search_input")

    if search and len(search.strip()) >= 1:
        q    = search.strip()
        mask = (st.session_state.df["product name"].str.contains(q, case=False, na=False) |
                st.session_state.df["product code"].str.contains(q, case=False, na=False))
        matches = st.session_state.df.loc[mask].head(20)

        if matches.empty:
            st.warning("No products found.")
        else:
            st.caption(f"{len(matches)} result{'s' if len(matches) != 1 else ''} — tap to select")
            for row_idx in matches.index:
                row      = st.session_state.df.loc[row_idx]
                tick     = "✅ " if row["last_updated"] else ""
                # Two-line label: code on first line, full name on second line
                btn_label = f"{tick}{row['product code']}  —  {row['product name']}"
                if st.button(btn_label, key=f"pick_{row_idx}", use_container_width=True):
                    st.session_state.selected_idx  = int(row_idx)
                    st.session_state.selected_code = str(row["product code"])
                    st.rerun()


# ─────────────────────────────────────────────
#  COUNT ENTRY — FIX 2: reads/writes through
#  st.session_state.df so Save and Close both work
# ─────────────────────────────────────────────
if st.session_state.get("selected_idx") is not None:
    idx = st.session_state.selected_idx

    if idx in st.session_state.df.index:
        row       = st.session_state.df.loc[idx]
        sys_qty   = int(row["systems count"])
        prev_phys = int(row["physical count"])

        with st.container(border=True):
            section("Physical Count")

            # Full product name displayed in a card — wraps naturally on any screen width
            st.markdown(f"""
            <div class="product-card">
              <div class="pc-code">{row['product code']}</div>
              <div class="pc-name">{row['product name']}</div>
            </div>""", unsafe_allow_html=True)

            if row["last_updated"]:
                st.caption(f"⏱ Last saved: {row['last_updated']}")

            q1, q2, q3 = st.columns(3)

            with q1:
                st.markdown(f'<div class="stat-box"><div class="stat-label">System Qty</div><div class="stat-value">{sys_qty}</div></div>', unsafe_allow_html=True)

            with q2:
                phys_val = st.number_input(
                    "Physical Count", value=prev_phys,
                    min_value=0, step=1, key=f"p_{idx}"
                )

            with q3:
                diff = phys_val - sys_qty
                cls  = "positive" if diff > 0 else "negative" if diff < 0 else "neutral"
                sign = "+" if diff > 0 else ""
                st.markdown(f'<div class="vbox {cls}"><div class="vbox-label">Variance</div><div class="vbox-value">{sign}{diff}</div></div>', unsafe_allow_html=True)

            # Live variance JS — cosmetic only, no Python rerun needed
            st.components.v1.html(f"""
            <script>
            (function() {{
              const sysQty = {sys_qty};
              function attach() {{
                const inputs = window.parent.document.querySelectorAll('input[type="number"]');
                let physIn = null;
                inputs.forEach(el => {{ if (el.closest('[data-testid="stNumberInput"]')) physIn = el; }});
                const vboxes = window.parent.document.querySelectorAll('.vbox-value');
                const vbox   = vboxes[vboxes.length - 1];
                const vboxEl = vbox ? vbox.closest('.vbox') : null;
                if (!physIn || !vbox) return;
                physIn.addEventListener('input', function() {{
                  const phys = parseInt(physIn.value) || 0;
                  const diff = phys - sysQty;
                  vbox.textContent = diff > 0 ? '+' + diff : String(diff);
                  if (diff > 0) {{
                    vboxEl.style.background = '#ECFDF5'; vboxEl.style.borderColor = '#6EE7B7';
                    vbox.style.color = '#059669';
                  }} else if (diff < 0) {{
                    vboxEl.style.background = '#FEF2F2'; vboxEl.style.borderColor = '#FCA5A5';
                    vbox.style.color = '#DC2626';
                  }} else {{
                    vboxEl.style.background = '#F4F6FA'; vboxEl.style.borderColor = '#E2E8F0';
                    vbox.style.color = '#0D1B2A';
                  }}
                }});
              }}
              attach(); setTimeout(attach, 500);
            }})();
            </script>
            """, height=0)

            # FIX 2: Save writes directly into st.session_state.df
            if st.button("💾  Save Count", use_container_width=True):
                now  = datetime.now().strftime("%H:%M:%S")
                diff = phys_val - sys_qty
                st.session_state.df.at[idx, "physical count"] = phys_val
                st.session_state.df.at[idx, "difference"]     = diff
                st.session_state.df.at[idx, "last_updated"]   = now
                st.session_state.save_counter += 1
                # Clear selection so form closes after save
                st.session_state.selected_idx  = None
                st.session_state.selected_code = None

                set_local_storage("bdo_df",      df_to_json(st.session_state.df))
                set_local_storage("bdo_counter", str(st.session_state.save_counter))

                p_code = str(row["product code"])
                if st.session_state.save_counter % 10 == 0:
                    save_audit_db(sid, CU, st.session_state.get("active_client",""), st.session_state.df)
                    st.toast(f"✅ {p_code} · ☁️ backed up!")
                else:
                    left = 10 - (st.session_state.save_counter % 10)
                    st.toast(f"✅ {p_code} saved · backup in {left}")
                st.rerun()

            # Cancel button — clears selection without saving
            if st.button("✖  Cancel", use_container_width=True):
                st.session_state.selected_idx  = None
                st.session_state.selected_code = None
                st.rerun()


# ─────────────────────────────────────────────
#  RECENT COUNTS
# ─────────────────────────────────────────────
recent_mask = st.session_state.df["last_updated"] != ""
if recent_mask.any():
    recent = (st.session_state.df.loc[recent_mask,
              ["product name","product code","difference","last_updated"]]
              .sort_values("last_updated", ascending=False).head(5))
    with st.container(border=True):
        section("Recent Counts")
        for _, r in recent.iterrows():
            d = int(r["difference"])
            badge = (f'<span class="badge-pos">+{d}</span>' if d > 0 else
                     f'<span class="badge-neg">{d}</span>'  if d < 0 else
                     f'<span class="badge-zero">±0</span>')
            st.markdown(f"""
            <div class="log-row">
              <div>
                <div class="log-name">{r['product name']}</div>
                <div class="log-meta">{r['product code']} · {r['last_updated']}</div>
              </div>
              {badge}
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  FOOTER ACTIONS
# ─────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
fa1, fa2, fa3 = st.columns(3)

with fa1:
    out_all = io.BytesIO()
    with pd.ExcelWriter(out_all, engine="openpyxl") as w:
        st.session_state.df.to_excel(w, index=False, sheet_name="Stock Count")
    st.download_button("📤 Export All", out_all.getvalue(),
        file_name=f"{sid}_StockCount_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

with fa2:
    out_var = io.BytesIO()
    with pd.ExcelWriter(out_var, engine="openpyxl") as w:
        st.session_state.df[st.session_state.df["difference"] != 0].to_excel(
            w, index=False, sheet_name="Variances")
    st.download_button("⚠️ Variances", out_var.getvalue(),
        file_name=f"{sid}_Variances_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

with fa3:
    # FIX 2: Backup Now uses st.session_state.df — same object Save writes to
    if st.button("☁️ Backup Now", use_container_width=True):
        save_audit_db(sid, CU, st.session_state.get("active_client",""), st.session_state.df)
        set_local_storage("bdo_counter", "0")
        st.session_state.save_counter = 0
        st.toast("☁️ Backed up to cloud!")
        st.rerun()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# FIX 2: Save & Close uses st.session_state.df — guaranteed to have latest counts
if st.button("🚪 Save & Close", use_container_width=True):
    save_audit_db(sid, CU, st.session_state.get("active_client",""), st.session_state.df)
    clear_local_storage()
    set_local_storage("bdo_user", CU)
    for k in ["active_sid","active_client","df","save_counter","selected_idx","selected_code"]:
        st.session_state.pop(k, None)
    st.query_params.clear()
    st.rerun()
