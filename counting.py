import streamlit as st
import os

st.set_page_config(
    page_title="Stock Count",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide all Streamlit chrome
st.markdown("""
<style>
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"],
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

# Read the counting HTML file
html_path = os.path.join(os.path.dirname(__file__), "..", "counting.html")
if not os.path.exists(html_path):
    # Try same directory
    html_path = os.path.join(os.path.dirname(__file__), "counting.html")

try:
    with open(html_path, "r") as f:
        html_content = f.read()
    # Serve full screen
    st.components.v1.html(html_content, height=900, scrolling=True)
except FileNotFoundError:
    st.error("counting.html not found. Make sure it's in the repo root.")
