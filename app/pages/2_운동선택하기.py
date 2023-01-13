import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import extra_streamlit_components as stx

# --- Logout 하면 로그인 화면으로 되돌아가기 ---
st.sidebar.title(f"Welcome {st.session_state['name']}")
cookie_manager = stx.CookieManager()

if st.session_state['authentication_status']:
    if st.sidebar.button("Logout"):
        cookie_manager.delete("ck_name")
        st.session_state['logout'] = True
        st.session_state['name'] = None
        st.session_state['username'] = None
        st.session_state['authentication_status'] = None
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