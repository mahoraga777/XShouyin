import json
import subprocess

# Load the user's config file
with open('config.json', 'r') as file:
    gesture_map = json.load(file)

def trigger_action(gesture_name):
    if gesture_name in gesture_map:
        command = gesture_map[gesture_name]
        print(f"Triggering command for {gesture_name}: {command}")
        try:
            subprocess.Popen(command, shell=True)
        except Exception as e:
            print(command,"command failed")
    else:
        print(f"No action mapped for: {gesture_name}")