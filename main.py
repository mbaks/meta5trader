import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import calendar
import streamlit.components.v1 as components
import warnings
import os
from html2image import Html2Image

# Import page modules
from pages import account_overview, performance_analytics, drawdown_analysis, trade_statistics, consecutive_metrics, advanced_metrics
from utils.mt5_connection import initialize_mt5, authenticate_mt5
from utils.data_processing import get_trading_history, get_daily_stats, calculate_monthly_stats
from utils.helpers import get_currency_symbol
from utils.calendar_renderer import render_calendar_html, generate_exportable_html

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MT5 Trading Dashboard",
    page_icon="📈",
    layout="wide",
)

# --- SESSION STATE MANAGEMENT ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'account_info' not in st.session_state:
    st.session_state.account_info = None
if 'currency_symbol' not in st.session_state:
    st.session_state.currency_symbol = '$'
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now()
if 'png_file' not in st.session_state:
    st.session_state.png_file = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Calendar'

# --- NAVIGATION ---
def show_navigation():
    """Display navigation menu."""
    pages = {
        'Calendar': '📅',
        'Account Overview': '📊',
        'Performance Analytics': '📈',
        'Drawdown Analysis': '📉',
        'Trade Statistics': '📋',
        'Consecutive Metrics': '🔄',
        'Advanced Metrics': '⚡'
    }
    
    cols = st.columns(len(pages))
    for i, (page_name, icon) in enumerate(pages.items()):
        with cols[i]:
            if st.button(f"{icon} {page_name}", key=f"nav_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()

# --- APP LAYOUT ---
if not st.session_state.logged_in:
    # --- LOGIN FORM ---
    st.title("Login to your MT5 Account")
    st.info("Please ensure your MetaTrader 5 terminal is running before you log in.")
    with st.form("login_form"):
        mt5_login = st.text_input("MT5 Login ID")
        mt5_password = st.text_input("Password", type="password")
        mt5_server = st.text_input("Server")
        submitted = st.form_submit_button("Login")
        if submitted:
            try:
                login_id = int(mt5_login)
                if initialize_mt5():
                    if authenticate_mt5(login_id, mt5_password, mt5_server):
                        info = mt5.account_info()
                        st.session_state.logged_in = True
                        st.session_state.account_info = info
                        st.session_state.currency_symbol = get_currency_symbol(info.currency)
                        st.rerun()
            except ValueError:
                st.error("Login ID must be a number.")
else:
    # --- MAIN DASHBOARD ---
    info = st.session_state.account_info
    currency_symbol = st.session_state.currency_symbol

    # --- Sidebar ---
    with st.sidebar:
        st.header("Account Details")
        if info:
            st.success(f"Logged in: {info.name}")
            st.info(f"Server: {info.server}")
            st.metric("Current Balance", f"{currency_symbol}{info.balance:,.2f}")
        if st.button("Logout", use_container_width=True):
            mt5.shutdown()
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

        st.header("History Range")
        st.info("Select the total range of history to analyze.")
        start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=730))
        end_date = st.date_input("End Date", datetime.now().date())
        
        # Store dates in session state for other pages
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date

    # --- Navigation ---
    show_navigation()
    
    # --- Page Content ---
    if st.session_state.current_page == 'Calendar':
        # --- CALENDAR PAGE (HOME) ---
        st.title("📅 Weekly Calendar Performance")
        
        # --- Data Fetching ---
        from_date = datetime.combine(start_date, datetime.min.time())
        to_date = datetime.combine(end_date, datetime.max.time())
        with st.spinner("Fetching and processing trading history..."):
            deals_df = get_trading_history(from_date, to_date)
            daily_stats_df = get_daily_stats(deals_df)

        if not daily_stats_df.empty:
            # Calculate monthly stats for display
            selected_year = st.session_state.selected_date.year
            selected_month = st.session_state.selected_date.month
            stats = calculate_monthly_stats(daily_stats_df, selected_year, selected_month)

            # --- Monthly Statistics & Export Button ---
            profit_color = "#2e7d32" if stats['current_profit'] > 0 else ("#b71c1c" if stats['current_profit'] < 0 else "#9E9E9E")
            delta_color = "#2e7d32" if stats['percentage_change'] > 0 else ("#b71c1c" if stats['percentage_change'] < 0 else "#9E9E9E")
            delta_symbol = "▲" if stats['percentage_change'] > 0 else ("▼" if stats['percentage_change'] < 0 else "●")

            col_title, col_menu = st.columns([0.95, 0.05])

            with col_title:
                 st.markdown(
                    f"""
                    <div style='text-align:center; padding: 15px; background-color: #1e1e1e; border-radius: 10px; margin-bottom: 20px;'>
                        <h2 style='margin: 0; color: white; margin-bottom: 10px;'>{calendar.month_name[selected_month]} {selected_year}</h2>
                        <div style='display: flex; justify-content: center; align-items: center; gap: 30px; flex-wrap: wrap;'>
                            <div style='text-align: center;'>
                                <div style='color: #9E9E9E; font-size: 0.9em; margin-bottom: 5px;'>Monthly P/L</div>
                                <div style='color: {profit_color}; font-size: 1.4em; font-weight: bold;'>
                                    {currency_symbol}{stats['current_profit']:,.2f}
                                </div>
                            </div>
                            <div style='text-align: center;'>
                                <div style='color: #9E9E9E; font-size: 0.9em; margin-bottom: 5px;'>Total Trades</div>
                                <div style='color: white; font-size: 1.4em; font-weight: bold;'>
                                    {stats['total_trades']}
                                </div>
                            </div>
                            <div style='text-align: center;'>
                                <div style='color: #9E9E9E; font-size: 0.9em; margin-bottom: 5px;'>vs. Previous Month</div>
                                <div style='color: {delta_color}; font-size: 1.1em; font-weight: bold;'>
                                    {delta_symbol} {abs(stats['percentage_change']):.1f}%
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_menu:
                with st.popover("⋮", use_container_width=False):
                    st.markdown("##### Export Options")
                    if st.button("Generate PNG"):
                        with st.spinner("Creating image... please wait."):
                            # Generate HTML for export
                            export_html = generate_exportable_html(
                                stats, daily_stats_df, selected_year, selected_month, currency_symbol
                            )
                            # Prepare file paths
                            output_dir = 'temp_exports'
                            if not os.path.exists(output_dir):
                                os.makedirs(output_dir)
                            filename = f"report_{selected_year}_{calendar.month_abbr[selected_month]}.png"
                            full_path = os.path.join(output_dir, filename)
                            
                            # Use html2image to generate the screenshot
                            hti = Html2Image(output_path=output_dir, size=(1200, 1400))
                            hti.screenshot(html_str=export_html, save_as=filename)
                            
                            # Read the generated image into session state for download
                            with open(full_path, "rb") as f:
                                st.session_state.png_file = {
                                    "data": f.read(),
                                    "name": filename
                                }
                            
                            os.remove(full_path) # Clean up the temp file
                            st.rerun()

                    if st.session_state.png_file:
                        st.download_button(
                            label="Download PNG",
                            data=st.session_state.png_file["data"],
                            file_name=st.session_state.png_file["name"],
                            mime="image/png",
                            # Clear state after download button is clicked
                            on_click=lambda: st.session_state.update(png_file=None)
                        )

            # --- Month/Year Navigation Controls with Arrow Icons ---
            st.markdown("""
            <style>
            .nav-button {
                background-color: #333;
                color: #BDBDBD;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 18px;
                cursor: pointer;
                width: 100%;
                transition: background-color 0.3s, color 0.3s;
            }
            .nav-button:hover {
                background-color: #424242;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                if st.button("⟪", key="prev_year", use_container_width=True, help="Previous Year"):
                    st.session_state.selected_date = st.session_state.selected_date.replace(year=st.session_state.selected_date.year - 1)
                    st.session_state.png_file = None
                    st.rerun()

            with col2:
                if st.button("◀", key="prev_month", use_container_width=True, help="Previous Month"):
                    sd = st.session_state.selected_date
                    st.session_state.selected_date = (sd.replace(day=1) - timedelta(days=1)).replace(day=1)
                    st.session_state.png_file = None
                    st.rerun()

            with col3:
                if st.button("Today", key="today", use_container_width=True):
                    st.session_state.selected_date = datetime.now()
                    st.session_state.png_file = None
                    st.rerun()

            with col4:
                if st.button("▶", key="next_month", use_container_width=True, help="Next Month"):
                    sd = st.session_state.selected_date
                    next_month = (sd.replace(day=28) + timedelta(days=4)).replace(day=1)
                    st.session_state.selected_date = next_month
                    st.session_state.png_file = None
                    st.rerun()

            with col5:
                if st.button("⟫", key="next_year", use_container_width=True, help="Next Year"):
                    st.session_state.selected_date = st.session_state.selected_date.replace(year=st.session_state.selected_date.year + 1)
                    st.session_state.png_file = None
                    st.rerun()

            # --- Calendar Display ---
            html_code = render_calendar_html(daily_stats_df, selected_year, selected_month, currency_symbol)
            components.html(html_code, height=800, scrolling=True)
        else:
            st.warning("No trading history found for the selected date range.")
    
    elif st.session_state.current_page == 'Account Overview':
        account_overview.show()
    elif st.session_state.current_page == 'Performance Analytics':
        performance_analytics.show()
    elif st.session_state.current_page == 'Drawdown Analysis':
        drawdown_analysis.show()
    elif st.session_state.current_page == 'Trade Statistics':
        trade_statistics.show()
    elif st.session_state.current_page == 'Consecutive Metrics':
        consecutive_metrics.show()
    elif st.session_state.current_page == 'Advanced Metrics':
        advanced_metrics.show()
