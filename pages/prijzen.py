import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# utils
from utils.data_loader import get_profile_key
from utils.entsoe import fetch_entsoe_prices_for_profile, fetch_entsoe_prices_for_range
from utils.pricing import (
    load_prices_15min,
    bereken_klantprijs_15min,
)
from utils.plot_style import apply_plotly_style, PLOT_COLORS

# ui
from ui.metrics import render_metric


# ✅ volledige prijzen pagina
def prices_page(profile, analysis=None):

    st.markdown(
        '<div class="section-title-large">Prijzen & kosten</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Combineer kwartierprijzen met verbruiksprofiel voor kostenanalyse."
    )

    profile_key = get_profile_key(profile)

    st.markdown('<div class="section-title">Prijsvisualisatie</div>', unsafe_allow_html=True)

    # 🔹 bron kiezen
    source = st.radio(
        "Prijsbron",
        ["CSV upload", "ENTSO-E"],
        horizontal=True
    )

    prices = None

    # 🔹 CSV
    if source == "CSV upload":
        uploaded_prices = st.file_uploader(
            "Upload kwartierprijzen (CSV)",
            type=["csv"],
            key="prijzen_csv"
        )

        if uploaded_prices:
            try:
                prices = load_prices_15min(uploaded_prices.getvalue())
                st.session_state["prices_df"] = prices
            except Exception as e:
                st.error(f"Fout bij inladen prijzen: {e}")

    # 🔹 ENTSO-E
    else:
        col1, col2 = st.columns(2)

        with col1:
            start = st.date_input("Start datum", key="entsoe_start")

        with col2:
            end = st.date_input("Eind datum", key="entsoe_end")

        if st.button("Haal ENTSO-E prijzen op"):
            try:
                prices = fetch_entsoe_prices_for_range(start, end)
                st.session_state["prices_df"] = prices
                st.success("Prijsdata opgehaald")
            except Exception as e:
                st.error(f"Fout bij ophalen ENTSO-E: {e}")

    # ✅ geladen data
    prices = st.session_state.get("prices_df")

    st.markdown('<div class="section-title-small">Prijsgrafiek</div>', unsafe_allow_html=True)

    if prices is None:
        st.info("Laad eerst prijsdata")
        return

    st.markdown('<div class="section-title">Prijsverloop</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 2])

    with col_left:

            st.markdown("### Parameters")

            factor = st.slider(
                "Factor op marktprijs",
                0.8, 1.3, 1.03, step=0.01
            )

            marge = st.slider(
                "Vaste marge (€/kWh)",
                0.0, 0.2, 0.02, step=0.005
            )

            prices = bereken_klantprijs_15min(prices, factor, marge)

            st.markdown("### Samenvatting")

            render_metric("Records prijzen", f"{len(prices):,}".replace(",", "."))

            render_metric(
                "Gem. EPEX",
                f"{prices['price_kwh'].mean():.3f} €/kWh"
            )

            render_metric(
                "Gem. klantprijs",
                f"{prices['klantprijs_kwh'].mean():.3f} €/kWh"
            )

    with col_right:

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=prices["Datetime"],
                    y=prices["price_kwh"],
                    mode="lines",
                    name="EPEX prijs",
                    line=dict(color=PLOT_COLORS["Afname"])  # blauw
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=prices["Datetime"],
                    y=prices["klantprijs_kwh"],
                    mode="lines",
                    name="Klantprijs",
                    line=dict(color=PLOT_COLORS["Consumption"])  # 🔴 rood
                )
            )

            fig.update_layout(
                title="Prijsverloop",
                height=450,
                hovermode="x unified"
            )

            fig = apply_plotly_style(fig)
            st.plotly_chart(fig, use_container_width=True)


    # 🔹 klantprijs berekenen
    # prices = bereken_klantprijs_15min(prices, factor, marge)

    # 🔹 merge met profiel
    st.markdown('<div class="section-title">Kostenberekening</div>', unsafe_allow_html=True)

    # 🔹 merge
    profile["Datetime"] = pd.to_datetime(profile["Datetime"]).dt.floor("15min")
    prices["Datetime"] = pd.to_datetime(prices["Datetime"]).dt.floor("15min")
    prices = prices.drop_duplicates(subset="Datetime")


    df = profile.merge(prices, on="Datetime", how="inner")

    coverage = len(df) / len(profile)
    st.caption(f"Match met profiel: {coverage:.1%}")

    # ✅ ALS MATCH OK
    if coverage > 0.9:

        st.success("Prijsdata komt overeen met profiel ✅")

    # ❌ ALS GEEN MATCH
    else:

        st.warning("Prijsdata komt niet overeen met profiel ❗")

        if st.button("Haal juiste ENTSO-E data voor profiel"):

            try:
                correct_prices = fetch_entsoe_prices_for_profile(profile)
                st.session_state["prices_df"] = correct_prices
                st.success("Nieuwe correcte prijsdata opgehaald")
                st.rerun()

            except Exception as e:
                st.error(str(e))

        return


    if df.empty:
        st.warning("Geen overlapping tussen profiel en prijsdata")
        return

    # 🔹 kosten berekening
    df["kost"] = df["Afname"] * df["klantprijs_kwh"]
    totale_kost = df["kost"].sum()

    st.markdown('<div class="section-title">Kost over tijd</div>', unsafe_allow_html=True)

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=df["Datetime"],
            y=df["kost"],
            mode="lines",
            name="Kost",
            line=dict(color=PLOT_COLORS["Consumption"])
        )
    )

    fig2.update_layout(
        height=450,
        hovermode="x unified"
    )

    fig2 = apply_plotly_style(fig2)
    st.plotly_chart(fig2, use_container_width=True)

    # 🔹 metrics
    c1, c2 = st.columns(2)

    with c1:
        render_metric(
            "Totale kost",
            f"{totale_kost:,.0f} €".replace(",", "."),
        )

    with c2:
        render_metric(
            "Gemiddelde prijs",
            f"{df['klantprijs_kwh'].mean():.3f} €/kWh"
        )

# ✅ wrapper
def show():

    profile = st.session_state.get("profile_df")
    analysis = st.session_state.get("analysis")

    if profile is None:
        st.warning("Upload eerst een verbruiksprofiel")
        return

    prices_page(profile, analysis)