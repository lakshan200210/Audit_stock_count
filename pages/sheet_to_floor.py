import streamlit as st
import pandas as pd
import psycopg2
import psycopg2.extras
import hashlib
import io
import json
from datetime import datetime

st.set_page_config(page_title="Sheet to Floor",page_icon="📋",layout="centered",initial_sidebar_state="collapsed")

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
  border-color:#00509E!important;box-shadow:0 0 0 3px rgba(0,80,158,.1)!important;outline:none!important}
.stButton>button,.stDownloadButton>button{
  background:linear-gradient(135deg,#002855,#00509E)!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-weight:600!important;height:auto!important;min-height:46px!important;
  box-shadow:0 2px 8px rgba(0,80,158,.22)!important;
  white-space:normal!important;word-break:break-word!important;
  text-align:left!important;padding:10px 14px!important;line-height:1.4!important}
.stButton>button *,.stDownloadButton>button *{color:#fff!important}
.count-header{background:linear-gradient(135deg,#002855,#00509E);border-radius:14px;
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
.stat-value{font-size:1.85rem;font-weight:700;color:#002855;line-height:1}
.vbox{border-radius:12px;padding:14px 10px;text-align:center}
.vbox.neutral{background:#F4F6FA;border:1px solid #E2E8F0}
.vbox.positive{background:#ECFDF5;border:1px solid #6EE7B7}
.vbox.negative{background:#FEF2F2;border:1px solid #FCA5A5}
.vbox-label{font-size:.69rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#8A9BAE;margin-bottom:5px}
.vbox-value{font-size:1.85rem;font-weight:700;line-height:1}
.vbox.neutral .vbox-value{color:#0D1B2A}
.vbox.positive .vbox-value{color:#059669}
.vbox.negative .vbox-value{color:#DC2626}
.prog-wrap{margin-top:16px}
.prog-head{display:flex;justify-content:space-between;font-size:.77rem;color:#8A9BAE;margin-bottom:6px}
.prog-track{background:#E2E8F0;border-radius:999px;height:7px;overflow:hidden}
.prog-fill{background:linear-gradient(90deg,#002855,#5BC4FF);height:100%;border-radius:999px}
.log-row{display:flex;align-items:center;justify-content:space-between;gap:10px;
  padding:11px 14px;background:#F8FAFC;border:1px solid #E8EDF3;border-radius:10px;margin-bottom:7px}
.log-left{flex:1;min-width:0}
.log-name{font-weight:600;font-size:.88rem;color:#0D1B2A;word-break:break-word;white-space:normal}
.log-meta{font-size:.76rem;color:#8A9BAE;margin-top:1px}
.log-badge{flex-shrink:0}
.badge-pos{background:#D1FAE5;color:#065F46!important;border-radius:6px;padding:3px 10px;font-size:.79rem;font-weight:700;font-family:'DM Mono',monospace;white-space:nowrap;display:inline-block}
.badge-neg{background:#FEE2E2;color:#991B1B!important;border-radius:6px;padding:3px 10px;font-size:.79rem;font-weight:700;font-family:'DM Mono',monospace;white-space:nowrap;display:inline-block}
.badge-zero{background:#E2E8F0;color:#374151!important;border-radius:6px;padding:3px 10px;font-size:.79rem;font-weight:700;font-family:'DM Mono',monospace;white-space:nowrap;display:inline-block}
.product-card{background:#EEF5FF;border:2px solid #00509E;border-radius:14px;padding:14px 16px;margin-bottom:14px}
.pc-code{font-family:'DM Mono',monospace;font-size:.76rem;color:#5A6A7A;margin-bottom:4px}
.pc-name{font-size:.98rem;font-weight:700;color:#002855;line-height:1.35;word-break:break-word}
.sync-bar{background:#EEF2F7;border:1px solid #E2E8F0;border-radius:10px;
  padding:10px 16px;display:flex;align-items:center;margin-bottom:14px;font-size:.82rem}
.sync-dot-ok{width:8px;height:8px;border-radius:50%;background:#10B981;display:inline-block;margin-right:6px}
.sync-dot-pending{width:8px;height:8px;border-radius:50%;background:#F59E0B;display:inline-block;margin-right:6px}
.divider{border:none;border-top:1px solid #E2E8F0;margin:18px 0}
</style>
""", unsafe_allow_html=True)


# ── DB ─────────────────────────────────────────────────────────────
def hash_password(p): return hashlib.sha256(p.strip().encode()).hexdigest()

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
    cols = ["product code","product name","systems count","physical count","difference","last_updated"]
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
           VALUES(%s,%s,%s,%s,%s,'sheet_to_floor')
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


# ── AUTH CHECK ─────────────────────────────────────────────────────
if "current_user" not in st.session_state or not st.session_state.current_user:
    st.warning("Please sign in first.")
    if st.button("← Go to Sign In"):
        st.switch_page("app.py")
    st.stop()

CU  = st.session_state.current_user
SID = st.session_state.get("s2f_sid")
LOC = st.session_state.get("s2f_loc","")

# ── LOAD SESSION ───────────────────────────────────────────────────
# Read sid from localStorage via query params if not in session_state
qp = st.query_params
if not SID:
    sid_qp = qp.get("sid","")
    if sid_qp:
        df_loaded = load_session(sid_qp)
        if df_loaded is not None:
            row = run("SELECT client FROM audit_sessions WHERE sid=%s",(sid_qp,),fetch="one")
            st.session_state.s2f_sid      = sid_qp
            st.session_state.s2f_loc      = row["client"] if row else ""
            st.session_state.s2f_df       = df_loaded
            st.session_state.s2f_counter  = 0
            st.session_state.s2f_sel_idx  = None
            SID = sid_qp
            LOC = st.session_state.s2f_loc

if not SID:
    # Inject JS to read localStorage and redirect with sid
    st.components.v1.html("""
    <script>
    const sid=localStorage.getItem("bdo_sid");
    if(sid){const url=new URL(window.parent.location.href);
      url.searchParams.set("sid",sid);
      window.parent.location.href=url.toString();}
    else{window.parent.location.href=window.parent.location.origin;}
    </script>""", height=0)
    st.stop()

# Init session_state keys if first load
if "s2f_df" not in st.session_state:
    df_loaded = load_session(SID)
    if df_loaded is None:
        st.error("Session not found."); st.stop()
    row = run("SELECT client FROM audit_sessions WHERE sid=%s",(SID,),fetch="one")
    st.session_state.s2f_df      = df_loaded
    st.session_state.s2f_loc     = row["client"] if row else ""
    st.session_state.s2f_counter = 0
    st.session_state.s2f_sel_idx = None
    LOC = st.session_state.s2f_loc

if "s2f_counter"  not in st.session_state: st.session_state.s2f_counter  = 0
if "s2f_sel_idx"  not in st.session_state: st.session_state.s2f_sel_idx  = None


# ══════════════════════════════════════════════════════════════════
#  COUNTING SCREEN — SHEET TO FLOOR
# ══════════════════════════════════════════════════════════════════
updated_mask = st.session_state.s2f_df["last_updated"] != ""
total   = len(st.session_state.s2f_df)
counted = int(updated_mask.sum())
n_vars  = int(((st.session_state.s2f_df["difference"]!=0)&updated_mask).sum())
pct     = round(counted/total*100,1) if total else 0.0

# Header
st.markdown(f"""
<div class="count-header">
  <div class="ch-mode">📋➡️📦 Sheet to Floor</div>
  <div class="ch-sid">{SID}</div>
  <div class="ch-loc">📍 {LOC or '—'}</div>
</div>""", unsafe_allow_html=True)

sync_status(st.session_state.s2f_counter)

# Stats
with st.container(border=True):
    section("Count Overview")
    m1,m2,m3 = st.columns(3)
    m1.markdown(f'<div class="stat-box"><div class="stat-label">Total</div><div class="stat-value">{total}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="stat-box"><div class="stat-label">Counted</div><div class="stat-value">{counted}</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="stat-box"><div class="stat-label">Variances</div><div class="stat-value" style="color:#DC2626">{n_vars}</div></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="prog-wrap">
      <div class="prog-head"><span>Progress</span><span><b style="color:#002855">{pct}%</b></span></div>
      <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
    </div>""", unsafe_allow_html=True)

# Search
with st.container(border=True):
    section("Search Product")
    search = st.text_input("", placeholder="🔍  Product name or code…",
                           label_visibility="collapsed", key="s2f_search")
    if search.strip():
        q    = search.strip()
        mask = (st.session_state.s2f_df["product name"].str.contains(q,case=False,na=False)|
                st.session_state.s2f_df["product code"].str.contains(q,case=False,na=False))
        matches = st.session_state.s2f_df.loc[mask].head(20)
        if matches.empty:
            st.warning("No products found.")
        else:
            st.caption(f"{len(matches)} result{'s' if len(matches)!=1 else ''} — tap to select")
            for ri in matches.index:
                r    = st.session_state.s2f_df.loc[ri]
                tick = "✅ " if r["last_updated"] else ""
                if st.button(f"{tick}{r['product code']}  —  {r['product name']}",
                             key=f"s2f_pick_{ri}", use_container_width=True):
                    st.session_state.s2f_sel_idx = int(ri)
                    st.rerun()

# Count entry
if st.session_state.s2f_sel_idx is not None:
    idx = st.session_state.s2f_sel_idx
    if idx in st.session_state.s2f_df.index:
        r         = st.session_state.s2f_df.loc[idx]
        sys_qty   = int(r["systems count"])
        prev_phys = int(r["physical count"])

        with st.container(border=True):
            section("Physical Count")
            st.markdown(f"""
            <div class="product-card">
              <div class="pc-code">{r['product code']}</div>
              <div class="pc-name">{r['product name']}</div>
            </div>""", unsafe_allow_html=True)
            if r["last_updated"]: st.caption(f"⏱ Last saved: {r['last_updated']}")

            q1,q2,q3 = st.columns(3)
            with q1:
                st.markdown(f'<div class="stat-box"><div class="stat-label">System Qty</div><div class="stat-value">{sys_qty}</div></div>', unsafe_allow_html=True)
            with q2:
                phys_val = st.number_input("Physical Count",value=prev_phys,min_value=0,step=1,key=f"s2f_p_{idx}")
            with q3:
                diff = phys_val - sys_qty
                cls  = "positive" if diff>0 else "negative" if diff<0 else "neutral"
                sign = "+" if diff>0 else ""
                st.markdown(f'<div class="vbox {cls}"><div class="vbox-label">Variance</div><div class="vbox-value">{sign}{diff}</div></div>', unsafe_allow_html=True)

            st.components.v1.html(f"""
            <script>(function(){{
              const sys={sys_qty};
              function attach(){{
                const inputs=window.parent.document.querySelectorAll('input[type="number"]');
                let physIn=null;
                inputs.forEach(el=>{{if(el.closest('[data-testid="stNumberInput"]'))physIn=el;}});
                const vboxes=window.parent.document.querySelectorAll('.vbox-value');
                const vbox=vboxes[vboxes.length-1];
                const vboxEl=vbox?vbox.closest('.vbox'):null;
                if(!physIn||!vbox)return;
                physIn.addEventListener('input',function(){{
                  const diff=(parseInt(physIn.value)||0)-sys;
                  vbox.textContent=diff>0?'+'+diff:String(diff);
                  if(diff>0){{vboxEl.style.background='#ECFDF5';vboxEl.style.borderColor='#6EE7B7';vbox.style.color='#059669';}}
                  else if(diff<0){{vboxEl.style.background='#FEF2F2';vboxEl.style.borderColor='#FCA5A5';vbox.style.color='#DC2626';}}
                  else{{vboxEl.style.background='#F4F6FA';vboxEl.style.borderColor='#E2E8F0';vbox.style.color='#0D1B2A';}}
                }});
              }}
              attach();setTimeout(attach,500);
            }})();</script>""", height=0)

            b1,b2 = st.columns(2)
            with b1:
                if st.button("💾  Save Count", use_container_width=True):
                    now  = datetime.now().strftime("%H:%M:%S")
                    diff = phys_val - sys_qty
                    st.session_state.s2f_df.at[idx,"physical count"] = phys_val
                    st.session_state.s2f_df.at[idx,"difference"]     = diff
                    st.session_state.s2f_df.at[idx,"last_updated"]   = now
                    st.session_state.s2f_counter += 1
                    st.session_state.s2f_sel_idx  = None
                    p_code = str(r["product code"])
                    if st.session_state.s2f_counter % 10 == 0:
                        save_session(SID, CU, LOC, st.session_state.s2f_df)
                        st.toast(f"✅ {p_code} · ☁️ backed up!")
                    else:
                        st.toast(f"✅ {p_code} saved · backup in {10-(st.session_state.s2f_counter%10)}")
                    st.rerun()
            with b2:
                if st.button("✖  Cancel", use_container_width=True):
                    st.session_state.s2f_sel_idx = None
                    st.rerun()

# Recent counts
recent_mask = st.session_state.s2f_df["last_updated"] != ""
if recent_mask.any():
    recent = (st.session_state.s2f_df.loc[recent_mask,
              ["product name","product code","difference","last_updated"]]
              .sort_values("last_updated",ascending=False).head(5))
    with st.container(border=True):
        section("Recent Counts")
        for _, r in recent.iterrows():
            d = int(r["difference"])
            badge = (f'<span class="badge-pos">+{d}</span>' if d>0 else
                     f'<span class="badge-neg">{d}</span>'  if d<0 else
                     f'<span class="badge-zero">±0</span>')
            st.markdown(f"""
            <div class="log-row">
              <div class="log-left">
                <div class="log-name">{r['product name']}</div>
                <div class="log-meta">{r['product code']} · {r['last_updated']}</div>
              </div>
              <div class="log-badge">{badge}</div>
            </div>""", unsafe_allow_html=True)

# Footer
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
fa1,fa2,fa3 = st.columns(3)
with fa1:
    out = io.BytesIO()
    with pd.ExcelWriter(out,engine="openpyxl") as w:
        st.session_state.s2f_df.to_excel(w,index=False,sheet_name="Stock Count")
    st.download_button("📤 Export All",out.getvalue(),
        file_name=f"{SID}_StockCount_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)
with fa2:
    out2 = io.BytesIO()
    with pd.ExcelWriter(out2,engine="openpyxl") as w:
        st.session_state.s2f_df[st.session_state.s2f_df["difference"]!=0].to_excel(w,index=False,sheet_name="Variances")
    st.download_button("⚠️ Variances",out2.getvalue(),
        file_name=f"{SID}_Variances_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)
with fa3:
    if st.button("☁️ Backup Now", use_container_width=True):
        save_session(SID, CU, LOC, st.session_state.s2f_df)
        st.session_state.s2f_counter = 0
        st.toast("☁️ Backed up!"); st.rerun()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
if st.button("🚪 Save & Close", use_container_width=True):
    save_session(SID, CU, LOC, st.session_state.s2f_df)
    for k in ["s2f_sid","s2f_loc","s2f_df","s2f_counter","s2f_sel_idx"]:
        st.session_state.pop(k,None)
    st.switch_page("app.py")
