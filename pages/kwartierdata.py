import streamlit as st
import plotly.graph_objects as go

# utils
from utils.helpers import (
    filter_timeseries_by_selector,
)
from utils.helpers import make_framework_wo_zon
from utils.plot_style import apply_plotly_style, PLOT_COLORS


# ui
from ui.metrics import render_metric


# ✅ volledige pagina (gebaseerd op jouw originele code)
def profiles_page(profile):

    st.markdown(
        '<div class="section-title">Kwartierdata</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Geüploade Excel met dezelfde structuur als JOC_profiel.xlsx, over alle beschikbare jaren."
    )

    # 🔹 zonder zon
    no_sun = make_framework_wo_zon(profile)

    # 🔹 FILTER
    with st.expander("Filter hoofdgrafiek", expanded=False):
        profile_main = filter_timeseries_by_selector(
            profile, "kw_main", "Selecteer periode hoofdgrafiek"
        )

    if profile_main.empty:
        st.warning("Geen data voor gekozen periode")
        profile_main = profile.copy()

    # 🔹 plot data aanpassen
    plot_df = profile_main.copy()

    if "Injectie" in plot_df.columns:
        plot_df["Injectie"] = -plot_df["Injectie"]

    # 🔹 HOOFDGRAFIEK
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=plot_df["Datetime"],
            y=plot_df["Afname"],
            mode="lines",
            name="Afname",
            line=dict(color=PLOT_COLORS["Afname"], width=1.5),
            opacity=0.7
        )
    )

    fig.add_trace(
        go.Scatter(
            x=plot_df["Datetime"],
            y=plot_df["Injectie"],
            mode="lines",
            name="Injectie",
            line=dict(color=PLOT_COLORS["Injectie"], width=1.5),
            opacity=0.7
        )
    )

    fig.add_trace(
        go.Scatter(
            x=plot_df["Datetime"],
            y=plot_df["Productie"],
            mode="lines",
            name="Productie",
            line=dict(color=PLOT_COLORS["Productie"], width=1.5),
            opacity=0.7
        )
    )

    fig.add_trace(
        go.Scatter(
            x=plot_df["Datetime"],
            y=plot_df["Consumption"],
            mode="lines",
            name="Consumption",
            line=dict(color=PLOT_COLORS["Consumption"], width=1.5),
            opacity=0.7
        )
    )

    fig.update_layout(
    height=600,
    title="Kwartierprofiel",
    hovermode="x unified",
    )

    # ✅ HIER toevoegen
    fig = apply_plotly_style(fig)

    st.plotly_chart(fig, use_container_width=True)

    # 🔹 METRICS
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric(
            "Afname",
            f"{profile['Afname'].sum():,.0f} kWh".replace(",", "."),
        )

    with c2:
        render_metric(
            "Injectie",
            f"{profile['Injectie'].sum():,.0f} kWh".replace(",", "."),
        )

    with c3:
        render_metric(
            "Productie",
            f"{profile['Productie'].sum():,.0f} kWh".replace(",", "."),
        )

    with c4:
        render_metric(
            "Zonder zon",
            f"{no_sun['Afname'].sum():,.0f} kWh".replace(",", "."),
        )

    # 🔹 LOSSE GRAFIEKEN
    st.markdown(
        '<div class="section-title">Losse grafieken per reeks</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Filter losse grafieken", expanded=False):
        profile_small = filter_timeseries_by_selector(
            profile, "kw_small", "Selecteer periode losse grafieken"
        )

    if profile_small.empty:
        profile_small = profile.copy()

    col1, col2 = st.columns(2)

    def small_plot(df, column):
        fig_small = go.Figure()

        fig_small.add_trace(
            go.Scatter(
                x=df["Datetime"],
                y=df[column],
                mode="lines",
                name=column,
            )
        )

        fig_small.update_layout(height=300, title=column)

        
        # ✅ HIER toevoegen
        fig_small = apply_plotly_style(fig_small)

        return fig_small

    with col1:
        st.plotly_chart(small_plot(profile_small, "Afname"), use_container_width=True)
        st.plotly_chart(
            small_plot(profile_small, "Productie"), use_container_width=True
        )

    with col2:
        st.plotly_chart(
            small_plot(profile_small, "Injectie"), use_container_width=True
        )
        st.plotly_chart(
            small_plot(profile_small, "Consumption"), use_container_width=True
        )

    # 🔹 WITHOUT SUN TABLE
    st.markdown(
        '<div class="section-title">Vergelijking zonder zon</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(no_sun.head(20), use_container_width=True)


# ✅ wrapper
def show():

    profile = st.session_state.get("profile_df")

    if profile is None:
        st.warning("Upload eerst een verbruiksprofiel")
        return

    profiles_page(profile)