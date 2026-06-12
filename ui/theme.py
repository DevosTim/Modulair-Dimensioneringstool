import streamlit as st

def apply_theme():
    st.markdown("""
    <style>

    /* ====== ROOT APP ====== */
    .stApp {
        background-color: #0A1F44;
    }

    /* ====== MAIN CONTENT ====== */
    .block-container {
        background-color: #0A1F44;
        color: white;
        padding-top: 2rem;
    }

    /* ====== SIDEBAR ====== */
    section[data-testid="stSidebar"] {
        background-color: #112A5C;
    }

    /* ====== TEXT ====== */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: white !important;
    }

    /* ====== SECTION TITLES ====== */
    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }
                
    .section-title-large {
        font-size: 50px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }
                
    .section-title-small {
        font-size: 15px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    /* ====== METRIC CARDS ====== */
    .metric-card {
        background: #112A5C;
        padding: 20px;
        border-radius: 16px;
    }

    .metric-label {
        color: #B8C5E0;
        font-size: 14px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 600;
        color: #FFFFFF;
    }

    /* ====== BUTTON ====== */
    .stButton > button {
        background-color: #E30613;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 18px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #b80510;
    }

    /* ====== INPUT / UPLOAD ====== */
    .stFileUploader {
        background-color: #112A5C;
        border-radius: 12px;
        padding: 10px;
    }

    /* ====== NAV (segmented control) ====== */
    div[data-baseweb="segmented-control"] {
        background-color: #112A5C !important;
        border-radius: 16px;
        padding: 4px;
    }

    div[data-baseweb="segmented-control"] [role="tab"] {
        color: white !important;
        border-radius: 12px !important;
    }

    div[data-baseweb="segmented-control"] [aria-selected="true"] {
        background-color: #E30613 !important;
        color: white !important;
    }

    /* ====== SLIDER ====== */
    .stSlider {
        color: white;
    }

    </style>
    """, unsafe_allow_html=True)