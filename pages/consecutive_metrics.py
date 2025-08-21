import streamlit as st
from datetime import datetime, timedelta
from utils.data_processing import get_trading_history, calculate_trading_metrics

def show():
    """Display consecutive trade metrics."""
    st.header("🔄 Consecutive Metrics")
    
    # Get date range
    start_date = st.session_state.get('start_date', datetime.now().date() - timedelta(days=730))
    end_date = st.session_state.get('end_date', datetime.now().date())
    
    from_date = datetime.combine(start_date, datetime.min.time())
    to_date = datetime.combine(end_date, datetime.max.time())
    
    with st.spinner("Analyzing consecutive patterns..."):
        deals_df = get_trading_history(from_date, to_date)
        metrics = calculate_trading_metrics(deals_df)
    
    if not metrics:
        st.warning("No trading data available for the selected period.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Winning Streaks")
        
        # Maximum Consecutive Wins
        st.metric("Maximum Consecutive Wins", f"{metrics['max_consecutive_wins']:,}",
                 help="The longest streak of consecutive winning trades.")
        
        # Average Consecutive Wins
        st.metric("Average Consecutive Wins", f"{metrics['avg_consecutive_wins']:.1f}",
                 help="Average length of winning streaks.")
        
        st.markdown("""
        ### Understanding Winning Streaks
        
        Consecutive wins show your ability to maintain profitable trading during good periods. 
        Higher numbers indicate:
        - Strong trend-following ability
        - Good market timing
        - Effective risk management during profitable periods
        """)
    
    with col2:
        st.subheader("Losing Streaks")
        
        # Maximum Consecutive Losses
        st.metric("Maximum Consecutive Losses", f"{metrics['max_consecutive_losses']:,}",
                 help="The longest streak of consecutive losing trades.")
        
        # Risk Assessment based on consecutive losses
        if metrics['max_consecutive_losses'] <= 3:
            risk_assessment = "🟢 Good Control"
        elif metrics['max_consecutive_losses'] <= 6:
            risk_assessment = "🟡 Moderate Risk"
        else:
            risk_assessment = "🔴 High Risk"
        
        st.markdown(f"**Risk Assessment:** {risk_assessment}")
        
        st.markdown("""
        ### Understanding Losing Streaks
        
        Consecutive losses are natural in trading but should be monitored:
        - **1-3 losses:** Normal market fluctuation
        - **4-6 losses:** Review strategy and risk management
        - **7+ losses:** Consider reducing position size or taking a break
        
        ### Streak Management Tips
        - Set maximum consecutive loss limits
        - Reduce position size after 3+ losses
        - Review strategy after unusual streaks
        """)
