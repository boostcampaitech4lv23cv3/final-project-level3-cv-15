import cv2
import numpy as np
import av
import mediapipe as mp
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from mediapipe.framework.formats import landmark_pb2
import math
import time

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)


# # # # # # # # # # # # # # # # # # implemented code # # # # # # # # # # # # # # # # # #


# initialize
temp_dict = {}
for i in range(35):
    temp_dict[i] = dict()
    # temp_dict[33], temp_dict[34] = 지면과 각도 구하기위한 벡터

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

# 운동 선택
# 0: side lunge, 1: shoulder press, 2: lying leg raises, 3: side lateral raise
# 4: standing side crunch(?) 5: push up
num_exercise = 3


# 각각 운동에서 사용할 global 변수들 초기화
if num_exercise == 0:
    min_right = 180
    min_left = 180

elif num_exercise == 1:
    min_right = 125
    min_right2 = 125
    min_left = 125
    min_left2 = 125

elif num_exercise == 2:
    min_right = 180
    min_right2 = 0
    count = 0

elif num_exercise == 3:
    min_right = 75
    min_left = 75
    min_right2 = 0
    count = 0

# stand side crunch
elif num_exercise == 4:
    min_left = 180
    min_right = 180
    min_ldistance = 999
    min_rdistance = 999  

# pushup
elif num_exercise == 5:
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

    # 잘하는 조건 : 90 / 180 + 좌우 각도 같아야 한다
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

    image_landmark = get_pos(image, landmark_list)

    # angle_list = (26, 28, 24, 25, 23, 27)
    # hand_list = (14, 16, 12, 13, 15, 11)

    angle_order = (((26, 28), (26, 24)), ((25, 23), (25, 27)))
    # hand_order = (((14, 16), (14, 12)), ((13, 15), (13, 11)))

    right_angle, left_angle = find_angles(angle_order, 2, default_angles=[180,180])

    left_distance = abs(image_landmark[13][1:][0] - image_landmark[25][1:][0]) + abs(image_landmark[13][1:][1] - image_landmark[25][1:][1])
    right_distance = abs(image_landmark[14][1:][0] - image_landmark[26][1:][0]) + abs(image_landmark[14][1:][1] - image_landmark[26][1:][1])

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

    threshold = 0.04

    nose_loc = temp_dict[0]
    right_wrist = temp_dict[15]
    left_wrist = temp_dict[16]
    
    if right_wrist['x'] == -10 or right_wrist['y'] == -10 \
        or left_wrist['x'] == -10 or left_wrist['y'] == -10:

        return False

    
    if ((right_wrist['x'] - left_wrist['x'])**2 \
        + (right_wrist['y'] - left_wrist['y'])**2) < threshold \
            and nose_loc['y'] > right_wrist['y']:
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
                continue

            temp_dict[idx]['x'] = landmark.x
            temp_dict[idx]['y'] = landmark.y
    

    if sequence == 0:       # 운동시작 전
        if check_state():
            sequence += 1
            # 운동 시작을 알려주는 표시를 해야한다.
            print("운동이 시작되었습니다.")
            time.sleep(1)

        return cv2.flip(image, 1)

    elif sequence == 1:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


        if num_exercise == 0: side_lunge()
        elif num_exercise == 1: shoulder_press()
        elif num_exercise == 2: lying_leg_raise()
        elif num_exercise == 3: side_lateral_raise()
        elif num_exercise == 4: stand_side_crunch(image, landmark_list)
        elif num_exercise == 5: push_up()

        if check_state():
            sequence += 1
            print("운동이 끝났습니다")
            time.sleep(1)

    elif sequence > 1:      # 운동 끝
        if sequence == 2:
            # 운동끝인 상태이므로, 여기서
            # database로 옮기고 sequence 3으로 올리면 된다. (다시 skeleton 사라짐)
            database = 100  # -> dummy code

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

# # # # # # # # # # # # # # # # # # implemented code # # # # # # # # # # # # # # # # # #

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    img = process(img)
    return av.VideoFrame.from_ndarray(img, format="bgr24")

webrtc_ctx = webrtc_streamer(
    key="Pose-estimation",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    video_frame_callback=video_frame_callback,
    async_processing=True,  # or False
)
