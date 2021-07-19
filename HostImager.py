#!/usr/local/bin/python3

import numpy as np
import ImageTransferService
import cv2 as cv

if __name__ == "__main__":

    host = '192.168.88.212'
    RemoteDisplay = ImageTransferService.ImageTransferService(host)
    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        print("Can't open camera")
        exit()

    # Check remote display is up
    print(RemoteDisplay.ping())

    # Create BGR image
    # w, h = 640, 480
    # im = np.zeros((h,w,3),dtype=np.uint8)

    # for c in range(256):
    while True:
        # im[:,:,0] = c
        ret, frame = cap.read()
        RemoteDisplay.sendImage(frame)
        if cv.waitKey(1) == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()