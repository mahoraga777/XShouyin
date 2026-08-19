import os
import urllib.request
import cv2
import mediapipe as mp
import time

MODEL_PATH = 'gesture_recognizer.task'
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task'

if not os.path.exists(MODEL_PATH):
    print("ML Model file is missing \n no worry we are on to it")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Ok model is download you are ready to go")

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

current_gesture = "None"
confidence_score = 0.0
last_seen_time = time.time()

index_x = 0.0
index_y = 0.0
point_direction = "Center"  # Added directional tracking state

callback_action = None

def handle_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global current_gesture, confidence_score, last_seen_time, callback_action, index_x, index_y, point_direction
    
    if result.gestures and result.hand_landmarks and len(result.gestures) > 0:
        top_gesture = result.gestures[0][0]
        current_gesture = top_gesture.category_name
        confidence_score = top_gesture.score
        last_seen_time = time.time() 

        # Index fingertip
        index_finger = result.hand_landmarks[0][8]
        index_x = index_finger.x
        index_y = index_finger.y

        # Index base joint (Vector Origin)
        index_base = result.hand_landmarks[0][5]
        
        # Calculate delta vectors
        dx = index_finger.x - index_base.x
        dy = index_finger.y - index_base.y
        
        # Determine dominant axis direction
        if abs(dx) > abs(dy) and abs(dx) > 0.05:
            point_direction = "Left" if dx > 0 else "Right"
        elif abs(dy) > abs(dx) and abs(dy) > 0.05:
            point_direction = "Down" if dy > 0 else "Up"
        else:
            point_direction = "Center"
    else:
        current_gesture = "None"
        time.sleep(0.01)
        confidence_score = 0.0  
        index_x = 0.0
        index_y = 0.0
        point_direction = "Center"

def get_latest_gesture():
    return current_gesture

def is_idle(timeout: int):
    return (time.time() - last_seen_time) > timeout

def get_index_coordinates():
    return index_x, index_y

def get_pointing_direction():
    return point_direction