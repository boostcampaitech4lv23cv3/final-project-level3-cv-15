from streamlit_extras.switch_page_button import switch_page
import streamlit as st
from localstorage import remove_from_local_storage, get_from_local_storage, get_exercise_num
import time
import asyncio
from streamlit_webrtc import webrtc_streamer
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av

exercise_list = ['스탠딩 사이드 크런치', '카트라이더', '닌자머스트다이', '롤토체스', '달리기', '숨쉬기']

st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	page_title=None,  # String or None. Strings get appended with "• Streamlit". 
)

# --- CSS

styl = f"""
    <style>
        .css-wjbhl0.e1fqkh3o9 > li:nth-child(1){{
            display: none;
        }}
        .css-hied5v.e1fqkh3o9 > li:nth-child(1){{
            display: none;
        }}
    </style>
    """
st.markdown(styl, unsafe_allow_html=True)

user_info = asyncio.run(get_from_local_storage())  # Login 된 사용자 정보 받아오기
ex_num = int(asyncio.run(get_exercise_num()))  # 운동 정보 가져오기

# --- 운동 종류
st.title(f"{exercise_list[ex_num]} 운동 시작!")

# --- Logout 하면 로그인 화면으로 되돌아가기 ---
st.sidebar.title(f"Welcome {user_info['nickname']}")

if st.sidebar.button("Logout"):
    remove_from_local_storage()
    time.sleep(0.3)
    switch_page("frontend")



st.title("Pose Estimation with Camera")

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class VideoProcessor:
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        return av.VideoFrame.from_ndarray(img, format="bgr24")
    
webrtc_ctx = webrtc_streamer(
    key="pose-estimation",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    video_processor_factory=VideoProcessor,
    async_processing=True,
)

######################################################
st.markdown("My Video")

stframe = st.empty()

import cv2
import numpy as np
import av
import mediapipe as mp
from streamlit_webrtc import (
    webrtc_streamer, WebRtcMode, RTCConfiguration, VideoProcessorBase
)
import time

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

# prevtime = 0
# fps = 0


def process(image):
    global perfect_cnt, good_cnt, miss_cnt, left_check, right_check, leftbody_list, lefthand_list, rightbody_list, righthand_list
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    
    #######################################################
    
    try:
        # 몸 좌표값 얻기
        landmarks = get_pos(image, results)

        left_list = []
        right_list = []

        # left body
        lefthip = landmarks[23][1:]
        leftknee = landmarks[25][1:]
        leftankle = landmarks[27][1:]
        left_list += lefthip
        left_list += leftknee
        left_list += leftankle

        # right body
        righthip = landmarks[24][1:]
        rightknee = landmarks[26][1:]
        rightankle = landmarks[28][1:]
        right_list += righthip
        right_list += rightknee
        right_list += rightankle

        # left elbow
        leftwrist = landmarks[15][1:]
        leftelbow = landmarks[13][1:]
        leftshoulder = landmarks[11][1:]
        left_list += leftshoulder
        left_list += leftwrist
        left_list += leftelbow
        
        # right elbow
        rightwrist = landmarks[16][1:]
        rightelbow = landmarks[14][1:]
        rightshoulder = landmarks[12][1:]
        right_list += rightshoulder
        right_list += rightwrist
        right_list += rightelbow
        

        leftbody = get_angle(leftknee, lefthip, leftankle)
        rightbody = get_angle(rightknee, righthip, rightankle)
        # lefthand = get_angle(leftshoulder, leftwrist, leftelbow)
        # righthand = get_angle(rightshoulder, rightwrist, rightelbow)
        
        left_list = normalization(left_list)
        right_list = normalization(right_list)    

        # print(leftbody, rightbody)
        # print(lefthand, righthand)
        # print(abs(leftelbow - leftknee))
        
        lefthand =  abs(leftelbow[0] - leftknee[0]) + abs(leftelbow[1] - leftknee[1])
        righthand =  abs(rightelbow[0] - rightknee[0]) + abs(rightelbow[1] - rightknee[1])

        # print("-------------------------------")
        # print(weightedDistanceMatching(right_answer, right_list))
        # print("-------------------------------")
        # if leftbody <= 70 and rightbody >= 150 and lefthand <= 100:
        
        if leftbody <= 100 and rightbody >= 160 and lefthand <= 120:
            leftbody_list.append(leftbody)
            lefthand_list.append(lefthand)
            left_check = True
        
        # if leftbody >= 150 and rightbody <= 70 and righthand <= 100:
        if leftbody >= 160 and rightbody <= 100 and righthand <= 120:
            rightbody_list.append(rightbody)
            righthand_list.append(righthand)
            right_check = True
            
            if left_check and right_check:
                max_left = max(leftbody_list)
                max_right = max(rightbody_list)
                min_lhand = min(lefthand_list)
                min_rhand = min(righthand_list)

                score = max_left + max_right + min_lhand + min_rhand
                left_check = False
                right_check = False

                leftbody_list = []
                lefthand_list = []
                rightbody_list = []
                righthand_list = []

                if score <= 230:
                    perfect_cnt += 1
                    # print(perfect_cnt, good_cnt, miss_cnt)
                elif score <= 260:
                    good_cnt += 1
                    # print(perfect_cnt, good_cnt, miss_cnt)
                else:
                    miss_cnt += 1
                    # print(perfect_cnt, good_cnt, miss_cnt)
    except:
        pass

    #########################################################

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

    # currTime = time.time()

    # fps = 1 / (currTime - prevtime)
    # prevtime = currTime

    return cv2.flip(image, 1)

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.frame_cnt = 0
        self.response = 0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = process(img)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

