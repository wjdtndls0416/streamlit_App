import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2

st.set_page_config(
    page_title="공영주차장 안내",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 공영주차장 요금 안내 서비스")

# -------------------------
# CSV 읽기
# -------------------------

def load_csv(file):
    for enc in ["utf-8","utf-8-sig","cp949","euc-kr"]:
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
# 컬럼명 자동 변환
# -------------------------

rename = {
    "소재지도로명주소":"주소",
    "주차기본요금":"기본요금",
    "추가단위요금":"추가요금"
}

df.rename(columns=rename, inplace=True)

required = ["주차장명","주소","위도","경도","기본요금"]

for c in required:
    if c not in df.columns:
        st.error(f"{c} 컬럼이 없습니다.")
        st.stop()

if "추가요금" not in df.columns:
    df["추가요금"]="-"

df["위도"]=pd.to_numeric(df["위도"],errors="coerce")
df["경도"]=pd.to_numeric(df["경도"],errors="coerce")

df=df.dropna(subset=["위도","경도"])

# -------------------------
# 주소 검색
# -------------------------

st.header("📍 주소 검색")

address = st.text_input("예) 서울특별시 중구 세종대로 110")

user_lat = None
user_lon = None

if address:

    geolocator = Nominatim(user_agent="parking")

    try:
        location = geolocator.geocode(address)

        if location:

            user_lat = location.latitude
            user_lon = location.longitude

        else:
            st.error("주소를 찾을 수 없습니다.")

    except:
        st.error("주소 검색 실패")

# -------------------------
# 거리 계산
# -------------------------

def distance(lat1,lon1,lat2,lon2):

    R=6371

    dlat=radians(lat2-lat1)
    dlon=radians(lon2-lon1)

    a=sin(dlat/2)**2+cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2

    c=2*atan2(sqrt(a),sqrt(1-a))

    return R*c

# -------------------------
# 가장 가까운 주차장 안내
# -------------------------

if user_lat is not None:

    df["거리"]=df.apply(
        lambda x: distance(
            user_lat,
            user_lon,
            x["위도"],
            x["경도"]
        ),
        axis=1
    )

    nearest=df.sort_values("거리").iloc[0]

    st.success("가장 가까운 공영주차장")

    st.markdown(f"""
### 🚗 {nearest['주차장명']}

**주소**

{nearest['주소']}

**기본요금**

{nearest['기본요금']}

**추가요금**

{nearest['추가요금']}

**거리**

{nearest['거리']:.2f} km
""")

# -------------------------
# 지도
# -------------------------

parking_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position="[경도, 위도]",
    get_radius=45,
    get_fill_color=[0,120,255,180],
    pickable=True
)

layers=[parking_layer]

if user_lat is not None:

    user_df=pd.DataFrame({
        "위도":[user_lat],
        "경도":[user_lon]
    })

    user_layer=pdk.Layer(
        "ScatterplotLayer",
        data=user_df,
        get_position="[경도, 위도]",
        get_radius=80,
        get_fill_color=[255,0,0,220]
    )

    layers.append(user_layer)

    center_lat=user_lat
    center_lon=user_lon

else:

    center_lat=df["위도"].mean()
    center_lon=df["경도"].mean()

tooltip={
"html":"""
<b>{주차장명}</b><br>

주소 : {주소}<br>

기본요금 : {기본요금}<br>

추가요금 : {추가요금}
""",
"style":{
"backgroundColor":"steelblue",
"color":"white"
}
}

st.pydeck_chart(
    pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=12
        ),
        tooltip=tooltip
    )
)

# -------------------------
# 전체 목록
# -------------------------

st.header("📋 공영주차장 목록")

st.dataframe(df,use_container_width=True)
