import streamlit as st
from pathlib import Path

# paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "Logo_Sparki.png"

# navigatie (zoals in je originele file)
NAV_ITEMS = {
    "Home": "🏠",
    "DXF-weergave": "📐",
    "Verbruiksprofiel": "📄",
    "Kwartierdata": "📈",
    "Zonne-dimensionering": "☀️",
    "Panelen & omvormers": "🔌",
    "Opslag & economie": "🔋",
    "Prijzen & kosten": "💶",
}


def render_top_nav(current_page: str) -> str:

    NAV_ITEMS = {
        "Home": "🏠",
        "Verbruiksprofiel": "📄",
        "Kwartierdata": "📈",
        "Prijzen & kosten": "💶",
        "Zonne-dimensionering": "☀️",
        "Panelen & omvormers": "🔌",
        "Opslag & economie": "🔋",
        "DXF-weergave": "📐",
    }

    labels = [f"{icon} {name}" for name, icon in NAV_ITEMS.items()]


# ✅ HERO (volledig uit jouw code)
def render_hero():

    lt = chr(60)
    gt = chr(62)

    html = (
        f"{lt}div style='"
        f"background:linear-gradient(135deg,#1e293b,#0f172a);"
        f"padding:30px;"
        f"border-radius:16px;"
        f"color:white;"
        f"margin-bottom:20px;"
        f"'{gt}"

        # 🔹 TOP BAR
        f"{lt}div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;'{gt}"

            # 🔹 LINKS (logo + naam)
            f"{lt}div style='display:flex; align-items:center; gap:10px;'{gt}"
                f"{lt}div style='background:#334155; padding:6px 10px; border-radius:8px; font-weight:bold;'{gt}✦{lt}/div{gt}"
                f"{lt}div{gt}"
                    f"{lt}div style='font-weight:600; font-size:14px;'{gt}SPARKI{lt}/div{gt}"
                    f"{lt}div style='opacity:0.6; font-size:12px;'{gt}Dimensioneringstool{lt}/div{gt}"
                f"{lt}/div{gt}"
            f"{lt}/div{gt}"

            # 🔹 RECHTS (slogan)
            f"{lt}div style='opacity:0.7; font-size:13px;'{gt}"
            f"Energie. Maar dan juist."
            f"{lt}/div{gt}"

        f"{lt}/div{gt}"

        # 🔹 TITEL
        f"{lt}h1 style='margin-bottom:5px;'{gt}Dimensioneringstool{lt}/h1{gt}"

        # 🔹 BESCHRIJVING
        f"{lt}p style='opacity:0.9; margin-bottom:15px;'{gt}"
        f"Analyseer verbruiksprofielen, optimaliseer PV-installaties "
        f"en bereken kosten op kwartierniveau."
        f"{lt}/p{gt}"

        # 🔹 PILLS (rode vakken)
        f"{lt}div style='display:flex; flex-wrap:wrap; gap:8px;'{gt}"

            f"{lt}span style='background:#ef4444; padding:6px 12px; border-radius:20px;' {gt}Kwartierdata{lt}/span{gt}"
            f"{lt}span style='background:#ef4444; padding:6px 12px; border-radius:20px;' {gt}PV-optimalisatie{lt}/span{gt}"
            f"{lt}span style='background:#ef4444; padding:6px 12px; border-radius:20px;' {gt}Paneelvergelijking{lt}/span{gt}"
            f"{lt}span style='background:#ef4444; padding:6px 12px; border-radius:20px;' {gt}Omvormers{lt}/span{gt}"
            f"{lt}span style='background:#ef4444; padding:6px 12px; border-radius:20px;' {gt}Batterij & ROI{lt}/span{gt}"

        f"{lt}/div{gt}"

        f"{lt}/div{gt}"
    )

    st.markdown(html, unsafe_allow_html=True)






# ✅ TOP NAV
def render_top_nav(current_page: str) -> str:

    nav_labels = [f"{icon} {name}" for name, icon in NAV_ITEMS.items()]

    selected = st.segmented_control(
        "Navigatie",
        nav_labels,
        default=f"{NAV_ITEMS[current_page]} {current_page}"
        if current_page in NAV_ITEMS else nav_labels[0],
    )

    # 🔹 NULL PROTECTIE
    if selected is None:
        return current_page

    for name, icon in NAV_ITEMS.items():
        if selected == f"{icon} {name}":
            return name

    return current_page


# ✅ SIDEBAR
def render_sidebar(current_page: str):

    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), use_container_width=True)

    page = st.sidebar.radio(
        "Navigatie",
        list(NAV_ITEMS.keys()),
        index=list(NAV_ITEMS.keys()).index(current_page)
        if current_page in NAV_ITEMS else 0,
    )

    # st.session_state["page"] = page

    return page