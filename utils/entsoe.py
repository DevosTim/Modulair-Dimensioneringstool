import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo
import streamlit as st



# ✅ jouw API key hier
ENTSOE_API_KEY = st.secrets["ENTSOE_API_KEY"]


# ✅ hoofd functie (gebruikt in prijzen.py)
def fetch_entsoe_prices_for_profile(profile: pd.DataFrame) -> pd.DataFrame:

    start = profile["Datetime"].min()
    end = profile["Datetime"].max()

    return fetch_entsoe_prices_for_range(start, end)


# ✅ fetch voor specifieke range
def fetch_entsoe_prices_for_range(start, end):

    url = "https://web-api.tp.entsoe.eu/api"

    periods = iter_entsoe_periods_between(start, end)

    all_chunks = []

    for period_start, period_end in periods:

        params = {
            "securityToken": ENTSOE_API_KEY,
            "documentType": "A44",
            "in_Domain": "10YBE----------2",
            "out_Domain": "10YBE----------2",
            "periodStart": period_start,
            "periodEnd": period_end,
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(f"ENTSO-E fout: {response.status_code}")

        chunk = _parse_entsoe_xml(response.content)

        if not chunk.empty:
            all_chunks.append(chunk)

    if not all_chunks:
        raise Exception("Geen data ontvangen van ENTSO-E")

    df = pd.concat(all_chunks)

    df = df.drop_duplicates(subset=["Datetime"])
    df = df.sort_values("Datetime").reset_index(drop=True)

    return df


def iter_entsoe_periods_between(start_local, end_local):

    tz = ZoneInfo("Europe/Brussels")

    start_local = pd.to_datetime(start_local).to_pydatetime().replace(tzinfo=tz)
    end_local = pd.to_datetime(end_local).to_pydatetime().replace(tzinfo=tz)

    periods = []

    chunk_start = start_local

    while chunk_start < end_local:

        # volgende maand
        if chunk_start.month == 12:
            next_month_start = datetime(chunk_start.year + 1, 1, 1, tzinfo=tz)
        else:
            next_month_start = datetime(chunk_start.year, chunk_start.month + 1, 1, tzinfo=tz)

        chunk_end = min(next_month_start, end_local)

        start_utc = chunk_start.astimezone(ZoneInfo("UTC"))
        end_utc = chunk_end.astimezone(ZoneInfo("UTC"))

        periods.append((
            start_utc.strftime("%Y%m%d%H%M"),
            end_utc.strftime("%Y%m%d%H%M")
        ))

        chunk_start = chunk_end

    return periods


# ✅ XML parsing (BELANGRIJK)
def _parse_entsoe_xml(xml_content: bytes) -> pd.DataFrame:

    root = ET.fromstring(xml_content)

    ns = {"ns": "urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3"}

    times = []
    prices = []

    for timeseries in root.findall(".//ns:TimeSeries", ns):

        for period in timeseries.findall(".//ns:Period", ns):

            start = period.find("ns:timeInterval/ns:start", ns).text
            resolution = period.find("ns:resolution", ns).text

            start_dt = pd.to_datetime(start)

            for point in period.findall(".//ns:Point", ns):

                position = int(point.find("ns:position", ns).text)
                price = float(
                    point.find("ns:price.amount", ns).text
                )

                if resolution == "PT60M":
                    time = start_dt + timedelta(hours=position - 1)
                else:
                    time = start_dt + timedelta(minutes=15 * (position - 1))

                times.append(time)
                prices.append(price)

    df = pd.DataFrame({
        "Datetime": times,
        "price_kwh": prices,
    })

    # ✅ timezone verwijderen (ZEER BELANGRIJK)
    df["Datetime"] = pd.to_datetime(df["Datetime"], utc=True).dt.tz_localize(None)

    # 🔹 €/MWh → €/kWh
    df["price_kwh"] = df["price_kwh"] / 1000.0

    df = df.sort_values("Datetime").reset_index(drop=True)

    # ✅ kwartier interpolatie indien nodig
    diffs = df["Datetime"].diff().dropna()

    if len(diffs) > 0 and diffs.min() >= pd.Timedelta(hours=1):
        df = df.set_index("Datetime").resample("15min").interpolate()
        df = df.reset_index()

    return df

import streamlit as st

def render_entsoe_price_fetcher(profile, profile_key, prefix="home"):

    st.markdown("### ENTSO‑E prijzen ophalen")

    if st.button("Haal prijzen op", key=f"{prefix}_btn"):
        try:
            prices = fetch_entsoe_prices_for_profile(profile)
            st.session_state["prices_df"] = prices
            st.success("Prijsdata opgehaald")
        except Exception as e:
            st.error(f"Fout: {e}")