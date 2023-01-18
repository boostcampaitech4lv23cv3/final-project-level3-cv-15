import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_echarts import st_echarts
from datetime import datetime
from PIL import Image
from localstorage import remove_from_local_storage, get_from_local_storage
from streamlit_extras.switch_page_button import switch_page
import time
from backend import user_exercise_info, user_exercise_day, user_calendar_data

# --- CSS

styl = f"""
    <style>
        .css-wjbhl0.e1fqkh3o9 > li:nth-child(1){{
            display: none;
        }}
    </style>
    """
st.markdown(styl, unsafe_allow_html=True)

user_info = get_from_local_storage()  # Login 된 사용자 정보 받아오기

# --- Logout 하면 로그인 화면으로 되돌아가기 ---
st.sidebar.title(f"Welcome {user_info['nickname']}")

if st.sidebar.button("Logout"):
    remove_from_local_storage()
    time.sleep(0.5)
    switch_page("frontend")


colored_header(
    label=f"{user_info['nickname']} 님의 운동 기록",
    description=datetime.today().strftime("%Y 년 %m 월 %d 일"),
    color_name="violet-70",
)

pd_user_exercise = user_exercise_info(user_info['hashed_pw'], datetime.today().date())
excercise_count = user_exercise_day(user_info['hashed_pw']).values[0][0]
# calorie = 0

st.write(f"운동 일수 : {excercise_count} 일")
# st.write(f"오늘의 소모 칼로리 : {calorie} kcal")
st.table(pd_user_exercise)

data =  user_calendar_data(user_info['hashed_pw']).values.tolist()

option = {
  "title": {
    "top": 50,
    "left": 'center',
    "text": 'Daily Exercise Count'
  },
  "tooltip": {},
  "visualMap": {
    "min": 0,
    "max": 6,
    "type": 'piecewise',
    "orient": 'horizontal',
    "left": 'center',
    "top": 65,
    "target": {
      "inRange": {
        "color": [
          "#ffffff",
          "#8acaf2",
          "#5caaed",
        ]
      }
    },
    "show": False,
    "splitNumber": 7,
  },
  "calendar": {
    "top": 120,
    "left": 30,
    "right": 30,
    "cellSize": ['auto', 13],
    "range": '2023',
    "itemStyle": {
      "borderWidth": 0.5
    },
    "yearLabel": { "show": False }
  },
  "series": {
    "type": 'heatmap',
    "coordinateSystem": 'calendar',
    "data": data,
  },
}
st_echarts(option)