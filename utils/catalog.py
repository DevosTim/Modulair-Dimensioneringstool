import pandas as pd
from pathlib import Path
import os

def load_panel_catalog():
    base_path = os.getcwd()
    file_path = os.path.join(base_path, "Sparki_Zonnepanelen.xlsx")

    return pd.read_excel(file_path, header=1)


def load_inverter_catalog():
    base_path = os.getcwd()
    file_path = os.path.join(base_path, "Sparki_Omvormers.xlsx")

    return pd.read_excel(file_path, header=1)