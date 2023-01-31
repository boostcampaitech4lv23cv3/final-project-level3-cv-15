import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from localstorage import remove_from_local_storage, get_from_local_storage, set_exercise_num
import time
import asyncio

st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	page_title=None,  # String or None. Strings get appended with "• Streamlit". 
)

st.title("⛹ 운동 선택하기")
st.write(
    f'<hr style="background-color: #DAE1E7; margin-top: 0;'
    ' margin-bottom: 0; height: px; border: none; border-radius: 3px;">',
    unsafe_allow_html=True,
)


# --- CSS
style = """
        .css-wjbhl0.e1fqkh3o9 > li:nth-child(1){
            display: none;
        }
        .css-hied5v.e1fqkh3o9 > li:nth-child(1){
            display: none;
        }
        .css-6qob1r.e1fqkh3o3{
            background-color: #DAE1E7;
        }
        .css-k1vhr4.egzxvld3 > div{
            background-color: #9FADC6;
        }
        img{
            margin: auto;
            width: 200.61px;
            height: 213.57px;
            border-radius: 10px;
        }
        .css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(5) {
            margin: 0 0 2.5% 0;
        }
        .css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(1) > div > div > div {
            margin: 3.6% 0 0 0;
        }
        [data-testid="stSidebarNav"] {
                background-image: url("https://i.ibb.co/sb3bvBR/after-app-logo.png");
                background-repeat: no-repeat;
                padding-top: 150px;
                background-position: 10px 10px;
                background-size: 160px 160px;
            }
        @import url('https://fonts.cdnfonts.com/css/inter');
    """
    
# margin: 세로 가로;
def get_button_indices(button_row, button_col):
    return {
        'n_row': button_row+5,
        'n_col': button_col+1,
    }

button_style = """
            .css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(%(n_row)s) > div:nth-child(%(n_col)s) > div:nth-child(1) > div > div:nth-child(1) > div > div {
                margin: auto;
                display: flex;
                justify-content: center;
            }
            .css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(%(n_row)s) > div:nth-child(%(n_col)s) > div:nth-child(1) > div > div:nth-child(2) > div > button {
                margin: auto;
                display: flex;
                justify-content: center;
                
                height: 64px;

                background: #292C36;
                border-radius: 10px;
            }
            .css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(%(n_row)s) > div:nth-child(%(n_col)s) > div:nth-child(1) > div > div:nth-child(2) > div > button > div > p {
                width: 200px;
                height: 21.08px;

                font-family: 'Inter', sans-serif;
                font-style: normal;
                font-weight: 700;
                font-size: 20px;
                line-height: 24px;

                color: #DAE1E7;
            }
        """
for c in range(3):
    for r in range(2):
        style += button_style % get_button_indices(r, c)
        
st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

user_info = asyncio.run(get_from_local_storage()) # Login 된 사용자 정보 받아오기

# --- Logout 하면 로그인 화면으로 되돌아가기 ---
st.sidebar.title(f"Welcome {user_info['nickname']}")

if st.sidebar.button("Logout"):
    remove_from_local_storage()
    time.sleep(0.3)
    switch_page("frontend")


# --- 운동 사진 ---
col1, col2, col3 = st.columns(3)
c1, c2, c3 = st.columns(3)

with col1:
    st.video('https://www.youtube.com/watch?v=gwWv7aPcD88')
    exercise_button = st.button("사이드 런지")
    if exercise_button:
        asyncio.run(set_exercise_num(0))
        switch_page("운동 시작하기")

with col2:
    st.video('https://www.youtube.com/watch?v=0JfYxMRsUCQ')
    exercise_button = st.button("숄더 프레스")
    if exercise_button:
        asyncio.run(set_exercise_num(1))
        switch_page("운동 시작하기")

with col3:
    st.video('https://www.youtube.com/watch?v=Wp4BlxcFTkE&list=PLwvDl9NjQOojM859nq5r6UttCEYV_J8nJ&index=43')
    exercise_button = st.button("라잉 레그 레이즈")
    if exercise_button:
        asyncio.run(set_exercise_num(2))
        switch_page("운동 시작하기")

with c1:
    st.video('https://www.youtube.com/watch?v=-WEZj9ePTYI')
    exercise_button = st.button("사이드 레트럴 레이즈")
    if exercise_button:
        asyncio.run(set_exercise_num(3))
        switch_page("운동 시작하기")

with c2:
    st.video('https://www.youtube.com/watch?v=aKAb3mbp1sw')
    exercise_button = st.button("스탠딩 사이드 크런치")
    if exercise_button:
        asyncio.run(set_exercise_num(4))
        switch_page("운동 시작하기")

with c3:
    st.video('https://www.youtube.com/watch?v=_l3ySVKYVJ8')
    exercise_button = st.button("푸쉬업")
    if exercise_button:
        asyncio.run(set_exercise_num(5))
        switch_page("운동 시작하기")