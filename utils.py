import pandas as pd
import plotly.graph_objects as go

def load_binance_data(pair, interval, lookback):
    import requests
    symbol = pair.replace("/", "")
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={lookback}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close",
        "volume", "close_time", "quote_asset_volume",
        "number_of_trades", "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df.astype(float)
    return df[["open", "high", "low", "close", "volume"]]


def plot_chart_with_signals(df, signals):
    fig = go.Figure()

    # Świece (candlestick)
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlesticks'
    ))

    # Sygnały BUY/SELL
    for signal in signals:
        color = 'green' if signal['type'] == 'BUY' else 'red'
        fig.add_trace(go.Scatter(
            x=[signal["time"]],
            y=[signal["price"]],
            mode='markers+text',
            marker=dict(color=color, size=12),
            text=[signal["type"]],
            textposition="top center",
            name=signal["type"]
        ))

        # Linie TP i SL
        fig.add_trace(go.Scatter(
            x=[signal["time"], signal["time"]],
            y=[signal["tp"], signal["sl"]],
            mode='lines',
            line=dict(color='blue', width=2, dash='dash'),
            name='TP/SL'
        ))

    fig.update_layout(
        title="📈 Wykres z sygnałami i poziomami TP/SL",
        xaxis_title="Czas",
        yaxis_title="Cena (USDT)",
        xaxis_rangeslider_visible=False,
        height=700
    )

    import streamlit as st
    st.plotly_chart(fig, use_container_width=True)
