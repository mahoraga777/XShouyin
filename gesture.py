import cv2
import mediapipe as mp
import time

#### MediaPipe Task Imports ####

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

#### State storage for recognized gesture ####

current_gesture = "None"
confidence_score = 0.0

#track exact second hand was last seen
last_seen_time = time.time()

#### Callback function executed in background thread whenever MediaPipe processes a frame ####

def handle_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global current_gesture, confidence_score, last_seen_time
    
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

#### Configure options, setting up hardware and path  ####
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='gesture_recognizer.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=handle_result
)

### live webcam loop ##

# saifty fall back # 
with GestureRecognizer.create_from_options(options) as recognizer:
    cap = cv2.VideoCapture(0)  # now we are up for live video 
    
    # todo: insted of opning video all the time what if we have shortcut to open it
    # todo: what if insted of 30fps we took low process speed while we are not using it and increase the speed once we see piticualr hand sign

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert BGR to RGB for MediaPipe since openCV don't support human redibility 
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Monotonically increasing timestamp
        timestamp_ms = int(time.time() * 1000)
        
        #provide image to mediaPipe ai 
        recognizer.recognize_async(mp_image, timestamp_ms)

        ### logic to break the loop when hand not seen for n = 15 sec 
        idle_time = time.time() - last_seen_time

        if idle_time > 15:
            print("me no see no hand")
            break

        # Print feed to terminal or handle sign stream
        if current_gesture != "None":
            print(f"Detected Sign: {current_gesture} ({confidence_score * 100:.1f}%)")

    cap.release()