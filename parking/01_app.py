import streamlit as st
import pandas as pd
import pydeck as pdk

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="공영주차장 안내",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 공영주차장 정보 제공 서비스")

st.write("CSV 파일을 업로드하면 주소 검색과 지도에서 주차요금을 확인할 수 있습니다.")

# -----------------------------
# CSV 읽기 함수
# -----------------------------
def load_csv(file):

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp949",
        "euc-kr"
    ]

    for enc in encodings:
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=enc)
            return df, enc
        except:
            continue

    return None, None


uploaded_file = st.file_uploader(
    "CSV 업로드",
    type=["csv"]
)

if uploaded_file is None:
    st.info("공영주차장 CSV를 업로드하세요.")
    st.stop()

# -----------------------------
# CSV 읽기
# -----------------------------
df, encoding = load_csv(uploaded_file)

if df is None:
    st.error("CSV 파일을 읽을 수 없습니다.")
    st.stop()

st.success(f"파일을 성공적으로 읽었습니다. (인코딩 : {encoding})")

# -----------------------------
# 컬럼 확인
# -----------------------------
st.subheader("CSV 컬럼")

st.write(df.columns.tolist())

required_columns = [
    "주차장명",
    "주소",
    "위도",
    "경도",
    "기본요금",
    "추가요금"
]

missing = [c for c in required_columns if c not in df.columns]

if len(missing) > 0:

    st.error("다음 컬럼이 없습니다.")

    st.write(missing)

    st.stop()

# -----------------------------
# 데이터 미리보기
# -----------------------------
with st.expander("데이터 보기"):

    st.dataframe(df)

# -----------------------------
# 주소 검색
# -----------------------------
st.header("🔍 주소 검색")

keyword = st.text_input(
    "주소를 입력하세요."
)

if keyword:

    result = df[
        df["주소"].astype(str).str.contains(
            keyword,
            case=False,
            na=False
        )
    ]

    if len(result) == 0:

        st.warning("검색 결과가 없습니다.")

    else:

        st.success(f"{len(result)}개의 주차장을 찾았습니다.")

        for _, row in result.iterrows():

            with st.container():

                st.markdown(f"### 🚗 {row['주차장명']}")

                st.write(f"**주소** : {row['주소']}")
                st.write(f"**기본요금** : {row['기본요금']}")
                st.write(f"**추가요금** : {row['추가요금']}")

                st.divider()

# -----------------------------
# 지도
# -----------------------------
st.header("🗺️ 공영주차장 위치")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position="[경도, 위도]",
    get_radius=35,
    get_fill_color=[0, 102, 255, 180],
    pickable=True,
    auto_highlight=True
)

tooltip = {
    "html": """
<b>주차장명</b><br>
{주차장명}
<br><br>

<b>주소</b><br>
{주소}
<br><br>

<b>기본요금</b><br>
{기본요금}
<br><br>

<b>추가요금</b><br>
{추가요금}
""",
    "style": {
        "backgroundColor": "#1E3A8A",
        "color": "white",
        "fontSize": "14px"
    }
}

view_state = pdk.ViewState(
    latitude=df["위도"].mean(),
    longitude=df["경도"].mean(),
    zoom=11,
    pitch=0
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip
)

st.pydeck_chart(deck)

# -----------------------------
# 요금순 정렬
# -----------------------------
st.header("💰 전체 주차장 정보")

st.dataframe(df, use_container_width=True)
