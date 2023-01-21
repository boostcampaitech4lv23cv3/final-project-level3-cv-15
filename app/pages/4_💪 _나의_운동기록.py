import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_echarts import st_echarts
from datetime import datetime, date
from PIL import Image
from localstorage import remove_from_local_storage, get_from_local_storage
from streamlit_extras.switch_page_button import switch_page
import time
from backend import user_exercise_info, user_exercise_day, user_calendar_data
import asyncio

user_info = asyncio.run(get_from_local_storage()) # Login 된 사용자 정보 받아오기

st.title(f"💪 {user_info['nickname']} 님의 운동 기록")    
st.write(
    f'<hr style="background-color: #DAE1E7; margin-top: 0;'
    ' margin-bottom: 0; height: px; border: none; border-radius: 3px;">',
    unsafe_allow_html=True,
)
st.caption(datetime.today().strftime("%Y 년 %m 월 %d 일"))


# --- CSS
style = """
        .css-wjbhl0.e1fqkh3o9 > li:nth-child(1){
            display: none;
        }
        .css-hied5v.e1fqkh3o9 > li:nth-child(1){
            display: none;
        }
        .css-k1vhr4.egzxvld3{
            background-color: #9FADC6;
        }
        .css-6qob1r.e1fqkh3o3{
            background-color: #DAE1E7;
        }
    """
st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

# --- Logout 하면 로그인 화면으로 되돌아가기 ---
st.sidebar.title(f"Welcome {user_info['nickname']}")

if st.sidebar.button("Logout"):
    remove_from_local_storage()
    time.sleep(0.3)
    switch_page("frontend")

work_date = st.date_input(  # 운동 날짜 선택하기, default : 오늘 날짜
  "운동 날짜 선택",
  date.today())

pd_user_exercise = user_exercise_info(user_info['hashed_pw'], work_date)
excercise_count = user_exercise_day(user_info['hashed_pw']).values[0][0]
# calorie = 0

st.write(f"운동 일수 : {excercise_count} 일")
# st.write(f"오늘의 소모 칼로리 : {calorie} kcal")
st.table(pd_user_exercise)

data =  user_calendar_data(user_info['hashed_pw'])

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