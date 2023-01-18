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

def set_exercise_num(i):
    st_javascript(
        f"localStorage.setItem('exercise', {i});"
    )

def get_exercise_num():
    v = st_javascript(
        f"localStorage.getItem('exercise');"
    )
    return v
