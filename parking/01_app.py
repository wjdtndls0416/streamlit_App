import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(
    page_title="공영주차장 안내",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 공영주차장 정보 안내")

uploaded_file = st.file_uploader(
    "CSV 파일을 업로드하세요.",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.success("데이터를 불러왔습니다.")

    st.subheader("주소 검색")

    keyword = st.text_input("주소를 입력하세요")

    if keyword:

        result = df[df["주소"].str.contains(keyword, case=False, na=False)]

        if len(result) > 0:

            st.write(f"검색 결과 : {len(result)}건")

            for _, row in result.iterrows():

                st.markdown(f"""
### 🚗 {row['주차장명']}

- 주소 : {row['주소']}
- 기본요금 : **{row['기본요금']}**
- 추가요금 : **{row['추가요금']}**
                """)

        else:
            st.warning("검색 결과가 없습니다.")

    st.subheader("공영주차장 지도")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[경도, 위도]',
        get_radius=40,
        get_fill_color=[255,0,0,180],
        pickable=True,
        auto_highlight=True
    )

    tooltip = {
        "html": """
        <b>주차장명</b> : {주차장명}<br>
        <b>주소</b> : {주소}<br>
        <b>기본요금</b> : {기본요금}<br>
        <b>추가요금</b> : {추가요금}
        """,
        "style": {
            "backgroundColor": "steelblue",
            "color": "white"
        }
    }

    view_state = pdk.ViewState(
        latitude=df["위도"].mean(),
        longitude=df["경도"].mean(),
        zoom=11
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip
    )

    st.pydeck_chart(deck)

    st.subheader("전체 데이터")

    st.dataframe(df)

else:
    st.info("CSV 파일을 업로드하세요.")
