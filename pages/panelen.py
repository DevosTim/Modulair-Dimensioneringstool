import streamlit as st
import pandas as pd

# utils (we voegen hier simpele loaders toe)
from utils.catalog import (
    load_panel_catalog,
    load_inverter_catalog,
)

# ui
from ui.metrics import render_metric


# ✅ volledige pagina
def panels_inverters_page(panel_df, inverter_df, analysis):

    # 🔹 benodigde capaciteit uit analyse
    target_kwp = analysis["capacity_opt_kwp"]
    target_kw = analysis["power_opt_kw"]

    st.markdown(
        '<div class="section-title">Panelen & omvormers</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Selecteer een paneel."
    )

    # 🔹 PANELEN
    st.markdown(
        '<div class="section-title">Zonnepanelen</div>',
        unsafe_allow_html=True,
    )

    panel_df = panel_df.copy()
    panel_df.columns = panel_df.columns.str.strip().str.lower()

    # ✅ numeric maken
    panel_df["pnom"] = pd.to_numeric(panel_df["pnom"], errors="coerce")

    # =========================================================
    # ✅ 1. MERK KEUZE
    # =========================================================

    merken = sorted(panel_df["merk"].dropna().unique().tolist())
    merken.insert(0, "Alles")

    col_filters = st.columns(2)

    with col_filters[0]:
        gekozen_merk = st.selectbox("Merk", merken)

    # =========================================================
    # ✅ 2. TYPE KEUZE (afhankelijk van merk)
    # =========================================================

    if gekozen_merk == "Alles":
        df_filtered = panel_df
    else:
        df_filtered = panel_df[panel_df["merk"] == gekozen_merk]

    types = sorted(df_filtered["type"].dropna().unique().tolist())
    types.insert(0, "Alles")

    with col_filters[1]:
        gekozen_type = st.selectbox("Type", types)

    # =========================================================
    # ✅ 3. FILTER TYPE
    # =========================================================

    if gekozen_type != "Alles":
        df_filtered = df_filtered[df_filtered["type"] == gekozen_type]

    # =========================================================
    # ✅ HANDMATIG AANTAL PANELEN
    # =========================================================

    st.markdown("### Aantal panelen")

    aantal_panelen_input = st.number_input(
        "Aantal panelen (handmatig)",
        min_value=1,
        max_value=200,
        value=10,
        step=1
    )

    # =========================================================
    # ✅ 4. OOST-WEST KEUZE
    # =========================================================

    st.markdown("### Opstelling")

    oost_west = st.radio(
        "Oost-West opstelling?",
        ["Ja", "Nee"]
    )

    # =========================================================
    # ✅ 5. CONDITIONELE DAKORIËNTATIE
    # =========================================================

    dak_orientatie = None

    if oost_west == "Nee":
        dak_orientatie = st.selectbox(
            "Dakoriëntatie",
            ["Zuid", "Oost", "West", "Noord"]
        )

    # =========================================================
    # ✅ 6. PANELEN BEREKENEN
    # =========================================================

    df_filtered = df_filtered.copy()

    df_filtered["Aantal panelen"] = aantal_panelen_input

    df_filtered["Totale kWp"] = (
        df_filtered["Aantal panelen"] * df_filtered["pnom"] / 1000).round(2)


    # =========================================================
    # ✅ 7. EXTRA LOGICA OOST-WEST (basic)
    # =========================================================

    if oost_west == "Ja":
        df_filtered["Panelen Oost"] = (df_filtered["Aantal panelen"] / 2).round(0)
        df_filtered["Panelen West"] = (df_filtered["Aantal panelen"] / 2).round(0)
    else:
        df_filtered["Oriëntatie"] = dak_orientatie

    # =========================================================
    # ✅ 8. RESULTAAT TABEL
    # =========================================================

    st.markdown("### Geselecteerd paneel")

    st.dataframe(df_filtered, use_container_width=True)

    st.caption(
        "Selecteer geschikte panelen en omvormers op basis van de berekende PV-installatie."
    )

    # =========================================================
    # ✅ TOTALE VERMOGEN BEREKENING (1 waarde)
    # =========================================================

    if len(df_filtered) > 0:
        # neem eerste geselecteerde paneel
        paneel_vermogen = df_filtered["pnom"].iloc[0]

        totale_kwp = (aantal_panelen_input * paneel_vermogen) / 1000
    else:
        totale_kwp = 0

    # =========================================================
    # ✅ VISUEEL VAK (metric)
    # =========================================================

    c_tot1, c_tot2 = st.columns(2)

    with c_tot1:
        render_metric("Aantal panelen", f"{aantal_panelen_input}")

    with c_tot2:
        render_metric("Totale capaciteit", f"{totale_kwp:.2f} kWp")




    # 🔹 metrics
    c1, c2 = st.columns(2)

    with c1:
        render_metric("PV capaciteit nodig", f"{target_kwp:.2f} kWp")

    with c2:
        render_metric("Omvormer vermogen", f"{target_kw:.2f} kW")

    # 🔹 PANELEN
    st.markdown(
        '<div class="section-title">Zonnepanelen</div>',
        unsafe_allow_html=True,
    )

    power_col = None
    
    panel_df = panel_df.copy()
    panel_df.columns = panel_df.columns.str.strip().str.lower()

    if "pnom" not in panel_df.columns:
        st.error("Kolom 'Pnom' niet gevonden. Beschikbare kolommen:")
        st.write(panel_df.columns)
    else:
        panel_df["pnom"] = pd.to_numeric(panel_df["pnom"], errors="coerce")
        panel_df["Aantal panelen"] = (
            target_kwp * 1000 / panel_df["pnom"]
        ).round(0)

    st.dataframe(panel_df, use_container_width=True)

    # 🔹 OMVORMERS
    st.markdown(
        '<div class="section-title">Omvormers</div>',
        unsafe_allow_html=True,
    )

    inverter_power_col = None
    
    inverter_df = inverter_df.copy()
    inverter_df.columns = inverter_df.columns.str.strip().str.lower()

    if "pac_nominaal" not in inverter_df.columns:
        st.error("Kolom 'Pac_nominaal' niet gevonden. Beschikbare kolommen:")
        st.write(inverter_df.columns)
    else:
        inverter_df["pac_nominaal"] = pd.to_numeric(inverter_df["pac_nominaal"], errors="coerce")

        inverter_df["geschikt"] = (
            inverter_df["pac_nominaal"] >= target_kw * 0.8
        ) & (
            inverter_df["pac_nominaal"] <= target_kw * 1.2
        )

        st.dataframe(inverter_df, use_container_width=True)



# ✅ wrapper
def show():

    analysis = st.session_state.get("analysis")

    if analysis is None:
        st.warning("Voer eerst zonne-dimensionering uit")
        return

    # 🔹 catalogus laden
    panel_df = load_panel_catalog()
    inverter_df = load_inverter_catalog()

    panels_inverters_page(panel_df, inverter_df, analysis)