"""
ARKHEION-X: Quant Engine v3.0 - Intelligence Command Center

This Streamlit application serves as an interactive dashboard to view, filter,
and analyze on-chain and off-chain alpha signals logged by ARKHEION-X agents.
"""
import streamlit as st
import pandas as pd
import sqlite3
import json
import plotly.express as px
from datetime import datetime, timedelta

# --- Configuration ---
DB_FILE = "arkheionx.db"

# --- Page Configuration ---
st.set_page_config(
    page_title="ARKHEION-X // Intel Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading and Processing ---
@st.cache_data(ttl=30)  # Refresh data cache every 30 seconds
def load_and_process_data():
    """Loads data from the SQLite DB, parses JSON metadata, and returns a DataFrame."""
    try:
        # Use a read-only connection to prevent database locking issues
        conn = sqlite3.connect(f"file:{DB_FILE}?mode=ro", uri=True)
        query = "SELECT timestamp, source, signal_type, metadata, confidence_level FROM alpha_signals ORDER BY timestamp DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()

        # If metadata is a JSON string, expand it into columns
        if not df.empty and isinstance(df['metadata'].iloc[0], str):
            try:
                meta_df = pd.json_normalize(df['metadata'].apply(json.loads))
                df = pd.concat([df.drop('metadata', axis=1), meta_df], axis=1)
            except json.JSONDecodeError:
                st.warning("Could not parse all metadata JSON strings.")
        
        # Convert timestamp to datetime objects for proper filtering
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception:
        return pd.DataFrame()

# --- Styling Functions ---
def style_dataframe(df):
    """Applies conditional formatting to the DataFrame for better visual cues."""
    def highlight_confidence(row):
        level = row['confidence_level']
        if level == 'CRITICAL':
            return ['background-color: #5a1e1e'] * len(row) # Dark Red
        elif level == 'HIGH':
            return ['background-color: #5a4d1e'] * len(row) # Dark Yellow
        return [''] * len(row)

    # Abbreviate long strings for cleaner display
    for col in ['from', 'to', 'tx_hash', 'commit_sha', 'commit_url']:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(lambda x: x[:6] + '...' + x[-4:] if len(x) > 10 else x)

    return df.style.apply(highlight_confidence, axis=1)

# --- Main Application ---
st.title("ARKHEION-X: Intelligence Command Center")
df_raw = load_and_process_data()

# --- Sidebar Filters ---
st.sidebar.title("Filter Controls")
if not df_raw.empty:
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(df_raw['timestamp'].min().date(), df_raw['timestamp'].max().date()),
        min_value=df_raw['timestamp'].min().date(),
        max_value=df_raw['timestamp'].max().date()
    )
    
    # Convert date_range to datetime for filtering
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1]) + timedelta(days=1) # Include the end day

    df_filtered = df_raw[(df_raw['timestamp'] >= start_date) & (df_raw['timestamp'] <= end_date)]

    signal_types = df_filtered['signal_type'].unique()
    selected_types = st.sidebar.multiselect("Signal Type", signal_types, default=signal_types)

    confidence_levels = df_filtered['confidence_level'].unique()
    selected_confidence = st.sidebar.multiselect("Confidence Level", confidence_levels, default=confidence_levels)

    if 'token' in df_filtered.columns:
        tokens = df_filtered['token'].dropna().unique()
        selected_tokens = st.sidebar.multiselect("Token", tokens, default=tokens)
        df_filtered = df_filtered[
            df_filtered['signal_type'].isin(selected_types) &
            df_filtered['confidence_level'].isin(selected_confidence) &
            df_filtered['token'].isin(selected_tokens)
        ]
    else:
        df_filtered = df_filtered[
            df_filtered['signal_type'].isin(selected_types) &
            df_filtered['confidence_level'].isin(selected_confidence)
        ]
else:
    df_filtered = df_raw

# --- Dashboard Display ---
if df_filtered.empty:
    st.warning("No signals match your criteria or the database is empty.")
else:
    # --- Latest Critical Signal Ticker ---
    st.markdown("### Latest Critical Intel")
    latest_critical = df_filtered[df_filtered['confidence_level'] == 'CRITICAL'].iloc[0:1]
    if not latest_critical.empty:
        signal = latest_critical.iloc[0]
        st.warning(
            f"**{signal['signal_type']}**: {signal.get('amount', 'N/A')} {signal.get('token', 'N/A')} "
            f"to wallet `{signal.get('to', 'N/A')}` (Tx Count: {signal.get('receiver_tx_count', 'N/A')}) at {signal['timestamp']}",
            icon="🚨"
        )
    else:
        st.info("No critical signals in the selected range.")

    # --- Key Metrics ---
    st.markdown("### High-Level Overview")
    total_signals = len(df_filtered)
    critical_signals = len(df_filtered[df_filtered['confidence_level'] == 'CRITICAL'])
    fresh_wallets = len(df_filtered[df_filtered['signal_type'] == 'Fresh Wallet Accumulation'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Signals Displayed", total_signals)
    col2.metric("Critical 'Smart Money' Alerts", critical_signals)
    col3.metric("Fresh Wallets Detected", fresh_wallets)

    # --- Visualizations ---
    st.markdown("### Data Visualization")
    col1_chart, col2_chart = st.columns(2)
    with col1_chart:
        st.subheader("Signal Confidence Breakdown")
        confidence_counts = df_filtered['confidence_level'].value_counts()
        fig_pie = px.pie(confidence_counts, values=confidence_counts.values, names=confidence_counts.index, hole=.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2_chart:
        if 'token' in df_filtered.columns:
            st.subheader("Signal Activity by Token")
            token_counts = df_filtered['token'].value_counts()
            fig_bar = px.bar(token_counts, x=token_counts.index, y=token_counts.values, labels={'x':'Token', 'y':'Signal Count'})
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- Data Table ---
    st.markdown("### Full Signal Log (Filtered)")
    st.dataframe(style_dataframe(df_filtered), use_container_width=True)