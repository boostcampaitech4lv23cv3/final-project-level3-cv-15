import streamlit as st
import streamlit_authenticator as stauth

# --- USER AUTHENTICATION ---
names = ["DH", "HJ"]
usernames = ["dh", "hj"]
passwords = ["1234", "1111"]
hash_pw = stauth.Hasher(passwords).generate()
credentials = {"usernames":{}}


# LINK TO THE CSS FILE
with open('style.css')as f:
 st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)


for un, name, pw in zip(usernames, names, hash_pw):
    user_dict = {"name":name,"password":pw}
    credentials["usernames"].update({un:user_dict})

authenticator = stauth.Authenticate(credentials, "sales_dashboard", "abcdef", cookie_expiry_days=30)


name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    st.sidebar.header("운동 선택하기")
    st.sidebar.header("운동 시작하기")
    st.sidebar.header("나의 운동 기록")