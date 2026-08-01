import os
import urllib.request

import cv2
import mediapipe as mp
import time

### Download model if not installed ###

MODEL_PATH = 'gesture_recognizer.task'
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task'

if not os.path.exists(MODEL_PATH):
    print("ML Model file is missing \n no worry we are on to it")
    urllib.request.urlretrive(MODEL_URL, MODEL_PATH)
    print("Ok model is download you are ready to go")


#### MediaPipe Task Imports ####

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

#### State storage for recognized gesture ####

current_gesture = "None"
confidence_score = 0.0
last_seen_time = time.time()

#### varible to hold external function ####

callback_action = None

#### Callback function executed in background thread whenever MediaPipe processes a frame ####

def handle_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global current_gesture, confidence_score, last_seen_time, callback_action
    
    ### if  model recoginize at least one hand ###
    if result.gestures and len(result.gestures) > 0:
        ## return most probibal gesture ##
        top_gesture = result.gestures[0][0]
        current_gesture = top_gesture.category_name
        confidence_score = top_gesture.score
        last_seen_time = time.time() #reset the last seen time
    else:
        current_gesture = "None"
        confidence_score = 0.0  # <-- Added this so it resets properly!

def get_latest_gesture():
    ###return the name of current gesture
    return current_gesture

def is_idle(timeout=15):
    return (time.time()- last_seen_time) > timeout