import cv2
import numpy as np

camera_width = 640

def find_target():
    target_found = False
    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
    arucoParams = cv2.aruco.DetectorParameters_create()
    cap = cv2.VideoCapture(2)
    print('Start Search')
    lastFound = 0
    while not target_found:
        ret, frame = cap.read()
        corners, ids, rejected = cv2.aruco.detectMarkers(frame, arucoDict,
                                                         parameters=arucoParams)
        frame_markers = cv2.aruco.drawDetectedMarkers(frame.copy(), corners, ids)
        cv2.imshow('frame', frame_markers)
        if len(corners) > 0:
            lastFound = 0
            print('Detected marker')
            if corners[0][0][0][0] > (camera_width/2) - 10:
                print('overshot')
            elif corners[0][0][1][0] <  (camera_width/2) + 10:
                print('other overshoot')
            else:
                print('centred')
                if corners[0][0][1][0] - corners[0][0][0][0] < 50:
                    print('Moving Closer')
                elif corners[0][0][1][0] - corners[0][0][0][0] > 50:
                    print('Backing Up')
                else:
                    print('Optimal distance')
                    target_found = True
        else:
            lastFound +=1

        if lastFound > 5:
            print('Target Lost')
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break




find_target()