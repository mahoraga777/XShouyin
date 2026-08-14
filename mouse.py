import subprocess
import math

class MouseController:
    def __init__(self, screen_width=1920, screen_height=1080, smoothing=0.6, deadzone=1.0):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.smoothing = smoothing
        self.deadzone = deadzone
        self.prev_x = 0.0
        self.prev_y = 0.0

    def move(self, norm_x, norm_y):
        target_x = (1.0 - norm_x) * self.screen_width
        target_y = norm_y * self.screen_height

        if self.prev_x == 0.0 and self.prev_y == 0.0:
            self.prev_x = target_x
            self.prev_y = target_y
            return

        new_x = self.prev_x + (target_x - self.prev_x) * self.smoothing
        new_y = self.prev_y + (target_y - self.prev_y) * self.smoothing

        distance = math.hypot(new_x - self.prev_x, new_y - self.prev_y)

        if distance > self.deadzone:
            # Clamp coordinates so they cannot exceed screen boundaries
            new_x = max(0, min(self.screen_width, new_x))
            new_y = max(0, min(self.screen_height, new_y))

            # Use explicit -x and -y flags 
            command = ["ydotool", "mousemove", "-a", "-x", str(int(new_x)), "-y", str(int(new_y))]
            subprocess.Popen(command)
            
            self.prev_x = new_x
            self.prev_y = new_y

    def reset(self):
        self.prev_x = 0.0
        self.prev_y = 0.0

    def left_click(self):
        # 0xC0 is the hardware code for a Left Click
        subprocess.Popen(["ydotool", "click", "0xC0"])