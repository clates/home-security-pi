import redis
import cv2
import numpy as np
import ImageTransferService
import pygame


pygame.mixer.init()
pygame.mixer.music.load("./Z_Nov_39_2.ogg")

def playChime():
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

if __name__ == "__main__":


    host = '192.168.88.212'
    RemoteDisplay = ImageTransferService.ImageTransferService(host)

    # Check remote display is up
    print(RemoteDisplay.ping())
    playChime()
    # Create BGR image
    # w, h = 640, 480
    # im = np.zeros((h,w,3),dtype=np.uint8)

    # for c in range(256):
    
    _lastAlert = RemoteDisplay.receiveImage('ALERT')
    while True:
        # Ignore duplicate alerts
        src = RemoteDisplay.receiveImage('ALERT')

        if src is not None:
            cv2.imshow('ALERT',src)

        if cv2.waitKey(1) == ord('q'):
            break

        if np.sum(cv2.subtract(_lastAlert, src)) == 0:
            continue

        _lastAlert = src
        playChime()
        


    cv2.destroyAllWindows()