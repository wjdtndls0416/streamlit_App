import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Global Top10 Market Cap Dashboard",
    layout="wide"
)

st.title("📈 Global Market Cap TOP10 Dashboard")
st.markdown("최근 1년간 글로벌 시가총액 TOP10 기업의 주가 변화를 비교합니다.")

# 시가총액 TOP10 기업 (2025 기준)
stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Saudi Aramco": "2222.SR",
    "Broadcom": "AVGO",
    "TSMC": "TSM",
    "Tesla": "TSLA"
}

selected = st.multiselect(
    "기업 선택",
    list(stocks.keys()),
    default=list(stocks.keys())[:5]
)

start = datetime.today() - timedelta(days=365)
end = datetime.today()

@st.cache_data
def load_data(tickers):
    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )["Close"]
    return data

tickers = [stocks[x] for x in selected]

data = load_data(tickers)

# ticker -> company name 변경
rename_dict = {v: k for k, v in stocks.items()}
data.rename(columns=rename_dict, inplace=True)

# 정규화 (첫날 = 100)
normalized = data / data.iloc[0] * 100

fig = go.Figure()

for col in normalized.columns:
    fig.add_trace(
        go.Scatter(
            x=normalized.index,
            y=normalized[col],
            mode="lines",
            name=col,
            line=dict(width=3)
        )
    )

fig.update_layout(
    title="최근 1년 주가 변화 (첫날 = 100)",
    xaxis_title="Date",
    yaxis_title="Normalized Price",
    hovermode="x unified",
    template="plotly_white",
    height=700
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("📊 현재 주가 및 1년 수익률")

cols = st.columns(len(selected))

for i, company in enumerate(selected):

    ticker = stocks[company]
    hist = yf.Ticker(ticker).history(period="1y", auto_adjust=True)

    current = hist["Close"].iloc[-1]
    first = hist["Close"].iloc[0]

    returns = (current / first - 1) * 100

    cols[i].metric(
        company,
        f"${current:.2f}",
        f"{returns:.2f}%"
    )

st.divider()

st.subheader("📋 Raw Data")

st.dataframe(data.tail())
