from streamlit_extras.switch_page_button import switch_page
import streamlit as st
from localstorage import remove_from_local_storage, get_from_local_storage, get_exercise_num
import time
import asyncio
from streamlit_webrtc import webrtc_streamer
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av

import cv2
import mediapipe as mp
import math
import requests
from datetime import date
from backend import user_exercise_info

exercise_list = ['스탠딩 사이드 크런치', '카트라이더', '닌자머스트다이', '롤토체스', '달리기', '숨쉬기']

st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	page_title=None,  # String or None. Strings get appended with "• Streamlit". 
)

user_info = asyncio.run(get_from_local_storage()) # Login 된 사용자 정보 받아오기
ex_num = int(asyncio.run(get_exercise_num()))  # 운동 정보 가져오기

st.title(f"🎥 {exercise_list[ex_num]} 운동 시작!")
st.write(
    f'<hr style="background-color: #DAE1E7; margin-top: 0;'
    ' margin-bottom: 0; height: px; border: none; border-radius: 3px;">',
    unsafe_allow_html=True,
)
# --- CSS
style = """
        .css-wjbhl0.e1fqkh3o9 > li:nth-child(1){
            display: none;
        }
        .css-hied5v.e1fqkh3o9 > li:nth-child(1){
            display: none;
        }
        .css-6qob1r.e1fqkh3o3{
            background-color: #DAE1E7;
        }
        .css-k1vhr4.egzxvld3 > div{
            background-color: #9FADC6;
        }
        .css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(2) {
            margin: 0;
            width: 0;
            height: 0;
        }
        .css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(1) {
            margin: 0;
            width: 0;
            height: 0;
        }
    """
st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

# --- Logout 하면 로그인 화면으로 되돌아가기 ---
st.sidebar.title(f"Welcome {user_info['nickname']}")

if st.sidebar.button("Logout"):
    remove_from_local_storage()
    time.sleep(0.3)
    switch_page("frontend")



st.title("Pose Estimation with Camera")

# TODO: 실제 시작 신호 연결
exercise_start = True

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)


angle_list = (26,28,24,25,23,27)
angle_order = (((26,28),(26,24)), ((25,23),(25,27)))
temp_dict = {}
for ag in angle_list:
    temp_dict[ag] = dict()

# state 0: start
# state 1: 왼쪽 동작 한번 수행
# state 2: 오른쪽 동작 한번 수행

state = 0
right_action = False
left_action = False 
min_right = 180
min_left = 180
A_count = 0
B_count = 0
C_count = 0


def find_angles(temp_dict):
    """
        calculate and return left, right knee's angles
        input : dictionary (angle infos)
        output : two float (angles)
    """
    angle_list = []
    for angle in angle_order:
        x, y = angle    # x = (14,16), y = (14,12)
        # define two vectors
        p1x, p1y = temp_dict[x[0]]['x'], temp_dict[x[0]]['y']
        p2x, p2y = temp_dict[x[1]]['x'], temp_dict[x[1]]['y']
        p3x, p3y = temp_dict[y[0]]['x'], temp_dict[y[0]]['y']
        p4x, p4y = temp_dict[y[1]]['x'], temp_dict[y[1]]['y']

        line1 = (p1x-p2x, p1y-p2y)
        line2 = (p3x-p4x, p3y-p4y)

        # if it is not visible, return 180 degree.
        if p1x == -10 or p2x == -10 or p3x == -10 or p4x == -10:
            angle_list.append((180))
            continue

        
        numerator = line1[0]*line2[0] + line1[1]*line2[1]
        denumerator = math.sqrt(line1[0]**2 + line1[1]**2) \
                        * math.sqrt(line2[0]**2+line2[1]**2)
        
        x = math.degrees(math.acos(numerator/denumerator))
        angle_list.append(x)

    return angle_list

def process(image):
    global left_action
    global right_action
    global count
    global min_left
    global min_right
    global A_count
    global B_count
    global C_count
    global exercise_start

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  
    results = pose.process(image)
    
    
    # calculate angle
    landmark_list = results.pose_landmarks
    if landmark_list:
        for idx, landmark in enumerate(landmark_list.landmark):
            if idx not in angle_list:
                continue
            
            if float(landmark.visibility) < 0.7:
                # 안 보이면 동작 수행 안 한걸로 처리해야 한다.
                temp_dict[idx]['x'] = -10
                temp_dict[idx]['y'] = -10
                continue

            temp_dict[idx]['x'] = landmark.x
            temp_dict[idx]['y'] = landmark.y

        right_angle, left_angle = find_angles(temp_dict)

        if right_action and left_action:
            if right_angle > 160 and left_angle > 160:
                right_action = False
                left_action = False
                if min_right < 120 and min_left < 120:
                    A_count += 1
                elif min_right < 140 and min_left < 140:
                    B_count += 1
                else:
                    C_count += 1

                print("Perfect : ",A_count, "Good : ", B_count, "Miss : ", B_count)
                min_right = 180
                min_left = 180


        if right_angle < 150:
            right_action = True
            min_right = min(min_right, right_angle)
        
        elif left_angle < 150:
            left_action = True
            min_left = min(min_left, left_angle)
            
        if A_count+B_count+C_count==3: # TODO: 실제 종료 신호 연결
            exercise_start = False
            user_exercise = user_exercise_info(user_info['hashed_pw'], date.today())
            user_exercise_type = user_exercise[user_exercise["type"]==exercise_list[ex_num]]
            # 오늘 해당 운동 타입을 이미 한 적이 있다면
            if len(user_exercise_type):
                new_exercise = {
                            "user_hash": user_info['hashed_pw'],
                            "type": exercise_list[ex_num],
                            "date": date.today().strftime('%Y-%m-%d'),
                            "perfect": int(user_exercise_type["perfect"][0] + A_count),
                            "good": int(user_exercise_type["good"][0] + B_count),
                            "miss": int(user_exercise_type["miss"][0] + C_count)
                            }
            else:
                new_exercise = {
                                "user_hash": user_info['hashed_pw'],
                                "type": exercise_list[ex_num],
                                "date": date.today().strftime('%Y-%m-%d'),
                                "perfect": A_count,
                                "good": B_count,
                                "miss": C_count
                                }
            requests.post('http://127.0.0.1:8000/exercises', json=new_exercise)
    
    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

    return image



RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    
    if exercise_start:
        img = process(img)
        
    img = cv2.flip(img, 1)
    
    return av.VideoFrame.from_ndarray(img, format="bgr24")

webrtc_ctx = webrtc_streamer(
    key="pose-estimation",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    video_frame_callback=video_frame_callback,
    async_processing=True,  # or False
)