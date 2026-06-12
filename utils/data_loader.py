import pandas as pd
from io import BytesIO

import pandas as pd
import numpy as np
from io import BytesIO
from datetime import timedelta

from utils.helpers import (
    find_first_column,
    infer_profile_step,
)


# ✅ kolomnamen
PROFILE_EXPORT_COLUMNS = [
    "Datum",
    "Tijd",
    "Afname_1",
    "Afname_2",
    "Injectie",
    "Productie",
    "Eenheid",
]


# ✅ BASIS PROFIEL CLEANER
def _coerce_profile_frame(df: pd.DataFrame) -> pd.DataFrame:

    profile = df.copy()

    # eerste 7 kolommen gebruiken
    profile = profile.iloc[:, :7].copy()
    profile.columns = PROFILE_EXPORT_COLUMNS

    # numeric conversie
    for col in ["Afname_1", "Afname_2", "Injectie", "Productie"]:
        profile[col] = pd.to_numeric(
            profile[col].astype(str).str.replace(",", "."),
            errors="coerce"
        )

    # datetime
    profile["Datetime"] = pd.to_datetime(
        profile["Datum"].astype(str) + " " + profile["Tijd"].astype(str),
        dayfirst=True,
        errors="coerce"
    )

    # berekeningen
    profile["Afname"] = profile["Afname_1"] + profile["Afname_2"]
    profile["Consumption"] = profile["Afname"] - profile["Injectie"]

    profile = profile[
        ["Datetime", "Afname", "Injectie", "Productie", "Consumption"]
    ]

    profile = profile.dropna(subset=["Datetime"]).sort_values("Datetime")

    return profile.reset_index(drop=True)


# ✅ FLEXIBLE EXCEL → PROFIEL
def _frame_to_internal_profile(df: pd.DataFrame):

    # 🔹 standaard structuur
    if df.shape[1] >= 7:
        try:
            return _coerce_profile_frame(df), False
        except Exception:
            pass

    # 🔹 fallback (slimme detectie)
    datetime_series = None

    dt_col = find_first_column(df, ["Datetime", "DatumTijd", "Timestamp"])
    if dt_col:
        datetime_series = pd.to_datetime(df[dt_col], errors="coerce")
    else:
        date_col = find_first_column(df, ["Datum", "Date"])
        time_col = find_first_column(df, ["Tijd", "Time"])

        if date_col and time_col:
            datetime_series = pd.to_datetime(
                df[date_col].astype(str) + " " + df[time_col].astype(str),
                errors="coerce",
                dayfirst=True,
            )

    if datetime_series is None:
        return None

    # 🔹 afname zoeken
    afname_col = find_first_column(df, ["Afname", "Verbruik", "Consumption"])
    if afname_col is None:
        return None

    afname = pd.to_numeric(df[afname_col], errors="coerce")

    productie_col = find_first_column(df, ["Productie", "PV"])
    injectie_col = find_first_column(df, ["Injectie", "Export"])

    productie = (
        pd.to_numeric(df[productie_col], errors="coerce")
        if productie_col else 0
    )

    injectie = (
        pd.to_numeric(df[injectie_col], errors="coerce")
        if injectie_col else 0
    )

    frame = pd.DataFrame({
        "Datetime": datetime_series,
        "Afname": afname,
        "Productie": productie,
        "Injectie": injectie,
    }).dropna(subset=["Datetime"])

    frame["Consumption"] = frame["Afname"] - frame["Injectie"]

    # 🔹 resample naar kwartier indien nodig
    step = infer_profile_step(frame)

    if step != timedelta(minutes=15):
        frame = frame.set_index("Datetime").resample("15min").sum()
        frame = frame.reset_index()

    return frame, True


# ✅ EXPORT NA EXCEL
def _profile_to_workbook_bytes(profile: pd.DataFrame) -> bytes:

    export_df = pd.DataFrame({
        "Datum": profile["Datetime"].dt.strftime("%d/%m/%Y"),
        "Tijd": profile["Datetime"].dt.strftime("%H:%M"),
        "Afname_1": profile["Afname"],
        "Afname_2": 0,
        "Injectie": profile["Injectie"],
        "Productie": profile["Productie"],
        "Eenheid": "kWh",
    })

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False)

    return output.getvalue()


# ✅ HOOFDFUNCTIE (BELANGRIJK)
def build_profile_from_excel(uploaded_excel: bytes):

    sheets = pd.read_excel(
        BytesIO(uploaded_excel),
        sheet_name=None,
        engine="openpyxl"
    )

    for sheet_name, df in sheets.items():

        try:
            result = _frame_to_internal_profile(df)
        except Exception:
            result = None

        if result is None:
            continue

        profile, rebuilt = result

        export_bytes = _profile_to_workbook_bytes(profile)

        return profile, export_bytes, rebuilt, sheet_name

    raise ValueError("Geen geldig profiel gevonden in Excel.")


# ✅ PROFIEL KEY (BELANGRIJK VOOR STATE)
def get_profile_key(profile: pd.DataFrame):

    dt = profile["Datetime"].dropna().sort_values()

    if dt.empty:
        return ("", "", 0)

    return (
        str(dt.iloc[0]),
        str(dt.iloc[-1]),
        int(len(dt)),
    )