import streamlit as st

from ui.theme import apply_theme

from ui.layout import render_top_nav, render_sidebar

from pages import (
    home,
    profile,
    kwartierdata,
    prijzen,
    solar,
    panelen,
    batterij,
    dxf,
)

st.set_page_config(
    page_title="Dimensioneringstool",
    page_icon="Sparki_Ster.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# ✅ Fallback
VALID_PAGES = [
    "Home",
    "Verbruiksprofiel",
    "Kwartierdata",
    "Prijzen & kosten",
    "Zonne-dimensionering",
    "Panelen & omvormers",
    "Opslag & economie",
    "DXF-weergave",
]


# ✅ init session
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# ✅ TOP NAV
page_top = render_top_nav(st.session_state["page"])

# ✅ SIDEBAR
page_side = render_sidebar(st.session_state["page"])

# ✅ PRIORITEIT: wat is veranderd?
if page_top is not None and page_top != st.session_state["page"]:
    st.session_state["page"] = page_top

elif page_side != st.session_state["page"]:
    st.session_state["page"] = page_side


page = st.session_state["page"]

if page == "Home":
    home.show()

elif page == "Verbruiksprofiel":
    profile.show()

elif page == "Kwartierdata":
    kwartierdata.show()

elif page == "Prijzen & kosten":
    prijzen.show()

elif page == "Zonne-dimensionering":
    solar.show()

elif page == "Panelen & omvormers":
    panelen.show()

elif page == "Opslag & economie":
    batterij.show()

elif page == "DXF-weergave":
    dxf.show()
