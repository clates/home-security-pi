#!/usr/bin/env python3
#export DISPLAY=:0

import WebsocketServer
import websocket
import ImageTransferService
import numpy as np
import cv2
import imutils
import json
import datetime
import ffmpeg
import pickle
import struct
import base64
from _thread import start_new_thread
import logging 
import time

VIDEO_CAPTURE_COOLDOWN_SECONDS = 30
VIDEO_CAPTURE_LENGTH_SECONDS = 10
BASE_FRAME_RESET_SECONDS = 60


_lastChime = datetime.datetime.now()
_lastBaseFrameReset = datetime.datetime.now()
_currVideo = None
gray1 = None
aviFileName = "./motion-logs/temp.avi"

def clip10s(frameIn):
    global _lastChime
    global _currVideo
    timeSinceLastChime = datetime.datetime.now() - _lastChime
    if timeSinceLastChime.total_seconds() > VIDEO_CAPTURE_COOLDOWN_SECONDS:
        print("Object in view! - " + str(timeSinceLastChime.total_seconds()))
        _lastChime = datetime.datetime.now()
        _currVideo = cv2.VideoWriter(aviFileName, cv2.VideoWriter_fourcc(*'MJPG'), 100.0, (640,480))
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
        # resetBaseFrames(frameIn, True)
        _currVideo.release()
        _currVideo = None
        convertToMP4()

def convertToMP4():
    ffmpeg.input(aviFileName).output("./motion-logs/motion-" + _lastChime.strftime("%Y-%m-%d_%T") + ".mp4").run()

def resetBaseFrames(newBaseFrame, force=False):
    global gray1
    global _lastBaseFrameReset
    timesinceLastBaseFrameReset = datetime.datetime.now() - _lastBaseFrameReset
    if force or timesinceLastBaseFrameReset.total_seconds() > BASE_FRAME_RESET_SECONDS:
        _lastBaseFrameReset = datetime.datetime.now()
        gray1 = cv2.cvtColor(newBaseFrame, cv2.COLOR_BGR2GRAY)
        print("Resetting base frame")


# Called for every client connecting (after handshake)
def new_client(client, server):
	print("New client connected and was given id %d" % client['id'])
	server.send_message_to_all("Hey all, a new client has joined us")


# Called for every client disconnecting
def client_left(client, server):
	print("Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
	if len(message) > 200:
		message = message[:200]+'..'
	print("Client(%d) said: %s" % (client['id'], message))
	server.send_message_to_all("Client(%d) said: %s" % (client['id'], message))

def startServer(serverIn):
    print("Starting the consolidated websocket on: " + str(serverIn))
    serverIn.run_forever()

def on_message(ws, message):
    '''
        This method is invoked when ever the client
        receives any message from server
    '''
    server.send_message_to_all(message)
def on_error(ws, error):
    '''
        This method is invoked when there is an error in connectivity
    '''
    print("received error as {}".format(error))

def on_close(ws):
    '''
        This method is invoked when the connection between the 
        client and server is closed
    '''
    print("Connection closed")
def on_open(ws):
    '''
        This method is invoked as soon as the connection between 
		client and server is opened and only for the first time
    '''
    ws.send("hello there")
    print("Connected to the Zigbee Websocket")


if __name__ == "__main__":
    live_feeds = {}
    
    # Build the web server
    server = WebsocketServer.WebsocketServer(9001, "0.0.0.0")
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)

    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://192.168.88.212:443", on_message = on_message, on_error = on_error, on_close = on_close)
    ws.on_open = on_open
    
    # Kick a thread off for 
    # wst = threading.Thread(target=)
    # wst.daemon = True
    # wst.start()
    start_new_thread(ws.run_forever, ())

    # Start a thread for the websocket server
    start_new_thread(startServer, (server, ))

    host = '0.0.0.0'
    src = ImageTransferService.ImageTransferService(host)

    # Check Redis is running 
    print("Checking redis server....")
    print(src.ping())

    # frameDict = src.receiveImage()
    # frame1 = frameDict['im']
    # gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)

    while True:
        frameDict = src.receiveImage()
        current_frame_camera_name = frameDict[b'cameraName']

        #If we don't have a live feed entry for the cameraName provided
        if current_frame_camera_name not in live_feeds:
            live_feeds[current_frame_camera_name] = {}
            live_feeds[current_frame_camera_name]['im'] = frameDict['im']
            live_feeds[current_frame_camera_name]['gray'] = cv2.cvtColor(frameDict['im'], cv2.COLOR_BGR2GRAY)

        lastFrame = live_feeds[current_frame_camera_name]['im']
        lastGray = live_feeds[current_frame_camera_name]['gray']

        currentFrame = frameDict['im']
        currentGray = cv2.cvtColor(currentFrame, cv2.COLOR_BGR2GRAY) 


        _, JPEG = cv2.imencode(".JPG", currentFrame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])

        try:
            lastFrame = lastFrame
            server.send_message_to_all(json.dumps({'cameraName': frameDict[b'cameraName'].decode('UTF-8'),"isVideo": True, "data": str(base64.b64encode(JPEG.tobytes()))}))
        except KeyboardInterrupt:
            quit()
        except:
            logging.exception('')
        
        # resetBaseFrames(frame2)

        currentGray = cv2.GaussianBlur(currentGray, (5, 5), 0)
        
        deltaframe=cv2.absdiff(lastGray,currentGray)
        threshold = cv2.threshold(deltaframe, 60, 255, cv2.THRESH_BINARY)[1]       
        threshold = cv2.dilate(threshold,None)

        countour,heirarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for i in countour:
            if cv2.contourArea(i) < 200:
                continue
            (x, y, w, h) = cv2.boundingRect(i)
            cv2.rectangle(currentFrame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # clip10s(frame2)
        
        # cv2.imshow('cameraName', currentFrame)
        # cv2.imshow(frameDict[b'cameraName'], currentFrame)
        # appendToVideo(currentFrame)
        cv2.waitKey(1)
        time.sleep(0.05)