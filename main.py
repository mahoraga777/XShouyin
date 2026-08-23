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
    min_hand_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

print("Starting Xshouyan System in headless mode...")

# Initialize Peripherals
mouse = MouseController() 
previous_sign = "None"
last_trigger_time = 0.0
cooldown_time = 2.0

# State Machine Variables
is_tracking = False
last_toggle_time = 0.0
toggle_cooldown = 1.0 

try:
    with gesture.GestureRecognizer.create_from_options(options) as recognizer:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Camera connection lost.")
                break

            frame = cv2.flip(frame, 1)

            # Frame Processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            recognizer.recognize_async(mp_image, int(time.monotonic() * 1000))

            # Retrieve Sensor State
            detected_sign = gesture.get_latest_gesture()
            current_time = time.time()
            index_x, index_y = gesture.get_index_coordinates()

            # 1. State Toggle Logic
            if detected_sign == "Closed_Fist":
                if (current_time - last_toggle_time) > toggle_cooldown:
                    is_tracking = not is_tracking
                    last_toggle_time = current_time
                    print(f"[*] Mouse Tracking: {'ENABLED' if is_tracking else 'DISABLED'}")

            # 2. Movement Logic
            if is_tracking:
                mouse.move_absolute(index_x, index_y)
            else:
                mouse.reset()
                
            # 3. Discrete Actions Logic
            if detected_sign != "None" and detected_sign != "Closed_Fist":
                if detected_sign != previous_sign and (current_time - last_trigger_time > cooldown_time):
                    last_trigger_time = current_time
                    previous_sign = detected_sign
                    
                    if detected_sign == "Victory":
                        mouse.left_click()
                    elif detected_sign == "Open_Palm":
                        mouse.right_click()
                    elif detected_sign not in ["Pointing_Up"]:
                        trigger_action(detected_sign)
            elif detected_sign == "None":
                previous_sign = "None"

            # Headless CPU Throttling
            time.sleep(0.01)

            if gesture.is_idle(timeout=15):
                print("\n[TIMEOUT] System idle. Shutting down...")
                break

except KeyboardInterrupt:
    print("\n[SIGINT] Daemon terminated.")

finally:
    if 'cap' in locals() and cap.isOpened():
        cap.release()
    print("Camera released cleanly. System offline.")
    sys.exit(0)