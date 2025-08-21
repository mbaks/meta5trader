import streamlit as st
from utils.data_processing import get_positions

def show():
    """Display account overview metrics."""
    st.header("📊 Account Overview")
    
    info = st.session_state.account_info
    currency_symbol = st.session_state.currency_symbol
    
    # Get current positions for floating P/L calculation
    positions_df = get_positions()
    floating_pl = 0
    margin_used = 0
    
    if positions_df is not None and not positions_df.empty:
        floating_pl = positions_df['profit'].sum()
        #margin_used = positions_df['margin'].sum()
        if "margin" in positions_df.columns:
            margin_used = positions_df["margin"].sum()
        else:
            margin_used = 0  # or compute it another way
    
    # Calculate metrics
    balance = info.balance
    equity = balance + floating_pl
    free_margin = info.margin_free
    credit = info.credit if hasattr(info, 'credit') else 0
    margin_level = (equity / margin_used * 100) if margin_used > 0 else 0
    
    # Display metrics in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Core Account Metrics")
        
        # Balance
        st.markdown("### Current Balance")
        st.markdown(f"""
        **{currency_symbol}{balance:,.2f}**
        
        Balance is the sum of equity minus floating profit/loss. This represents your account's 
        base value without considering current open positions.
        """)
        
        # Equity
        st.markdown("### Equity")
        equity_color = "🟢" if floating_pl >= 0 else "🔴"
        st.markdown(f"""
        **{currency_symbol}{equity:,.2f}** {equity_color}
        
        Equity is the sum of Balance and Floating P/L. This is your real-time account value 
        including all open positions.
        """)
        
        # Free Margin
        st.markdown("### Free Margin")
        st.markdown(f"""
        **{currency_symbol}{free_margin:,.2f}**
        
        Free Margin is the available fund for placing new trades. It is equity minus the 
        open position margin.
        """)
        
        # Credit Facility
        st.markdown("### Credit Facility")
        st.markdown(f"""
        **{currency_symbol}{credit:,.2f}**
        
        Credit Facility is the bonus or credit that your broker has provided you.
        """)
    
    with col2:
        st.subheader("Position & Risk Metrics")
        
        # Margin
        st.markdown("### Margin")
        st.markdown(f"""
        **{currency_symbol}{margin_used:,.2f}**
        
        Margin is the amount of funds used for placing open positions. This amount depends 
        on the leverage that you choose.
        """)
        
        # Floating P/L
        st.markdown("### Floating P/L")
        pl_color = "🟢" if floating_pl >= 0 else "🔴"
        st.markdown(f"""
        **{currency_symbol}{floating_pl:,.2f}** {pl_color}
        
        Floating P/L is the amount of unrealized profit or loss due to open positions. 
        It will be zero when you don't have any open positions.
        """)
        
        # Margin Level
        st.markdown("### Margin Level")
        level_color = "🟢" if margin_level > 100 else ("🟡" if margin_level > 50 else "🔴")
        st.markdown(f"""
        **{margin_level:.2f}%** {level_color}
        
        Margin Level is the ratio between your equity and the margin (Equity/Margin*100). 
        Higher percentages indicate lower risk.
        """)
        
        # Current positions summary
        st.markdown("### Open Positions")
        if positions_df is not None and not positions_df.empty:
            st.markdown(f"""
            **{len(positions_df)} positions open**
            
            Total volume: {positions_df['volume'].sum():.2f} lots
            """)
        else:
            st.markdown("**No open positions**")
