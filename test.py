import cv2
import pyautogui
import time
import streamlit as st
import mediapipe as mp
import numpy as np
import tempfile
from cvzone.HandTrackingModule import HandDetector
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from distance import dist
from PIL import Image

max_num_hands = 1
k = 0
q = list(0 for i in range(30))
qc = list(0 for i in range(30))
reset = np.zeros(30)

fn = ''

st.title("WIMM(PPT Controler)")

rad = st.sidebar.radio("Solution", ["MAIN", "Explain", "etc"])
FRAME_WINDOW = st.image([])

mpHands = mp.solutions.hands
my_hands = mpHands.Hands(max_num_hands=max_num_hands,
                         min_detection_confidence=0.5,
                         min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

def mouse():
    mouse_name = "mouse"
    st.info(mouse_name)

    k = 0
    q = list(0 for i in range(30))
    qc = list(0 for i in range(30))

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    screenWidth, screenHeight = pyautogui.size()
    pyautogui.FAILSAFE = False

    compareIndex = [[10, 4], [6, 8], [10, 12], [14, 16], [18, 20]]
    open = [False, False, False, False, False]
    gesture = [[False, True, False, False, False, '1'],
               [False, True, True, False, False, '2'],
               [False, True, False, False, True, 'mouse'],
               [False, False, False, False, True, 'quit']]
    while True:
        success, img = cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = my_hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                gumx = handLms.landmark[8].x
                gumy = handLms.landmark[8].y
                for i in range(0, 5):
                    open[i] = dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[compareIndex[i][0]].x,
                                   handLms.landmark[compareIndex[i][0]].y) < \
                              dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[compareIndex[i][1]].x,
                                   handLms.landmark[compareIndex[i][1]].y)

            for i in range(0, len(gesture)):
                flag = True
                for j in range(0, 5):
                    if (gesture[i][j] != open[j]):
                        flag = False
                if (flag == True):
                    ges = gesture[i][5]

                    if gesture[i][5] == '1':
                        pyautogui.moveTo(gumx * screenWidth, gumy * screenHeight)
                    elif gesture[i][5] == '2':
                        pyautogui.mouseDown()
                        pyautogui.mouseUp()
                        time.sleep(1)
                    elif gesture[i][5] == 'mouse':
                        pyautogui.press('left')
                        time.sleep(1)

                    if k < 30:
                        q[k] = ges
                        k += 1
                    else:
                        for h in range(29):
                            qc[h] = q[h + 1]
                        qc[29] = ges
                        q = qc

                    if q.count('quit') == 30:
                        cap.release()
                        cv2.destroyAllWindows()
                        return

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        fimg = cv2.flip(img, 1)
        FRAME_WINDOW.image(fimg)
def volume():
    vol_name = "volume"
    st.info(vol_name)

    k = 0
    q = list(0 for i in range(30))
    qc = list(0 for i in range(30))

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    devices = AudioUtilities.GetSpeakers()  # ????????? ????????????
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    pyautogui.FAILSAFE = False

    while True:
        success, img = cap.read()
        h, w, c = img.shape
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = my_hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:  # ?????? ?????? ??????
                open = dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[14].x,
                            handLms.landmark[14].y) < \
                       dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[16].x,
                            handLms.landmark[16].y)

                quit = dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[17].x,
                            handLms.landmark[17].y) < \
                       dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[20].x,
                            handLms.landmark[20].y)

                if open == False:
                    curdist = -dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[8].x,
                                    handLms.landmark[8].y) / \
                              (dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[5].x,
                                    handLms.landmark[5].y) * 2)
                    curdist = curdist * 100
                    curdist = -96 - curdist
                    curdist = min(0, curdist)
                    if curdist > -64 and curdist < 0:
                        volume.SetMasterVolumeLevel(curdist, None)
                    else:
                        continue

                if k < 30:
                    q[k] = str(bool(quit))
                    k += 1
                else:
                    for h in range(29):
                        qc[h] = q[h + 1]
                    qc[29] = str(bool(quit))
                    q = qc

                if q.count('True') == 30:
                    cap.release()
                    cv2.destroyAllWindows()
                    return

                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        fimg = cv2.flip(img, 1)
        FRAME_WINDOW.image(fimg)
