from streamlit_javascript import st_javascript

def set_to_local_storage(v):
    st_javascript(
        f"localStorage.setItem('user', JSON.stringify({v}));"
    )

def remove_from_local_storage():
    st_javascript(
        f"localStorage.removeItem('user');"
    )

def get_from_local_storage():
    v = st_javascript(
        f"JSON.parse(localStorage.getItem('user'));"
    )
    return v