def apply_plotly_style(fig):

    fig.update_layout(
        # ✅ kleuren Sparki
        plot_bgcolor="#0F2A5A",
        paper_bgcolor="#0A1F44",

        # ✅ tekst
        font=dict(color="white"),

        # ✅ grid
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.08)",
            zerolinecolor="rgba(255,255,255,0.2)",
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.08)",
            zerolinecolor="rgba(255,255,255,0.2)",
        ),

        # ✅ legend
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(color="white"),
        ),

        # ✅ hover
        hovermode="x unified",

        hoverlabel=dict(
            bgcolor="#112A5C",
            font_size=12,
            font_color="white"
        ),
    )

    return fig

PLOT_COLORS = {
    "Afname": "#4FC3F7",
    "Injectie": "#0288D1",
    "Productie": "#E0E0E0",
    "Consumption": "#E30613",
}
