import redis
import cv2
import numpy as np

if __name__ == "__main__":

    host = '192.168.88.212'
    RemoteDisplay = ImageTransferService.ImageTransferService(host)

    # Check remote display is up
    print(RemoteDisplay.ping())

    # Create BGR image
    # w, h = 640, 480
    # im = np.zeros((h,w,3),dtype=np.uint8)

    # for c in range(256):
    while True:
        # im[:,:,0] = c
        src = RemoteDisplay.receiveImage('ALERT')

        if src is not None:
            cv2.imshow('ALERT',src)

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()