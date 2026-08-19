import subprocess
import math

class MouseController:
    def __init__(self, sensitivity=2.5, smoothing=0.3, deadzone=0.002):
        self.prev_cam_x = None
        self.prev_cam_y = None
        
        # Velocity accumulators for the gliding effect
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        self.sensitivity = sensitivity
        self.smoothing = smoothing
        self.deadzone = deadzone  # Filters out camera noise

    def move_relative(self, camera_x, camera_y):
        # 1. Drop anchor on the first frame
        if self.prev_cam_x is None:
            self.prev_cam_x = camera_x
            self.prev_cam_y = camera_y
            return

        # 2. Calculate the delta (finger movement distance)
        # We negate X to account for the webcam mirror effect
        delta_x = -(camera_x - self.prev_cam_x)
        delta_y = (camera_y - self.prev_cam_y)

        self.prev_cam_x = camera_x
        self.prev_cam_y = camera_y

        # 3. Filter out micro-jitters
        if math.hypot(delta_x, delta_y) < self.deadzone:
            return

        # 4. Multiply finger twitches into screen pixels
        # Assuming standard 1080p ratio base for multiplication
        target_vel_x = delta_x * 1920 * self.sensitivity
        target_vel_y = delta_y * 1080 * self.sensitivity

        # 5. Apply Low-Pass smoothing to the velocity
        self.vel_x += (target_vel_x - self.vel_x) * self.smoothing
        self.vel_y += (target_vel_y - self.vel_y) * self.smoothing

        # 6. Push to kernel
        if abs(self.vel_x) > 1 or abs(self.vel_y) > 1:
            command = ["ydotool", "mousemove", "-x", str(int(self.vel_x)), "-y", str(int(self.vel_y))]
            subprocess.Popen(command)

    def reset(self):
        # Clears the anchor so the mouse doesn't jump when you drop your hand
        self.prev_cam_x = None
        self.prev_cam_y = None
        self.vel_x = 0.0
        self.vel_y = 0.0

    def left_click(self):
        subprocess.Popen(["ydotool", "click", "0xC0"])