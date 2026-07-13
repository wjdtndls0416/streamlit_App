import streamlit as st
import time

st.set_page_config(page_title="이름 궁합", page_icon="💕")

st.title("💕 이름 궁합")

# 예시 획수
numbers = [2, 4, 7, 6, 7, 4]

# ------------------------
# 계산 함수
# ------------------------
def make_steps(nums):
    steps = [nums]

    while len(nums) > 2:
        nums = [(nums[i] + nums[i+1]) % 10 for i in range(len(nums)-1)]
        steps.append(nums)

    return steps

steps = make_steps(numbers)

if st.button("궁합 보기"):

    placeholder = st.empty()

    html = """
    <style>

    .row{
        display:flex;
        justify-content:center;
        gap:28px;
        margin:20px 0;
        animation: fadeUp .7s;
        font-size:34px;
        font-family: Georgia;
    }

    .result{
        animation: fadeUp 1s;
        font-size:70px;
        text-align:center;
        color:#ff4d88;
        font-weight:bold;
        margin-top:40px;
    }

    @keyframes fadeUp{
        from{
            opacity:0;
            transform:translateY(30px);
        }
        to{
            opacity:1;
            transform:translateY(0px);
        }
    }

    </style>
    """

    content = html

    for row in steps:

        nums = ""

        for n in row:
            nums += f"<div>{n}</div>"

        content += f"<div class='row'>{nums}</div>"

        placeholder.markdown(content, unsafe_allow_html=True)

        time.sleep(0.8)

    # 마지막 점수 계산
    score = steps[-1][0] * 10 + steps[-1][1]

    if score == 0:
        score = 100

    # 점수 애니메이션
    score_placeholder = st.empty()

    for i in range(score + 1):
        score_placeholder.markdown(
            f"""
            <div class="result">
                💕<br>
                {i}%
            </div>
            """,
            unsafe_allow_html=True,
        )
        time.sleep(0.02)

    st.balloons()
