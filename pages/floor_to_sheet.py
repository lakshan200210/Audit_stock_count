import streamlit as st
import pandas as pd
import psycopg2
import psycopg2.extras
import hashlib
import io
import json
from datetime import datetime

st.set_page_config(page_title="Floor to Sheet",page_icon="📦",layout="centered",initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
.stApp,section[data-testid="stMain"],div[data-testid="stAppViewContainer"],
div[data-testid="stMainBlockContainer"],div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"],div[data-testid="column"],
div[data-testid="stMarkdownContainer"],div[data-testid="stWidgetLabel"],
div[data-testid="stCaptionContainer"],div[data-testid="stNumberInput"]>div,
div[data-testid="stTextInput"]>div,div[data-baseweb="tab-panel"],
div[data-baseweb="form-control-label"],div[data-baseweb="block"],
div[data-baseweb="card"],div.stTabs,div[data-testid="stTabsContent"]{
  background:transparent!important;box-shadow:none!important;border:none!important}
html,body{color-scheme:light!important}
.stApp{background:#F4F6FA!important;font-family:'DM Sans',sans-serif!important;color:#0D1B2A!important}
.stApp *{color:#0D1B2A!important}
html,body,section[data-testid="stMain"],div[data-testid="stAppViewContainer"]{background:#F4F6FA!important}
input,textarea,select{color:#0D1B2A!important;background:#F8FAFC!important;-webkit-text-fill-color:#0D1B2A!important}
input::placeholder{color:#A0AEC0!important;-webkit-text-fill-color:#A0AEC0!important;opacity:1!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:1.5rem 1.5rem 4rem!important;max-width:720px!important}
div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff!important;
  border:1px solid #E2E8F0!important;border-radius:16px!important;
  box-shadow:0 2px 14px rgba(0,0,0,.06)!important;padding:4px 0!important;margin-bottom:14px!important}
div[data-testid="stVerticalBlockBorderWrapper"]>div{background:transparent!important;box-shadow:none!important;border:none!important}
.stTextInput>div>div>input,.stNumberInput>div>div>input{
  border:1.5px solid #CBD5E0!important;border-radius:10px!important;
  padding:10px 14px!important;font-size:.95rem!important;background:#F8FAFC!important}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus{
  border-color:#059669!important;box-shadow:0 0 0 3px rgba(5,150,105,.1)!important;outline:none!important}
.stButton>button,.stDownloadButton>button{
  background:linear-gradient(135deg,#065F46,#059669)!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-weight:600!important;height:auto!important;min-height:46px!important;
  box-shadow:0 2px 8px rgba(5,150,105,.22)!important;
  white-space:normal!important;word-break:break-word!important;
  text-align:left!important;padding:10px 14px!important;line-height:1.4!important}
.stButton>button *,.stDownloadButton>button *{color:#fff!important}
.count-header{background:linear-gradient(135deg,#065F46,#059669);border-radius:14px;
  padding:14px 20px;margin-bottom:16px}
.count-header *{color:#fff!important}
.ch-mode{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;
  color:rgba(255,255,255,.6)!important;margin-bottom:4px}
.ch-sid{font-size:1.1rem;font-weight:700}
.ch-loc{font-size:.76rem;color:rgba(255,255,255,.7)!important;margin-top:2px}
.section-label{font-size:.71rem;font-weight:700;text-transform:uppercase;
  letter-spacing:1.2px;color:#8A9BAE;margin-bottom:14px}
.stat-box{background:#F4F6FA;border:1px solid #E2E8F0;border-radius:12px;padding:14px 10px;text-align:center}
.stat-label{font-size:.69rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#8A9BAE;margin-bottom:5px}
.stat-value{font-size:1.85rem;font-weight:700;color:#065F46;line-height:1}
.prog-wrap{margin-top:16px}
.prog-head{display:flex;justify-content:space-between;font-size:.77rem;color:#8A9BAE;margin-bottom:6px}
.prog-track{background:#E2E8F0;border-radius:999px;height:7px;overflow:hidden}
.prog-fill{background:linear-gradient(90deg,#065F46,#6EE7B7);height:100%;border-radius:999px}
.log-row{display:flex;align-items:center;justify-content:space-between;gap:10px;
  padding:11px 14px;background:#F8FAFC;border:1px solid #E8EDF3;border-radius:10px;margin-bottom:7px}
.log-left{flex:1;min-width:0}
.log-name{font-weight:600;font-size:.88rem;color:#0D1B2A;word-break:break-word;white-space:normal}
.log-meta{font-size:.76rem;color:#8A9BAE;margin-top:1px}
.log-badge{flex-shrink:0}
.badge-count{background:#D1FAE5;color:#065F46!important;border-radius:6px;padding:3px 10px;
  font-size:.79rem;font-weight:700;font-family:'DM Mono',monospace;white-space:nowrap;display:inline-block}
.product-card{background:#ECFDF5;border:2px solid #059669;border-radius:14px;padding:14px 16px;margin-bottom:14px}
.pc-code{font-family:'DM Mono',monospace;font-size:.76rem;color:#5A6A7A;margin-bottom:4px}
.pc-name{font-size:.98rem;font-weight:700;color:#065F46;line-height:1.35;word-break:break-word}
.sync-bar{background:#ECFDF5;border:1px solid #6EE7B7;border-radius:10px;
  padding:10px 16px;display:flex;align-items:center;margin-bottom:14px;font-size:.82rem}
.sync-dot-ok{width:8px;height:8px;border-radius:50%;background:#10B981;display:inline-block;margin-right:6px}
.sync-dot-pending{width:8px;height:8px;border-radius:50%;background:#F59E0B;display:inline-block;margin-right:6px}
.divider{border:none;border-top:1px solid #E2E8F0;margin:18px 0}
</style>
""", unsafe_allow_html=True)


# ── DB ─────────────────────────────────────────────────────────────
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
        conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
    if fetch == "one": return cur.fetchone()
    if fetch == "all": return cur.fetchall()

def df_to_bytes(df):
    cols = ["product code","product name","physical count","last_updated"]
    buf  = io.BytesIO()
    df[[c for c in cols if c in df.columns]].to_pickle(buf, compression="gzip")
    return buf.getvalue()

def bytes_to_df(raw):
    try:    return pd.read_pickle(io.BytesIO(raw), compression="gzip")
    except: return pd.read_pickle(io.BytesIO(raw))

def save_session(sid, username, client, df):
    data = psycopg2.Binary(df_to_bytes(df))
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M")
    run("""INSERT INTO audit_sessions(sid,username,client,data,updated,mode)
           VALUES(%s,%s,%s,%s,%s,'floor_to_sheet')
           ON CONFLICT(sid) DO UPDATE SET data=%s,client=%s,updated=%s""",
        (sid,username,client,data,ts, data,client,ts))

def load_session(sid):
    row = run("SELECT data FROM audit_sessions WHERE sid=%s",(sid,),fetch="one")
    return bytes_to_df(bytes(row["data"])) if row else None

def section(t): st.markdown(f'<div class="section-label">{t}</div>', unsafe_allow_html=True)

def sync_status(counter):
    pending = counter % 10
    if pending == 0:
        st.markdown('<div class="sync-bar"><span class="sync-dot-ok"></span>All changes backed up</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sync-bar"><span class="sync-dot-pending"></span>{pending} unsaved · auto-backup in {10-pending}</div>', unsafe_allow_html=True)


# ── AUTH + SESSION CHECK ──────────────────────────────────────────
if "current_user" not in st.session_state or not st.session_state.current_user:
    st.warning("Please sign in first.")
    if st.button("← Go to Sign In"): st.switch_page("app.py")
    st.stop()

CU = st.session_state.current_user

# Pick up session passed from app.py via session_state
if "active_sid" in st.session_state and st.session_state.active_sid:
    if st.session_state.get("f2s_sid") != st.session_state.active_sid:
        st.session_state.f2s_sid     = st.session_state.active_sid
        st.session_state.f2s_loc     = st.session_state.get("active_loc","")
        st.session_state.f2s_df      = st.session_state.active_df
        st.session_state.f2s_counter = 0
        st.session_state.f2s_sel_idx = None

if "f2s_sid" not in st.session_state or not st.session_state.f2s_sid:
    st.warning("No session loaded. Please go back and select a session.")
    if st.button("← Back to Dashboard"): st.switch_page("app.py")
    st.stop()

if "f2s_df" not in st.session_state or st.session_state.f2s_df is None:
    df_loaded = load_session(st.session_state.f2s_sid)
    if df_loaded is None:
        st.error("Session not found in database.")
        if st.button("← Back"): st.switch_page("app.py")
        st.stop()
    st.session_state.f2s_df = df_loaded

if "f2s_counter" not in st.session_state: st.session_state.f2s_counter = 0
if "f2s_sel_idx" not in st.session_state: st.session_state.f2s_sel_idx = None

SID = st.session_state.f2s_sid
LOC = st.session_state.get("f2s_loc","")


# ══════════════════════════════════════════════════════════════════
#  COUNTING SCREEN — FLOOR TO SHEET
# ══════════════════════════════════════════════════════════════════
updated_mask = st.session_state.f2s_df["last_updated"] != ""
total   = len(st.session_state.f2s_df)
counted = int(updated_mask.sum())
pct     = round(counted/total*100,1) if total else 0.0

# Header — green theme for floor to sheet
st.markdown(f"""
<div class="count-header">
  <div class="ch-mode">📦➡️📋 Floor to Sheet</div>
  <div class="ch-sid">{SID}</div>
  <div class="ch-loc">📍 {LOC or '—'}</div>
</div>""", unsafe_allow_html=True)

sync_status(st.session_state.f2s_counter)

# Stats — only Total and Counted, no variance
with st.container(border=True):
    section("Count Overview")
    m1, m2 = st.columns(2)
    m1.markdown(f'<div class="stat-box"><div class="stat-label">Total Products</div><div class="stat-value">{total}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="stat-box"><div class="stat-label">Counted</div><div class="stat-value">{counted}</div></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="prog-wrap">
      <div class="prog-head"><span>Progress</span><span><b style="color:#065F46">{pct}%</b></span></div>
      <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
    </div>""", unsafe_allow_html=True)

# Search
with st.container(border=True):
    section("Search Product")
    search = st.text_input("", placeholder="🔍  Product name or code…",
                           label_visibility="collapsed", key="f2s_search")
    if search.strip():
        q    = search.strip()
        mask = (st.session_state.f2s_df["product name"].str.contains(q,case=False,na=False)|
                st.session_state.f2s_df["product code"].str.contains(q,case=False,na=False))
        matches = st.session_state.f2s_df.loc[mask].head(20)
        if matches.empty:
            st.warning("No products found.")
        else:
            st.caption(f"{len(matches)} result{'s' if len(matches)!=1 else ''} — tap to select")
            for ri in matches.index:
                r    = st.session_state.f2s_df.loc[ri]
                tick = "✅ " if r["last_updated"] else ""
                if st.button(f"{tick}{r['product code']}  —  {r['product name']}",
                             key=f"f2s_pick_{ri}", use_container_width=True):
                    st.session_state.f2s_sel_idx = int(ri)
                    st.rerun()

# Count entry — no system qty, no variance box
if st.session_state.f2s_sel_idx is not None:
    idx = st.session_state.f2s_sel_idx
    if idx in st.session_state.f2s_df.index:
        r         = st.session_state.f2s_df.loc[idx]
        prev_phys = int(r["physical count"])

        with st.container(border=True):
            section("Enter Physical Count")
            st.markdown(f"""
            <div class="product-card">
              <div class="pc-code">{r['product code']}</div>
              <div class="pc-name">{r['product name']}</div>
            </div>""", unsafe_allow_html=True)
            if r["last_updated"]: st.caption(f"⏱ Last saved: {r['last_updated']}")

            # Just one input — how many did you count on the floor?
            phys_val = st.number_input(
                "Physical Count — how many did you find?",
                value=prev_phys, min_value=0, step=1, key=f"f2s_p_{idx}")

            b1, b2 = st.columns(2)
            with b1:
                if st.button("💾  Save Count", use_container_width=True):
                    now = datetime.now().strftime("%H:%M:%S")
                    st.session_state.f2s_df.at[idx,"physical count"] = phys_val
                    st.session_state.f2s_df.at[idx,"last_updated"]   = now
                    st.session_state.f2s_counter += 1
                    st.session_state.f2s_sel_idx  = None
                    p_code = str(r["product code"])
                    if st.session_state.f2s_counter % 10 == 0:
                        save_session(SID, CU, LOC, st.session_state.f2s_df)
                        st.toast(f"✅ {p_code} · ☁️ backed up!")
                    else:
                        st.toast(f"✅ {p_code} saved · backup in {10-(st.session_state.f2s_counter%10)}")
                    st.rerun()
            with b2:
                if st.button("✖  Cancel", use_container_width=True):
                    st.session_state.f2s_sel_idx = None
                    st.rerun()

# Recent counts
recent_mask = st.session_state.f2s_df["last_updated"] != ""
if recent_mask.any():
    recent = (st.session_state.f2s_df.loc[recent_mask,
              ["product name","product code","physical count","last_updated"]]
              .sort_values("last_updated",ascending=False).head(5))
    with st.container(border=True):
        section("Recent Counts")
        for _, r in recent.iterrows():
            cnt = int(r["physical count"])
            st.markdown(f"""
            <div class="log-row">
              <div class="log-left">
                <div class="log-name">{r['product name']}</div>
                <div class="log-meta">{r['product code']} · {r['last_updated']}</div>
              </div>
              <div class="log-badge">
                <span class="badge-count">{cnt}</span>
              </div>
            </div>""", unsafe_allow_html=True)

# Footer
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
fa1, fa2 = st.columns(2)
with fa1:
    out = io.BytesIO()
    export_df = st.session_state.f2s_df[["product code","product name","physical count","last_updated"]]
    with pd.ExcelWriter(out,engine="openpyxl") as w:
        export_df.to_excel(w,index=False,sheet_name="Floor Count")
    st.download_button("📤 Export Count",out.getvalue(),
        file_name=f"{SID}_FloorCount_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)
with fa2:
    if st.button("☁️ Backup Now", use_container_width=True):
        save_session(SID, CU, LOC, st.session_state.f2s_df)
        st.session_state.f2s_counter = 0
        st.toast("☁️ Backed up!"); st.rerun()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
if st.button("🚪 Save & Close", use_container_width=True):
    save_session(SID, CU, LOC, st.session_state.f2s_df)
    for k in ["f2s_sid","f2s_loc","f2s_df","f2s_counter","f2s_sel_idx"]:
        st.session_state.pop(k,None)
    st.switch_page("app.py")
