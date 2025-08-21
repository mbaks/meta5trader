import streamlit as st
from datetime import datetime, timedelta
from utils.data_processing import get_trading_history, calculate_trading_metrics

def show():
    """Display drawdown analysis."""
    st.header("📉 Drawdown Analysis")
    
    # Get date range
    start_date = st.session_state.get('start_date', datetime.now().date() - timedelta(days=730))
    end_date = st.session_state.get('end_date', datetime.now().date())
    
    from_date = datetime.combine(start_date, datetime.min.time())
    to_date = datetime.combine(end_date, datetime.max.time())
    
    with st.spinner("Analyzing drawdowns..."):
        deals_df = get_trading_history(from_date, to_date)
        metrics = calculate_trading_metrics(deals_df)
    
    if not metrics:
        st.warning("No trading data available for the selected period.")
        return
    
    currency_symbol = st.session_state.currency_symbol
    info = st.session_state.account_info
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Drawdown Metrics")
        
        # Balance Absolute Drawdown
        initial_balance = info.balance - metrics['net_profit']  # Approximate initial balance
        absolute_drawdown = initial_balance - (initial_balance - metrics['max_drawdown'])
        
        st.metric("Balance Absolute Drawdown", f"{currency_symbol}{absolute_drawdown:,.2f}",
                 help="Balance Absolute Drawdown represents the difference between the initial balance and the minimum balance.")
        
        # Balance Drawdown Maximal
        max_dd_percent = (metrics['max_drawdown'] / initial_balance * 100) if initial_balance > 0 else 0
        st.metric("Balance Drawdown Maximal", 
                 f"{currency_symbol}{metrics['max_drawdown']:,.2f} ({max_dd_percent:.1f}%)",
                 help="Maximum drawdown is the largest loss from a peak to a low in the balance before changing direction upward again.")
        
        # Risk Assessment
        if max_dd_percent < 5:
            risk_level = "🟢 Low Risk"
        elif max_dd_percent < 15:
            risk_level = "🟡 Moderate Risk"
        else:
            risk_level = "🔴 High Risk"
        
        st.markdown(f"**Risk Level:** {risk_level}")
    
    with col2:
        st.subheader("Risk Management")
        
        st.markdown("""
        ### Understanding Drawdown
        
        A drawdown is the amount of loss from a peak to a low in the balance before changing 
        direction to the upside again. In the Balance Graph, the Balance Drawdown Maximal 
        is the largest drawdown.
        
        ### Risk Guidelines
        - **Low Risk (< 5%):** Conservative trading approach
        - **Moderate Risk (5-15%):** Balanced risk management
        - **High Risk (> 15%):** Aggressive trading, consider reducing position sizes
        
        ### Recovery Metrics
        """)
        
        # Recovery statistics
        if metrics['max_drawdown'] > 0:
            recovery_ratio = metrics['net_profit'] / metrics['max_drawdown']
            st.metric("Recovery Ratio", f"{recovery_ratio:.2f}x",
                     help="How many times the net profit covers the maximum drawdown.")
