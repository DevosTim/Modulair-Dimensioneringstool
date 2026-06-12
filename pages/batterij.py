import streamlit as st
import plotly.graph_objects as go

# utils
from utils.battery import simulate_battery, battery_economics
from utils.plot_style import apply_plotly_style, PLOT_COLORS

# ui
from ui.metrics import render_metric


# ✅ volledige batterijpagina
def battery_page(profile):

    st.markdown(
        '<div class="section-title">Opslag & economie</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Simuleer batterijopslag en analyseer impact op eigenverbruik en kosten."
    )

    # 🔹 instellingen
    col1, col2, col3 = st.columns(3)

    with col1:
        capacity = st.slider(
            "Capaciteit (kWh)",
            1.0,
            100.0,
            10.0,
            step=1.0,
        )

    with col2:
        power = st.slider(
            "Vermogen (kW)",
            1.0,
            50.0,
            5.0,
            step=1.0,
        )

    with col3:
        efficiency = st.slider(
            "Efficiëntie",
            0.7,
            1.0,
            0.95,
            step=0.01,
        )

    # 🔹 simulatie uitvoeren
    result = simulate_battery(
        profile,
        capacity,
        power,
        efficiency
    )

    df = result["df"]

    # 🔹 metrics
    c1, c2, c3 = st.columns(3)

    with c1:
        render_metric("Self-consumption", f"{result['SC']:.3f}")

    with c2:
        render_metric("Self-sufficiency", f"{result['SS']:.3f}")

    with c3:
        render_metric(
            "Netafname",
            f"{result['grid_import']:,.0f} kWh".replace(",", ".")
        )

    # 🔹 SOC grafiek
    fig_soc = go.Figure()

    fig_soc.add_trace(
        go.Scatter(
            x=df["Datetime"],
            y=df["SOC"],
            mode="lines",
            name="State of Charge",
        )
    )

    fig_soc.update_layout(
        title="Battery State of Charge",
        height=400,
    )

    fig_soc = apply_plotly_style(fig_soc)
    st.plotly_chart(fig_soc, use_container_width=True)

    # 🔹 import/export grafiek
    fig_grid = go.Figure()

    fig_grid.add_trace(
        go.Scatter(
            x=df["Datetime"],
            y=df["Grid_Import"],
            mode="lines",
            name="Grid import",
        )
    )

    fig_grid.add_trace(
        go.Scatter(
            x=df["Datetime"],
            y=df["Grid_Export"],
            mode="lines",
            name="Grid export",
        )
    )

    fig_grid.update_layout(
        title="Net interactie",
        height=400,
    )

    fig_grid = apply_plotly_style(fig_grid)
    st.plotly_chart(fig_grid, use_container_width=True)

    # 🔹 ECONOMIE (optioneel)
    prices = st.session_state.get("prices_df")

    if prices is not None:

        eco = battery_economics(result, prices)

        if eco is not None:

            savings = eco["savings"]

            st.markdown(
                '<div class="section-title">Economische impact</div>',
                unsafe_allow_html=True,
            )

            render_metric(
                "Besparing",
                f"{savings:,.0f} €".replace(",", ".")
            )

            df_eco = eco["df"]

            fig_cost = go.Figure()

            fig_cost.add_trace(
                go.Scatter(
                    x=df_eco["Datetime"],
                    y=df_eco["kost_zonder"],
                    mode="lines",
                    name="Zonder batterij",
                )
            )

            fig_cost.add_trace(
                go.Scatter(
                    x=df_eco["Datetime"],
                    y=df_eco["kost_met"],
                    mode="lines",
                    name="Met batterij",
                )
            )

            fig_cost.update_layout(
                title="Kostvergelijking",
                height=400,
            )

            st.plotly_chart(fig_cost, use_container_width=True)

    else:
        st.info("Laad prijsdata om economische analyse te zien")


# ✅ wrapper
def show():

    profile = st.session_state.get("profile_df")

    if profile is None:
        st.warning("Upload eerst een verbruiksprofiel")
        return

    battery_page(profile)