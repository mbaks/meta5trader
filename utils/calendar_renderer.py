import calendar
import pandas as pd

def render_calendar_html(daily_stats, year, month, currency_symbol='$'):
    """Generates the HTML string for the calendar with weekly totals."""
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(year, month)

    css = """
    <style>
        .calendar-container { font-family: Arial, sans-serif; color: white; }
        .calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr) auto; gap: 5px; }
        .day-header, .weekly-header { font-weight: bold; text-align: center; padding: 10px 5px; background-color: #333; border-radius: 5px; font-size: 0.9em; }
        .day-box { background-color: #212121; border-radius: 5px; min-height: 100px; display: flex; flex-direction: column; padding: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        .day-date { font-weight: bold; font-size: 1.2rem; color: #BDBDBD; }
        .day-profit { font-weight: bold; font-size: 1.1rem; margin-top: 5px; }
        .day-trades { font-size: 0.9rem; color: #9E9E9E; }
        .weekly-total { display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: bold; font-size: 1.1em; padding: 10px; border-radius: 5px; }
        .weekly-trades { font-size: 0.9rem; color: #9E9E9E; margin-top: 5px; }
        .green { background-color: #2e7d32; }
        .red { background-color: #b71c1c; }
        .neutral { background-color: #424242; }
        .day-box-empty { background-color: #121212; border-radius: 5px; }
    </style>
    """

    html_content = '<div class="calendar-grid">'
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day_name in day_labels:
        html_content += f'<div class="day-header">{day_name}</div>'
    html_content += '<div class="weekly-header">Week Total</div>'

    for week in month_days:
        weekly_profit = 0.0
        weekly_trades = 0
        for date_obj in week:
            if date_obj.month != month:
                html_content += '<div class="day-box-empty"></div>'
            else:
                day_data = daily_stats[daily_stats['Date'] == pd.to_datetime(date_obj)]
                if not day_data.empty:
                    profit = day_data['Profit'].iloc[0]
                    trades = day_data['Trades'].iloc[0]
                    weekly_profit += profit
                    weekly_trades += trades
                    profit_class = 'green' if profit > 0 else ('red' if profit < 0 else 'neutral')
                    profit_text = f"{currency_symbol}{profit:,.2f}"
                    html_content += f'''
                    <div class="day-box {profit_class}">
                        <div class="day-date">{date_obj.day}</div>
                        <div class="day-profit">{profit_text}</div>
                        <div class="day-trades">{int(trades)} trades</div>
                    </div>'''
                else:
                    html_content += f'''
                    <div class="day-box neutral">
                        <div class="day-date">{date_obj.day}</div>
                        <div class="day-profit">{currency_symbol}0.00</div>
                        <div class="day-trades">0 trades</div>
                    </div>'''

        total_class = 'green' if weekly_profit > 0 else ('red' if weekly_profit < 0 else 'neutral')
        html_content += f'''
        <div class="weekly-total {total_class}">
            <div>{currency_symbol}{weekly_profit:,.2f}</div>
            <div class="weekly-trades">{int(weekly_trades)} trades</div>
        </div>'''

    html_content += '</div>'
    return f"{css}<div class='calendar-container'>{html_content}</div>"

def generate_exportable_html(stats, daily_stats_df, year, month, currency_symbol):
    """Generates a single, self-contained HTML string for PNG export."""
    calendar_full_html = render_calendar_html(daily_stats_df, year, month, currency_symbol)
    
    # Extract CSS and calendar body HTML from the rendered component
    try:
        css = calendar_full_html.split('<style>')[1].split('</style>')[0]
    except IndexError:
        css = ""
    try:
        calendar_body_html = calendar_full_html.split('<div class=\'calendar-container\'>')[1]
        calendar_body_html = f'<div class="calendar-container">{calendar_body_html}'
    except IndexError:
        calendar_body_html = "<div>Calendar could not be rendered.</div>"

    # Recreate the stats block HTML with slightly larger fonts for clarity in the image
    month_name = calendar.month_name[month]
    profit_color = "#2e7d32" if stats['current_profit'] > 0 else ("#b71c1c" if stats['current_profit'] < 0 else "#9E9E9E")
    delta_color = "#2e7d32" if stats['percentage_change'] > 0 else ("#b71c1c" if stats['percentage_change'] < 0 else "#9E9E9E")
    delta_symbol = "▲" if stats['percentage_change'] > 0 else ("▼" if stats['percentage_change'] < 0 else "●")

    stats_html = f"""
    <div style='text-align:center; padding: 25px; background-color: #1e1e1e; border-radius: 10px; margin-bottom: 20px; font-family: Arial, sans-serif;'>
        <h2 style='margin: 0; color: white; margin-bottom: 15px; font-size: 2em;'>{month_name} {year}</h2>
        <div style='display: flex; justify-content: center; align-items: center; gap: 40px; flex-wrap: wrap;'>
            <div style='text-align: center;'>
                <div style='color: #BDBDBD; font-size: 1.1em; margin-bottom: 8px;'>Monthly P/L</div>
                <div style='color: {profit_color}; font-size: 1.8em; font-weight: bold;'>
                    {currency_symbol}{stats['current_profit']:,.2f}
                </div>
            </div>
            <div style='text-align: center;'>
                <div style='color: #BDBDBD; font-size: 1.1em; margin-bottom: 8px;'>Total Trades</div>
                <div style='color: white; font-size: 1.8em; font-weight: bold;'>
                    {stats['total_trades']}
                </div>
            </div>
            <div style='text-align: center;'>
                <div style='color: #BDBDBD; font-size: 1.1em; margin-bottom: 8px;'>vs. Previous Month</div>
                <div style='color: {delta_color}; font-size: 1.4em; font-weight: bold;'>
                    {delta_symbol} {abs(stats['percentage_change']):.1f}%
                </div>
            </div>
        </div>
    </div>
    """

    # Combine all parts into a final HTML document for export
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ background-color: #0E1117; padding: 20px; }}
        {css}
    </style>
    </head>
    <body>
        {stats_html}
        {calendar_body_html}
    </body>
    </html>
    """
    return full_html
