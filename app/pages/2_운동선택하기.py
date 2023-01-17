import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from localstorage import remove_from_local_storage, get_from_local_storage
import time


user_info = get_from_local_storage()  # Login 된 사용자 정보 받아오기

# --- Logout 하면 로그인 화면으로 되돌아가기 ---
st.sidebar.title(f"Welcome {user_info['nickname']}")

if st.sidebar.button("Logout"):
    remove_from_local_storage()
    time.sleep(0.5)
    switch_page("frontend")


# --- 운동 사진 ---
col1, col2, col3 = st.columns(3)
c1, c2, c3 = st.columns(3)

with col1:
    st.header("스탠딩 사이드 크런치")
    st.image("img/1.jpg")
    exercise_button = st.button("운동 시작하기1")
    if exercise_button:
        st.session_state.num = 0
        switch_page("운동시작하기")

with col2:
    st.header("스탠딩 사이드 크런치")
    st.image("img/1.jpg")
    exercise_button = st.button("운동 시작하기2")
    if exercise_button:
        st.session_state.num = 1
        switch_page("운동시작하기")

with col3:
    st.header("스탠딩 사이드 크런치")
    st.image("img/1.jpg")
    exercise_button = st.button("운동 시작하기3")
    if exercise_button:
        st.session_state.num = 2
        switch_page("운동시작하기")

with c1:
    st.header("스탠딩 사이드 크런치")
    st.image("img/1.jpg")
    exercise_button = st.button("운동 시작하기4")
    if exercise_button:
        st.session_state.num = 3
        switch_page("운동시작하기")

with c2:
    st.header("스탠딩 사이드 크런치")
    st.image("img/1.jpg")
    exercise_button = st.button("운동 시작하기5")
    if exercise_button:
        st.session_state.num = 4
        switch_page("운동시작하기")

with c3:
    st.header("스탠딩 사이드 크런치")
    st.image("img/1.jpg")
    exercise_button = st.button("운동 시작하기6")
    if exercise_button:
        st.session_state.num = 5
        switch_page("운동시작하기")