left_check = False
right_check = False
leftbody_list = []
lefthand_list = []
rightbody_list = []
righthand_list = []

def get_pos(image, result):
    mark_list = []
    for idx, value in enumerate(result.pose_landmarks.landmark):
        h, w, c = image.shape
        cx, cy = int(value.x * w), int(value.y * h)
        mark_list.append([idx, cx, cy])
    return mark_list

import numpy as np
def get_angle(p1 : list, p2 : list ,p3 : list) -> float:
    rad = np.arctan2(p3[1] - p1[1], p3[0] - p1[0]) - np.arctan2(p2[1] - p1[1], p2[0] - p1[0])
    deg = rad * (180 / np.pi)
    if abs(deg) > 180:
        deg = 360-abs(deg)
    return abs(deg)

def normalization(x):
    min_value = min(x)
    max_value = max(x) 

    return list(map(lambda x: (x-min_value)/(max_value-min_value), x))

def weightedDistanceMatching(poseVector1, poseVector2):
    # test coordinate
    vector1PoseXY = poseVector1

    vector1ConfidenceSum = len(poseVector1)
    
    # train coordinate
    vector2PoseXY = poseVector2

    summation1 = 1 / vector1ConfidenceSum
    summation2 = 0
    
    count = 0
    for i in range(len(vector1PoseXY)):
        count += 1
        # multiplying each joint's reliability and distance
        tempSum = abs(vector1PoseXY[i] - vector2PoseXY[i])
        # Add joint distance by joint count
        summation2 = summation2 + tempSum
    
    # WeightedDistance
    summation = summation1 * summation2
    
    return summation

perfect_cnt = 0
good_cnt = 0
miss_cnt = 0


webrtc_ctx = webrtc_streamer(
    key="WYH",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": {"frameRate": {"ideal": 30}}, "audio": False},
    video_processor_factory=VideoProcessor,
    async_processing=True,
)

ltitle, ptitle, gtitle, mtitle = st.columns(4)

with ltitle:
    st.markdown("**Frame Rate**")
    kpi1_text = st.markdown("0")

with ptitle:
    st.markdown("**Perfect Count**")
    kpi2_text = st.markdown("0")

with gtitle:
    st.markdown("**Good Count**")
    kpi3_text = st.markdown("0")

with mtitle:
    st.markdown("**Miss Count**")
    kpi4_text = st.markdown("0")

st.markdown("<hr/>", unsafe_allow_html=True)

# kpi1_text.write(f"<h1 style='text-align: left; color: red;'>{int(fps)}</h1>", unsafe_allow_html=True)
# kpi2_text.write(f"<h1 style='text-align: left; color: red;'>{perfect_cnt}</h1>", unsafe_allow_html=True)
# kpi3_text.write(f"<h1 style='text-align: left; color: red;'>{good_cnt}</h1>", unsafe_allow_html=True)
# kpi4_text.write(f"<h1 style='text-align: left; color: red;'>{miss_cnt}</h1>", unsafe_allow_html=True)