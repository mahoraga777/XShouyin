import cv2
import mediapipe as mp
import time
import sys

# Internal Modules
import gesture
from action import trigger_action
from mouse import MouseController

# MediaPipe Configuration
options = gesture.GestureRecognizerOptions(
    base_options=gesture.BaseOptions(model_asset_path=gesture.MODEL_PATH),
    running_mode=gesture.VisionRunningMode.LIVE_STREAM,
    result_callback=gesture.handle_result,
    min_hand_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

print("Starting Xshouyan System...")

# Initialize Peripherals
mouse = MouseController() 
previous_sign = "None"
last_trigger_time = 0.0
cooldown_time = 2.0


try:
    with gesture.GestureRecognizer.create_from_options(options) as recognizer:
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Camera connection lost.")
                break

            # Frame Processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            recognizer.recognize_async(mp_image, int(time.time() * 1000))

            # Retrieve Sensor State
            detected_sign = gesture.get_latest_gesture()
            direction = gesture.get_pointing_direction()
            current_time = time.time()
            index_x, index_y = gesture.get_index_coordinates()
            

            # Event Routing
            if detected_sign == "Pointing_Up":
                # Delegate movement to the mouse module
                mouse.move_relative(index_x, index_y)
        
            elif detected_sign != "None":
                if detected_sign != previous_sign and (current_time - last_trigger_time > cooldown_time):
                    last_trigger_time = current_time
                    previous_sign = detected_sign
                    trigger_action(detected_sign)
            else:
                previous_sign = "None"

            # Watchdog Timer
            if gesture.is_idle(timeout=15):
                print("\n[TIMEOUT] No hand detected for 15 seconds. Shutting down...")
                break
                
            time.sleep(0.01)

except KeyboardInterrupt:
    print("\n[SIGINT] Daemon terminated by user.")

finally:
    if 'cap' in locals() and cap.isOpened():
        cap.release()
    print("Camera released cleanly. System offline.")
    sys.exit(0)