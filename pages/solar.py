import streamlit as st
import plotly.graph_objects as go

# utils
from utils.pv_analysis import build_pv_analysis

# ui
from ui.metrics import render_metric

from utils.plot_style import apply_plotly_style, PLOT_COLORS


# ✅ volledige zonnepagina
def solar_page(profile):

    st.markdown(
        '<div class="section-title">Zonne-dimensionering</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Bepaal de optimale PV-installatie op basis van verbruik en productie."
    )

    # 🔹 instellingen
    col_left, col_right = st.columns([1, 2])

    with col_left:

        st.markdown("### Instellingen")

        specific_yield = st.slider(
            "Specifieke opbrengst (kWh/kWp/jaar)",
            700.0, 1200.0, 950.0, step=10.0
        )

        inverter_ratio = st.slider(
            "DC/AC verhouding",
            0.7, 1.2, 0.85, step=0.01
        )

        analysis = build_pv_analysis(
            profile,
            specific_yield,
            inverter_ratio
        )

        # 🔹 aanbevolen zone (vroeg optimum)
        pu_opt = analysis["pu_opt"]
        pu_early = pu_opt * 0.8
        pu_max = max(analysis["pu_range"])


        st.markdown("### Resultaten")

        render_metric("Optimale capaciteit", f"{analysis['capacity_opt_kwp']:.2f} kWp")
        render_metric("Omvormer", f"{analysis['power_opt_kw']:.2f} kW")

        st.markdown("### Inzichten")

        render_metric("PU optimum", f"{analysis['pu_opt']:.2f}")
        render_metric("Aanbevolen zone", f"{analysis['pu_opt']*0.8:.2f}")

    # 🔹 grafiek SC / SS
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=analysis["pu_range"],
            y=analysis["sc"],
            mode="lines",
            name="Self-consumption",
            line=dict(color=PLOT_COLORS["Consumption"], width=1.5),
            opacity=0.7
        )
    )

    fig.add_trace(
        go.Scatter(
            x=analysis["pu_range"],
            y=analysis["ss"],
            mode="lines",
            name="Self-sufficiency",
            line=dict(color=PLOT_COLORS["Injectie"], width=1.5),
            opacity=0.7
        )
    )

    # 🔹 optimum markers
    fig.add_trace(
        go.Scatter(
            x=[analysis["pu_opt"]],
            y=[analysis["sc"][analysis["idx_opt"]]],
            mode="markers",
            marker=dict(size=10, color="red"),
            name="Aanbevolen",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[analysis["pu_opt"]],
            y=[analysis["ss"][analysis["idx_opt"]]],
            mode="markers",
            marker=dict(size=10, color="red"),
            name="Optimum",
        )
    )

    fig.add_vline(
        x=[analysis["pu_opt"]],
        line=dict(color="red", dash="dash"),
        name="Optimum"
    )

    fig.update_layout(
        title="PV optimalisatie (SC & SS)",
        height=500,
        hovermode="x unified",
    )


    # ✅ HIER toevoegen
    fig = apply_plotly_style(fig)


    # 🔹 optimum evaluatie (marginale winst)
    fig_opt = go.Figure()

    # 🔹 marginale winst berekenen (afgeleide-achtig)
    marginale_winst = [
        analysis["sc"][i] - analysis["sc"][i - 1]
        for i in range(1, len(analysis["sc"]))
    ]
    pu_marg = analysis["pu_range"][1:]

    fig_opt.add_trace(
        go.Scatter(
            x=pu_marg,
            y=marginale_winst,
            mode="lines",
            name="Marginale winst",
        )
    )

    
    # ✅ GROENE ZONE (beste)
    fig_opt.add_vrect(
        x0=0,
        x1=pu_early,
        fillcolor="rgba(34,197,94,0.15)",  # groen
        line_width=0,
    )

    # ✅ GELE ZONE (ok)
    fig_opt.add_vrect(
        x0=pu_early,
        x1=pu_opt,
        fillcolor="rgba(234,179,8,0.15)",  # geel
        line_width=0,
    )

    # ✅ RODE ZONE (overdimensionering)
    fig_opt.add_vrect(
        x0=pu_opt,
        x1=pu_max,
        fillcolor="rgba(239,68,68,0.12)",  # rood
        line_width=0,
    )


    fig_opt.add_vline(
        x=pu_opt,
        line=dict(color="yellow", dash="dash"),
        name="Optimum"
    )

    # optioneel: vroege grens (bv 80%)
    pu_early = pu_opt * 0.8

    fig_opt.add_vline(
        x=pu_early,
        line=dict(color="green", dash="dash"),
        name="Aanbevolen zone"
    )

    # 🔹 visuele zone (zoals oude tool)
    fig_opt.add_vrect(
        x0=0,
        x1=pu_opt,
        fillcolor="rgba(59,130,246,0.1)",
        line_width=0,
    )

    fig_opt.update_layout(
        title="Optimum evaluatie — marginale winst",
        height=400,
    )

    fig_opt = apply_plotly_style(fig_opt)


    # 🔹 extra grafiek: energie
    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=analysis["pu_range"],
            y=analysis["pv_energy"],
            mode="lines",
            name="PV energie",
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=analysis["pu_range"],
            y=analysis["self_use"],
            mode="lines",
            name="Eigenverbruik",
            line=dict(color=PLOT_COLORS["Consumption"], width=1.5),
            opacity=0.7
        )
    )

    fig2.update_layout(
        title="Energie vs dimensionering",
        height=400,
    )

    
    # ✅ HIER toevoegen
    fig2 = apply_plotly_style(fig2)

    with col_right:

        # SC/SS grafiek
        st.plotly_chart(fig, use_container_width=True)

        st.caption("Groen = aanbevolen zone | Geel = optimum bereik | Rood = overdimensionering")

        # Optimum evaluatie
        st.plotly_chart(fig_opt, use_container_width=True)

        # Energie grafiek
        st.plotly_chart(fig2, use_container_width=True)

    return analysis


# ✅ wrapper
def show():

    profile = st.session_state.get("profile_df")

    if profile is None:
        st.warning("Upload eerst een verbruiksprofiel")
        return

    analysis = solar_page(profile)

    # 🔹 BELANGRIJK → opslaan voor andere pagina’s
    st.session_state["analysis"] = analysis
