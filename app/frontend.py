import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page
import requests
from backend import get_user
import time
from localstorage import set_to_local_storage

# --- LINK TO THE CSS FILE ---
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)


col1, col2 = st.columns(2)
with col1:
    # --- Login Page
    st.title("LOGIN")

    login = st.form("login form")
    userid = login.text_input("User id")
    pw = login.text_input("Password", type='password')
    login_submit = login.form_submit_button()

    if login_submit:
        users = get_user()
        for u in users:
            if u.user_id == userid:
                if u.user_password == pw:
                    # TODO : 사용자의 암호화된 비밀번호를 다른 페이지에서도 접근가능하도록 설정
                    hashed_passwords = u.user_hash
                    user_info = {"userid" : userid, "nickname": u.nickname, "pw": hashed_passwords}
                    set_to_local_storage(user_info)  # Local Storage 에 정보 저장
                    time.sleep(0.5)
                    switch_page("운동선택하기")  # 로그인 하면 운동 선택 페이지로 이동
                else: # 해당 id에 일치하는 비밀번호가 아닌 경우
                    st.warning("Incorrect password.", icon="⚠️")
                break
        else: # 존재하지 않는 user_id인 경우
            st.warning("Please create an account first.", icon="⚠️")
            
            
with col2:
    # --- Signup Page
    st.title("SIGN UP")

    login = st.form("signup form")
    userid = login.text_input("User id")
    pw = login.text_input("Password", type='password')
    nickname = login.text_input("Nick name")
    signup_submit = login.form_submit_button()
    
    if signup_submit:
        hashed_passwords = stauth.Hasher([pw]).generate()[0]
        new_user = {"user_password": pw,
                    "user_id": userid,
                    "user_hash": hashed_passwords,
                    "nickname": nickname}
        users = get_user()
        new = True

        for u in users:
            if u.user_id == userid:
                new = False
                break
        
        if new: # 기존의 DB에 존재하지 않는 user_id인 경우
            requests.post('http://127.0.0.1:8000/users', json=new_user)
        else:
            st.warning("Identical ID already exists.", icon="⚠️")