def video(fn):
    video_name = "video"
    st.info(video_name)

    k = 0

    q = list(0 for i in range(30))
    qc = list(0 for i in range(30))

    LENGTH_THRESHOLD = 50
    detector = HandDetector(detectionCon=0.8, maxHands=1)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap_video = cv2.VideoCapture(fn)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    total_frames = int(cap_video.get(cv2.CAP_PROP_FRAME_COUNT))
    _, video_img = cap_video.read()

    def draw_timeline(img, rel_x):
        img_h, img_w, _ = img.shape
        timeline_w = max(int(img_w * rel_x) - 50, 50)
        cv2.rectangle(img, pt1=(50, img_h - 50), pt2=(timeline_w, img_h - 49), color=(0, 0, 255), thickness=-1)

    rel_x = 0
    frame_idx = 0
    draw_timeline(video_img, 0)

    mp_hands = mp.solutions.hands
    with mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:

        while cap.isOpened():
            _, cam_img = cap.read()
            cam_img = cv2.flip(cam_img, 1)

            hands, cam_img = detector.findHands(cam_img)

            if total_frames == frame_idx+1:
                cap.release()
                cv2.destroyAllWindows()
                return

            if hands:
                lm_list = hands[0]['lmList']
                fingers = detector.fingersUp(hands[0])
                length, info, cam_img = detector.findDistance(lm_list[4], lm_list[8], cam_img)  # ??????, ????????? ???????????? ??????

                if fingers == [0, 0, 0, 0, 1]:  # ??????
                    if k<30:
                        q[k] = '1'
                        k += 1
                    else:
                        for h in range(29):
                            qc[h] = q[h+1]
                        qc[29] = '1'
                        q = qc
                    pass
                else:  # Play
                    if k<30:
                        q[k] = '0'
                        k += 1
                    else:
                        for h in range(29):
                            qc[h] = q[h+1]
                        qc[29] = '0'
                        q = qc

                    if length < LENGTH_THRESHOLD:  # Navigate
                        rel_x = lm_list[4][0] / w
                        frame_idx = int(rel_x * total_frames)
                        frame_idx = min(max(frame_idx, 0), total_frames)

                        cap_video.set(1, frame_idx)
                    else:
                        frame_idx += 1
                        rel_x = frame_idx / total_frames

                _, video_img = cap_video.read()
                draw_timeline(video_img, rel_x)

            if q.count('1') == 30:
                cap.release()
                cv2.destroyAllWindows()
                return

            video_cvt = cv2.cvtColor(video_img, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(video_cvt)

if rad == "MAIN":
    mouse_name = "MAIN"
    st.success(mouse_name)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    f = False

    uf = st.checkbox('Upload file')
    if uf == True:
        f = st.file_uploader("Upload file")
        if bool(f) == False:
            st.warning('????????? ???????????? ????????????.')
        elif bool(f) == True:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(f.read())
            fn = tfile.name

    FRAME_WINDOW = st.image([])

    pyautogui.FAILSAFE = False

    compareIndex = [[5, 4], [6, 8], [10, 12], [14, 16], [18, 20]]
    open = [False, False, False, False, False]
    gesture = [[False, True, False, False, False, '1'],
               [False, True, True, False, False, '2'],
               [True, True, True, False, False, '3'],
               [False, True, True, True, True, '4'],
               [True, True, True, True, True, '5'],
               [True, True, False, False, True, 'mouse'],
               [False, False, False, False, True, 'quit']]

    while True:
        success, img = cap.read()
        h, w, c = img.shape
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = my_hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for i in range(0, 5):
                    open[i] = dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[compareIndex[i][0]].x,
                                   handLms.landmark[compareIndex[i][0]].y) < \
                              dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[compareIndex[i][1]].x,
                                   handLms.landmark[compareIndex[i][1]].y)
            for i in range(0, len(gesture)):
                flag = True
                for j in range(0, 5):
                    if (gesture[i][j] != open[j]):
                        flag = False
                if (flag == True):
                    ges = gesture[i][5]

                    if k < 30:
                        q[k] = ges
                        k += 1
                    else:
                        for h in range(29):
                            qc[h] = q[h + 1]
                        qc[29] = ges
                        q = qc

                    if q.count('1') == 30:
                        cap.release()
                        cv2.destroyAllWindows()
                        q = reset
                        mouse()
                        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                        st.success(mouse_name)

                    elif q.count('2') == 30:
                        cap.release()
                        cv2.destroyAllWindows()
                        q = reset
                        volume()
                        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                        st.success(mouse_name)

                    elif q.count('3') == 30 and bool(f) == False:
                        st.warning("????????? ????????? Upload ????????? ?????????.")
                        q = reset
                    elif q.count('3') == 30 and bool(f) == True:
                        cap.release()
                        # cv2.destroyAllWindows()
                        q = reset
                        video(fn)
                        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                        st.info(mouse_name)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        fimg = cv2.flip(img, 1)
        FRAME_WINDOW.image(fimg)
