import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page

# --- USER AUTHENTICATION(나중에 db로 연결) ---
names = ["DH", "HJ"]
usernames = ["dh", "hj"]
passwords = ["1234", "1111"]
hash_pw = stauth.Hasher(passwords).generate()
credentials = {"usernames":{}}


# --- LINK TO THE CSS FILE ---
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)


def loginPage():
    # --- Login Page
    st.title("LOGIN")

    login = st.form("login form")
    username = login.text_input("User name")
    pw = login.text_input("Password", type='password')
    submit = login.form_submit_button("submit")


def signupPage():
    # --- Signup Page
    st.title("SIGN UP")

    login = st.form("signup form")
    username = login.text_input("User name")
    pw = login.text_input("Password", type='password')
    nickname = login.text_input("Nick name")
    submit = login.form_submit_button("submit")


col1, col2 = st.columns(2)
with col1:
    st.button(
        label="Sign in",
        on_click=loginPage,
    )
with col2:
    st.button(
        label="Sign up",
        on_click=signupPage,
    )


"""
# --- LOGIN AUTHENTICATION ---
for un, name, pw in zip(usernames, names, hash_pw):
    user_dict = {"name":name,"password":pw}
    credentials["usernames"].update({un:user_dict})

authenticator = stauth.Authenticate(credentials, "ck_name", "abcd", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    authenticator.logout("Logout", "sidebar")
    switch_page("운동선택하기")  # 로그인 하면 운동 선택 페이지로 이동
"""