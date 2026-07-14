"""
글로벌 시가총액 TOP 10 주가 변화 대시보드
Streamlit Cloud 배포용 앱
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="글로벌 시총 TOP10 주가 대시보드",
    page_icon="📈",
    layout="wide",
)

# 시가총액 순위는 시점에 따라 계속 바뀌므로, 대표적인 초대형주 10종목을 기본값으로 둡니다.
# 사이드바에서 사용자가 직접 종목을 수정/추가할 수 있습니다.
DEFAULT_TICKERS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "GOOGL": "Alphabet (Google)",
    "AMZN": "Amazon",
    "META": "Meta Platforms",
    "AVGO": "Broadcom",
    "TSM": "TSMC",
    "BRK-B": "Berkshire Hathaway",
    "LLY": "Eli Lilly",
}

# ----------------------------------------------------------------------------
# 데이터 로딩 함수
# ----------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def load_price_data(tickers: list[str], start: datetime, end: datetime) -> pd.DataFrame:
    """여러 종목의 종가(Close) 데이터를 한 번에 받아와 DataFrame으로 반환"""
    data = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="ticker",
    )

    # 종목이 1개일 때와 여러 개일 때 컬럼 구조가 달라서 통일 처리
    close_dict = {}
    if len(tickers) == 1:
        close_dict[tickers[0]] = data["Close"]
    else:
        for t in tickers:
            try:
                close_dict[t] = data[t]["Close"]
            except (KeyError, TypeError):
                continue

    df = pd.DataFrame(close_dict)
    df = df.dropna(how="all")
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_market_caps(tickers: list[str]) -> dict:
    """각 종목의 현재 시가총액을 받아옴 (정렬/표시용, 참고치)"""
    caps = {}
    for t in tickers:
        try:
            info = yf.Ticker(t).fast_info
            caps[t] = info.get("market_cap", None)
        except Exception:
            caps[t] = None
    return caps


def format_market_cap(value):
    if value is None:
        return "N/A"
    trillion = 1_000_000_000_000
    billion = 1_000_000_000
    if value >= trillion:
        return f"${value / trillion:.2f}T"
    return f"${value / billion:.1f}B"


# ----------------------------------------------------------------------------
# 사이드바 - 사용자 설정
# ----------------------------------------------------------------------------
st.sidebar.title("⚙️ 설정")

st.sidebar.markdown(
    "시가총액 순위는 실시간으로 변하기 때문에, 아래 종목 리스트는 "
    "대표 초대형주 기준 기본값입니다. 필요하면 자유롭게 수정하세요."
)

ticker_input = st.sidebar.text_area(
    "종목 티커 (쉼표로 구분)",
    value=", ".join(DEFAULT_TICKERS.keys()),
    height=100,
)
tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

period_option = st.sidebar.selectbox(
    "조회 기간",
    options=["최근 1년", "최근 6개월", "최근 3개월", "직접 선택"],
    index=0,
)

end_date = datetime.today()
if period_option == "최근 1년":
    start_date = end_date - timedelta(days=365)
elif period_option == "최근 6개월":
    start_date = end_date - timedelta(days=182)
elif period_option == "최근 3개월":
    start_date = end_date - timedelta(days=91)
else:
    date_range = st.sidebar.date_input(
        "기간 선택",
        value=(end_date - timedelta(days=365), end_date),
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date - timedelta(days=365)

chart_mode = st.sidebar.radio(
    "차트 표시 방식",
    options=["정규화 수익률 (%)", "실제 주가 ($)"],
    index=0,
    help="여러 종목을 비교할 때는 시작일 대비 등락률(%)로 보는 것이 직관적입니다.",
)

st.sidebar.markdown("---")
st.sidebar.caption("데이터 출처: Yahoo Finance (yfinance)")

# ----------------------------------------------------------------------------
# 메인 화면
# ----------------------------------------------------------------------------
st.title("📈 글로벌 시가총액 TOP10 주가 변화 대시보드")
st.caption(
    f"조회 기간: {start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime) else start_date} "
    f"~ {end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else end_date}"
)

if not tickers:
    st.warning("최소 1개 이상의 종목 티커를 입력해주세요.")
    st.stop()

with st.spinner("주가 데이터를 불러오는 중입니다..."):
    price_df = load_price_data(tickers, start_date, end_date)
    market_caps = load_market_caps(tickers)

if price_df.empty:
    st.error("데이터를 가져오지 못했습니다. 티커가 올바른지 확인해주세요.")
    st.stop()

valid_tickers = list(price_df.columns)
company_names = {t: DEFAULT_TICKERS.get(t, t) for t in valid_tickers}

# ----------------------------------------------------------------------------
# 상단 요약 카드
# ----------------------------------------------------------------------------
st.subheader("종목별 요약")

sorted_tickers = sorted(
    valid_tickers,
    key=lambda t: (market_caps.get(t) or 0),
    reverse=True,
)

cols = st.columns(5)
for i, t in enumerate(sorted_tickers):
    col = cols[i % 5]
    series = price_df[t].dropna()
    if len(series) < 2:
        continue
    change_pct = (series.iloc[-1] / series.iloc[0] - 1) * 100
    with col:
        st.metric(
            label=f"{company_names[t]} ({t})",
            value=f"${series.iloc[-1]:,.2f}",
            delta=f"{change_pct:+.1f}%",
        )
        st.caption(f"시총: {format_market_cap(market_caps.get(t))}")

st.markdown("---")

# ----------------------------------------------------------------------------
# Plotly 비교 차트
# ----------------------------------------------------------------------------
st.subheader("주가 변화 비교 차트")

fig = go.Figure()

for t in sorted_tickers:
    series = price_df[t].dropna()
    if series.empty:
        continue

    if chart_mode == "정규화 수익률 (%)":
        y_values = (series / series.iloc[0] - 1) * 100
        hover_suffix = "%"
    else:
        y_values = series
        hover_suffix = "$"

    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=y_values,
            mode="lines",
            name=f"{company_names[t]} ({t})",
            hovertemplate=f"%{{x|%Y-%m-%d}}<br>{company_names[t]}: %{{y:.2f}}{hover_suffix}<extra></extra>",
        )
    )

y_axis_title = "시작일 대비 수익률 (%)" if chart_mode == "정규화 수익률 (%)" else "주가 (USD)"

fig.update_layout(
    height=600,
    xaxis_title="날짜",
    yaxis_title=y_axis_title,
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=40, b=40),
    template="plotly_white",
)

if chart_mode == "정규화 수익률 (%)":
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# 개별 종목 상세 차트 (캔들스틱 옵션)
# ----------------------------------------------------------------------------
st.markdown("---")
st.subheader("개별 종목 상세 보기")

selected_ticker = st.selectbox(
    "종목 선택",
    options=sorted_tickers,
    format_func=lambda t: f"{company_names[t]} ({t})",
)

detail_series = price_df[selected_ticker].dropna()

fig_detail = go.Figure()
fig_detail.add_trace(
    go.Scatter(
        x=detail_series.index,
        y=detail_series.values,
        mode="lines",
        fill="tozeroy",
        name=selected_ticker,
        line=dict(width=2),
    )
)
fig_detail.update_layout(
    height=400,
    title=f"{company_names[selected_ticker]} ({selected_ticker}) 주가 추이",
    xaxis_title="날짜",
    yaxis_title="주가 (USD)",
    template="plotly_white",
    margin=dict(l=40, r=40, t=60, b=40),
)
st.plotly_chart(fig_detail, use_container_width=True)

# ----------------------------------------------------------------------------
# 원본 데이터 테이블
# ----------------------------------------------------------------------------
with st.expander("📋 원본 데이터 보기"):
    st.dataframe(price_df.sort_index(ascending=False), use_container_width=True)

    csv = price_df.to_csv().encode("utf-8")
    st.download_button(
        label="CSV로 다운로드",
        data=csv,
        file_name="stock_prices.csv",
        mime="text/csv",
    )

st.caption(
    "⚠️ 본 대시보드는 정보 제공 목적이며 투자 조언이 아닙니다. "
    "시가총액 순위는 시점에 따라 변동될 수 있습니다."
)
