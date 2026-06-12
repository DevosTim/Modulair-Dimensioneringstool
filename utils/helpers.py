import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import timedelta


# ✅ NUMERIC CLEANING
def safe_numeric_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    for col in out.columns:
        if pd.api.types.is_numeric_dtype(out[col]):
            continue

        raw = (
            out[col]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )

        converted = pd.to_numeric(raw, errors="coerce")

        if converted.notna().sum() >= max(3, int(len(out) * 0.5)):
            out[col] = converted

    return out


# ✅ COLUMN FINDER
def find_first_column(df: pd.DataFrame, candidates: list[str]):

    lowered = {str(col).lower(): col for col in df.columns}

    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]

    for candidate in candidates:
        needle = candidate.lower()
        for key, original in lowered.items():
            if needle in key:
                return original

    return None


# ✅ PROFILE STEP DETECTION
def infer_profile_step(profile: pd.DataFrame) -> timedelta:

    dt = pd.to_datetime(profile["Datetime"], errors="coerce") \
        .dropna().sort_values().drop_duplicates()

    if len(dt) < 2:
        return timedelta(minutes=15)

    diffs = dt.diff().dropna()
    positive_diffs = diffs[diffs > pd.Timedelta(0)]

    if positive_diffs.empty:
        return timedelta(minutes=15)

    return positive_diffs.min().to_pytimedelta()


# ✅ DATETIME DETECTION
def _find_profile_datetime(df: pd.DataFrame):

    datetime_col = find_first_column(df, [
        "Datetime", "DateTime", "Timestamp", "datumtijd"
    ])

    if datetime_col:
        return pd.to_datetime(df[datetime_col], errors="coerce")

    date_col = find_first_column(df, ["Datum", "Date"])
    time_col = find_first_column(df, ["Tijd", "Time"])

    if date_col and time_col:
        return pd.to_datetime(
            df[date_col].astype(str) + " " + df[time_col].astype(str),
            errors="coerce",
            dayfirst=True,
        )

    return None


# ✅ COMBINE MULTIPLE COLUMNS
def _combine_numeric_columns(df, names):

    available = [col for col in names if col in df.columns]

    if not available:
        return None

    numeric = []

    for col in available:
        numeric.append(
            pd.to_numeric(
                df[col].astype(str).str.replace(",", ".", regex=False),
                errors="coerce"
            )
        )

    return pd.concat(numeric, axis=1).sum(axis=1, min_count=1)


# ✅ FILTER UI (BELANGRIJK)
def filter_timeseries_by_selector(df, key_prefix, title="Filter"):

    out = df.copy()

    out["Datetime"] = pd.to_datetime(out["Datetime"], errors="coerce")
    out = out.dropna(subset=["Datetime"]).sort_values("Datetime")

    if out.empty:
        return out

    mode = st.segmented_control(
        title,
        ["Alles", "Datum uitgebreid", "Maand", "Jaar"],
        default="Alles",
        key=f"{key_prefix}_mode",
    )

    if mode == "Alles":
        return out

    if mode == "Datum uitgebreid":
        dmin = out["Datetime"].min().date()
        dmax = out["Datetime"].max().date()

        start, end = st.date_input(
            "Selecteer data",
            (dmin, dmax),
            key=f"{key_prefix}_date"
        )

        mask = (
            (out["Datetime"].dt.date >= start) &
            (out["Datetime"].dt.date <= end)
        )

        return out[mask]

    if mode == "Maand":
        month = st.selectbox(
            "Maand",
            sorted(out["Datetime"].dt.to_period("M").unique()),
            key=f"{key_prefix}_month"
        )

        return out[out["Datetime"].dt.to_period("M") == month]

    if mode == "Jaar":
        year = st.selectbox(
            "Jaar",
            sorted(out["Datetime"].dt.year.unique()),
            key=f"{key_prefix}_year"
        )

        return out[out["Datetime"].dt.year == year]

    return out


# ✅ GEEN ZON FRAME
def make_framework_wo_zon(df: pd.DataFrame):

    out = df.copy()

    if "Injectie" not in out.columns:
        out["Injectie"] = 0.0

    if "Productie" not in out.columns:
        out["Productie"] = 0.0

    out["Afname"] = (
        out["Afname"].fillna(0).astype(float)
        + out["Injectie"].fillna(0).astype(float)
    )

    out["Injectie"] = 0.0
    out["Productie"] = 0.0
    out["Consumption"] = out["Afname"]

    return out