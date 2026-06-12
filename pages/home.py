import streamlit as st

from ui.layout import render_hero
from ui.metrics import render_metric

from utils.entsoe import render_entsoe_price_fetcher


# ✅ PLAK HIER je volledige originele functie:
def home_page(profile, analysis, profile_key):
    # volledige code uit jouw bestand
    
    render_hero()

    st.markdown("### Wat zit er in deze app?")

    st.markdown("""
    - Verbruiksprofiel: Excel-upload, structuurdetectie
    - Kwartierdata: analyse afname/injectie
    - Zone-dimensionering
    - Panelen & omvormers
    - Opslag & economie
    """)

    st.markdown("### Snelle referentie")

    st.table({
        "Onderdeel": ["Profiel", "PV-analyse", "Catalogi", "Opslag"],
        "Status": [
            "Verbruiksprofiel laden",
            "SC/SS optimum",
            "Compatibiliteit check",
            "LFP model"
        ]
    })

    if profile is not None and analysis is not None:

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            render_metric("Jaarprofiel", "134.246 kWh")

        with c2:
            render_metric("Optimale PV", "90.5 kWp")

        with c3:
            render_metric("Omvormer", "76.9 kW")

        with c4:
            render_metric("Kniepunt", "PU 0.70")

    if profile is not None:

        st.markdown("### Prijzen ophalen")

        render_entsoe_price_fetcher(profile, profile_key)


    if profile is None or analysis is None:
        st.markdown(
            """
            <div style="padding:10px; border:1px solid #f87171; border-radius:8px;">
            ⚠️ Upload eerst een verbruiksprofiel om alle functies te activeren.
            </div>
            """,
            unsafe_allow_html=True
        )


    pass


# ✅ wrapper
def show():
    profile = st.session_state.get("profile_df")
    analysis = st.session_state.get("analysis")
    profile_key = st.session_state.get("profile_key")

    home_page(profile, analysis, profile_key)
