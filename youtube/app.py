import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from collections import Counter
from konlpy.tag import Okt
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="유튜브 댓글 분석기", layout="wide")
st.title("📺 유튜브 댓글 분석기")
st.caption("Streamlit Cloud에서 바로 실행 가능한 간단 버전")

# -----------------------------
# 사이드바 입력
# -----------------------------
api_key = st.sidebar.text_input("YouTube API Key", type="password")
video_url = st.text_input("유튜브 영상 링크")
max_comments = st.slider("수집할 댓글 수", 50, 500, 200, 50)

# -----------------------------
# 영상 ID 추출
# -----------------------------
def get_video_id(url):
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    query = urlparse(url)
    return parse_qs(query.query).get("v", [None])[0]

# -----------------------------
# 댓글 수집
# -----------------------------
def get_comments(api_key, video_id, max_results):
    youtube = build("youtube", "v3", developerKey=api_key)

    comments = []
    next_page = None

    while len(comments) < max_results:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_results - len(comments)),
            pageToken=next_page,
            textFormat="plainText"
        )

        response = request.execute()

        for item in response["items"]:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "time": snippet["publishedAt"],
                "comment": snippet["textDisplay"]
            })

        next_page = response.get("nextPageToken")
        if not next_page:
            break

    return pd.DataFrame(comments)

# -----------------------------
# 워드클라우드 생성
# -----------------------------
def create_wordcloud(texts):
    okt = Okt()
    text = " ".join(texts)
    text = re.sub(r"[^가-힣 ]", " ", text)

    nouns = okt.nouns(text)
    nouns = [n for n in nouns if len(n) >= 2]

    counts = Counter(nouns)

    wc = WordCloud(
        font_path="NanumGothic.ttf",
        width=800,
        height=400,
        background_color="white"
    ).generate_from_frequencies(counts)

    return wc, counts

# -----------------------------
# 실행
# -----------------------------
if api_key and video_url:
    video_id = get_video_id(video_url)

    if video_id:
        st.video(video_url)

        if st.button("댓글 분석 시작"):
            with st.spinner("댓글 수집 중..."):
                try:
                    df = get_comments(api_key, video_id, max_comments)

                    if df.empty:
                        st.warning("댓글이 없습니다.")
                        st.stop()

                    st.success(f"댓글 {len(df)}개 수집 완료!")

                    # -----------------------------
                    # 시간대별 추이
                    # -----------------------------
                    st.subheader("🕒 시간대별 댓글 작성 추이")

                    df["time"] = pd.to_datetime(df["time"])
                    df["hour"] = df["time"].dt.hour

                    hourly = df.groupby("hour").size().reset_index(name="count")
                    st.line_chart(hourly.set_index("hour"))

                    # -----------------------------
                    # 워드클라우드
                    # -----------------------------
                    st.subheader("☁️ 한글 워드클라우드")

                    wc, counts = create_wordcloud(df["comment"])

                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wc, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)

                    # -----------------------------
                    # 많이 나온 단어
                    # -----------------------------
                    st.subheader("🔝 많이 나온 단어 TOP 20")

                    top_words = pd.DataFrame(counts.most_common(20), columns=["단어", "횟수"])
                    st.dataframe(top_words, use_container_width=True)

                    # -----------------------------
                    # CSV 다운로드
                    # -----------------------------
                    st.subheader("⬇️ 댓글 CSV 다운로드")

                    csv = df.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        "CSV 다운로드",
                        csv,
                        "youtube_comments.csv",
                        "text/csv"
                    )

                except Exception as e:
                    st.error(f"오류 발생: {e}")

    else:
        st.error("올바른 유튜브 링크를 입력하세요.")

else:
    st.info("API Key와 유튜브 링크를 입력하세요.")
