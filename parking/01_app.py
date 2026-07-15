import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(
    page_title="공영주차장 안내 서비스",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 공영주차장 안내 서비스")

# ----------------------------
# CSV 읽기
# ----------------------------
def load_csv(file):
    for enc in ["utf-8", "utf-8-sig", "cp949", "euc-kr"]:
        try:
            file.seek(0)
            return pd.read_csv(file, encoding=enc)
        except:
            pass
    return None

uploaded = st.file_uploader(
    "공영주차장 CSV 업로드",
    type="csv"
)

if uploaded is None:
    st.stop()

df = load_csv(uploaded)

if df is None:
    st.error("CSV를 읽을 수 없습니다.")
    st.stop()

# ----------------------------
# 필수 컬럼 확인
# ----------------------------
required = [
    "주차장명",
    "주소",
    "위도",
    "경도",
    "기본 주차 요금",
    "추가 단위 요금",
    "일 최대 요금"
]

for col in required:
    if col not in df.columns:
        st.error(f"'{col}' 컬럼이 없습니다.")
        st.stop()

# 위도, 경도 숫자형 변환
df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
df["경도"] = pd.to_numeric(df["경도"], errors="coerce")

# ----------------------------
# 검색
# ----------------------------
st.header("📍 지역 검색")

search = st.text_input(
    "구 또는 동을 입력하세요 (예 : 성동구, 마장동, 성동구 마장동)"
)

# 검색 결과 기본값
result = df.copy()

if search:

    keywords = search.split()

    result = df.copy()

    for word in keywords:
        result = result[
            result["주소"].astype(str).str.contains(
                word,
                case=False,
                na=False
            )
        ]

if result.empty:

    st.warning("검색 결과가 없습니다.")

else:

    st.success(f"{len(result)}개의 공영주차장을 찾았습니다.")

    st.dataframe(
        result[
            [
                "주차장명",
                "주소",
                "기본 주차 요금",
                "기본 주차 시간(분 단위)",
                "추가 단위 요금",
                "일 최대 요금",
                "총 주차면",
                "전화번호"
            ]
        ],
        use_container_width=True
    )

# ----------------------------
# 지도
# ----------------------------

map_df = result.dropna(subset=["위도", "경도"])

st.header("🗺️ 공영주차장 위치")

if len(map_df) > 0:

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[경도, 위도]",
        get_radius=120,
        get_fill_color=[0, 120, 255, 180],
        pickable=True
    )

    tooltip = {
        "html": """
        <b>{주차장명}</b><br>

        주소 : {주소}<br><br>

        기본요금 : {기본 주차 요금}원<br>
        기본시간 : {기본 주차 시간(분 단위)}분<br>
        추가요금 : {추가 단위 요금}원<br>
        일 최대요금 : {일 최대 요금}원<br>
        총 주차면 : {총 주차면}면
        """,
        "style": {
            "backgroundColor": "steelblue",
            "color": "white"
        }
    }

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=pdk.ViewState(
                latitude=map_df["위도"].mean(),
                longitude=map_df["경도"].mean(),
                zoom=13
            ),
            tooltip=tooltip
        )
    )

else:

    st.info("지도에 표시할 좌표 정보가 없습니다.")

# ----------------------------
# 전체 목록
# ----------------------------

with st.expander("📋 전체 공영주차장 목록"):

    st.dataframe(
        df[
            [
                "주차장명",
                "주소",
                "기본 주차 요금",
                "일 최대 요금",
                "총 주차면",
                "전화번호"
            ]
        ],
        use_container_width=True
    )
