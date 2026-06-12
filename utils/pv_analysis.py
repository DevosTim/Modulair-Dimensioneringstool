import numpy as np
import pandas as pd


# ✅ hoofd PV analyse functie
def build_pv_analysis(profile: pd.DataFrame, specific_yield: float, inverter_ratio: float):

    df = profile.copy()

    # 🔹 basis arrays
    load = df["Afname"].fillna(0).values
    production_base = df["Productie"].fillna(0).values

    total_load = load.sum()

    # 🔹 indien geen productie aanwezig → normaal profiel maken
    if production_base.sum() <= 0:
        # simpele genormaliseerde productiecurve op basis van load
        production_base = load / (load.max() + 1e-9)

    # 🔹 PU range
    pu_range = np.linspace(0.05, 2.5, 120)

    sc_list = []
    ss_list = []
    pv_energy_list = []
    self_use_list = []

    # 🔹 simulatie over alle groottes
    for pu in pu_range:

        # PV schaal
        pv = production_base * pu * specific_yield / 1000.0

        pv_total = pv.sum()

        if pv_total <= 0:
            sc_list.append(0)
            ss_list.append(0)
            pv_energy_list.append(0)
            self_use_list.append(0)
            continue

        # 🔹 eigenverbruik per tijdstap
        self_use = np.minimum(pv, load)

        self_use_total = self_use.sum()

        sc = self_use_total / pv_total
        ss = self_use_total / total_load if total_load > 0 else 0

        sc_list.append(sc)
        ss_list.append(ss)
        pv_energy_list.append(pv_total)
        self_use_list.append(self_use_total)

    sc_array = np.array(sc_list)
    ss_array = np.array(ss_list)

    # 🔹 optimale index
    combined = sc_array + ss_array
    idx_opt = np.argmax(combined)

    # 🔹 knikpunt (heuristiek)
    gradient = np.gradient(combined)
    idx_knee = np.argmax(gradient < gradient.mean() * 0.5)

    # 🔹 resultaten
    pu_opt = pu_range[idx_opt]
    pu_knee = pu_range[idx_knee]

    capacity_opt_kwp = pu_opt
    inverter_power_kw = capacity_opt_kwp * inverter_ratio

    return {
        "pu_range": pu_range,

        "sc": sc_array,
        "ss": ss_array,

        "pv_energy": np.array(pv_energy_list),
        "self_use": np.array(self_use_list),

        "pu_opt": pu_opt,
        "pu_knee": pu_knee,

        "capacity_opt_kwp": capacity_opt_kwp,
        "power_opt_kw": inverter_power_kw,

        "idx_opt": idx_opt,
        "idx_knee": idx_knee,
    }