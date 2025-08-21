import streamlit as st
from datetime import datetime, timedelta
from utils.data_processing import get_trading_history, calculate_trading_metrics

def show():
    """Display detailed trade statistics."""
    st.header("📋 Trade Statistics")
    
    # Get date range
    start_date = st.session_state.get('start_date', datetime.now().date() - timedelta(days=730))
    end_date = st.session_state.get('end_date', datetime.now().date())
    
    from_date = datetime.combine(start_date, datetime.min.time())
    to_date = datetime.combine(end_date, datetime.max.time())
    
    with st.spinner("Analyzing trade statistics..."):
        deals_df = get_trading_history(from_date, to_date)
        metrics = calculate_trading_metrics(deals_df)
    
    if not metrics:
        st.warning("No trading data available for the selected period.")
        return
    
    currency_symbol = st.session_state.currency_symbol
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Trade Performance")
        
        # Total Trades
        st.metric("Total Trades", f"{metrics['total_trades']:,}",
                 help="Total number of completed trades in the selected period.")
        
        # Winning Trades
        st.metric("Winning Trades", f"{metrics['winning_trades_count']:,} ({metrics['win_rate']:.1f}%)",
                 help="Number and percentage of profitable trades.")
        
        # Losing Trades
        losing_rate = 100 - metrics['win_rate']
        st.metric("Losing Trades", f"{metrics['losing_trades_count']:,} ({losing_rate:.1f}%)",
                 help="Number and percentage of losing trades.")
        
        # Largest Win
        st.metric("Largest Winning Trade", f"{currency_symbol}{metrics['largest_win']:,.2f}",
                 help="The most profitable single trade.")
        
        # Largest Loss
        st.metric("Largest Losing Trade", f"{currency_symbol}{metrics['largest_loss']:,.2f}",
                 help="The most unprofitable single trade.")
    
    with col2:
        st.subheader("Average Performance")
        
        # Average Win
        st.metric("Average Winning Trade", f"{currency_symbol}{metrics['avg_win']:,.2f}",
                 help="Average profit per winning trade.")
        
        # Average Loss
        st.metric("Average Losing Trade", f"{currency_symbol}{metrics['avg_loss']:,.2f}",
                 help="Average loss per losing trade.")
        
        # Win/Loss Ratio
        win_loss_ratio = abs(metrics['avg_win'] / metrics['avg_loss']) if metrics['avg_loss'] != 0 else float('inf')
        ratio_display = f"{win_loss_ratio:.2f}" if win_loss_ratio != float('inf') else "∞"
        st.metric("Average Win/Loss Ratio", ratio_display,
                 help="Ratio of average winning trade to average losing trade.")
        
        # Short Trades Analysis
        st.metric("Short Trades", f"{metrics['short_trades_total']:,}",
                 help="Total number of short (sell) trades.")
        
        st.metric("Short Trade Win Rate", f"{metrics['short_win_rate']:.1f}%",
                 help="Win rate specifically for short trades.")
