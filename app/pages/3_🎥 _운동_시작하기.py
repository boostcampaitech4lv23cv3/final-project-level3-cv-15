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