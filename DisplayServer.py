#!/usr/bin/env python3

import ImageTransferService
import numpy as np
import cv2
import datetime
import ffmpeg


VIDEO_CAPTURE_COOLDOWN_SECONDS = 30
VIDEO_CAPTURE_LENGTH_SECONDS = 10
BASE_FRAME_RESET_SECONDS = 60


_lastChime = datetime.datetime.now()
_lastBaseFrameReset = datetime.datetime.now()
_currVideo = None
gray1 = None
aviFileName = "./temp.avi"

def clip10s(frameIn):
    global _lastChime
    global _currVideo
    timeSinceLastChime = datetime.datetime.now() - _lastChime
    if timeSinceLastChime.total_seconds() > VIDEO_CAPTURE_COOLDOWN_SECONDS:
        print("Object in view! - " + str(timeSinceLastChime.total_seconds()))
        _lastChime = datetime.datetime.now()
        _currVideo = cv2.VideoWriter(aviFileName, cv2.VideoWriter_fourcc(*'MJPG'), 100.0, (480,640))
        src.sendImage(frameIn, "ALERT")
    return _lastChime

def appendToVideo(frameIn):
    global _lastChime
    global _currVideo
    timeSinceLastChime = datetime.datetime.now() - _lastChime
    if timeSinceLastChime.total_seconds() < VIDEO_CAPTURE_LENGTH_SECONDS and _currVideo is not None:
        print("writing frames to video...")
        _currVideo.write(frameIn)
    if timeSinceLastChime.total_seconds() >= VIDEO_CAPTURE_LENGTH_SECONDS and _currVideo is not None:
        print("Finalizing video and closing...")
        _currVideo.release()
        _currVideo = None
        convertToMP4()

def convertToMP4():
    ffmpeg.input(aviFileName).output("./motion" + _lastChime.strftime("%d-%B-%H-%M-%S") + ".mp4").run()


def resetBaseFrames(newBaseFrame):
    global gray1
    global _lastBaseFrameReset
    timesinceLastBaseFrameReset = datetime.datetime.now() - _lastBaseFrameReset
    if timesinceLastBaseFrameReset.total_seconds() > BASE_FRAME_RESET_SECONDS:
        _lastBaseFrameReset = datetime.datetime.now()
        gray1 = cv2.cvtColor(newBaseFrame, cv2.COLOR_BGR2GRAY)
        print("Resetting base frame")


if __name__ == "__main__":

    host = '0.0.0.0'
    src = ImageTransferService.ImageTransferService(host)

    # Check Redis is running 
    print(src.ping())

    frame1= src.receiveImage()
    frame1= cv2.rotate(frame1, cv2.ROTATE_90_CLOCKWISE)
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    
    while True:
        frame2 = src.receiveImage()
        frame2 = cv2.rotate(frame2, cv2.ROTATE_90_CLOCKWISE)
        # Reset the base frame before it gets mutated from cv2.rectangle
        resetBaseFrames(frame2)

        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.GaussianBlur(gray2, (5, 5), 0)
        
        deltaframe=cv2.absdiff(gray1,gray2)
        cv2.imshow('delta',deltaframe)
        threshold = cv2.threshold(deltaframe, 60, 255, cv2.THRESH_BINARY)[1]
        threshold = cv2.dilate(threshold,None)
        cv2.imshow('threshold',threshold)
        countour,heirarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for i in countour:
            if cv2.contourArea(i) < 200:
                continue
            (x, y, w, h) = cv2.boundingRect(i)
            cv2.rectangle(frame2, (x, y), (x + w, y + h), (255, 0, 0), 2)
            clip10s(frame2)
        
        cv2.imshow('window',frame2)
        appendToVideo(frame2)
        cv2.waitKey(1)