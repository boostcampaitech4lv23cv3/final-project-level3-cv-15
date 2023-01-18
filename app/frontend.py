import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page
import requests
from backend import user_info
import time
from localstorage import set_to_local_storage

st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	page_title=None,  # String or None. Strings get appended with "• Streamlit". 
)

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
        user_check = user_info(userid)
        if len(user_check): # 기존에 DB에 존재하는 user_id인 경우
            if user_check["user_password"][0]==pw:
                user_info = {"userid" : userid, "nickname": user_check["nickname"][0], "hashed_pw": user_check["user_hash"][0]}
                set_to_local_storage(user_info) # Local Storage 에 정보 저장
                time.sleep(0.5)
                switch_page("운동선택하기") # 로그인 하면 운동 선택 페이지로 이동
            else: # 해당 id에 일치하는 비밀번호가 아닌 경우
                st.warning("Incorrect password.", icon="⚠️")
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
        
        if len(user_info(userid)): # 기존에 DB에 존재하는 user_id인 경우
            st.warning("Identical ID already exists.", icon="⚠️")
        else:
            requests.post('http://127.0.0.1:8000/users', json=new_user)