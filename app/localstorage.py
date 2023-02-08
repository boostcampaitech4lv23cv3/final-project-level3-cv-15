from streamlit_javascript import st_javascript
import asyncio

def set_to_local_storage(v):
    st_javascript(
        f"localStorage.setItem('user', JSON.stringify({v}));"
    )

def remove_from_local_storage():
    st_javascript(
        f"localStorage.removeItem('user');"
    )

async def get_from_local_storage():
    v = st_javascript(
        f"JSON.parse(localStorage.getItem('user'));"
    )
    await asyncio.sleep(0.3)
    return v

async def set_exercise_num(i):
    st_javascript(
        f"localStorage.setItem('exercise', {i});"
    )
    await asyncio.sleep(0.5)

async def get_exercise_num():
    v = st_javascript(
        f"localStorage.getItem('exercise');"
    )
    await asyncio.sleep(0.3)
    return v
