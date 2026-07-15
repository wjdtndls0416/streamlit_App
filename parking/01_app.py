import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(
    page_title="공영주차장 안내",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 공영주차장 안내 서비스")

# -------------------------
# CSV 읽기
# -------------------------
def load_csv(file):
    for enc in ["utf-8", "utf-8-sig", "cp949", "euc-kr"]:
        try:
            file.seek(0)
            return pd.read_csv(file, encoding=enc)
        except:
            pass
    return None

uploaded = st.file_uploader("공영주차장 CSV 업로드", type="csv")

if uploaded is None:
    st.stop()

df = load_csv(uploaded)

if df is None:
    st.error("CSV를 읽을 수 없습니다.")
    st.stop()

# -------------------------
# 컬럼명 변경
# -------------------------
rename = {
    "소재지도로명주소": "주소",
    "기본 주차 요금": "기본요금",
    "기본 주차 시간(분 단위)": "기본시간",
    "추가 단위 요금": "추가요금",
    "추가 단위 시간(분 단위)": "추가시간",
    "일 최대 요금": "일최대요금",
    "총 주차면": "주차면수",
    "전화번호": "전화번호",
    "유무료구분명": "유무료",
    "야간무료개방여부명": "야간개방"
}

df.rename(columns=rename, inplace=True)

required = ["주차장명", "주소", "위도", "경도"]

for c in required:
    if c not in df.columns:
        st.error(f"'{c}' 컬럼이 없습니다.")
        st.stop()

# 숫자형 변환
df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
df["경도"] = pd.to_numeric(df["경도"], errors="coerce")

parking_layer = pdk.Layer(
    ...
    data=map_df
)

# -------------------------
# 지역 검색
# -------------------------
st.header("📍 지역 검색")

search = st.text_input(
    "시·구·동을 입력하세요 (예 : 강남구 역삼동, 종로구 청운동)"
)

# 기본값
result = df.copy()

if search:

    result = df[
        df["주소"].astype(str).str.contains(search, case=False, na=False)
    ]

    if result.empty:

        st.warning("해당 지역의 공영주차장을 찾을 수 없습니다.")

    else:

        st.success(f"'{search}' 지역의 공영주차장 {len(result)}개를 찾았습니다.")

        st.subheader("📋 검색 결과")

        st.dataframe(
            result[
                [
                    "주차장명",
                    "주소",
                    "기본요금",
                    "기본시간",
                    "추가요금",
                    "일최대요금",
                    "주차면수",
                    "전화번호"
                ]
            ],
            use_container_width=True
        )

# -------------------------
# 지도
# -------------------------

parking_layer = pdk.Layer(
    "ScatterplotLayer",
    data=result,
    get_position="[경도, 위도]",
    get_radius=120,
    get_fill_color=[0, 120, 255, 180],
    pickable=True
)

tooltip = {
    "html": """
    <b>{주차장명}</b><br>

    주소 : {주소}<br><br>

    기본요금 : {기본요금}원<br>
    기본시간 : {기본시간}분<br>
    추가요금 : {추가요금}원<br>
    일 최대요금 : {일최대요금}원<br>
    주차면수 : {주차면수}면
    """,
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}

if len(result) > 0:

    center_lat = result["위도"].mean()
    center_lon = result["경도"].mean()

else:

    center_lat = df["위도"].mean()
    center_lon = df["경도"].mean()

st.header("🗺️ 공영주차장 위치")

st.pydeck_chart(
    pdk.Deck(
        layers=[parking_layer],
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=13
        ),
        tooltip=tooltip
    )
)

# -------------------------
# 전체 목록
# -------------------------

with st.expander("📋 전체 공영주차장 목록 보기"):

    st.dataframe(
        df[
            [
                "주차장명",
                "주소",
                "기본요금",
                "일최대요금",
                "주차면수",
                "전화번호"
            ]
        ],
        use_container_width=True
    )
