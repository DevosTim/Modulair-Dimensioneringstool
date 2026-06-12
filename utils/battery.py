import numpy as np
import pandas as pd


# ✅ batterij simulatie
def simulate_battery(
    profile: pd.DataFrame,
    capacity_kwh: float,
    power_kw: float,
    efficiency: float = 0.95,
):

    df = profile.copy()

    load = df["Afname"].fillna(0).values
    pv = df["Productie"].fillna(0).values

    n = len(df)

    soc = 0.0  # state of charge
    soc_series = []

    grid_import = []
    grid_export = []

    for i in range(n):

        l = load[i]
        p = pv[i]

        # 🔹 overschot PV → laden
        if p > l:
            surplus = p - l

            charge = min(surplus, power_kw)
            charge *= efficiency

            space_left = capacity_kwh - soc
            charge = min(charge, space_left)

            soc += charge

            grid_export.append(surplus - charge)
            grid_import.append(0)

        # 🔹 tekort → ontladen
        else:
            deficit = l - p

            discharge = min(deficit, power_kw)
            discharge /= efficiency

            discharge = min(discharge, soc)

            soc -= discharge

            grid_import.append(deficit - discharge)
            grid_export.append(0)

        soc_series.append(soc)

    df_out = df.copy()

    df_out["SOC"] = soc_series
    df_out["Grid_Import"] = grid_import
    df_out["Grid_Export"] = grid_export

    # 🔹 KPI’s
    total_load = load.sum()
    total_pv = pv.sum()

    self_use = total_pv - np.sum(grid_export)

    sc = self_use / total_pv if total_pv > 0 else 0
    ss = (total_load - np.sum(grid_import)) / total_load if total_load > 0 else 0

    return {
        "df": df_out,
        "SC": sc,
        "SS": ss,
        "grid_import": np.sum(grid_import),
        "grid_export": np.sum(grid_export),
    }


# ✅ economische analyse
def battery_economics(
    battery_result: dict,
    prices: pd.DataFrame,
):

    df = battery_result["df"].copy()

    if prices is None:
        return None

    merged = df.merge(prices, on="Datetime", how="inner")

    if merged.empty:
        return None

    # 🔹 kosten zonder batterij (ruw)
    merged["kost_zonder"] = merged["Afname"] * merged["klantprijs_kwh"]

    # 🔹 kosten met batterij
    merged["kost_met"] = merged["Grid_Import"] * merged["klantprijs_kwh"]

    savings = merged["kost_zonder"].sum() - merged["kost_met"].sum()

    return {
        "savings": savings,
        "df": merged
    }


# ✅ nearest batterij (optioneel)
def find_nearest_battery(target_capacity, options):

    best = None
    best_diff = float("inf")

    for opt in options:
        diff = abs(opt - target_capacity)

        if diff < best_diff:
            best = opt
            best_diff = diff

    return best