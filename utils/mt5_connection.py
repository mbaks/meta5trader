import streamlit as st
import MetaTrader5 as mt5

def initialize_mt5():
    """Initializes connection to the MetaTrader 5 terminal."""
    if not mt5.initialize():
        st.error(f"MT5 initialization failed. Error code: {mt5.last_error()}")
        st.info("Please ensure your MetaTrader 5 terminal is running.")
        return False
    return True

def authenticate_mt5(login, password, server):
    """Authorizes a connection to an MT5 account."""
    try:
        if mt5.login(login=login, password=password, server=server):
            st.success("Successfully logged in!")
            return True
        else:
            st.error(f"Login failed. Error code: {mt5.last_error()}")
            st.info("Please check your credentials and try again.")
            mt5.shutdown()
            return False
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        mt5.shutdown()
        return False
