import streamlit as st
import pandas as pd
import psycopg2
import psycopg2.extras
import hashlib
import io
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="BDO Audit Pro",
    page_icon="🔷",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── NUCLEAR RESET ── */
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

/* ── FORCE LIGHT MODE ── */
html, body { color-scheme: light !important; }
.stApp {
    background-color: #F4F6FA !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #0D1B2A !important;
    color-scheme: light !important;
}
.stApp * { color: #0D1B2A !important; }

/* ── Blue header — white text ── */
.app-header * { color: #ffffff !important; }
.app-header .brand span { color: #5BC4FF !important; }
.app-header .admin-badge { color: #92400E !important; }

html, body,
section[data-testid="stMain"],
div[data-testid="stAppViewContainer"] {
    background-color: #F4F6FA !important;
}

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

/* ── Bordered containers ── */
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

/* ── Header ── */
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

/* ── Inputs ── */
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

/* ── Buttons ── */
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

/* ── Tabs ── */
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

/* ── Stat boxes ── */
.stat-box { background: #F4F6FA; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 10px; text-align: center; }
.stat-label { font-size: 0.69rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #8A9BAE; margin-bottom: 5px; }
.stat-value { font-size: 1.85rem; font-weight: 700; color: #002855; line-height: 1; }

/* ── Variance box ── */
.vbox { border-radius: 12px; padding: 14px 10px; text-align: center; }
.vbox.neutral  { background: #F4F6FA; border: 1px solid #E2E8F0; }
.vbox.positive { background: #ECFDF5; border: 1px solid #6EE7B7; }
.vbox.negative { background: #FEF2F2; border: 1px solid #FCA5A5; }
.vbox-label { font-size: 0.69rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #8A9BAE; margin-bottom: 5px; }
.vbox-value { font-size: 1.85rem; font-weight: 700; line-height: 1; }
.vbox.neutral  .vbox-value { color: #0D1B2A; }
.vbox.positive .vbox-value { color: #059669; }
.vbox.negative .vbox-value { color: #DC2626; }

/* ── Progress ── */
.prog-wrap { margin-top: 16px; }
.prog-head { display: flex; justify-content: space-between; font-size: 0.77rem; color: #8A9BAE; margin-bottom: 6px; }
.prog-track { background: #E2E8F0; border-radius: 999px; height: 7px; overflow: hidden; }
.prog-fill  { background: linear-gradient(90deg, #002855, #5BC4FF); height: 100%; border-radius: 999px; }

/* ── Log row ── */
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
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed #CBD5E0 !important; border-radius: 12px !important; background: #F8FAFC !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SECURITY
# ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode()).hexdigest()


# ─────────────────────────────────────────────
#  DATABASE — SUPABASE (PostgreSQL)
# ─────────────────────────────────────────────
def get_db():
    url = st.secrets["DATABASE_URL"]
    conn = psycopg2.connect(url, connect_timeout=10)
    conn.autocommit = True
    return conn

def run(sql, params=(), fetch=None):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        if fetch == "one": return cur.fetchone()
        if fetch == "all": return cur.fetchall()
    finally:
        conn.close()

def init_db():
    run("""
        CREATE TABLE IF NOT EXISTS users (
            username      TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            is_admin      BOOLEAN DEFAULT FALSE,
            created       TEXT
        )
    """)
    run("""
        CREATE TABLE IF NOT EXISTS audit_sessions (
            sid      TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            client   TEXT,
            data     BYTEA,
            updated  TEXT
        )
    """)
    # Seed default admin if no users exist
    row = run("SELECT COUNT(*) as c FROM users", fetch="one")
    if row and row["c"] == 0:
        run(
            "INSERT INTO users VALUES (%s, %s, %s, %s)",
            ("admin", hash_password("admin123"), True, datetime.now().strftime("%Y-%m-%d"))
        )

init_db()


# ─────────────────────────────────────────────
#  USER CRUD
# ─────────────────────────────────────────────
def get_user(username: str):
    return run(
        "SELECT username, password_hash, is_admin FROM users WHERE username=%s",
        (username.strip().lower(),), fetch="one"
    )

def get_all_users():
    rows = run("SELECT username, is_admin, created FROM users ORDER BY username", fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["username","is_admin","created"])

def create_user(username: str, password: str, is_admin: bool = False) -> bool:
    username = username.strip().lower()
    if not username or not password:
        return False
    existing = get_user(username)
    if existing:
        return False
    run(
        "INSERT INTO users VALUES (%s, %s, %s, %s)",
        (username, hash_password(password), is_admin, datetime.now().strftime("%Y-%m-%d"))
    )
    return True

def delete_user(username: str):
    run("DELETE FROM users WHERE username=%s", (username,))

def change_password(username: str, new_password: str):
    run("UPDATE users SET password_hash=%s WHERE username=%s",
        (hash_password(new_password), username))


# ─────────────────────────────────────────────
#  AUDIT SESSION CRUD
# ─────────────────────────────────────────────
def save_audit(sid: str, username: str, client: str, df: pd.DataFrame):
    buf = io.BytesIO()
    df.to_pickle(buf)
    data = psycopg2.Binary(buf.getvalue())
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M")
    run("""
        INSERT INTO audit_sessions (sid, username, client, data, updated)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (sid) DO UPDATE
        SET data=%s, client=%s, updated=%s
    """, (sid, username, client, data, ts, data, client, ts))

def load_audit(sid: str):
    row = run("SELECT data FROM audit_sessions WHERE sid=%s", (sid,), fetch="one")
    if row:
        return pd.read_pickle(io.BytesIO(bytes(row["data"])))
    return None

def get_user_sessions(username: str) -> pd.DataFrame:
    rows = run(
        "SELECT sid, client, updated FROM audit_sessions WHERE username=%s ORDER BY updated DESC",
        (username,), fetch="all"
    )
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["sid","client","updated"])

def get_all_sessions_admin() -> pd.DataFrame:
    rows = run(
        "SELECT sid, username, client, updated FROM audit_sessions ORDER BY updated DESC",
        fetch="all"
    )
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["sid","username","client","updated"])


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
    df["product code"]  = df["product code"].astype(str).str.strip()
    df["product name"]  = df["product name"].astype(str).str.strip()
    df["systems count"] = pd.to_numeric(df["systems count"], errors="coerce").fillna(0)
    if "physical count" in df.columns:
        df["physical count"] = pd.to_numeric(df["physical count"], errors="coerce").fillna(0).astype(int)
    else:
        df["physical count"] = 0
    df["difference"]   = 0
    df["last_updated"] = ""
    return df

def pct_done(df):
    n = len(df)
    return round((df["last_updated"] != "").sum() / n * 100, 1) if n else 0.0

def render_header(username="", session_id="", is_admin=False):
    admin_badge = '<span class="admin-badge">ADMIN</span>' if is_admin else ""
    user_pill   = f'<span class="user-pill">👤 {username}{admin_badge}</span>' if username else ""
    sess_pill   = f'<span class="session-pill">📍 {session_id}</span>' if session_id else ""
    st.markdown(f"""
    <div class="app-header">
        <div class="brand">🔷 BDO <span>Audit Pro</span></div>
        <div class="right">{sess_pill}{user_pill}</div>
    </div>""", unsafe_allow_html=True)

def section(label):
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────
if "current_user" not in st.session_state:
    st.session_state.current_user = None
    st.session_state.is_admin     = False

if st.session_state.current_user is None:
    render_header()
    with st.container(border=True):
        section("Sign In")
        st.markdown("#### Welcome to BDO Audit Pro")
        st.write("Enter your credentials to access your audits.")
        username_input = st.text_input("Username", placeholder="your username")
        password_input = st.text_input("Password", type="password", placeholder="••••••••")
        if st.button("Sign In →", use_container_width=True):
            uname = username_input.strip().lower()
            row   = get_user(uname)
            if row and row["password_hash"] == hash_password(password_input):
                st.session_state.current_user = row["username"]
                st.session_state.is_admin     = bool(row["is_admin"])
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
        cp1 = st.text_input("New password", type="password", key="cp1")
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
        for k in ["current_user", "is_admin", "active_sid", "active_client", "df"]:
            st.session_state.pop(k, None)
        st.rerun()


# ─────────────────────────────────────────────
#  SESSION SELECTION
# ─────────────────────────────────────────────
if "active_sid" not in st.session_state:
    render_header(username=CU, is_admin=IS_ADMIN)

    tabs     = (["  ✨  New Audit  ", "  📁  My Audits  ", "  ⚙️  Admin Panel  "]
                if IS_ADMIN else
                ["  ✨  New Audit  ", "  📁  My Audits  "])
    tab_objs = st.tabs(tabs)
    t1, t2   = tab_objs[0], tab_objs[1]

    # ── New Audit ──
    with t1:
        with st.container(border=True):
            section("Start New Count")
            sid_new    = st.text_input("Session ID", placeholder="e.g. BDO-2026-001")
            client_new = st.text_input("Client / Location", placeholder="e.g. Warehouse A")
            file_new   = st.file_uploader("Upload Master Sheet (.xlsx)", type=["xlsx"])
            if file_new:
                st.caption(f"📎 {file_new.name} — ready")
            if st.button("🚀  Start Audit", use_container_width=True):
                if not sid_new:
                    st.warning("Please enter a Session ID.")
                elif not file_new:
                    st.warning("Please upload a master sheet.")
                else:
                    existing = run("SELECT 1 FROM audit_sessions WHERE sid=%s", (sid_new,), fetch="one")
                    if existing:
                        st.error(f"Session ID **{sid_new}** is already taken.")
                    else:
                        try:
                            df = normalise_df(pd.read_excel(file_new))
                            st.session_state.active_sid    = sid_new
                            st.session_state.active_client = client_new
                            st.session_state.df            = df
                            save_audit(sid_new, CU, client_new, df)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to read file: {e}")

    # ── My Audits ──
    with t2:
        with st.container(border=True):
            section("My Sessions")
            history = get_user_sessions(CU)
            if history.empty:
                st.info("You have no saved audit sessions yet.")
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
                            loaded = load_audit(row["sid"])
                            if loaded is not None:
                                st.session_state.active_sid    = row["sid"]
                                st.session_state.active_client = row["client"]
                                st.session_state.df            = loaded
                                st.rerun()
                            else:
                                st.error("Could not load session.")

    # ── Admin Panel ──
    if IS_ADMIN:
        t3 = tab_objs[2]
        with t3:
            at1, at2, at3 = st.tabs(["  👥  Users  ", "  📋  All Audits  ", "  ➕  Add User  "])

            with at1:
                with st.container(border=True):
                    section("All Users")
                    all_users = get_all_users()
                    for _, u in all_users.iterrows():
                        uc1, uc2 = st.columns([4, 1])
                        with uc1:
                            role = "🔑 Admin" if u["is_admin"] else "👤 Auditor"
                            st.markdown(f"""
                            <div class="user-row">
                              <div>
                                <div class="user-name">{u['username']}</div>
                                <div class="user-meta">{role} · Joined {u['created'] or '—'}</div>
                              </div>
                            </div>""", unsafe_allow_html=True)
                        with uc2:
                            if u["username"] != CU:
                                if st.button("Delete", key=f"del_{u['username']}", use_container_width=True):
                                    delete_user(u["username"])
                                    st.success(f"Deleted {u['username']}")
                                    st.rerun()
                            else:
                                st.caption("(you)")

            with at2:
                with st.container(border=True):
                    section("All Audit Sessions")
                    all_sess = get_all_sessions_admin()
                    if all_sess.empty:
                        st.info("No sessions found.")
                    else:
                        for _, row in all_sess.iterrows():
                            sc1, sc2 = st.columns([4, 1])
                            with sc1:
                                st.markdown(f"""
                                <div style="padding:4px 0">
                                  <div style="font-weight:600;font-size:0.9rem">{row['sid']}</div>
                                  <div style="font-size:0.77rem;color:#8A9BAE">
                                    👤 {row['username']} · {row['client'] or '—'} · {row['updated'] or '—'}
                                  </div>
                                </div>""", unsafe_allow_html=True)
                            with sc2:
                                if st.button("Load", key=f"aload_{row['sid']}", use_container_width=True):
                                    loaded = load_audit(row["sid"])
                                    if loaded is not None:
                                        st.session_state.active_sid    = row["sid"]
                                        st.session_state.active_client = row["client"]
                                        st.session_state.df            = loaded
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
                            if ok:
                                st.success(f"User **{nu_user.strip().lower()}** created!")
                            else:
                                st.error(f"Username **{nu_user}** already exists.")

    st.stop()


# ─────────────────────────────────────────────
#  MAIN COUNTING SCREEN
# ─────────────────────────────────────────────
df  = st.session_state.df
sid = st.session_state.active_sid
pct = pct_done(df)
total   = len(df)
counted = int((df["last_updated"] != "").sum())
n_vars  = int(((df["difference"] != 0) & (df["last_updated"] != "")).sum())

render_header(username=CU, session_id=sid, is_admin=IS_ADMIN)

with st.container(border=True):
    section("Session Overview")
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="stat-box"><div class="stat-label">Total Items</div><div class="stat-value">{total}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="stat-box"><div class="stat-label">Counted</div><div class="stat-value">{counted}</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="stat-box"><div class="stat-label">Variances</div><div class="stat-value" style="color:#DC2626">{n_vars}</div></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="prog-wrap">
      <div class="prog-head"><span>Progress</span><span><b style="color:#002855">{pct}%</b> complete</span></div>
      <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
    </div>""", unsafe_allow_html=True)

with st.container(border=True):
    section("Count Entry")
    search = st.text_input("Search", placeholder="🔍  Product name or code…", label_visibility="collapsed")

    if search and search.strip():
        mask = (
            df["product name"].str.contains(search.strip(), case=False, na=False) |
            df["product code"].str.contains(search.strip(), case=False, na=False)
        )
        matches = df[mask]
        if matches.empty:
            st.warning("No products found.")
        else:
            opts   = matches.apply(lambda x: f"{x['product code']}  —  {x['product name']}", axis=1).tolist()
            choice = st.selectbox("Product", opts, label_visibility="collapsed")
            p_code = choice.split("  —  ")[0].strip()
            idxs   = df[df["product code"] == p_code].index.tolist()

            if idxs:
                idx       = idxs[0]
                sys_qty   = int(df.at[idx, "systems count"])
                prev_phys = int(df.at[idx, "physical count"])
                already   = df.at[idx, "last_updated"] != ""

                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                q1, q2, q3 = st.columns(3)
                with q1:
                    st.markdown(f'<div class="stat-box"><div class="stat-label">System Qty</div><div class="stat-value">{sys_qty}</div></div>', unsafe_allow_html=True)
                with q2:
                    phys_val = st.number_input("Physical Count", value=prev_phys, min_value=0, step=1, key=f"p_{idx}")
                with q3:
                    diff = phys_val - sys_qty
                    cls  = "positive" if diff > 0 else "negative" if diff < 0 else "neutral"
                    sign = "+" if diff > 0 else ""
                    st.markdown(f'<div class="vbox {cls}"><div class="vbox-label">Variance</div><div class="vbox-value">{sign}{diff}</div></div>', unsafe_allow_html=True)

                if already:
                    st.caption(f"⏱ Last saved: {df.at[idx, 'last_updated']}")

                if st.button("💾  Save Count", use_container_width=True):
                    df.at[idx, "physical count"] = phys_val
                    df.at[idx, "difference"]     = diff
                    df.at[idx, "last_updated"]   = datetime.now().strftime("%H:%M:%S")
                    st.session_state.df = df
                    save_audit(sid, CU, st.session_state.get("active_client", ""), df)
                    st.toast(f"Saved {p_code} ✅")
                    st.rerun()

recent = df[df["last_updated"] != ""].sort_values("last_updated", ascending=False).head(5)
if not recent.empty:
    with st.container(border=True):
        section("Recent Activity")
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

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
fa1, fa2, fa3 = st.columns(3)

with fa1:
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Audit")
    st.download_button("📤 Export All", out.getvalue(),
        file_name=f"{sid}_Audit_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

with fa2:
    out2 = io.BytesIO()
    with pd.ExcelWriter(out2, engine="openpyxl") as w:
        df[df["difference"] != 0].to_excel(w, index=False, sheet_name="Variances")
    st.download_button("⚠️ Variances", out2.getvalue(),
        file_name=f"{sid}_Variances_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

with fa3:
    if st.button("🚪 Close Session", use_container_width=True):
        for k in ["active_sid", "active_client", "df"]:
            st.session_state.pop(k, None)
        st.rerun()
