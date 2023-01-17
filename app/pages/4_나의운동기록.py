import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_echarts import st_echarts
from datetime import datetime
from PIL import Image
from localstorage import remove_from_local_storage, get_from_local_storage
from streamlit_extras.switch_page_button import switch_page
import time


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

# DB 에서 받아와야 할 변수들?
excercise_count = 0
calorie = 0

st.write(f"운동 일수 : {excercise_count} 일")
st.write(f"오늘의 소모 칼로리 : {calorie} kcal")


hours = [
    "첫째주",
    "둘째주",
    "셋째주",
    "넷째주",
]
days = [
    "Saturday",
    "Friday",
    "Thursday",
    "Wednesday",
    "Tuesday",
    "Monday",
    "Sunday",
]

data = [
    [0, 0, 5],
    [0, 1, 1],
    [0, 2, 0],
    [0, 3, 0],
    [1, 0, 7],
    [1, 1, 0],
    [1, 2, 0],
    [1, 3, 0],
    [2, 0, 1],
    [2, 1, 1],
    [2, 2, 0],
    [2, 3, 0],
    [3, 0, 7],
    [3, 1, 3],
    [3, 2, 0],
    [3, 3, 0],
    [4, 0, 1],
    [4, 1, 3],
    [4, 2, 0],
    [4, 3, 0],
    [5, 0, 2],
    [5, 1, 1],
    [5, 2, 0],
    [5, 3, 3],
    [6, 0, 1],
    [6, 1, 0],
    [6, 2, 0],
    [6, 3, 0],
]
data = [[d[1], d[0], d[2] if d[2] != 0 else "-"] for d in data]

option = {
    "title": {"text": "운동 일수 히트맵"},
    "tooltip": {"position": "top"},
    "grid": {"height": "50%", "top": "10%"},
    "xAxis": {"type": "category", "data": hours, "splitArea": {"show": True}},
    "yAxis": {"type": "category", "data": days, "splitArea": {"show": True}},
    "series": [
        {
            "name": "Work Day",
            "type": "heatmap",
            "data": data,
            "emphasis": {
                "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0, 0, 0, 0.5)"}
            },
        }
    ],
}
st_echarts(option, height="500px")

option = {
    "title": {"text": "운동그래프"},
    "legend": {"data": ["운동그래프"]},
    "radar": {
        "indicator": [
            {"name": "팔운동", "max": 6500},
            {"name": "다리운동", "max": 16000},
            {"name": "숨쉬기운동", "max": 30000},
            {"name": "걷기운동", "max": 38000},
            {"name": "머리운동", "max": 52000},
            {"name": "그냥운동", "max": 25000},
        ]
    },
    "series": [
        {
            "name": "운동그래프",
            "type": "radar",
            "data": [
                {
                    "value": [4200, 3000, 20000, 35000, 50000, 18000],
                    "name": "운동그래프",
                },
            ],
        }
    ],
}
st_echarts(option, height="500px")