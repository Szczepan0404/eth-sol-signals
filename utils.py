import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import datetime

def load_binance_data(symbol, interval, limit):
    symbol = symbol.replace("/", "")
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close',
            'volume', 'close_time', 'quote_asset_volume',
            'number_of_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df.astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def plot_chart_with_signals(df, signals):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candles'
    ))

    for signal in signals:
        color = 'green' if signal['type'] == 'BUY' else 'red'
        fig.add_trace(go.Scatter(
            x=[df.index[-1]],
            y=[signal['price']],
            mode='markers',
            marker=dict(color=color, size=12),
            name=signal['type']
        ))
        fig.add_hline(y=signal['sl'], line=dict(color='orange', dash='dash'), name='Stop Loss')
        fig.add_hline(y=signal['tp'], line=dict(color='blue', dash='dash'), name='Take Profit')

    fig.update_layout(title="Chart with Signals", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)