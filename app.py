import streamlit as st
import pandas as pd
import psycopg2, psycopg2.extras
import hashlib, io, json
from datetime import datetime

st.set_page_config(page_title="Stock Count Pro", page_icon="📦",
                   layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
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
html,body,section[data-testid="stMain"],
div[data-testid="stAppViewContainer"]{background:#F4F6FA!important}
input,textarea,select{color:#0D1B2A!important;background:#F8FAFC!important;
  -webkit-text-fill-color:#0D1B2A!important}
input::placeholder{color:#A0AEC0!important;-webkit-text-fill-color:#A0AEC0!important;opacity:1!important}
[data-baseweb="select"] *{color:#0D1B2A!important}
[data-baseweb="menu"]{background:#fff!important}
[data-baseweb="option"]{background:#fff!important;color:#0D1B2A!important}
[data-baseweb="option"]:hover{background:#EEF2F7!important}
.stTabs [data-baseweb="tab"]{color:#5A6A7A!important}
.stTabs [aria-selected="true"]{color:#002855!important}
section[data-testid="stSidebar"]{background:#fff!important;border-right:1px solid #E2E8F0!important}
section[data-testid="stSidebar"] *{color:#0D1B2A!important}
div[data-testid="stExpander"]{background:#fff!important;border:1px solid #E2E8F0!important;border-radius:10px!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:1.5rem 1.5rem 4rem!important;max-width:720px!important}
div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff!important;
  border:1px solid #E2E8F0!important;border-radius:16px!important;
  box-shadow:0 2px 14px rgba(0,0,0,.06)!important;padding:4px 0!important;margin-bottom:14px!important}
div[data-testid="stVerticalBlockBorderWrapper"]>div{background:transparent!important;
  box-shadow:none!important;border:none!important}
.app-header{background:linear-gradient(135deg,#002855,#00509E);border-radius:14px;
  padding:18px 24px;margin-bottom:20px;display:flex;align-items:center;
  justify-content:space-between;box-shadow:0 4px 24px rgba(0,40,85,.18)}
.app-header .brand{font-size:1.3rem;font-weight:700;letter-spacing:-.5px}
.app-header .brand,.app-header .brand *{color:#fff!important}
.app-header .brand span{color:#5BC4FF!important}
.user-pill{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.28);
  border-radius:999px;padding:4px 12px;font-size:.76rem;font-weight:500;
  font-family:'DM Mono',monospace}
.user-pill,.user-pill *{color:#fff!important}
.admin-badge{display:inline-block;background:#FEF3C7;border:1px solid #FCD34D;
  border-radius:6px;padding:2px 8px;font-size:.7rem;font-weight:700;
  color:#92400E!important;letter-spacing:.5px;margin-left:6px}
.section-label{font-size:.7rem;font-weight:700;text-transform:uppercase;
  letter-spacing:1.2px;color:#8A9BAE;margin-bottom:12px}
.stTextInput>div>div>input,.stNumberInput>div>div>input{
  border:1.5px solid #CBD5E0!important;border-radius:10px!important;
  padding:10px 14px!important;font-size:.95rem!important;
  background:#F8FAFC!important;color:#0D1B2A!important}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus{
  border-color:#00509E!important;box-shadow:0 0 0 3px rgba(0,80,158,.1)!important}
.stSelectbox>div>div>div{border:1.5px solid #CBD5E0!important;
  border-radius:10px!important;background:#F8FAFC!important}
.stButton>button,.stDownloadButton>button{
  background:linear-gradient(135deg,#002855,#00509E)!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-weight:600!important;font-size:.88rem!important;height:44px!important;
  box-shadow:0 2px 8px rgba(0,80,158,.22)!important}
.stButton>button *,.stDownloadButton>button *{color:#fff!important}
.stTabs [data-baseweb="tab-list"]{background:#EEF2F7!important;border-radius:10px!important;
  padding:4px!important;gap:4px!important;border-bottom:none!important}
.stTabs [data-baseweb="tab"]{border-radius:8px!important;font-weight:600!important;
  font-size:.86rem!important;padding:7px 18px!important;border:none!important;background:transparent!important}
.stTabs [aria-selected="true"]{background:#fff!important;color:#002855!important;
  box-shadow:0 1px 6px rgba(0,0,0,.1)!important}
[data-testid="stFileUploaderDropzone"]{border:2px dashed #CBD5E0!important;
  border-radius:12px!important;background:#F8FAFC!important}
.count-header{background:linear-gradient(135deg,#002855,#00509E);
  border-radius:14px;padding:14px 20px;margin-bottom:16px}
.count-header *{color:#fff!important}
.ch-sid{color:#5BC4FF!important;font-family:'DM Mono',monospace;font-size:.76rem;font-weight:600}
.ch-loc{color:rgba(255,255,255,.75)!important;font-size:.76rem;margin-top:2px}
.stat-row{display:flex;gap:10px;margin-bottom:14px}
.stat-box{flex:1;background:#F4F6FA;border:1px solid #E2E8F0;border-radius:12px;
  padding:12px 8px;text-align:center}
.stat-label{font-size:.62rem;font-weight:700;text-transform:uppercase;
  letter-spacing:1px;color:#8A9BAE;margin-bottom:4px}
.stat-value{font-size:1.5rem;font-weight:700;color:#002855;line-height:1}
.stat-value.red{color:#DC2626!important}
.prog-head{display:flex;justify-content:space-between;font-size:.74rem;color:#8A9BAE;margin-bottom:5px}
.prog-track{background:#E2E8F0;border-radius:999px;height:7px;overflow:hidden}
.prog-fill{background:linear-gradient(90deg,#002855,#5BC4FF);height:100%;border-radius:999px}
.product-card{background:#EEF5FF;border:2px solid #00509E;border-radius:14px;padding:14px 16px;margin-bottom:12px}
.product-code{font-family:'DM Mono',monospace;font-size:.76rem;color:#5A6A7A;margin-bottom:3px}
.product-name{font-size:1rem;font-weight:700;color:#002855}
.recent-item{display:flex;align-items:center;justify-content:space-between;
  padding:9px 12px;background:#F8FAFC;border:1px solid #E8EDF3;border-radius:10px;margin-bottom:6px}
.ri-name{font-weight:600;font-size:.85rem}
.ri-meta{font-size:.72rem;color:#8A9BAE;margin-top:1px}
.badge{border-radius:6px;padding:3px 9px;font-size:.74rem;font-weight:700;
  font-family:'DM Mono',monospace;white-space:nowrap}
.badge-pos{background:#D1FAE5;color:#065F46!important}
.badge-neg{background:#FEE2E2;color:#991B1B!important}
.badge-zero{background:#E2E8F0;color:#374151!important}
</style>
""", unsafe_allow_html=True)


# ── SECURITY ───────────────────────────────────────────────────────
def hash_pw(p): return hashlib.sha256(p.strip().encode()).hexdigest()


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
            username TEXT PRIMARY KEY, password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE, created TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS stock_sessions(
            sid TEXT PRIMARY KEY, username TEXT NOT NULL,
            location TEXT, data TEXT, updated TEXT)""")
    if run("SELECT COUNT(*) as c FROM users", fetch="one")["c"] == 0:
        run("INSERT INTO users VALUES(%s,%s,%s,%s)",
            ("admin", hash_pw("admin123"), True, datetime.now().strftime("%Y-%m-%d")))

init_db()


# ── USER CRUD ──────────────────────────────────────────────────────
def get_user(u):
    return run("SELECT * FROM users WHERE username=%s", (u.strip().lower(),), fetch="one")
def get_all_users():
    rows = run("SELECT username,is_admin,created FROM users ORDER BY username", fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["username","is_admin","created"])
def create_user(u, p, admin=False):
    u = u.strip().lower()
    if not u or not p or get_user(u): return False
    run("INSERT INTO users VALUES(%s,%s,%s,%s)",
        (u, hash_pw(p), admin, datetime.now().strftime("%Y-%m-%d")))
    return True
def delete_user(u): run("DELETE FROM users WHERE username=%s", (u,))
def change_pw(u, p): run("UPDATE users SET password_hash=%s WHERE username=%s", (hash_pw(p), u))


# ── SESSION CRUD ───────────────────────────────────────────────────
def df_to_json(df):
    cols = ["product code","product name","systems count","physical count","difference","last_updated"]
    return df[[c for c in cols if c in df.columns]].to_json(orient="records")

def json_to_df(j):
    if not j or j == "[]": return pd.DataFrame()
    df = pd.DataFrame(json.loads(j))
    df["physical count"] = pd.to_numeric(df.get("physical count", 0), errors="coerce").fillna(0).astype(int)
    df["difference"]     = pd.to_numeric(df.get("difference", 0),     errors="coerce").fillna(0).astype(int)
    df["systems count"]  = pd.to_numeric(df.get("systems count", 0),  errors="coerce").fillna(0)
    df["last_updated"]   = df.get("last_updated", pd.Series([""]*len(df))).fillna("").astype(str)
    df["product code"]   = df["product code"].astype(str)
    df["product name"]   = df["product name"].astype(str)
    return df

def save_session(sid, username, location, df):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    run("""INSERT INTO stock_sessions(sid,username,location,data,updated)
           VALUES(%s,%s,%s,%s,%s)
           ON CONFLICT(sid) DO UPDATE SET data=%s,location=%s,updated=%s""",
        (sid, username, location, df_to_json(df), ts,
         df_to_json(df), location, ts))

def load_session(sid):
    row = run("SELECT data FROM stock_sessions WHERE sid=%s", (sid,), fetch="one")
    return json_to_df(row["data"]) if row else None

def get_my_sessions(username):
    rows = run("SELECT sid,location,updated FROM stock_sessions WHERE username=%s ORDER BY updated DESC",
               (username,), fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["sid","location","updated"])

def get_all_sessions():
    rows = run("SELECT sid,username,location,updated FROM stock_sessions ORDER BY updated DESC", fetch="all")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["sid","username","location","updated"])


# ── EXCEL NORMALISE ────────────────────────────────────────────────
def normalise(df):
    df.columns = [c.strip().lower() for c in df.columns]
    missing = {"product name","product code","systems count"} - set(df.columns)
    if missing: st.error(f"Missing columns: {', '.join(missing)}"); st.stop()
    df["product code"]  = df["product code"].astype(str).str.strip()
    df["product name"]  = df["product name"].astype(str).str.strip()
    df["systems count"] = pd.to_numeric(df["systems count"], errors="coerce").fillna(0)
    df["physical count"] = 0; df["difference"] = 0; df["last_updated"] = ""
    return df


# ── UI HELPERS ─────────────────────────────────────────────────────
def ui_header(username="", is_admin=False):
    badge = '<span class="admin-badge">ADMIN</span>' if is_admin else ""
    pill  = f'<span class="user-pill">👤 {username}{badge}</span>' if username else ""
    st.markdown(
        f'<div class="app-header">'
        f'<div class="brand">📦 Stock <span>Count Pro</span></div>'
        f'<div>{pill}</div></div>',
        unsafe_allow_html=True)

def section(t):
    st.markdown(f'<div class="section-label">{t}</div>', unsafe_allow_html=True)


# ── AUTH ───────────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False

if not st.session_state.user:
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


# ── SIDEBAR ────────────────────────────────────────────────────────
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


# ═══════════════════════════════════════════════════════════════════
#  COUNTING SCREEN
#  Shown instead of dashboard when a session is active.
#  Every "Save Count" press writes directly to Supabase — no sync needed.
# ═══════════════════════════════════════════════════════════════════
if "counting_sid" in st.session_state:
    sid = st.session_state.counting_sid
    loc = st.session_state.get("counting_location", "")

    # Load df into session_state once; kept in memory while counting
    if "counting_df" not in st.session_state:
        st.session_state.counting_df = load_session(sid) or pd.DataFrame()

    df = st.session_state.counting_df

    # ── Header ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="count-header">
      <div>
        <div style="font-size:1.1rem;font-weight:700">📦 Stock Count</div>
        <div class="ch-sid">{sid}</div>
        <div class="ch-loc">📍 {loc or '—'}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Progress stats ───────────────────────────────────────────────
    total   = len(df)
    counted = int((df["last_updated"] != "").sum()) if not df.empty else 0
    n_vars  = int(((df["difference"] != 0) & (df["last_updated"] != "")).sum()) if not df.empty else 0
    pct     = round(counted / total * 100) if total else 0

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-box">
        <div class="stat-label">Total</div>
        <div class="stat-value">{total}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Counted</div>
        <div class="stat-value">{counted}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Variances</div>
        <div class="stat-value red">{n_vars}</div>
      </div>
    </div>
    <div class="prog-head">
      <span>Progress</span><span><b>{pct}%</b> complete</span>
    </div>
    <div class="prog-track">
      <div class="prog-fill" style="width:{pct}%"></div>
    </div>
    <br>""", unsafe_allow_html=True)

    # ── Search & select product ──────────────────────────────────────
    with st.container(border=True):
        section("Search Product")
        search = st.text_input("", placeholder="🔍  Product name or code…",
                               key="search_q", label_visibility="collapsed")

        if search.strip():
            ql = search.strip().lower()
            mask = (df["product name"].str.lower().str.contains(ql, na=False) |
                    df["product code"].str.lower().str.contains(ql, na=False))
            results = df[mask].head(20)

            if results.empty:
                st.caption("No products found.")
            else:
                for idx in results.index:
                    row = df.loc[idx]
                    tick = "✅ " if row["last_updated"] else ""
                    label = f"{tick}{row['product code']}  —  {row['product name']}"
                    if st.button(label, key=f"pick_{idx}", use_container_width=True):
                        st.session_state.selected_idx = int(idx)
                        st.session_state.search_q = ""
                        st.rerun()

    # ── Count entry form ─────────────────────────────────────────────
    if "selected_idx" in st.session_state:
        idx = st.session_state.selected_idx
        if idx in df.index:
            row     = df.loc[idx]
            sys_qty = int(row["systems count"])
            prev    = int(row["physical count"])

            with st.container(border=True):
                section("Enter Physical Count")

                st.markdown(f"""
                <div class="product-card">
                  <div class="product-code">{row['product code']}</div>
                  <div class="product-name">{row['product name']}</div>
                </div>""", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("System Qty", sys_qty)
                with col2:
                    phys = st.number_input(
                        "Physical Count", min_value=0,
                        value=prev, step=1, key=f"phys_{idx}")

                diff = phys - sys_qty
                sign = "+" if diff > 0 else ""

                if diff > 0:
                    st.success(f"**Variance: {sign}{diff}** — surplus")
                elif diff < 0:
                    st.error(f"**Variance: {diff}** — shortage")
                else:
                    st.info("**Variance: 0** — exact match ✓")

                if row["last_updated"]:
                    st.caption(f"⏱ Last saved: {row['last_updated']}")

                if st.button("💾  Save Count", use_container_width=True, type="primary"):
                    now = datetime.now().strftime("%H:%M:%S")
                    st.session_state.counting_df.at[idx, "physical count"] = phys
                    st.session_state.counting_df.at[idx, "difference"]     = diff
                    st.session_state.counting_df.at[idx, "last_updated"]   = now
                    # ✅ Save directly to Supabase — no sync button needed
                    save_session(sid, CU, loc, st.session_state.counting_df)
                    st.session_state.pop("selected_idx", None)
                    st.success(f"✅ Saved to cloud — {row['product code']}")
                    st.rerun()

    # ── Recent counts list ───────────────────────────────────────────
    done = (df[df["last_updated"] != ""]
            .sort_values("last_updated", ascending=False)
            .head(8))
    if not done.empty:
        with st.container(border=True):
            section("Recent Counts")
            for _, r in done.iterrows():
                d = int(r["difference"])
                badge = (f'<span class="badge badge-pos">+{d}</span>' if d > 0
                         else f'<span class="badge badge-neg">{d}</span>' if d < 0
                         else '<span class="badge badge-zero">±0</span>')
                st.markdown(f"""
                <div class="recent-item">
                  <div>
                    <div class="ri-name">{r['product name']}</div>
                    <div class="ri-meta">{r['product code']} · {r['last_updated']}</div>
                  </div>
                  {badge}
                </div>""", unsafe_allow_html=True)

    # ── Footer actions ───────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("← Dashboard", use_container_width=True):
            for k in ["counting_sid","counting_location","counting_df","selected_idx"]:
                st.session_state.pop(k, None)
            st.rerun()
    with c2:
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name="Stock Count")
        st.download_button("📤 Export", out.getvalue(),
            file_name=f"{sid}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)
    with c3:
        out2 = io.BytesIO()
        with pd.ExcelWriter(out2, engine="openpyxl") as w:
            df[df["difference"] != 0].to_excel(w, index=False, sheet_name="Variances")
        st.download_button("⚠️ Variances", out2.getvalue(),
            file_name=f"{sid}_variances_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

    st.stop()


# ═══════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════════
ui_header(username=CU, is_admin=IS_ADMIN)

tab_labels = (["  ✨  New Count  ","  📁  My Sessions  ","  ⚙️  Admin Panel  "]
              if IS_ADMIN else ["  ✨  New Count  ","  📁  My Sessions  "])
tabs  = st.tabs(tab_labels)
t_new = tabs[0]
t_my  = tabs[1]


# ── NEW COUNT ──────────────────────────────────────────────────────
with t_new:
    with st.container(border=True):
        section("Start New Stock Count")
        sid_in  = st.text_input("Session ID", placeholder="e.g. SC-2026-001")
        loc_in  = st.text_input("Warehouse / Location", placeholder="e.g. Main Warehouse")
        file_in = st.file_uploader("Upload Master Sheet (.xlsx)", type=["xlsx"])
        if file_in: st.caption(f"📎 {file_in.name} — ready")

        if st.button("🚀  Create & Start Counting", use_container_width=True):
            if not sid_in:
                st.warning("Please enter a Session ID.")
            elif not file_in:
                st.warning("Please upload a master sheet.")
            else:
                if run("SELECT 1 FROM stock_sessions WHERE sid=%s", (sid_in,), fetch="one"):
                    st.error(f"Session **{sid_in}** already exists.")
                else:
                    try:
                        df = normalise(pd.read_excel(file_in))
                        save_session(sid_in, CU, loc_in, df)
                        st.session_state.counting_sid      = sid_in
                        st.session_state.counting_location = loc_in
                        st.session_state.counting_df       = df
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to read file: {e}")


# ── MY SESSIONS ────────────────────────────────────────────────────
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
                counted = int((df_row["last_updated"]!="").sum()) if df_row is not None else 0
                pct     = round(counted/total*100) if total else 0
                n_vars  = int(((df_row["difference"]!=0)&(df_row["last_updated"]!="")).sum()) if df_row is not None else 0

                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"""
                        <div style="font-weight:700;font-size:.92rem;color:#002855">{row['sid']}</div>
                        <div style="font-size:.76rem;color:#8A9BAE;margin-top:2px">
                          📍 {row['location'] or '—'} · 🕐 {row['updated'] or '—'}
                        </div>
                        <div style="font-size:.76rem;color:#8A9BAE;margin-top:3px">
                          {counted}/{total} counted · {pct}% ·
                          <span style="color:#DC2626">{n_vars} variances</span>
                        </div>""", unsafe_allow_html=True)
                    with c2:
                        if st.button("▶ Count", key=f"res_{row['sid']}", use_container_width=True):
                            st.session_state.counting_sid      = row["sid"]
                            st.session_state.counting_location = row["location"] or ""
                            st.session_state.counting_df       = df_row
                            st.rerun()

                if df_row is not None:
                    e1, e2 = st.columns(2)
                    with e1:
                        out = io.BytesIO()
                        with pd.ExcelWriter(out, engine="openpyxl") as w:
                            df_row.to_excel(w, index=False, sheet_name="Stock Count")
                        st.download_button("📤 Export All", out.getvalue(),
                            file_name=f"{row['sid']}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True, key=f"exp_{row['sid']}")
                    with e2:
                        out2 = io.BytesIO()
                        with pd.ExcelWriter(out2, engine="openpyxl") as w:
                            df_row[df_row["difference"]!=0].to_excel(w, index=False, sheet_name="Variances")
                        st.download_button("⚠️ Variances", out2.getvalue(),
                            file_name=f"{row['sid']}_variances_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True, key=f"var_{row['sid']}")


# ── ADMIN PANEL ────────────────────────────────────────────────────
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
                        st.markdown(
                            f'<div style="padding:8px 0"><b>{u["username"]}</b>'
                            f'<span style="color:#8A9BAE;font-size:.8rem;margin-left:8px">'
                            f'{role} · {u["created"] or "—"}</span></div>',
                            unsafe_allow_html=True)
                    with uc2:
                        if u["username"] != CU:
                            if st.button("Delete", key=f"del_{u['username']}", use_container_width=True):
                                delete_user(u["username"]); st.rerun()
                        else:
                            st.caption("(you)")

        with at2:
            with st.container(border=True):
                section("All Sessions")
                all_s = get_all_sessions()
                if all_s.empty:
                    st.info("No sessions.")
                else:
                    for _, row in all_s.iterrows():
                        st.markdown(
                            f'<div style="padding:8px 0"><b>{row["sid"]}</b>'
                            f'<span style="color:#8A9BAE;font-size:.8rem;margin-left:8px">'
                            f'👤 {row["username"]} · 📍 {row["location"] or "—"} · 🕐 {row["updated"] or "—"}'
                            f'</span></div>',
                            unsafe_allow_html=True)

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
