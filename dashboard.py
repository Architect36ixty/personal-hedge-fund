import streamlit as st
import pandas as pd
import plotly.express as px
from agents.common.db import get_supabase_client

st.set_page_config(page_title="Hedge Fund Dashboard", layout="wide")

def load_data(table, limit=100, order_col="created_at"):
    supabase = get_supabase_client()
    try:
        if order_col:
            response = supabase.table(table).select("*").order(order_col, desc=True).limit(limit).execute()
        else:
            response = supabase.table(table).select("*").limit(limit).execute()
        return pd.DataFrame(response.data)
    except supabase.exceptions.APIError as e:
        st.error(f"Error loading {table}: {e}")
        return pd.DataFrame()

st.title("🤖 Personal Hedge Fund: Evaluation Internal")

# Sidebar
st.sidebar.header("Agent Status")
st.sidebar.success("Agents are Active (GitHub Actions)")
if st.sidebar.button("Refresh Data"):
    st.rerun()

# Tabs
tab1, tab2, tab3 = st.tabs(["Overview", "The Coach (Brain)", "Market Data"])

with tab1:
    st.header("Portfolio Overview")
    
    # Metrics
    # Fetch latest Portfolio Ledger
    ledger_df = load_data("portfolio_ledger", limit=100, order_col="last_updated")
    
    col1, col2, col3 = st.columns(3)
    
    total_val = 0
    cash = 0
    if not ledger_df.empty:
        # Sum up current_value of everything
        # Note: In our simple schema, we might have multiple rows. Ideally we group by asset_type.
        # But 'portfolio_ledger' rows are unique by id.
        total_val = ledger_df['current_value'].sum()
        cash_row = ledger_df[ledger_df['asset_type'] == 'CASH']
        if not cash_row.empty:
            cash = cash_row.iloc[0]['current_value']
            
    col1.metric("Total Portfolio Value", f"${total_val:,.2f}")
    col2.metric("Cash Balance", f"${cash:,.2f}")
    
    # Recent Signals
    st.subheader("Recent Agent Signals")
    signals_df = load_data("signals", limit=20, order_col="generated_at")
    if not signals_df.empty:
        st.dataframe(signals_df[['generated_at', 'symbol', 'signal_type', 'confidence', 'agent_id']])
    else:
        st.info("No recent signals.")

with tab2:
    st.header("The Coach: Self-Improvement Loop")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🧠 Active Configuration")
        st.caption("Parameters currently used by agents")
        config_df = load_data("system_config", limit=50, order_col="updated_at")
        if not config_df.empty:
            st.dataframe(config_df)
        else:
            st.info("No configuration found.")
            
    with col_b:
        st.subheader("📝 Coach Decisions (Logs)")
        st.caption("How the system has tuned itself recently")
        logs_df = load_data("system_logs", limit=20, order_col="created_at")
        if not logs_df.empty:
            st.dataframe(logs_df[['created_at', 'event_type', 'details']])
        else:
            st.info("No Coach logs yet. (Runs weekly)")

with tab3:
    st.header("Market Data & Correlations")
    
    # Crypto Data
    st.subheader("Crypto Price vs Weather Sentiment")
    crypto_df = load_data("market_data_crypto", limit=100, order_col="date")
    
    if not crypto_df.empty:
        # Create dual-axis chart?
        # Normalize for visualization or just show two lines
        
        # Sort by date asc for chart
        crypto_df = crypto_df.sort_values("date")
        
        fig = px.line(crypto_df, x="date", y=["close", "weather_score"], 
                      title="Bitcoin Price (ZAR) vs Weather Score (0-100)",
                      labels={"value": "Metrics", "variable": "Indicator"})
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No crypto market data yet.")
        
    # Trade Logs
    st.subheader("Trade Execution History")
    trades_df = load_data("trade_logs", limit=50, order_col="timestamp")
    if not trades_df.empty:
        st.dataframe(trades_df)
    else:
        st.info("No trades executed yet.")
