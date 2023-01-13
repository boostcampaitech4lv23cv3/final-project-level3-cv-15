import streamlit as st
from streamlit_extras.colored_header import colored_header
from datetime import datetime
from PIL import Image

# DB 에서 받아와야 할 변수들?
excercise_count = 0
calorie = 0


my_name = st.session_state['name']

colored_header(
    label=f"{my_name} 님의 오늘 운동 기록",
    description=datetime.today().strftime("%Y 년 %m 월 %d 일"),
    color_name="violet-70",
)

img = Image.open("img/2.png")
st.image(img, width=200)