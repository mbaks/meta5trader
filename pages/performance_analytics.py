import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_processing import get_trading_history, calculate_trading_metrics

def show():
    """Display performance analytics."""
    st.header("📈 Performance Analytics")
    
    # Get date range from session state
    start_date = st.session_state.get('start_date', datetime.now().date() - timedelta(days=730))
    end_date = st.session_state.get('end_date', datetime.now().date())
    
    from_date = datetime.combine(start_date, datetime.min.time())
    to_date = datetime.combine(end_date, datetime.max.time())
    
    with st.spinner("Calculating performance metrics..."):
        deals_df = get_trading_history(from_date, to_date)
        metrics = calculate_trading_metrics(deals_df)
    
    if not metrics:
        st.warning("No trading data available for the selected period.")
        return
    
    currency_symbol = st.session_state.currency_symbol
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Profit & Loss Metrics")
        
        # Net Profit
        profit_color = "🟢" if metrics['net_profit'] >= 0 else "🔴"
        st.metric("Net Profit", f"{currency_symbol}{metrics['net_profit']:,.2f}", 
                 help="Net Profit is the Gross Profit minus your losses.")
        
        # Gross Profit
        st.metric("Gross Profit", f"{currency_symbol}{metrics['gross_profit']:,.2f}",
                 help="Gross Profit is the sum of all of your winning trades.")
        
        # Gross Loss
        st.metric("Gross Loss", f"{currency_symbol}{metrics['gross_loss']:,.2f}",
                 help="Gross Loss is the sum of all of your losing trades.")
        
        # Profit Factor
        pf_display = f"{metrics['profit_factor']:.2f}" if metrics['profit_factor'] != float('inf') else "∞"
        st.metric("Profit Factor", pf_display,
                 help="Profit Factor is the ratio of gross profits to gross losses (Gross Profit/Gross Loss).")
    
    with col2:
        st.subheader("Advanced Metrics")
        
        # Expected Payoff
        st.metric("Expected Payoff", f"{currency_symbol}{metrics['expected_payoff']:,.2f}",
                 help="Expected Payoff is the average profit expected to make for each trade (Net Profit/Number of Trades).")
        
        # Recovery Factor
        rf_display = f"{metrics['recovery_factor']:.2f}" if metrics['recovery_factor'] != float('inf') else "∞"
        st.metric("Recovery Factor", rf_display,
                 help="Recovery Factor is the ratio of net profit to maximum drawdown.")
        
        # Sharpe Ratio
        st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}",
                 help="Sharpe Ratio evaluates risk-adjusted returns, considering both returns and risk of trades.")
        
        # Total Trades
        st.metric("Total Trades", f"{metrics['total_trades']:,}",
                 help="Total number of completed trades in the selected period.")
    
    # Balance Graph
    st.subheader("Balance Graph")
    st.markdown("""
    The Balance Graph shows your trading performance over time. The X-axis shows the progression 
    of trades, and the Y-axis shows your account balance evolution.
    """)
    
    if metrics['cumulative_profit']:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(metrics['cumulative_profit']) + 1)),
            y=metrics['cumulative_profit'],
            mode='lines',
            name='Cumulative Profit',
            line=dict(color='#00ff88', width=2)
        ))
        fig.update_layout(
            title="Cumulative Profit Over Trades",
            xaxis_title="Number of Trades",
            yaxis_title=f"Cumulative Profit ({st.session_state.account_info.currency})",
            template="plotly_dark",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
