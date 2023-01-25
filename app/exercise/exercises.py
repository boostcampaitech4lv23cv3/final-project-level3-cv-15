import cv2
import numpy as np
import av
import mediapipe as mp
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from mediapipe.framework.formats import landmark_pb2
import math

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)


# # # # # # # # # # # # # # # # # # implemented code # # # # # # # # # # # # # # # # # #


# initialize
temp_dict = {}
for i in range(33):
    temp_dict[i] = dict()

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

num_exercise = 1    # 0: side lunge, 1: shoulder press, 2: lying leg raises, 3: side lateral raise
                    # 4: standing side crunch(?) 5: push up


if num_exercise == 0:
    min_right = 180
    min_left = 180

elif num_exercise == 1:
    min_right = 125
    min_right2 = 125
    min_left = 125
    min_left2 = 125



def find_angles(angle_order, num, default_angles):
    """
        calculate necessary angles
        input : set : set of angles
                int : num of angles, 
                list : default_angles

        output :  float (angles) 0~180
    """

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
    global A_count
    global B_count
    global C_count
    print("Perfect : ", A_count, "Good : ", B_count, "Miss : ", C_count)

def side_lunge():
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
    global A_count
    global B_count
    global C_count
    global state

    print("왼쪽이나 오른쪽으로 서 주세요")

    # state 0 : 시작자세
    # state 1 : 왼쪽 기준으로 하면 된다.
    
    
    





def side_lateral_raise():
    pass



def process(image):
    global A_count
    global B_count
    global C_count

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  
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
    
    if num_exercise == 0: side_lunge()
    elif num_exercise == 1: shoulder_press()
    elif num_exercise == 2: lying_leg_raise()
    elif num_exercise == 3: side_lateral_raise()

        
    
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
    key="WYH",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    video_frame_callback=video_frame_callback,
    async_processing=True,  # or False
)
