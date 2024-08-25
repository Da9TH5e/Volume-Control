import threading
import numpy as np
import cv2
import time
import math
import HandTrackingModule as htm
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wcam, hcam = 640, 480
cap = cv2.VideoCapture(1)
cap.set(3, wcam)
cap.set(4, hcam)


pTime=0

detector = htm.handDetector()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volume.GetMute()
volume.GetMasterVolumeLevel()
volume.GetVolumeRange()
volume.SetMasterVolumeLevel(-20.0, None)
vol = 0
volBar = 400
volPer = 0


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    
    if len(lmList)!= 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        
        length = math.hypot(x2 - x1, y2 - y1)
        
        vol = np.interp(length, [20, 170], [0, 1])
        volume.SetMasterVolumeLevelScalar(vol, None)
        volBar = np.interp(length, [20, 170], [400, 150])
        volPer = np.interp(length, [20, 170], [0, 100])
        
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 100), 3)
        if length < 35:
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
    
    cv2.rectangle(img, (50, 150), (35, 400), (0, 255, 0), 2)
    cv2.rectangle(img, (50, int(volBar)), (35, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{str(int(volPer))}%', (30, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    
    cv2.putText(img, f'FPS: {str(int(fps))}', (20, 20), 
                cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
    
    cv2.imshow("Image", img)
    cv2.waitKey(1)