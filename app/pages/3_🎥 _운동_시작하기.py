from streamlit_extras.switch_page_button import switch_page
import streamlit as st
from localstorage import remove_from_local_storage, get_from_local_storage, get_exercise_num
import time
import asyncio
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av

import cv2
import mediapipe as mp
import math
import requests
from datetime import date
from backend import user_exercise_info

exercise_list = ['사이드 런지', '숄더 프레스', '라잉 레그 레이즈', '사이드 레트럴 레이즈', '스탠딩 사이드 크런치', '푸쉬업']

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
        [data-testid="stSidebarNav"] {
                background-image: url("https://i.ibb.co/sb3bvBR/after-app-logo.png");
                background-repeat: no-repeat;
                padding-top: 150px;
                background-position: 10px 10px;
                background-size: 160px 160px;
            }
    """
st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

# --- Logout 하면 로그인 화면으로 되돌아가기 ---
st.sidebar.title(f"Welcome {user_info['nickname']}")

if st.sidebar.button("Logout"):
    remove_from_local_storage()
    time.sleep(0.3)
    switch_page("frontend")


if ex_num == 2:
    st.title("카메라가 측면을 향하게 해주세요.")
else:
    st.title("카메라가 정면을 향하게 해주세요.")

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)


# # # # # # # # # # # # # # # # # # implemented code # # # # # # # # # # # # # # # # # #


# initialize
temp_dict = {}
for i in range(35):
    temp_dict[i] = dict()
    # temp_dict[33], temp_dict[34] = 지면과 각도 구하기위한 벡터

for i in range(33):
    temp_dict[i]['x'] = -10
    temp_dict[i]['y'] = -10
    temp_dict[i]['z'] = 10

temp_dict[33]['x'] = 1
temp_dict[33]['y'] = 0
temp_dict[34]['x'] = 2
temp_dict[34]['y'] = 0



right_action = False
left_action = False 
min_right = 180
min_left = 180
min_right2 = 180
min_left2 = 180
A_count = 0
B_count = 0
C_count = 0
state = 0
count = 0
sequence = 0

message_length = 0
A_pre = 0
B_pre = 0
C_pre = 0

# 각각 운동에서 사용할 global 변수들 초기화
if ex_num == 0:
    min_right = 180
    min_left = 180

elif ex_num == 1:
    min_right = 125
    min_right2 = 125
    min_left = 125
    min_left2 = 125

elif ex_num == 2:
    min_right = 180
    min_right2 = 0
    count = 0

elif ex_num == 3:
    min_right = 75
    min_left = 75
    min_right2 = 0
    count = 0

# stand side crunch
elif ex_num == 4:
    min_left = 180
    min_right = 180
    min_ldistance = 999
    min_rdistance = 999  

# pushup
elif ex_num == 5:
    min_left = 180
    min_right = 180


def find_angles(angle_order, num, default_angles):
    """
        calculate necessary angles
        input : set : set of angles
                int : num of angles, 
                list : default_angles

        output :  float (angles) 0~180
    """

    # print("num :", num)
    # print("len : ", len(angle_order))
    assert num == len(angle_order)

    angle_list = []
    for i, angle in enumerate(angle_order):
        x, y = angle
        # define two vectors for the angle
        p1x, p1y = temp_dict[x[0]]['x'], temp_dict[x[0]]['y']
        p2x, p2y = temp_dict[x[1]]['x'], temp_dict[x[1]]['y']
        p3x, p3y = temp_dict[y[0]]['x'], temp_dict[y[0]]['y']
        p4x, p4y = temp_dict[y[1]]['x'], temp_dict[y[1]]['y']

        line1 = (p1x-p2x, p1y-p2y)
        line2 = (p3x-p4x, p3y-p4y)

        # if it is not visible, return 180 degree.
        if p1x == -10 or p2x == -10 or p3x == -10 or p4x == -10:
            angle_list.append((default_angles[i]))
            continue

        
        numerator = line1[0]*line2[0] + line1[1]*line2[1]
        denumerator = math.sqrt(line1[0]**2 + line1[1]**2) \
                        * math.sqrt(line2[0]**2+line2[1]**2)
        
        x = math.degrees(math.acos(numerator/denumerator))
        angle_list.append(x)

    return angle_list

def print_score():
    """
        print Perfect/ Good/ Miss scores
    """

    global A_count
    global B_count
    global C_count
    print("Perfect : ", A_count, "Good : ", B_count, "Miss : ", C_count)

def side_lunge():
    """
        Exercise for side lunge process is defined
    """
    global A_count
    global B_count
    global C_count
    global left_action
    global right_action
    global min_right
    global min_left

    point_used = (26,28,24,25,23,27)
    for point in point_used:
        if temp_dict[point]['x'] == -10:
            return

    angle_order = (((26,28),(26,24)), ((25,23),(25,27)))

    right_angle, left_angle = find_angles(angle_order, 2, default_angles=[180,180])

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

            print_score()            
            min_right = 180
            min_left = 180


    if right_angle < 150:
        right_action = True
        min_right = min(min_right, right_angle)
    
    elif left_angle < 150:
        left_action = True
        min_left = min(min_left, left_angle)



def shoulder_press():
    """
        Exercise for side shoulder press is defined
    """
    global A_count
    global B_count
    global C_count
    global state
    global min_right
    global min_left
    global min_right2
    global min_left2
    
    st = 10 # st : start_threshold


    point_used = (14,16,12,11,13,15)
    for point in point_used:
        if temp_dict[point]['x'] == -10:
            return
    
    angle_order = (((14,16),(14,12)), ((12,14),(12,11)), ((13,15),(13,11)),((11,12),(11,13)))
    right_elbow, right_shoulder, left_elbow, left_shoulder = find_angles(angle_order, 4, default_angles=[180,270,180,270])

    # state 0 : 시작자세
    # state 1 : 준비자세
    # state 2 : 동작
    
    if state == 0 and 90-st < right_elbow < 90+st and 90-st < left_elbow < 90+st \
        and 180-st < right_shoulder < 180+st and 180-st < left_shoulder < 180+st:
        state = 1   
    
    if state == 1:
        if 150 < right_elbow and 150 < left_elbow:
            state = 2
    
    if state == 2:
        min_right = max(min_right, right_elbow)
        min_right2 = min(min_right2, right_shoulder)
        min_left = max(min_left, left_elbow)
        min_left2 = min(min_left2, left_shoulder)

        if right_elbow < 100 and left_elbow < 100:
            # count and calculate
            if min_right > 170 and min_left > 170 \
                and min_right2 < 95 and min_left2 < 95:
                A_count += 1

            elif min_right > 160 and min_left > 160 \
                and min_right2 < 100 and min_left2 < 100:
                B_count += 1
            
            else:
                C_count += 1
            
            print_score()
            state = 0
            min_right = 125
            min_right2 = 125
            min_left = 125
            min_left2 = 125


def lying_leg_raise():
    """
        Exercise for lying leg raise process is defined
    """
    global A_count
    global B_count
    global C_count
    global state
    global min_right
    global min_right2   # 더 많으면
    global count

    # print("카메라에 몸의 왼쪽이나 오른쪽이 보이게 누워주세요")
    point_used = (12,24,26,28)
    for point in point_used:
        if temp_dict[point]['x'] == -10:
            return

    angle_order = (((33,34),(12,24)),((24,12),(24,26)),((26,24),(26,28)))  # 33, 34는 지면과 벡터
    angle_x_axis, angle_hip, angle_knee = find_angles(angle_order, 3, default_angles=[180, 180, 75])
    # state 0 : 시작자세
    # state 1 : 오른쪽 기준으로

    if state == 0 and angle_x_axis > 150 and angle_hip > 150\
        and angle_knee > 120:
        state = 1
    
    if state == 1:
        if angle_hip < 120:
            state = 2
    
    if state == 2:
        min_right = min(min_right, angle_hip)
        if angle_knee > 140:
            min_right2 += 2
        elif angle_knee > 120:
            min_right2 += 1
        count += 1

        if angle_hip > 160:
            mean_knee = min_right2/count
            if min_right > 80 and mean_knee > 1.0:
                A_count += 1
            elif min_right > 65 and mean_knee > 0.8:
                B_count += 1
            else:
                C_count += 1
            
            print_score()
            state = 0
            min_right2 = 0
            min_right = 180
            count = 0
    
def side_lateral_raise():
    """
        Exercise for side lateral raise process is defined
    """
    global A_count
    global B_count
    global C_count
    global state
    global min_right
    global min_right2   # 더 많으면 1
    global min_left
    global min_left2
    global count

    point_used = (12,14,11,16,13,15)
    for point in point_used:
        if temp_dict[point]['x'] == -10:
            return

    angle_order = (((12,14),(12,11)),((14,12),(14,16)),((11,13),(11,12)),((13,11),(13,15)))
    right_shoulder, right_elbow, left_shoulder, left_elbow = find_angles(angle_order, 4, [75, 90, 90, 75])

    if state == 0 and right_elbow > 75 and left_elbow > 75 \
        and right_shoulder > 80 and left_shoulder > 80:
        state = 1
    
    if state == 1:
        if right_shoulder > 120 and left_shoulder > 120:
            state = 2
    
    if state == 2:
        min_right = max(min_right, right_shoulder)
        min_left = max(min_left, left_shoulder)
        if right_elbow > 85 and left_elbow > 85:
            min_right2 += 2
        elif right_elbow > 80 and left_elbow > 80:
            min_right2 += 1
        else:
            min_right2 += 1
        
        count += 1
        mean_score = min_right2/count 

        if right_shoulder < 100 and left_shoulder < 100:
            if min_right > 170 and min_left > 170 \
                and mean_score > 1.8:
                A_count += 1

            elif min_right > 165 or min_right > 165 \
                or mean_score < 1.5:
                B_count += 1
            
            else:
                C_count += 1
            
            print_score()
            state = 0
            min_right2 = 0
            count = 0
            min_right = 75
            min_left = 75

def get_pos(image, landmark_list):
    mark_list = []
    for idx, value in enumerate(landmark_list.landmark):
        h, w, c = image.shape
        cx, cy = int(value.x * w), int(value.y * h)
        mark_list.append([idx, cx, cy])
    return mark_list

def stand_side_crunch(image, landmark_list):
    global A_count
    global B_count
    global C_count
    global min_left
    global min_right
    global min_ldistance
    global min_rdistance
    global left_action
    global right_action

    image_landmark = get_pos(image, landmark_list)

    # angle_list = (26, 28, 24, 25, 23, 27)
    # hand_list = (14, 16, 12, 13, 15, 11)

    point_used = (26,28,24,25,23,27)
    for point in point_used:
        if temp_dict[point]['x'] == -10:
            return

    angle_order = (((26, 28), (26, 24)), ((25, 23), (25, 27)))
    # hand_order = (((14, 16), (14, 12)), ((13, 15), (13, 11)))

    right_angle, left_angle = find_angles(angle_order, 2, default_angles=[180,180])

    try:
        image_landmark = get_pos(image, landmark_list)
        left_distance = abs(image_landmark[13][1:][0] - image_landmark[25][1:][0]) + abs(image_landmark[13][1:][1] - image_landmark[25][1:][1])
        right_distance = abs(image_landmark[14][1:][0] - image_landmark[26][1:][0]) + abs(image_landmark[14][1:][1] - image_landmark[26][1:][1])
    except:
        pass

    if left_action and right_action:
        if right_angle > 160 and left_angle > 160:
            right_action = False
            left_action = False
            score = min_left + min_right + min_rdistance + min_ldistance
            # print(min_left, min_right, min_rdistance, min_ldistance)
            if score <= 200:
                A_count += 1
            elif score <= 230:
                B_count += 1
            else:
                C_count += 1

            print_score()
            min_right = 180
            min_left = 180
            min_ldistance = 999
            min_rdistance = 999
            
    if right_angle < 100 and left_angle > 160 and right_distance <= 120:
        right_action = True
        min_right = min(min_right, right_angle)
        min_rdistance = min(min_rdistance, right_distance)
    
    elif left_angle < 100 and right_angle > 160 and left_distance <= 120:
        left_action = True
        min_left = min(min_left, left_angle)
        min_ldistance = min(min_ldistance, left_distance)


def push_up():
    global A_count
    global B_count
    global C_count
    global left_action
    global right_action
    global min_right
    global min_left

    point_used = (14,16,12,11,13,15)
    for point in point_used:
        if temp_dict[point]['x'] == -10:
            return
            
    angle_order = (((14, 16), (14, 12)), ((13, 15), (13, 11)))

    right_angle, left_angle = find_angles(angle_order, 2, default_angles=[180,180])

    if right_action and left_action:
        if right_angle > 150 and left_angle > 150:
            right_action = False
            left_action = False
            # score = min_left + min_right + min_rdistance + min_ldistance
            # print(min_left, min_right, min_rdistance, min_ldistance)
            if min_left <= 80:
                A_count += 1
            elif min_left <= 100:
                B_count += 1
            else:
                C_count += 1

            print_score()
            min_right = 180
            min_left = 180
    
    if left_angle < 120 and right_angle < 120:
        left_action = True
        right_action = True
        min_left = min(min_left, left_angle)

def check_state():
    """
        if check state -> increase sequence
        sequence 0 : not count yet (운동 시작 전)
        sequence 1 : count exercise (운동 중)
        sequence 2 : finished the exercise (운동 끝, 디비에 보낸다.)
    """

    threshold = 0.02

    nose_loc = temp_dict[0]
    right_wrist = temp_dict[15]
    left_wrist = temp_dict[16]
    
    if right_wrist['x'] == -10 or right_wrist['y'] == -10 \
        or left_wrist['x'] == -10 or left_wrist['y'] == -10:

        return False
    
    if nose_loc['z'] <= right_wrist['z'] or nose_loc['z'] <= left_wrist['z']:
        return False

    if ((right_wrist['x'] - left_wrist['x'])**2 \
        + (right_wrist['y'] - left_wrist['y'])**2) < threshold \
            and ((nose_loc['x'] - left_wrist['x'])**2 \
            + (nose_loc['y'] - left_wrist['y'])**2) < threshold \
                :
            return True
    
    return False



def process(image):
    global A_count
    global B_count
    global C_count
    global sequence

    image.flags.writeable = False
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  
    results = pose.process(image)
    
    
    # calculate angle
    landmark_list = results.pose_landmarks
    if landmark_list:
        for idx, landmark in enumerate(landmark_list.landmark):
            if float(landmark.visibility) < 0.7:
                # 안 보이면 동작 수행 안 한걸로 처리해야 한다.
                temp_dict[idx]['x'] = -10
                temp_dict[idx]['y'] = -10
                temp_dict[idx]['z'] = 10
                continue

            temp_dict[idx]['x'] = landmark.x
            temp_dict[idx]['y'] = landmark.y
            temp_dict[idx]['z'] = landmark.z
    

    if sequence == 0:       # 운동시작 전
        if check_state():
            sequence += 1
            # 운동 시작을 알려주는 표시를 해야한다.
            print("운동이 시작되었습니다.")
            time.sleep(1)

        return cv2.flip(image, 1)

    elif sequence == 1:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


        if ex_num == 0: side_lunge()
        elif ex_num == 1: shoulder_press()
        elif ex_num == 2: lying_leg_raise()
        elif ex_num == 3: side_lateral_raise()
        elif ex_num == 4: stand_side_crunch(image, landmark_list)
        elif ex_num == 5: push_up()

        if check_state():
            sequence += 1
            print("운동이 끝났습니다")
            time.sleep(1)

    elif sequence > 1:      # 운동 끝
        if sequence == 2:
            # 운동끝인 상태이므로, 여기서
            # database로 옮기고 sequence 3으로 올리면 된다. (다시 skeleton 사라짐)
            user_exercise = user_exercise_info(user_info['hashed_pw'], date.today())
            user_exercise_type = user_exercise[user_exercise["type"]==exercise_list[ex_num]]
            # 운동 카운트가 0이라면 DB 저장 안하도록
            if A_count+B_count+C_count == 0:
                pass
            # 오늘 해당 운동 타입을 이미 한 적이 있다면
            elif len(user_exercise_type):
                new_exercise = {
                            "user_hash": user_info['hashed_pw'],
                            "type": exercise_list[ex_num],
                            "date": date.today().strftime('%Y-%m-%d'),
                            "perfect": int(user_exercise_type["perfect"][0] + A_count),
                            "good": int(user_exercise_type["good"][0] + B_count),
                            "miss": int(user_exercise_type["miss"][0] + C_count)
                            }
                requests.post('http://127.0.0.1:8000/exercises', json=new_exercise)
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
            sequence += 1

        return cv2.flip(image, 1)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

    return cv2.flip(image, 1)

perfect_img =cv2.imread("./img/perfect.png")
good_img = cv2.imread("./img/good.png")
miss_img = cv2.imread("./img/miss.png")

flag = 0
def process2(image):
    global A_count
    global B_count
    global C_count
    global A_pre
    global B_pre
    global C_pre
    global message_length
    global flag
    
    if message_length > 12:
        flag = 0
        
    if A_pre != A_count:
        flag = 1
        message_length = 0
        A_pre = A_count
    elif B_pre != B_count:
        flag = 2
        message_length = 0
        B_pre = B_count
    elif C_pre != C_count:
        flag = 3
        message_length = 0
        C_pre = C_count
        
    if flag == 0:
        return image
    elif flag == 1:
        score_img = perfect_img
        message_length += 1
    elif flag == 2:
        score_img = good_img
        message_length += 1
    elif flag == 3:
        score_img = miss_img
        message_length += 1
    
    h, w, _ = score_img.shape
    h = int(h/1.5)
    w = int(w/1.5)
    score_img = cv2.resize(score_img,(w,h))
    roi = image[50:50+h, 50:50+w]#배경이미지의 변경할(다음 로고 넣을) 영역
    mask = cv2.cvtColor(score_img, cv2.COLOR_BGR2GRAY)#로고를 흑백처리
    #이미지 이진화 => 배경은 검정. 글자는 흰색
    mask[mask[:]==255]=0
    mask[mask[:]>0]=255
    mask_inv = cv2.bitwise_not(mask) #mask반전.  => 배경은 흰색. 글자는 검정
    score_image = cv2.bitwise_and(score_img, score_img, mask=mask)#마스크와 로고 칼라이미지 and하면 글자만 추출됨
    back = cv2.bitwise_and(roi, roi, mask=mask_inv)#roi와 mask_inv와 and하면 roi에 글자모양만 검정색으로 됨
    dst = cv2.bitwise_or(score_image, back)#로고 글자와 글자모양이 뚤린 배경을 합침
    image[50:50+h, 50:50+w] = dst  #roi를 제자리에 넣음

    return image


# # # # # # # # # # # # # # # # # # implemented code # # # # # # # # # # # # # # # # # #

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    img = process(img)
    if sequence == 1:
        img = process2(img)
    return av.VideoFrame.from_ndarray(img, format="bgr24")

webrtc_ctx = webrtc_streamer(
    key="Pose-estimation",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": {"width":1200, "height":640}, 
                              "audio": False},
    video_frame_callback=video_frame_callback,
    async_processing=True,  # or False
)