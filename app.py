
"""
Ai text summarisation using NLP and transformer model — entry point
Run:  streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Ai text summarisation using NLP and transformer model",
    page_icon="logo.png",   
    layout="wide",
    initial_sidebar_state="collapsed",
)


# Logo on top (same as before)
st.markdown("""
<style>
.logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: -20px;
    margin-bottom: 10px;
}
.logo-container img {
    width: 220px;
    transition: transform 0.4s ease;
}
.logo-container img:hover {
    transform: scale(1.08) rotate(1deg);
}
</style>
""", unsafe_allow_html=True)

# st.markdown(
#     '<div class="logo-container"><img src="assets/logo.png"></div>',
#     unsafe_allow_html=True
# )

from app.ui import render_page
render_page()