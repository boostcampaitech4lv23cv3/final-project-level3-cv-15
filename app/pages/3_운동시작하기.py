from streamlit_extras.switch_page_button import switch_page
import streamlit as st
from localstorage import remove_from_local_storage, get_from_local_storage
import cv2
import time

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

# --- 운동 종류
#st.title(f"Excercise Num : {}")

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