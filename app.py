
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from prophet import Prophet
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value
import requests

# Default battery constants
DEFAULT_CAPACITY = 10.0  # kWh
DEFAULT_P_MAX = 5.0      # kW max charge/discharge
DEFAULT_ETA = 0.9        # Efficiency
DEFAULT_INITIAL_SOC = 5.0
DEFAULT_MIN_SOC = 1.0    # Minimum SOC threshold

# Load data
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file, parse_dates=["datetime"])
    return df

# Forecasting
@st.cache_data
def forecast_prices(df):
    df_prophet = df.rename(columns={"datetime": "ds", "price": "y"})
    model = Prophet(daily_seasonality=True)
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    df_forecast = forecast[['ds', 'yhat']].rename(columns={'ds': 'datetime', 'yhat': 'forecast_price'})
    return df_forecast

# Optimization
def optimize(df, CAPACITY, P_MAX, ETA, INITIAL_SOC, MIN_SOC):
    df = df.copy()
    df['hour'] = range(len(df))

    model = LpProblem("Battery_Optimizer", LpMinimize)

    charge = LpVariable.dicts("charge", df['hour'], lowBound=0, upBound=P_MAX)
    discharge = LpVariable.dicts("discharge", df['hour'], lowBound=0, upBound=P_MAX)
    soc = LpVariable.dicts("soc", df['hour'], lowBound=MIN_SOC, upBound=CAPACITY)

    model += lpSum([(df.price[t] * (df.load[t] - discharge[t] + charge[t])) for t in df['hour']])

    for t in df['hour']:
        if t == 0:
            model += soc[t] == INITIAL_SOC + ETA * charge[t] - discharge[t] * (1 / ETA)
        else:
            model += soc[t] == soc[t-1] + ETA * charge[t] - discharge[t] * (1 / ETA)

    model.solve()

    df['charge_power'] = [value(charge[t]) for t in df['hour']]
    df['discharge_power'] = [value(discharge[t]) for t in df['hour']]
    df['SOC'] = [value(soc[t]) for t in df['hour']]
    df['net_load'] = df['load'] - df['discharge_power'] + df['charge_power']

    df['action'] = ['charge' if c > 0 else 'discharge' if d > 0 else 'idle'
                    for c, d in zip(df['charge_power'], df['discharge_power'])]

    return df

# Main UI
st.set_page_config(layout="wide")
st.title("🔋 Battery Storage Optimization Dashboard")

with st.sidebar:
    st.header("Controls")
    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
    if uploaded_file is None:
        st.warning("Please upload a CSV file.")
        st.stop()

    df_raw = load_data(uploaded_file)

    selected_region = st.selectbox("Select Region", df_raw['region'].unique())
    df_region = df_raw[df_raw['region'] == selected_region].copy()

    min_date = df_region['datetime'].min().date()
    max_date = df_region['datetime'].max().date()

    start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

    # Additional battery control parameters
    st.subheader("Battery Parameters")
    CAPACITY = st.number_input("Battery Capacity (kWh)", min_value=1.0, value=DEFAULT_CAPACITY)
    P_MAX = st.number_input("Max Charge/Discharge Power (kW)", min_value=0.1, value=DEFAULT_P_MAX)
    ETA = st.number_input("Efficiency (0-1)", min_value=0.1, max_value=1.0, value=DEFAULT_ETA)
    INITIAL_SOC = st.number_input("Initial State of Charge (kWh)", min_value=0.0, max_value=CAPACITY, value=DEFAULT_INITIAL_SOC)
    MIN_SOC = st.number_input("Minimum State of Charge (kWh)", min_value=0.0, max_value=CAPACITY, value=DEFAULT_MIN_SOC)

# Filter data by date range
mask = (df_region['datetime'].dt.date >= start_date) & (df_region['datetime'].dt.date <= end_date)
df_filtered = df_region.loc[mask].copy()

if df_filtered.empty:
    st.warning("No data available in this time range.")
    st.stop()

# Forecast
with st.spinner("Forecasting prices using Prophet..."):
    forecast_df = forecast_prices(df_filtered)
    df_merged = pd.merge(df_filtered, forecast_df, on='datetime', how='left')

# Optimize
with st.spinner("Optimizing battery schedule..."):
    df_result = optimize(df_merged, CAPACITY, P_MAX, ETA, INITIAL_SOC, MIN_SOC)

# Graphs
st.subheader(f"📊 Results for Region: {selected_region}")

col1, col2 = st.columns(2)

with col1:
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_result['datetime'], y=df_result['price'], name='Actual Price'))
    fig1.add_trace(go.Scatter(x=df_result['datetime'], y=df_result['forecast_price'], name='Forecast Price'))
    fig1.update_layout(title="Price and Forecast", xaxis_title="Time", yaxis_title="$/kWh")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_result['datetime'], y=df_result['SOC'], name='SOC'))
    fig2.update_layout(title="State of Charge", xaxis_title="Time", yaxis_title="kWh")
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    action_map = {'charge': 1, 'idle': 0, 'discharge': -1}
    fig3 = go.Figure(go.Bar(
        x=df_result['datetime'],
        y=df_result['action'].map(action_map),
        name='Action'))
    fig3.update_layout(title="Battery Action (1=Charge, -1=Discharge)",
                       yaxis=dict(tickvals=[-1, 0, 1], ticktext=['Discharge', 'Idle', 'Charge']))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    df_result['date'] = df_result['datetime'].dt.date
    daily_summary = df_result.groupby(['date', 'action']).size().unstack(fill_value=0)
    daily_summary = daily_summary.reindex(columns=['charge', 'idle', 'discharge'], fill_value=0)
    fig4 = go.Figure()
    for act in ['charge', 'idle', 'discharge']:
        fig4.add_trace(go.Bar(
            x=daily_summary.index,
            y=100 * daily_summary[act] / 24,
            name=f"{act.capitalize()} %"))
    fig4.update_layout(barmode='stack', title='Daily Action Summary (Percentage of 24 hours)')
    st.plotly_chart(fig4, use_container_width=True)

# Download
st.download_button("📥 Download Results CSV", df_result.to_csv(index=False), file_name="battery_results.csv")
