import cv2
import mediapipe as mp
import time
import sys  # Added missing import

# Import functions from your two modules!
import gesture
from action import trigger_action

# Configure MediaPipe options using gesture.py's setup
options = gesture.GestureRecognizerOptions(
    base_options=gesture.BaseOptions(model_asset_path=gesture.MODEL_PATH),
    running_mode=gesture.VisionRunningMode.LIVE_STREAM,
    result_callback=gesture.handle_result
    min_hand_detection_confidence = 0.7
    
)

print("Starting Xshouyan System...")

previous_sign = "None"
last_trigger_time = 0.0
cooldown_time = 2.0

# 1. Added try block to catch Ctrl+C safely
try:
    with gesture.GestureRecognizer.create_from_options(options) as recognizer:
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = int(time.time() * 1000)
            
            recognizer.recognize_async(mp_image, timestamp_ms)

            # 1. Ask gesture.py for the latest hand sign detected
            detected_sign = gesture.get_latest_gesture()
            current_time = time.time()

            # 2. Trigger ONLY if:
            # - Hand is showing a valid sign
            # - It's a DIFFERENT sign than last time (OR hand was reset)
            # - Cooldown period has passed
            if detected_sign != "None":
                if detected_sign != previous_sign and (current_time - last_trigger_time > cooldown_time):
                    last_trigger_time = current_time
                    previous_sign = detected_sign
                    trigger_action(detected_sign)
            else:
                # Reset previous sign when hand disappears
                previous_sign = "None"

            # 3. Check idle timeout from gesture.py
            if gesture.is_idle(timeout=15):
                print("\nNo hand detected for 15 seconds. Shutting down...")
                break

            # Prevent high CPU spinning
            time.sleep(0.01)

# 2. Gracefully handle Ctrl+C without showing an ugly Traceback
except KeyboardInterrupt:
    print("\n[SIGINT] Manual exit triggered by user.")

# 3. ALWAYS release hardware resources, no matter what happens!
finally:
    if 'cap' in locals() and cap.isOpened():
        cap.release()
    print("Camera released cleanly. System off.")
    sys.exit(0)