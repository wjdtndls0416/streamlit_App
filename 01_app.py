import streamlit as st
import time

st.set_page_config(page_title="이름 궁합", page_icon="💕")

st.title("💕 이름 궁합")

name1 = st.text_input("첫 번째 이름")
name2 = st.text_input("두 번째 이름")

# -----------------------------
# 한글 자모
# -----------------------------
CHOSUNG = [
    'ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ',
    'ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
]

JUNGSUNG = [
    'ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ',
    'ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ',
    'ㅡ','ㅢ','ㅣ'
]

JONGSUNG = [
    "",
    "ㄱ","ㄲ","ㄳ","ㄴ","ㄵ","ㄶ","ㄷ","ㄹ","ㄺ",
    "ㄻ","ㄼ","ㄽ","ㄾ","ㄿ","ㅀ","ㅁ","ㅂ","ㅄ",
    "ㅅ","ㅆ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"
]

# -----------------------------
# 획수 정의
# -----------------------------
CHO_STROKES = {
    "ㄱ":2, "ㄲ":4, "ㄴ":2, "ㄷ":3, "ㄸ":6,
    "ㄹ":5, "ㅁ":4, "ㅂ":4, "ㅃ":8, "ㅅ":2,
    "ㅆ":4, "ㅇ":1, "ㅈ":3, "ㅉ":6, "ㅊ":4,
    "ㅋ":3, "ㅌ":4, "ㅍ":4, "ㅎ":3
}

JUNG_STROKES = {
    "ㅏ":2, "ㅐ":3, "ㅑ":3, "ㅒ":4,
    "ㅓ":2, "ㅔ":3, "ㅕ":3, "ㅖ":4,
    "ㅗ":2, "ㅘ":4, "ㅙ":5, "ㅚ":3,
    "ㅛ":3, "ㅜ":2, "ㅝ":4, "ㅞ":5,
    "ㅟ":3, "ㅠ":3, "ㅡ":1, "ㅢ":2, "ㅣ":1
}

JONG_STROKES = {
    "":0,
    "ㄱ":2,
    "ㄲ":4,
    "ㄳ":4,
    "ㄴ":2,
    "ㄵ":5,
    "ㄶ":5,
    "ㄷ":3,
    "ㄹ":5,
    "ㄺ":7,
    "ㄻ":9,
    "ㄼ":9,
    "ㄽ":7,
    "ㄾ":9,
    "ㄿ":9,
    "ㅀ":8,
    "ㅁ":4,
    "ㅂ":4,
    "ㅄ":6,
    "ㅅ":2,
    "ㅆ":4,
    "ㅇ":1,
    "ㅈ":3,
    "ㅊ":4,
    "ㅋ":3,
    "ㅌ":4,
    "ㅍ":4,
    "ㅎ":3
}

# -----------------------------
# 이름 획수 계산
# -----------------------------
def get_strokes(name):
    result = []

    for ch in name:
        if '가' <= ch <= '힣':
            code = ord(ch) - ord('가')

            cho = code // 588
            jung = (code % 588) // 28
            jong = code % 28

            stroke = (
                CHO_STROKES[CHOSUNG[cho]]
                + JUNG_STROKES[JUNGSUNG[jung]]
                + JONG_STROKES[JONGSUNG[jong]]
            )

            result.append(stroke)

        else:
            result.append(0)

    return result

# -----------------------------
# 궁합 계산
# -----------------------------
def make_steps(nums):

    steps = [nums]

    while len(nums) > 2:
        nums = [
            (nums[i] + nums[i+1]) % 10
            for i in range(len(nums)-1)
        ]
        steps.append(nums)

    return steps

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>

.row{
    display:flex;
    justify-content:center;
    gap:18px;
    margin:18px;
    font-size:34px;
    animation:fade .7s;
}

.name{
    color:#2f5cff;
    font-weight:bold;
}

.score{
    font-size:70px;
    color:#ff4b87;
    text-align:center;
    animation:pop .6s;
}

@keyframes fade{

from{
opacity:0;
transform:translateY(30px);
}

to{
opacity:1;
transform:translateY(0px);
}

}

@keyframes pop{

0%{
transform:scale(.3);
opacity:0;
}

100%{
transform:scale(1);
opacity:1;
}

}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# 버튼
# -----------------------------
if st.button("💕 궁합 보기"):

    if not name1 or not name2:
        st.warning("두 이름을 모두 입력해주세요.")
        st.stop()

    nums1 = get_strokes(name1)
    nums2 = get_strokes(name2)

    numbers = nums1 + nums2

    steps = make_steps(numbers)

    placeholder = st.empty()

    html = ""

    # 이름 출력
    names = ""

    for c in name1:
        names += f"<div class='name'>{c}</div>"

    names += "<div style='width:50px'></div>"

    for c in name2:
        names += f"<div class='name'>{c}</div>"

    html += f"<div class='row'>{names}</div>"

    placeholder.markdown(html, unsafe_allow_html=True)

    time.sleep(0.8)

    # 획수 출력
    nums = ""

    for n in numbers:
        nums += f"<div>{n}</div>"

    html += f"<div class='row'>{nums}</div>"

    placeholder.markdown(html, unsafe_allow_html=True)

    time.sleep(0.8)

    # 계산 과정
    for row in steps[1:]:

        nums = ""

        for n in row:
            nums += f"<div>{n}</div>"

        html += f"<div class='row'>{nums}</div>"

        placeholder.markdown(html, unsafe_allow_html=True)

        time.sleep(0.8)

    # 최종 점수
    score = steps[-1][0] * 10 + steps[-1][1]

    if score == 0:
        score = 100

    score_box = st.empty()

    for i in range(score + 1):
        score_box.markdown(
            f"<div class='score'>💕 {i}%</div>",
            unsafe_allow_html=True
        )
        time.sleep(0.02)

    st.balloons()
