import streamlit as st

# utils
from utils.data_loader import (
    build_profile_from_excel,
    get_profile_key,
)


# 🔹 helper uit jouw originele code
def _sanitize_profile_filename(name: str) -> str:
    import re
    safe_name = re.sub(r'[<>:"/\\|?*]+', "_", name).strip().strip(".")
    return safe_name or "Verbruiksprofiel"


# 🔹 VOLLEDIGE PAGE LOGICA
def profile_import_page():

    st.markdown(
        '<div class="section-title">Verbruiksprofiel</div>',
        unsafe_allow_html=True
    )

    profile = st.session_state.get("profile_df")

    # ✅ init
    if "last_uploaded_file" not in st.session_state:
        st.session_state["last_uploaded_file"] = None

    uploaded_profile = st.file_uploader(
        "Upload excel voor verbruiksprofiel",
        type=["xlsx", "csv"],
        key="profile_import_uploader",
    )

    # ✅ ENKEL VERWERKEN ALS HET NIEUW BESTAND IS
    if uploaded_profile is not None:

        if uploaded_profile.name != st.session_state["last_uploaded_file"]:

            try:
                profile_new, export_bytes, rebuilt, sheet_name = build_profile_from_excel(
                    uploaded_profile.getvalue()
                )
            except Exception as exc:
                st.error(f"Fout bij inladen: {exc}")
                return

            st.session_state["profile_df"] = profile_new
            st.session_state["profile_key"] = get_profile_key(profile_new)
            st.session_state["profile_export_bytes"] = export_bytes

            # ✅ markeer als verwerkt
            st.session_state["last_uploaded_file"] = uploaded_profile.name

            st.success("Nieuw profiel geladen ✅")

            st.rerun()

    # ✅ BESTAAND PROFIEL TONEN
    if profile is not None:

        st.success("Verbruiksprofiel geladen ✅")

        # ✅ statistieken berekenen
        records = len(profile)

        periode_start = profile["Datetime"].min()
        periode_einde = profile["Datetime"].max()

        # ✅ Kleine spacing
        st.markdown("<br>", unsafe_allow_html=True)

        st.caption("Werkblad gebruikt: Sheet1")
        
        st.markdown("<br>", unsafe_allow_html=True)


        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">RECORDS</div>
                <div class="metric-value">{records:,}</div>
                <div class="metric-subtext">Kwartierregels in het profiel</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">PERIODE START</div>
                <div class="metric-value">{periode_start}</div>
                <div class="metric-subtext">Eerste geldige kwartier</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">PERIODE EINDE</div>
                <div class="metric-value">{periode_einde}</div>
                <div class="metric-subtext">Laatste geldige kwartier</div>
            </div>
            """, unsafe_allow_html=True)

        # ✅ Kleine spacing
        st.markdown("<br>", unsafe_allow_html=True)


        st.dataframe(profile.head(20), use_container_width=True)

        # ✅ DOWNLOAD BLOK
        st.markdown('<div class="section-title">Download verwerkt profiel</div>', unsafe_allow_html=True)

        
        # 🔹 BONUS tekst
        st.caption("Download het automatisch verwerkte kwartierprofiel.")


        # 🔹 standaard naam
        default_name = st.session_state.get("download_name", "Verbruiksprofiel")

        file_name = st.text_input(
            "Bestandsnaam",
            value=default_name,
            key="download_name_input"
        )

        # 🔹 opslaan in state
        st.session_state["download_name"] = file_name

        # 🔹 haal export bytes
        export_bytes = st.session_state.get("profile_export_bytes")

        if export_bytes is not None:

            st.download_button(
                label="Download Excel",
                data=export_bytes,
                file_name=f"{file_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Verwijder profiel"):
                st.session_state.pop("profile_df", None)
                st.session_state.pop("profile_key", None)
                st.session_state.pop("profile_export_bytes", None)
                st.session_state["last_uploaded_file"] = None
                st.rerun()

        with col2:
            st.info("Upload nieuw bestand om te vervangen")

    else:
        st.info("Upload een Excelbestand om te starten.")



# 🔹 wrapper
def show():
    profile_import_page()