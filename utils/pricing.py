import pandas as pd
import numpy as np
from io import BytesIO


# ✅ PRIJZEN CSV INLADEN
def load_prices_15min(file_bytes: bytes) -> pd.DataFrame:

    df = pd.read_csv(BytesIO(file_bytes))

    # 🔹 datetime vinden
    datetime_col = None
    for col in df.columns:
        if "time" in col.lower() or "datum" in col.lower():
            datetime_col = col
            break

    if datetime_col is None:
        raise ValueError("Geen datum/tijd kolom gevonden in CSV")

    df["Datetime"] = pd.to_datetime(df[datetime_col], errors="coerce")

    # 🔹 prijskolom zoeken
    price_col = None
    for col in df.columns:
        if "price" in col.lower() or "prijs" in col.lower():
            price_col = col
            break

    if price_col is None:
        raise ValueError("Geen prijskolom gevonden in CSV")

    df["price_kwh"] = pd.to_numeric(
        df[price_col],
        errors="coerce"
    )

    # 🔹 sommige files zijn €/MWh → omzetten
    if df["price_kwh"].mean() > 10:
        df["price_kwh"] = df["price_kwh"] / 1000.0

    df = df[["Datetime", "price_kwh"]]
    df = df.dropna().sort_values("Datetime")

    return df.reset_index(drop=True)


# ✅ KLANTPRIJS BEREKENEN
def bereken_klantprijs_15min(
    prices: pd.DataFrame,
    factor: float,
    marge: float
) -> pd.DataFrame:

    df = prices.copy()

    # 🔹 basis prijsformule
    df["klantprijs_kwh"] = df["price_kwh"] * factor + marge

    # 🔹 negatieve prijzen beperken (optioneel)
    df["klantprijs_kwh"] = df["klantprijs_kwh"].clip(lower=0)

    return df