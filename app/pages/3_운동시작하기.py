from streamlit_extras.switch_page_button import switch_page
import streamlit as st
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