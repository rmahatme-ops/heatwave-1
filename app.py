from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Heatwave Watch", page_icon="🌡️", layout="wide")
DATA_FILE = Path(__file__).parent / "heatwave_data.csv"

st.title("🌡️ Heatwave Watch")
st.caption("Climate Intelligence for Heatwave Monitoring and Early Warning")

@st.cache_data
def load_data(file_bytes=None):
    if file_bytes is None:
        data = pd.read_csv(DATA_FILE)
    else:
        data = pd.read_csv(file_bytes)

    # Match the uploaded dataset's original column names to the app's standard names.
    data = data.rename(columns={
        "Date": "date",
        "Temp Max": "tmax",
        "Temp Min": "tmin",
    })

    required = {"region", "date", "lat", "lon", "tmax"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(sorted(missing))
            + ". Required columns are region, Date/date, lat, lon, and Temp Max/tmax."
        )

    # The supplied dataset uses dates such as 01-01-1951 (day-month-year).
    data["date"] = pd.to_datetime(data["date"], dayfirst=True, errors="coerce")
    for col in ("tmax", "lat", "lon"):
        data[col] = pd.to_numeric(data[col], errors="coerce")
    if "tmin" in data.columns:
        data["tmin"] = pd.to_numeric(data["tmin"], errors="coerce")
    if "Rain" in data.columns:
        data["Rain"] = pd.to_numeric(data["Rain"], errors="coerce")

    data["region"] = data["region"].astype("string").str.strip()
    data = data.dropna(subset=["region", "date", "lat", "lon", "tmax"])
    data = data[data["region"] != ""]
    return data.sort_values("date")

try:
    df = load_data()
except FileNotFoundError:
    st.error("heatwave_data.csv was not found. Keep it in the same folder as app.py.")
    st.stop()
except (ValueError, pd.errors.ParserError) as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

if df.empty:
    st.error("No valid observations were found in the dataset.")
    st.stop()

with st.sidebar:
    st.header("Search observations")
    uploaded_file = st.file_uploader(
        "Upload another CSV (optional)",
        type=["csv"],
        help="Use columns region, Date, lat, lon, and Temp Max, or their lowercase equivalents.",
    )

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
    except (ValueError, pd.errors.ParserError) as exc:
        st.sidebar.error(f"Could not load uploaded CSV: {exc}")
        st.stop()
    if df.empty:
        st.warning("The uploaded CSV contains no valid observations.")
        st.stop()

regions = sorted(df["region"].dropna().unique().tolist())
with st.sidebar:
    region = st.selectbox("Select region", regions)
    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    start = st.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
    end = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)
    threshold = st.slider("Hot-day threshold (°C)", 30.0, 50.0, 40.0, 0.5)

if start > end:
    st.error("Start date must be on or before the end date.")
    st.stop()

result = df[
    (df["region"] == region)
    & (df["date"].dt.date >= start)
    & (df["date"].dt.date <= end)
].copy()

if result.empty:
    st.warning("No observations found for this region and date range. Try another selection.")
    st.stop()

a, b, c, d = st.columns(4)
a.metric("Records", f"{len(result):,}")
b.metric("Average Tmax", f"{result['tmax'].mean():.2f} °C")
c.metric("Highest Tmax", f"{result['tmax'].max():.2f} °C")
d.metric("Records above threshold", f"{int((result['tmax'] >= threshold).sum()):,}")

daily = result.groupby("date", as_index=False)["tmax"].mean()
fig = px.line(
    daily, x="date", y="tmax", markers=True,
    title=f"Temperature Trend: {region}",
    labels={"date": "Date", "tmax": "Average Tmax (°C)"},
)
fig.add_hline(y=threshold, line_dash="dash", annotation_text="Selected threshold")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    fig2 = px.histogram(
        result, x="tmax", nbins=25, title="Temperature Distribution",
        labels={"tmax": "Maximum temperature (°C)"},
    )
    st.plotly_chart(fig2, use_container_width=True)

with right:
    period = df[(df["date"].dt.date >= start) & (df["date"].dt.date <= end)]
    summary = period.groupby("region", as_index=False)["tmax"].mean().sort_values("tmax", ascending=False)
    fig3 = px.bar(
        summary, x="region", y="tmax", title="Average Maximum Temperature by Region",
        labels={"region": "Region", "tmax": "Average Tmax (°C)"},
    )
    st.plotly_chart(fig3, use_container_width=True)

if "tmin" in result.columns:
    st.subheader("Minimum Temperature Trend")
    daily_min = result.groupby("date", as_index=False)["tmin"].mean()
    fig4 = px.line(
        daily_min, x="date", y="tmin", markers=True,
        title=f"Daily Average Minimum Temperature: {region}",
        labels={"date": "Date", "tmin": "Average Tmin (°C)"},
    )
    st.plotly_chart(fig4, use_container_width=True)

st.subheader("Temperature Records")
st.dataframe(result, use_container_width=True, hide_index=True)
st.download_button(
    "Download filtered results as CSV",
    data=result.to_csv(index=False).encode("utf-8"),
    file_name="heatwave_results.csv",
    mime="text/csv",
)
