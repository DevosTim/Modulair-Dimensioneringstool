import tempfile
import streamlit as st
import io
import plotly.graph_objects as go
from shapely.geometry import MultiPoint
import math

def hoek_naar_richting_zuid(angle):

    if -45 <= angle <= 45:
        return "Zuid"
    elif 45 < angle <= 135:
        return "West"
    elif -135 <= angle < -45:
        return "Oost"
    else:
        return "Noord"


# probeer ezdxf (optioneel)
try:
    import ezdxf
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False


# ✅ volledige DXF pagina
def render_dxf_viewer_page():

    st.markdown(
        '<div class="section-title">DXF-weergave</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Upload een DXF-bestand om geometrie en elementen te inspecteren."
    )

    uploaded_file = st.file_uploader(
        "Upload DXF bestand",
        type=["dxf"]
    )

    if uploaded_file is None:
        st.info("Upload een DXF bestand om te starten")
        return

    # 🔴 als library ontbreekt
    if not EZDXF_AVAILABLE:
        st.error(
            "ezdxf library niet geïnstalleerd. Installeer met: pip install ezdxf"
        )
        return

    try:
        uploaded_file.seek(0)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()

    except Exception as e:
        st.error(f"Fout bij lezen DXF: {e}")
        return


    st.success("DXF succesvol geladen")

    lines = []
    circles = []

    for e in msp:
        if e.dxftype() == "LINE":
            lines.append({
                "x1": e.dxf.start.x,
                "y1": e.dxf.start.y,
                "x2": e.dxf.end.x,
                "y2": e.dxf.end.y,
            })

        elif e.dxftype() == "CIRCLE":
            circles.append({
                "x": e.dxf.center.x,
                "y": e.dxf.center.y,
                "r": e.dxf.radius,
            })

    if lines:

        fig = go.Figure()

        # 🔹 lijnen tekenen
        for line in lines:
            fig.add_trace(
                go.Scatter(
                    x=[line["x1"], line["x2"]],
                    y=[line["y1"], line["y2"]],
                    mode="lines",
                    line=dict(color="#3b82f6", width=2),
                    showlegend=False
                )
            )

        # 🔹 bounding box berekenen
        xs = []
        ys = []
        for line in lines:
            xs.extend([line["x1"], line["x2"]])
            ys.extend([line["y1"], line["y2"]])



        if xs and ys:
            points = list(zip(xs, ys))

            # 🔹 convex hull + minimum rotated rectangle
            poly = MultiPoint(points)
            min_rect = poly.minimum_rotated_rectangle

            # 🔹 hoekpunten
            xs_rect, ys_rect = min_rect.exterior.xy

            xs_rect = list(xs_rect)
            ys_rect = list(ys_rect)


            # 🔴 rode box tekenen
            fig.add_trace(
                go.Scatter(
                    x=xs_rect,
                    y=ys_rect,
                    mode="lines",
                    line=dict(color="red", width=3),
                    name="MinRotRect"
                )
            )


            # hoekpunten
            coords = list(min_rect.exterior.coords)

            dx1 = coords[1][0] - coords[0][0]
            dy1 = coords[1][1] - coords[0][1]

            dx2 = coords[2][0] - coords[1][0]
            dy2 = coords[2][1] - coords[1][1]

            side1 = math.hypot(dx1, dy1)
            side2 = math.hypot(dx2, dy2)

            width = max(side1, side2)
            height = min(side1, side2)

            angle = math.degrees(math.atan2(dy1, dx1))

            # 🔹 normaliseren#if angle < 0:
            angle += 180

            # 🔹 user correctie (BELANGRIJK)
            north_offset = st.number_input(
                "Noord correctie (°)",
                value=0.0,
                step=1.0
            )

            angle_corr = angle + north_offset

            angle_raw = math.degrees(math.atan2(dy1, dx1))

            # normaliseren 0–360
            if angle_raw < 0:
                angle_raw += 360

            # 🔹 Zuid-referentie (BELANGRIJK)
            angle_south = angle_raw - 180

            # normaliseren naar -180 → +180
            if angle_south > 180:
                angle_south -= 360
            if angle_south < -180:
                angle_south += 360

            # 🔹 richting bepalen
            richting = hoek_naar_richting_zuid(angle_south)

            st.markdown('<div class="section-title-large">Geometrie analyse</div>',
                unsafe_allow_html=True,)

            st.write("")  # spacing

            st.caption("Oriëntatie t.o.v. het zuiden (Zuid = 0°, West = positief, Oost = negatief)")

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric("Lengte", f"{width:.2f}")

            with c2:
                st.metric("Breedte", f"{height:.2f}")

            with c3:
                st.metric("Oriëntatiehoek", f"{angle_south:.2f}°")

            with c4:
                st.metric("Oriëntatie (Z=0°)", richting)



            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)

            fig.add_trace(
                go.Scatter(
                    x=[cx],
                    y=[cy],
                    mode="markers",
                    marker=dict(color="white", size=6),
                    name="Centroid"
                )
            )

            # 🔹 pijl lengte (afhankelijk van schaal)
            arrow_length = max(width, height) * 0.6

            # 🔹 hoek in radialen (BELANGRIJK: omzetten!)
            angle_rad = math.radians(angle_raw)

            # 🔹 eindpunt pijl
            x_arrow = cx + arrow_length * math.cos(angle_rad)
            y_arrow = cy + arrow_length * math.sin(angle_rad)

            # 🔹 pijl tekenen
            fig.add_trace(
                go.Scatter(
                    x=[cx, x_arrow],
                    y=[cy, y_arrow],
                    mode="lines+markers",
                    marker=dict(size=6, color="yellow"),
                    line=dict(color="yellow", width=3),
                    name="Oriëntatie"
                )
            )

            fig.add_annotation(
                x=x_arrow,
                y=y_arrow,
                text=f"{angle_south:.1f}°",
                showarrow=False,
                font=dict(color="yellow", size=12)
            )

            fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=ys,
                    fill="toself",
                    opacity=0.1,
                    line=dict(color="blue"),
                    name="Shape"
                )
            )

        # 🔹 layout
        fig.update_layout(
            height=600,
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font=dict(color="white"),
        )

        # 🔹 correcte schaal (ZEER BELANGRIJK)
        fig.update_yaxes(scaleanchor="x", scaleratio=1)

        st.plotly_chart(fig, use_container_width=True)

        st.divider()

    if lines:
        st.write(f"Aantal lijnen: {len(lines)}")

    if circles:
        st.write(f"Aantal cirkels: {len(circles)}")


# ✅ wrapper
def show():
    render_dxf_viewer_page()