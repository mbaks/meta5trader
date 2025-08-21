import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_trading_history(from_date, to_date):
    """Fetch trading history from MT5."""
    deals = mt5.history_deals_get(from_date, to_date)
    if deals is None or len(deals) == 0:
        return None
    deals_df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
    deals_df['time'] = pd.to_datetime(deals_df['time'], unit='s')
    deals_df['entry'] = deals_df['entry'].map({0: 'Entry', 1: 'Exit'})
    return deals_df

@st.cache_data(ttl=300)
def get_positions():
    """Get current open positions."""
    positions = mt5.positions_get()
    if positions is None or len(positions) == 0:
        return None
    positions_df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    positions_df['time'] = pd.to_datetime(positions_df['time'], unit='s')
    return positions_df

def get_daily_stats(deals_df):
    """Aggregates deal data into daily profit/loss and trade counts."""
    if deals_df is None or deals_df.empty:
        return pd.DataFrame()

    daily_stats = deals_df[deals_df['entry'] == 'Exit'].groupby(deals_df['time'].dt.date).agg(
        Profit=('profit', 'sum'),
        Trades=('profit', 'count'),
    ).reset_index()
    daily_stats.rename(columns={'time': 'Date'}, inplace=True)
    daily_stats['Date'] = pd.to_datetime(daily_stats['Date'])
    return daily_stats

def calculate_trading_metrics(deals_df):
    """Calculate comprehensive trading metrics."""
    if deals_df is None or deals_df.empty:
        return {}
    
    # Filter exit trades only
    exit_trades = deals_df[deals_df['entry'] == 'Exit'].copy()
    
    if exit_trades.empty:
        return {}
    
    # Basic metrics
    total_trades = len(exit_trades)
    winning_trades = exit_trades[exit_trades['profit'] > 0]
    losing_trades = exit_trades[exit_trades['profit'] < 0]
    
    gross_profit = winning_trades['profit'].sum() if not winning_trades.empty else 0
    gross_loss = abs(losing_trades['profit'].sum()) if not losing_trades.empty else 0
    net_profit = gross_profit - gross_loss
    
    # Profit factor
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0
    
    # Expected payoff
    expected_payoff = net_profit / total_trades if total_trades > 0 else 0
    
    # Win rate
    win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
    
    # Average trades
    avg_win = winning_trades['profit'].mean() if not winning_trades.empty else 0
    avg_loss = losing_trades['profit'].mean() if not losing_trades.empty else 0
    
    # Largest trades
    largest_win = winning_trades['profit'].max() if not winning_trades.empty else 0
    largest_loss = losing_trades['profit'].min() if not losing_trades.empty else 0
    
    # Calculate drawdown
    exit_trades_sorted = exit_trades.sort_values('time')
    cumulative_profit = exit_trades_sorted['profit'].cumsum()
    running_max = cumulative_profit.expanding().max()
    drawdown = cumulative_profit - running_max
    max_drawdown = abs(drawdown.min()) if not drawdown.empty else 0
    
    # Recovery factor
    recovery_factor = net_profit / max_drawdown if max_drawdown > 0 else float('inf') if net_profit > 0 else 0
    
    # Sharpe ratio (simplified - using daily returns)
    daily_returns = exit_trades.groupby(exit_trades['time'].dt.date)['profit'].sum()
    if len(daily_returns) > 1:
        sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252) if daily_returns.std() > 0 else 0
    else:
        sharpe_ratio = 0
    
    # Consecutive wins/losses
    consecutive_wins = []
    consecutive_losses = []
    current_win_streak = 0
    current_loss_streak = 0
    
    for profit in exit_trades_sorted['profit']:
        if profit > 0:
            current_win_streak += 1
            if current_loss_streak > 0:
                consecutive_losses.append(current_loss_streak)
                current_loss_streak = 0
        elif profit < 0:
            current_loss_streak += 1
            if current_win_streak > 0:
                consecutive_wins.append(current_win_streak)
                current_win_streak = 0
    
    # Add final streaks
    if current_win_streak > 0:
        consecutive_wins.append(current_win_streak)
    if current_loss_streak > 0:
        consecutive_losses.append(current_loss_streak)
    
    max_consecutive_wins = max(consecutive_wins) if consecutive_wins else 0
    max_consecutive_losses = max(consecutive_losses) if consecutive_losses else 0
    avg_consecutive_wins = np.mean(consecutive_wins) if consecutive_wins else 0
    
    # Short trades analysis
    short_trades = exit_trades[exit_trades['type'] == 1]  # Assuming 1 is sell
    short_wins = short_trades[short_trades['profit'] > 0] if not short_trades.empty else pd.DataFrame()
    short_win_rate = len(short_wins) / len(short_trades) * 100 if not short_trades.empty else 0
    
    return {
        'total_trades': total_trades,
        'gross_profit': gross_profit,
        'gross_loss': gross_loss,
        'net_profit': net_profit,
        'profit_factor': profit_factor,
        'expected_payoff': expected_payoff,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'largest_win': largest_win,
        'largest_loss': largest_loss,
        'max_drawdown': max_drawdown,
        'recovery_factor': recovery_factor,
        'sharpe_ratio': sharpe_ratio,
        'max_consecutive_wins': max_consecutive_wins,
        'max_consecutive_losses': max_consecutive_losses,
        'avg_consecutive_wins': avg_consecutive_wins,
        'short_trades_total': len(short_trades),
        'short_win_rate': short_win_rate,
        'cumulative_profit': cumulative_profit.tolist() if not cumulative_profit.empty else [],
        'winning_trades_count': len(winning_trades),
        'losing_trades_count': len(losing_trades)
    }

def calculate_monthly_stats(daily_stats, year, month):
    """Calculates statistics for the given month and compares to the previous one."""
    if daily_stats.empty:
        return {'current_profit': 0, 'percentage_change': 0, 'total_trades': 0}

    current_month_data = daily_stats[
        (daily_stats['Date'].dt.year == year) &
        (daily_stats['Date'].dt.month == month)
    ]

    current_month_profit = current_month_data['Profit'].sum()
    total_trades = current_month_data['Trades'].sum()

    prev_month_date = datetime(year, month, 1) - timedelta(days=1)
    previous_month_profit = daily_stats[
        (daily_stats['Date'].dt.year == prev_month_date.year) &
        (daily_stats['Date'].dt.month == prev_month_date.month)
    ]['Profit'].sum()

    if previous_month_profit != 0:
        percentage_change = ((current_month_profit - previous_month_profit) / abs(previous_month_profit)) * 100
    elif current_month_profit != 0:
        percentage_change = 100.0
    else:
        percentage_change = 0.0

    return {
        'current_profit': current_month_profit,
        'percentage_change': percentage_change,
        'total_trades': int(total_trades)
    }
