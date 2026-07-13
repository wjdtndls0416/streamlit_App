import streamlit as st
import time

st.set_page_config(page_title="이름 궁합", page_icon="💕")

st.title("💕 이름 궁합")

name1 = st.text_input("첫 번째 이름")
name2 = st.text_input("두 번째 이름")


# -----------------------------
# 예시 획수 함수
# (여기를 실제 획수 계산 함수로 교체)
# -----------------------------
stroke_dict = {
    "김":7,
    "이":2,
    "박":7,
    "최":11,
    "정":8,
    "홍":9,
    "길":4,
    "동":5,
    "철":9,
    "수":4
}

def get_strokes(name):
    return [stroke_dict.get(ch, 5) for ch in name]


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

    # 결과
    score = steps[-1][0]*10 + steps[-1][1]

    if score == 0:
        score = 100

    score_box = st.empty()

    for i in range(score+1):

        score_box.markdown(
            f"<div class='score'>💕 {i}%</div>",
            unsafe_allow_html=True
        )

        time.sleep(0.02)

    st.balloons()