if rad == "Explain":
    st.write("Main?????? ??? ???????????? ?????? ??????.")
    image1 = Image.open('1.png')
    image2 = Image.open('2.png')
    image3 = Image.open('3.png')
    image4 = Image.open('back.png')
    image5 = Image.open('quit.png')
    image6 = Image.open('sound.png')
    image7 = Image.open('video.png')
    st.write("---------------------------------------------------------------")
    st.image(image1, caption='?????????')
    st.write("??? ??? ???????????? ????????? ??????????????? ??? ??? ??????.")
    st.image(image1, width=150, caption='Cursor')
    st.image(image2, width=150, caption='Click')
    st.image(image4, width=150, caption='Back')
    st.write("??? ?????? ?????? ???????????? PPT(?????? ??????)??? ?????? ??? ??? ??????.")
    st.write("---------------------------------------------------------------")
    st.image(image2, caption='??????')
    st.write("??? ??? ???????????? ?????? ??????????????? ??? ??? ??????.")
    st.image(image6, width=150, caption='Sound Control')
    st.write("?????? ???????????? ????????? ????????? ?????? ????????? ????????????.")
    st.write("---------------------------------------------------------------")
    st.image(image3, caption='?????????')
    st.write("??? ??? ???????????? ????????? ??????????????? ??? ??? ??????.")
    st.write("??? \'MAIN > Upload file\' ?????? ????????? ????????? ?????? ????????? ????????????.")
    st.image(image7, width=150, caption='Video Control')
    st.write("????????? ????????? ???????????? ??? ????????? x ????????? ?????? ????????? ??????????????? ????????????.")
    st.write("---------------------------------------------------------------")
    st.image(image5, 'Quit')
    st.write("??? ???????????? ?????? ??????????????? ??????????????? ?????????????????? ???????????? ??????.")
    st.write("\"???????????????\"??? \"????????? ????????????\"?????? ????????? ?????? ?????????????????? ????????? ??????.")
    st.write("\"??????????????????\"?????? ?????? ???????????? ???????????? ?????????????????? ?????? ???????????? ??? ??????.")
    st.write("?????????????????? ?????? ????????? ?????? ????????? ?????? ???????????? ?????? ????????? ???????????? ?????????.")


    #st.image(image3, width=100 ,caption='text')
if rad == "etc":
    st.write("????????? ???????????????")
    st.write("import cv2")
    st.write("import pyautogui")
    st.write("import time")
    st.write("import streamlit as st")
    st.write("import mediapipe as mp")
    st.write("import numpy as np")
    st.write("import tempfile")
    st.write("from ctypes import cast, POINTER")
    st.write("from cvzone.HandTrackingModule import HandDetector")
    st.write("from comtypes import CLSCTX_ALL")
    st.write("from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume")
    st.write("from PIL import Image")

    image = Image.open('together.jpg')
    st.image(image,'HANSEI TEAM 2')
    st.write("?????? ????????? ??????????????? ??????????????? APK??? ????????? ???????????? ??? ?????????.")
    st.write("????????? PC????????? ??? ??? ?????? ??????????????? ????????? ????????? ????????? ?????????.")
    st.write("????????? .exe????????? ????????? ?????? ?????? ????????????.")
    st.write("????????? ??????????????? ????????? ?????????????????? ??? ????????? ????????????.")
    st.write("??????????????? ?????????.")
    st.write("---------------------------------------------------------------")
    st.write("?????? ?????? ????????????")



