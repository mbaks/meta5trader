import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from utils.data_processing import get_trading_history, calculate_trading_metrics

def show():
    """Display advanced trading metrics and analysis."""
    st.header("⚡ Advanced Metrics")
    
    # Get date range
    start_date = st.session_state.get('start_date', datetime.now().date() - timedelta(days=730))
    end_date = st.session_state.get('end_date', datetime.now().date())
    
    from_date = datetime.combine(start_date, datetime.min.time())
    to_date = datetime.combine(end_date, datetime.max.time())
    
    with st.spinner("Calculating advanced metrics..."):
        deals_df = get_trading_history(from_date, to_date)
        metrics = calculate_trading_metrics(deals_df)
    
    if not metrics:
        st.warning("No trading data available for the selected period.")
        return
    
    currency_symbol = st.session_state.currency_symbol
    
    # Advanced Metrics Display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Risk-Adjusted Returns")
        
        # Sharpe Ratio
        st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}",
                 help="Risk-adjusted return metric. Higher is better. >1 is good, >2 is excellent.")
        
        # Profit Factor
        pf_display = f"{metrics['profit_factor']:.2f}" if metrics['profit_factor'] != float('inf') else "∞"
        st.metric("Profit Factor", pf_display,
                 help="Gross Profit / Gross Loss. >1.25 is good, >2 is excellent.")
    
    with col2:
        st.subheader("Recovery Metrics")
        
        # Recovery Factor
        rf_display = f"{metrics['recovery_factor']:.2f}" if metrics['recovery_factor'] != float('inf') else "∞"
        st.metric("Recovery Factor", rf_display,
                 help="Net Profit / Max Drawdown. Higher values indicate better recovery ability.")
        
        # Expected Payoff
        st.metric("Expected Payoff", f"{currency_symbol}{metrics['expected_payoff']:,.2f}",
                 help="Average profit per trade. Should be positive for profitable systems.")
    
    with col3:
        st.subheader("Efficiency Metrics")
        
        # Win Rate
        st.metric("Win Rate", f"{metrics['win_rate']:.1f}%",
                 help="Percentage of winning trades. 50%+ is generally good.")
        
        # Average Win/Loss Ratio
        if metrics['avg_loss'] != 0:
            win_loss_ratio = abs(metrics['avg_win'] / metrics['avg_loss'])
            st.metric("Win/Loss Ratio", f"{win_loss_ratio:.2f}",
                     help="Average win divided by average loss. >1 is preferred.")
        else:
            st.metric("Win/Loss Ratio", "∞")
    
    # Performance Analysis
    st.subheader("Performance Analysis")
    
    if deals_df is not None and not deals_df.empty:
        exit_trades = deals_df[deals_df['entry'] == 'Exit'].copy()
        
        if not exit_trades.empty:
            # Profit Distribution Chart
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Profit Distribution")
                fig = px.histogram(
                    exit_trades, 
                    x='profit', 
                    nbins=30,
                    title="Distribution of Trade Profits",
                    labels={'profit': f'Profit ({st.session_state.account_info.currency})', 'count': 'Number of Trades'}
                )
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Monthly Performance")
                # Monthly aggregation
                exit_trades['month'] = exit_trades['time'].dt.to_period('M')
                monthly_profit = exit_trades.groupby('month')['profit'].sum().reset_index()
                monthly_profit['month'] = monthly_profit['month'].astype(str)
                
                fig = px.bar(
                    monthly_profit,
                    x='month',
                    y='profit',
                    title="Monthly Profit/Loss",
                    labels={'profit': f'Profit ({st.session_state.account_info.currency})', 'month': 'Month'}
                )
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
    
    # Performance Ratings
    st.subheader("Performance Rating")
    
    # Calculate overall score
    # Performance Ratings (continued)
    st.subheader("Performance Rating")
    
    # Calculate overall score
    score = 0
    max_score = 100
    
    # Profit Factor Score (25 points)
    if metrics['profit_factor'] >= 2:
        pf_score = 25
    elif metrics['profit_factor'] >= 1.5:
        pf_score = 20
    elif metrics['profit_factor'] >= 1.25:
        pf_score = 15
    elif metrics['profit_factor'] >= 1:
        pf_score = 10
    else:
        pf_score = 0
    score += pf_score
    
    # Win Rate Score (25 points)
    if metrics['win_rate'] >= 60:
        wr_score = 25
    elif metrics['win_rate'] >= 50:
        wr_score = 20
    elif metrics['win_rate'] >= 40:
        wr_score = 15
    elif metrics['win_rate'] >= 30:
        wr_score = 10
    else:
        wr_score = 5
    score += wr_score
    
    # Sharpe Ratio Score (25 points)
    if metrics['sharpe_ratio'] >= 2:
        sr_score = 25
    elif metrics['sharpe_ratio'] >= 1:
        sr_score = 20
    elif metrics['sharpe_ratio'] >= 0.5:
        sr_score = 15
    elif metrics['sharpe_ratio'] >= 0:
        sr_score = 10
    else:
        sr_score = 0
    score += sr_score
    
    # Recovery Factor Score (25 points)
    if metrics['recovery_factor'] >= 5:
        rf_score = 25
    elif metrics['recovery_factor'] >= 3:
        rf_score = 20
    elif metrics['recovery_factor'] >= 2:
        rf_score = 15
    elif metrics['recovery_factor'] >= 1:
        rf_score = 10
    else:
        rf_score = 0
    score += rf_score
    
    # Display rating
    if score >= 80:
        rating = "🏆 Excellent"
        color = "#2e7d32"
    elif score >= 60:
        rating = "🥈 Good"
        color = "#1976d2"
    elif score >= 40:
        rating = "🥉 Average"
        color = "#f57c00"
    else:
        rating = "⚠️ Needs Improvement"
        color = "#d32f2f"
    
    st.markdown(f"""
    <div style='text-align: center; padding: 20px; background-color: {color}; border-radius: 10px; margin: 20px 0;'>
        <h2 style='color: white; margin: 0;'>{rating}</h2>
        <h3 style='color: white; margin: 10px 0;'>Overall Score: {score}/100</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Score breakdown
    st.subheader("Score Breakdown")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Profit Factor", f"{pf_score}/25", 
                 help=f"Current: {metrics['profit_factor']:.2f}")
    
    with col2:
        st.metric("Win Rate", f"{wr_score}/25", 
                 help=f"Current: {metrics['win_rate']:.1f}%")
    
    with col3:
        st.metric("Sharpe Ratio", f"{sr_score}/25", 
                 help=f"Current: {metrics['sharpe_ratio']:.2f}")
    
    with col4:
        st.metric("Recovery Factor", f"{rf_score}/25", 
                 help=f"Current: {metrics['recovery_factor']:.2f}")
    
    # Recommendations
    st.subheader("Recommendations")
    
    recommendations = []
    
    if metrics['profit_factor'] < 1.25:
        recommendations.append("🔸 **Improve Profit Factor**: Focus on cutting losses early and letting winners run longer.")
    
    if metrics['win_rate'] < 50:
        recommendations.append("🔸 **Increase Win Rate**: Review entry criteria and market analysis to improve trade selection.")
    
    if metrics['sharpe_ratio'] < 1:
        recommendations.append("🔸 **Enhance Risk-Adjusted Returns**: Consider reducing position sizes during volatile periods.")
    
    if metrics['recovery_factor'] < 2:
        recommendations.append("🔸 **Improve Recovery Factor**: Focus on reducing maximum drawdown through better risk management.")
    
    if metrics['max_consecutive_losses'] > 5:
        recommendations.append("🔸 **Manage Losing Streaks**: Implement rules to reduce position size after consecutive losses.")
    
    if not recommendations:
        recommendations.append("🎉 **Excellent Performance**: Your trading system shows strong metrics across all categories!")
    
    for rec in recommendations:
        st.markdown(rec)
