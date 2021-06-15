import cv2
import numpy as np

cap = cv2.VideoCapture(2)


ret1, lastFrame = cap.read()
first_detected = 0
last_detected = 0
while(True):

    ret, frame = cap.read()

    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
    arucoParams = cv2.aruco.DetectorParameters_create()
    corners, ids, rejected = cv2.aruco.detectMarkers(frame, arucoDict,
                                                     parameters=arucoParams)
    frame_markers = cv2.aruco.drawDetectedMarkers(frame.copy(), corners, ids)
    cv2.imshow('frame',frame_markers)
    if len(corners) > 0:
        first_detected += 1
        print("Detected Marker " + str(first_detected) + " frames ago")
        # flatten the ArUco IDs list
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned in
            # top-left, top-right, bottom-right, and bottom-left order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[0]))

            lastdectdist = topRight[0] - topLeft[0]
            print('Length of top ' +  str(lastdectdist) + ' pixels')
    else:
        print('lost')
        first_detected = 0
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
