import streamlit as st
import pandas as pd
import psycopg2
import psycopg2.extras
import hashlib
import io
import json
from datetime import datetime

st.set_page_config(
    page_title="Stock Count Pro",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

SHARED_CSS = """
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
  background:transparent!important;box-shadow:none!important;border:none!important}
html,body{color-scheme:light!important}
.stApp{background:#F4F6FA!important;font-family:'DM Sans',sans-serif!important;color:#0D1B2A!important}
.stApp *{color:#0D1B2A!important}
.app-header *{color:#fff!important}
.app-header .brand span{color:#5BC4FF!important}
html,body,section[data-testid="stMain"],
div[data-testid="stAppViewContainer"]{background:#F4F6FA!important}
input,textarea,select{color:#0D1B2A!important;background:#F8FAFC!important;-webkit-text-fill-color:#0D1B2A!important}
input::placeholder,textarea::placeholder{color:#A0AEC0!important;-webkit-text-fill-color:#A0AEC0!important;opacity:1!important}
[data-baseweb="select"] *{color:#0D1B2A!important}
[data-baseweb="menu"]{background:#fff!important}
[data-baseweb="option"]{background:#fff!important;color:#0D1B2A!important}
[data-baseweb="option"]:hover{background:#EEF2F7!important}
.stTabs [data-baseweb="tab"]{color:#5A6A7A!important}
.stTabs [aria-selected="true"]{color:#002855!important}
section[data-testid="stSidebar"]{background:#fff!important;border-right:1px solid #E2E8F0!important}
section[data-testid="stSidebar"] *{color:#0D1B2A!important}
div[data-testid="stExpander"]{background:#fff!important;border:1px solid #E2E8F0!important;border-radius:10px!important}
.stCheckbox label,.stCheckbox span{color:#0D1B2A!important}
.stCaption,small{color:#8A9BAE!important}
div[data-testid="stToast"]{background:#fff!important;border:1px solid #E2E8F0!important}
div[data-testid="stAlert"]{background:transparent!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:2rem 1.5rem 4rem!important;max-width:720px!important}
div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff!important;
  border:1px solid #E2E8F0!important;border-radius:16px!important;
  box-shadow:0 2px 14px rgba(0,0,0,.06)!important;padding:4px 0!important;margin-bottom:18px!important}
div[data-testid="stVerticalBlockBorderWrapper"]>div{background:transparent!important;
  box-shadow:none!important;border:none!important}
.app-header{background:linear-gradient(135deg,#002855,#00509E);border-radius:16px;
  padding:22px 28px;margin-bottom:24px;display:flex;align-items:center;
  justify-content:space-between;box-shadow:0 4px 24px rgba(0,40,85,.18)}
.app-header .brand{font-size:1.4rem;font-weight:700;letter-spacing:-.5px}
.app-header .right{display:flex;align-items:center;gap:10px}
.app-header .user-pill{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.28);
  border-radius:999px;padding:5px 14px;font-size:.78rem;font-weight:500;font-family:'DM Mono',monospace}
.admin-badge{display:inline-block;background:#FEF3C7;border:1px solid #FCD34D;
  border-radius:6px;padding:2px 8px;font-size:.72rem;font-weight:700;
  color:#92400E!important;letter-spacing:.5px;margin-left:8px;vertical-align:middle}
.section-label{font-size:.71rem;font-weight:700;text-transform:uppercase;
  letter-spacing:1.2px;color:#8A9BAE;margin-bottom:14px}
.stTextInput>div>div>input,.stNumberInput>div>div>input{
  border:1.5px solid #CBD5E0!important;border-radius:10px!important;
  padding:10px 14px!important;font-size:.95rem!important;
  background:#F8FAFC!important;color:#0D1B2A!important}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus{
  border-color:#00509E!important;box-shadow:0 0 0 3px rgba(0,80,158,.1)!important;outline:none!important}
.stButton>button,.stDownloadButton>button{
  background:linear-gradient(135deg,#002855,#00509E)!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-weight:600!important;font-size:.88rem!important;
  height:auto!important;min-height:46px!important;
  box-shadow:0 2px 8px rgba(0,80,158,.22)!important;
  white-space:normal!important;word-break:break-word!important;
  text-align:left!important;padding:10px 14px!important;line-height:1.4!important}
.stButton>button *,.stDownloadButton>button *{color:#fff!important}
.stTabs [data-baseweb="tab-list"]{background:#EEF2F7!important;border-radius:10px!important;
  padding:4px!important;gap:4px!important;border-bottom:none!important}
.stTabs [data-baseweb="tab"]{border-radius:8px!important;font-weight:600!important;
  font-size:.88rem!important;padding:8px 20px!important;border:none!important;background:transparent!important}
.stTabs [aria-selected="true"]{background:#fff!important;color:#002855!important;
  box-shadow:0 1px 6px rgba(0,0,0,.1)!important}
[data-testid="stFileUploaderDropzone"]{border:2px dashed #CBD5E0!important;
  border-radius:12px!important;background:#F8FAFC!important}
.divider{border:none;border-top:1px solid #E2E8F0;margin:18px 0}
/* Mode cards */
.mode-card{border-radius:16px;padding:20px;margin-bottom:12px;cursor:pointer;
  border:2px solid #E2E8F0;background:#fff;transition:all .2s}
.mode-card.s2f{border-color:#00509E;background:#EEF5FF}
.mode-card.f2s{border-color:#059669;background:#ECFDF5}
.mode-icon{font-size:2rem;margin-bottom:8px}
.mode-title{font-size:1rem;font-weight:700;color:#002855;margin-bottom:4px}
.mode-title.green{color:#065F46}
.mode-desc{font-size:.82rem;color:#5A6A7A;line-height:1.5}
.mode-excel{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;
  padding:8px 12px;margin-top:10px;font-size:.78rem;color:#374151}
.mode-excel code{background:#E2E8F0;border-radius:4px;padding:1px 5px;
  font-family:'DM Mono',monospace;font-size:.76rem;color:#002855!important}
/* Session list */
.sess-row{display:flex;align-items:center;justify-content:space-between;gap:10px;
  padding:11px 14px;background:#F8FAFC;border:1px solid #E8EDF3;border-radius:10px;margin-bottom:7px}
.sess-left{flex:1;min-width:0}
.sess-sid{font-weight:600;font-size:.9rem;color:#002855}
.sess-meta{font-size:.76rem;color:#8A9BAE;margin-top:2px}
.mode-pill-s2f{display:inline-block;background:#EEF5FF;border:1px solid #93C5FD;
  border-radius:6px;padding:1px 7px;font-size:.7rem;font-weight:700;color:#1D4ED8!important;margin-right:5px}
.mode-pill-f2s{display:inline-block;background:#ECFDF5;border:1px solid #6EE7B7;
  border-radius:6px;padding:1px 7px;font-size:.7rem;font-weight:700;color:#065F46!important;margin-right:5px}
.user-row{display:flex;align-items:center;justify-content:space-between;
  padding:10px 14px;background:#F8FAFC;border:1px solid #E8EDF3;border-radius:10px;margin-bottom:7px}
</style>
"""
st.markdown(SHARED_CSS, unsafe_allow_html=True)


# ── SECURITY ───────────────────────────────────────────────────────
def hash_password(p): return hashlib.sha256(p.strip().encode()).hexdigest()


# ── DATABASE ───────────────────────────────────────────────────────
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
    run("""CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,created TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS audit_sessions(
            sid TEXT PRIMARY KEY,username TEXT NOT NULL,
            client TEXT,data BYTEA,updated TEXT,
            mode TEXT DEFAULT 'sheet_to_floor')""")
    # Add mode column if upgrading from old version
    run("ALTER TABLE audit_sessions ADD COLUMN IF NOT EXISTS mode TEXT DEFAULT 'sheet_to_floor'")

init_db()


# ── USER CRUD ──────────────────────────────────────────────────────
def get_user(u):
    return run("SELECT username,password_hash,is_admin FROM users WHERE username=%s",
               (u.strip().lower(),), fetch="one")

def get_all_users():
    rows = run("SELECT username,is_admin,created FROM users ORDER BY created ASC", fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["username","is_admin","created"])

def user_count():
    r = run("SELECT COUNT(*) as c FROM users", fetch="one")
    return r["c"] if r else 0

def create_user(u, p, is_admin=False):
    u = u.strip().lower()
    if not u or not p or get_user(u): return False
    run("INSERT INTO users VALUES(%s,%s,%s,%s)",
        (u, hash_password(p), is_admin, datetime.now().strftime("%Y-%m-%d")))
    return True

def delete_user(u): run("DELETE FROM users WHERE username=%s", (u,))
def set_admin(u, v): run("UPDATE users SET is_admin=%s WHERE username=%s", (v, u))
def change_password(u, p): run("UPDATE users SET password_hash=%s WHERE username=%s", (hash_password(p), u))


# ── SESSION CRUD ───────────────────────────────────────────────────
def df_to_bytes(df):
    cols = ["product code","product name","systems count","physical count","difference","last_updated"]
    buf  = io.BytesIO()
    df[[c for c in cols if c in df.columns]].to_pickle(buf, compression="gzip")
    return buf.getvalue()

def bytes_to_df(raw):
    try:    return pd.read_pickle(io.BytesIO(raw), compression="gzip")
    except: return pd.read_pickle(io.BytesIO(raw))

def save_session(sid, username, client, df, mode="sheet_to_floor"):
    data = psycopg2.Binary(df_to_bytes(df))
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M")
    run("""INSERT INTO audit_sessions(sid,username,client,data,updated,mode)
           VALUES(%s,%s,%s,%s,%s,%s)
           ON CONFLICT(sid) DO UPDATE
           SET data=%s,client=%s,updated=%s,mode=%s""",
        (sid,username,client,data,ts,mode, data,client,ts,mode))

def load_session(sid):
    row = run("SELECT data FROM audit_sessions WHERE sid=%s", (sid,), fetch="one")
    return bytes_to_df(bytes(row["data"])) if row else None

def get_user_sessions(username):
    rows = run("""SELECT sid,client,updated,mode FROM audit_sessions
                  WHERE username=%s ORDER BY updated DESC""", (username,), fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["sid","client","updated","mode"])

def get_all_sessions():
    rows = run("SELECT sid,username,client,updated,mode FROM audit_sessions ORDER BY updated DESC", fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["sid","username","client","updated","mode"])

def delete_session(sid):
    run("DELETE FROM audit_sessions WHERE sid=%s", (sid,))


# ── LOCAL STORAGE ──────────────────────────────────────────────────
def set_ls(key, value):
    safe = value.replace("`","\\`").replace("\\","\\\\")
    st.components.v1.html(f'<script>localStorage.setItem("{key}",`{safe}`);</script>', height=0)

def clear_ls():
    st.components.v1.html("""
    <script>["bdo_user","bdo_sid","bdo_client","bdo_mode"].forEach(k=>localStorage.removeItem(k));</script>
    """, height=0)


# ── UI HELPERS ─────────────────────────────────────────────────────
def render_header(username="", is_admin=False):
    badge = '<span class="admin-badge">ADMIN</span>' if is_admin else ""
    pill  = f'<span class="user-pill">👤 {username}{badge}</span>' if username else ""
    st.markdown(f"""
    <div class="app-header">
      <div class="brand">📦 Stock <span style="color:#5BC4FF">Count Pro</span></div>
      <div class="right">{pill}</div>
    </div>""", unsafe_allow_html=True)

def section(t):
    st.markdown(f'<div class="section-label">{t}</div>', unsafe_allow_html=True)


# ── SESSION STATE INIT ─────────────────────────────────────────────
if "init" not in st.session_state:
    st.session_state.init         = True
    st.session_state.current_user = None
    st.session_state.is_admin     = False

qp      = st.query_params
ls_user = qp.get("ls_user", "")

if ls_user and not st.session_state.current_user:
    row = get_user(ls_user)
    if row:
        st.session_state.current_user = row["username"]
        st.session_state.is_admin     = bool(row["is_admin"])


# ══════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════
if not st.session_state.current_user:
    render_header()

    st.components.v1.html("""
    <script>
    const u=localStorage.getItem("bdo_user");
    if(u){const url=new URL(window.parent.location.href);
      url.searchParams.set("ls_user",u);
      window.parent.location.href=url.toString();}
    </script>""", height=0)

    tab_in, tab_up = st.tabs(["  🔑  Sign In  ","  ✏️  Create Account  "])

    with tab_in:
        with st.container(border=True):
            section("Sign In")
            u_in = st.text_input("Username", placeholder="your username", key="li_u")
            p_in = st.text_input("Password", type="password", placeholder="••••••••", key="li_p")
            if st.button("Sign In →", use_container_width=True, key="li_btn"):
                row = get_user(u_in)
                if row and row["password_hash"] == hash_password(p_in):
                    st.session_state.current_user = row["username"]
                    st.session_state.is_admin     = bool(row["is_admin"])
                    set_ls("bdo_user", row["username"])
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

    with tab_up:
        with st.container(border=True):
            section("Create Account")
            st.caption("The first account registered becomes the admin automatically.")
            su_u  = st.text_input("Choose a username", placeholder="e.g. john", key="su_u")
            su_p  = st.text_input("Choose a password", type="password", key="su_p")
            su_p2 = st.text_input("Confirm password",  type="password", key="su_p2")
            if st.button("Create Account →", use_container_width=True, key="su_btn"):
                u = su_u.strip().lower()
                if not u or not su_p:          st.warning("Username and password required.")
                elif len(su_p) < 4:            st.warning("Password must be at least 4 characters.")
                elif su_p != su_p2:            st.error("Passwords do not match.")
                elif get_user(u):              st.error(f"Username **{u}** already taken.")
                else:
                    first = user_count() == 0
                    create_user(u, su_p, is_admin=first)
                    row = get_user(u)
                    st.session_state.current_user = row["username"]
                    st.session_state.is_admin     = bool(row["is_admin"])
                    set_ls("bdo_user", row["username"])
                    msg = "Welcome! You're the first user — admin access granted." if first else f"Account created! Welcome, **{u}**."
                    st.success(msg)
                    st.rerun()
    st.stop()


CU       = st.session_state.current_user
IS_ADMIN = st.session_state.is_admin


# ── SIDEBAR ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**Signed in as:** `{CU}`")
    st.markdown("**Role:** Admin 🔑" if IS_ADMIN else "**Role:** Counter 📦")
    st.divider()
    with st.expander("🔒 Change Password"):
        cp1 = st.text_input("New password",     type="password", key="cp1")
        cp2 = st.text_input("Confirm password", type="password", key="cp2")
        if st.button("Update Password"):
            if not cp1:        st.warning("Cannot be empty.")
            elif cp1 != cp2:   st.error("Passwords do not match.")
            else:              change_password(CU, cp1); st.success("Updated!")
    st.divider()
    if st.button("🚪 Sign Out", use_container_width=True):
        clear_ls()
        for k in ["current_user","is_admin","init"]:
            st.session_state.pop(k, None)
        st.query_params.clear()
        st.rerun()


# ══════════════════════════════════════════════════════════════════
#  DASHBOARD — session setup + mode selection
# ══════════════════════════════════════════════════════════════════
render_header(username=CU, is_admin=IS_ADMIN)

tab_labels = (["  ✨  New Count  ","  📁  My Sessions  ","  ⚙️  Admin Panel  "]
              if IS_ADMIN else ["  ✨  New Count  ","  📁  My Sessions  "])
tabs = st.tabs(tab_labels)
t_new, t_my = tabs[0], tabs[1]


# ── NEW COUNT ──────────────────────────────────────────────────────
with t_new:
    with st.container(border=True):
        section("Session Details")
        sid_in  = st.text_input("Session ID",           placeholder="e.g. SC-2026-001")
        loc_in  = st.text_input("Warehouse / Location", placeholder="e.g. Main Warehouse")

    # Mode selection cards
    st.markdown("""
    <div class="section-label" style="margin-top:4px">Choose Count Type</div>
    <div class="mode-card s2f">
      <div class="mode-icon">📋➡️📦</div>
      <div class="mode-title">Sheet to Floor</div>
      <div class="mode-desc">You have a system stock list. Walk the warehouse and verify
      what's physically there against your system quantities. Variances are calculated automatically.</div>
      <div class="mode-excel">
        Excel needs: <code>product code</code> <code>product name</code> <code>systems count</code>
      </div>
    </div>
    <div class="mode-card f2s">
      <div class="mode-icon">📦➡️📋</div>
      <div class="mode-title" style="color:#065F46">Floor to Sheet</div>
      <div class="mode-desc">You have a product list but no system quantities. Walk the warehouse,
      count what you find, and build the count sheet from scratch.</div>
      <div class="mode-excel">
        Excel needs: <code>product code</code> <code>product name</code> &nbsp;— no system count column needed
      </div>
    </div>
    """, unsafe_allow_html=True)

    file_in = st.file_uploader("Upload Excel Sheet (.xlsx)", type=["xlsx"])
    if file_in: st.caption(f"📎 {file_in.name} — ready")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("📋➡️📦  Sheet to Floor", use_container_width=True):
            if not sid_in:   st.warning("Please enter a Session ID.")
            elif not file_in: st.warning("Please upload your Excel sheet.")
            else:
                if run("SELECT 1 FROM audit_sessions WHERE sid=%s",(sid_in,),fetch="one"):
                    st.error(f"Session **{sid_in}** already exists.")
                else:
                    try:
                        df = pd.read_excel(file_in)
                        df.columns = [c.strip().lower() for c in df.columns]
                        needed = {"product code","product name","systems count"}
                        missing = needed - set(df.columns)
                        if missing:
                            st.error(f"Missing columns: {', '.join(missing)}")
                        else:
                            df["product code"]   = df["product code"].astype(str).str.strip()
                            df["product name"]   = df["product name"].astype(str).str.strip()
                            df["systems count"]  = pd.to_numeric(df["systems count"],errors="coerce").fillna(0)
                            df["physical count"] = 0
                            df["difference"]     = 0
                            df["last_updated"]   = ""
                            save_session(sid_in, CU, loc_in, df, mode="sheet_to_floor")
                            st.session_state.active_sid    = sid_in
                            st.session_state.active_loc    = loc_in
                            st.session_state.active_mode   = "sheet_to_floor"
                            st.session_state.active_df     = df
                            st.switch_page("pages/sheet_to_floor.py")
                    except Exception as e:
                        st.error(f"Failed to read file: {e}")

    with c2:
        if st.button("📦➡️📋  Floor to Sheet", use_container_width=True):
            if not sid_in:   st.warning("Please enter a Session ID.")
            elif not file_in: st.warning("Please upload your Excel sheet.")
            else:
                if run("SELECT 1 FROM audit_sessions WHERE sid=%s",(sid_in,),fetch="one"):
                    st.error(f"Session **{sid_in}** already exists.")
                else:
                    try:
                        df = pd.read_excel(file_in)
                        df.columns = [c.strip().lower() for c in df.columns]
                        needed = {"product code","product name"}
                        missing = needed - set(df.columns)
                        if missing:
                            st.error(f"Missing columns: {', '.join(missing)}")
                        else:
                            df["product code"]   = df["product code"].astype(str).str.strip()
                            df["product name"]   = df["product name"].astype(str).str.strip()
                            df["physical count"] = 0
                            df["last_updated"]   = ""
                            save_session(sid_in, CU, loc_in, df, mode="floor_to_sheet")
                            st.session_state.active_sid    = sid_in
                            st.session_state.active_loc    = loc_in
                            st.session_state.active_mode   = "floor_to_sheet"
                            st.session_state.active_df     = df
                            st.switch_page("pages/floor_to_sheet.py")
                    except Exception as e:
                        st.error(f"Failed to read file: {e}")


# ── MY SESSIONS ────────────────────────────────────────────────────
with t_my:
    with st.container(border=True):
        section("My Sessions")
        history = get_user_sessions(CU)
        if history.empty:
            st.info("No sessions yet. Create one in the New Count tab.")
        else:
            for _, row in history.iterrows():
                mode     = row.get("mode","sheet_to_floor")
                pill     = ('<span class="mode-pill-s2f">Sheet→Floor</span>' if mode=="sheet_to_floor"
                            else '<span class="mode-pill-f2s">Floor→Sheet</span>')
                sid_key  = row["sid"]
                confirm_key = f"confirm_del_{sid_key}"

                with st.container(border=True):
                    st.markdown(f"""
                    <div style="padding:2px 0 6px 0">
                      <div class="sess-sid">{pill} {sid_key}</div>
                      <div class="sess-meta">📍 {row['client'] or '—'} · 🕐 {row['updated'] or '—'}</div>
                    </div>""", unsafe_allow_html=True)

                    # Show confirm warning if delete was clicked
                    if st.session_state.get(confirm_key):
                        st.warning(
                            f"⚠️ **All data for session `{sid_key}` will be permanently deleted** "
                            f"and cannot be recovered. Are you sure?")
                        ca, cb = st.columns(2)
                        with ca:
                            if st.button("✅ Yes, Delete Permanently",
                                         key=f"confirm_yes_{sid_key}", use_container_width=True):
                                delete_session(sid_key)
                                st.session_state.pop(confirm_key, None)
                                st.success(f"Session `{sid_key}` deleted.")
                                st.rerun()
                        with cb:
                            if st.button("✖ Cancel",
                                         key=f"confirm_no_{sid_key}", use_container_width=True):
                                st.session_state.pop(confirm_key, None)
                                st.rerun()
                    else:
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("▶ Open", key=f"open_{sid_key}", use_container_width=True):
                                db_row = run("SELECT data,client FROM audit_sessions WHERE sid=%s",
                                             (sid_key,), fetch="one")
                                if db_row:
                                    try:    df_open = pd.read_pickle(io.BytesIO(bytes(db_row["data"])), compression="gzip")
                                    except: df_open = pd.read_pickle(io.BytesIO(bytes(db_row["data"])))
                                    st.session_state.active_sid  = sid_key
                                    st.session_state.active_loc  = db_row["client"] or ""
                                    st.session_state.active_mode = mode
                                    st.session_state.active_df   = df_open
                                    target = ("pages/sheet_to_floor.py" if mode=="sheet_to_floor"
                                              else "pages/floor_to_sheet.py")
                                    st.switch_page(target)
                        with c2:
                            if st.button("🗑 Delete", key=f"del_{sid_key}", use_container_width=True):
                                st.session_state[confirm_key] = True
                                st.rerun()


# ── ADMIN PANEL ────────────────────────────────────────────────────
if IS_ADMIN:
    with tabs[2]:
        at1, at2 = st.tabs(["  👥  Users  ","  📋  All Sessions  "])
        with at1:
            with st.container(border=True):
                section("All Users")
                for _, u in get_all_users().iterrows():
                    uc1, uc2, uc3 = st.columns([3,1,1])
                    with uc1:
                        role = "🔑 Admin" if u["is_admin"] else "📦 Counter"
                        st.markdown(f"""
                        <div style="padding:6px 0">
                          <div style="font-weight:600;font-size:.9rem">{u['username']}</div>
                          <div style="font-size:.76rem;color:#8A9BAE">{role} · joined {u['created'] or '—'}</div>
                        </div>""", unsafe_allow_html=True)
                    with uc2:
                        if u["username"] != CU:
                            label = "→ Counter" if u["is_admin"] else "→ Admin"
                            if st.button(label, key=f"role_{u['username']}", use_container_width=True):
                                set_admin(u["username"], not bool(u["is_admin"]))
                                st.rerun()
                        else:
                            st.caption("(you)")
                    with uc3:
                        if u["username"] != CU:
                            if st.button("Remove", key=f"del_{u['username']}", use_container_width=True):
                                delete_user(u["username"]); st.rerun()

        with at2:
            with st.container(border=True):
                section("All Sessions")
                all_s = get_all_sessions()
                if all_s.empty:
                    st.info("No sessions yet.")
                else:
                    for _, row in all_s.iterrows():
                        mode     = row.get("mode","sheet_to_floor")
                        pill     = ('<span class="mode-pill-s2f">Sheet→Floor</span>' if mode=="sheet_to_floor"
                                    else '<span class="mode-pill-f2s">Floor→Sheet</span>')
                        sid_key  = row["sid"]
                        aconfirm = f"admin_confirm_del_{sid_key}"

                        with st.container(border=True):
                            st.markdown(f"""
                            <div style="padding:2px 0 6px 0">
                              <div style="font-weight:600;font-size:.9rem">{pill} {sid_key}</div>
                              <div style="font-size:.76rem;color:#8A9BAE">
                                👤 {row['username']} · 📍 {row['client'] or '—'} · 🕐 {row['updated'] or '—'}
                              </div>
                            </div>""", unsafe_allow_html=True)

                            if st.session_state.get(aconfirm):
                                st.warning(
                                    f"⚠️ **All data for session `{sid_key}` will be permanently deleted** "
                                    f"and cannot be recovered. Are you sure?")
                                ac1, ac2 = st.columns(2)
                                with ac1:
                                    if st.button("✅ Yes, Delete Permanently",
                                                 key=f"aconfirm_yes_{sid_key}", use_container_width=True):
                                        delete_session(sid_key)
                                        st.session_state.pop(aconfirm, None)
                                        st.success(f"Session `{sid_key}` deleted.")
                                        st.rerun()
                                with ac2:
                                    if st.button("✖ Cancel",
                                                 key=f"aconfirm_no_{sid_key}", use_container_width=True):
                                        st.session_state.pop(aconfirm, None)
                                        st.rerun()
                            else:
                                if st.button(f"🗑 Delete", key=f"adel_{sid_key}", use_container_width=True):
                                    st.session_state[aconfirm] = True
                                    st.rerun()
