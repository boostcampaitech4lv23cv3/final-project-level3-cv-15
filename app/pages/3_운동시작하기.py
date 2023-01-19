from streamlit_extras.switch_page_button import switch_page
import streamlit as st
from localstorage import remove_from_local_storage, get_from_local_storage, get_exercise_num
import cv2
import time
import asyncio

exercise_list = ['스탠딩 사이드 크런치', '카트라이더', '닌자머스트다이', '롤토체스', '달리기', '숨쉬기']

st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	page_title=None,  # String or None. Strings get appended with "• Streamlit". 
)

# --- CSS

styl = f"""
    <style>
        .css-wjbhl0.e1fqkh3o9 > li:nth-child(1){{
            display: none;
        }}
    </style>
    """
st.markdown(styl, unsafe_allow_html=True)

user_info = get_from_local_storage()  # Login 된 사용자 정보 받아오기
ex_num = int(asyncio.run(get_exercise_num()))  # 운동 정보 가져오기

# --- 운동 종류
st.title(f"{exercise_list[ex_num]} 운동 시작!")

# --- Logout 하면 로그인 화면으로 되돌아가기 ---
st.sidebar.title(f"Welcome {user_info['nickname']}")

if st.sidebar.button("Logout"):
    remove_from_local_storage()
    time.sleep(0.5)
    switch_page("frontend")



st.title("Pose Estimation with Camera")


# --- Camera
cap = cv2.VideoCapture(0)
frameST = st.empty()

stopper_started = False
while True:
    success, frame = cap.read()
    if not success: break

    frameST.image(frame, channels="BGR")