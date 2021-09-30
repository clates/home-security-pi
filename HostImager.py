#!/usr/local/bin/python3

import ImageTransferService
import cv2 as cv
import sys

if len(sys.argv) < 2:
    print("Provide a name argument")
    exit()

if __name__ == "__main__":

    host = '192.168.88.212'
    RemoteDisplay = ImageTransferService.ImageTransferService(host)
    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        print("Can't open camera")
        exit()

    # Check remote display is up
    print(RemoteDisplay.ping())

    while True:
        ret, frame = cap.read()
        RemoteDisplay.sendImage(frame, sys.argv[1])
        if cv.waitKey(1) == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()