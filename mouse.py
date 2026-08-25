import math
import tkinter as tk
from evdev import UInput, ecodes as e, AbsInfo

class MouseController:
    """
    Direct kernel-level mouse controller.
    Writes zero-latency hardware interrupts to /dev/uinput.
    """
    
    def __init__(self):
        # 1. Hardware Resolution
        root = tk.Tk()
        root.withdraw()
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()
        
        # 2. Kernel Device Initialization
        # We define a virtual hardware device with absolute positioning capabilities
        cap = {
            e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT],
            e.EV_ABS: [
                (e.ABS_X, AbsInfo(value=0, min=0, max=self.screen_w, fuzz=0, flat=0, resolution=0)),
                (e.ABS_Y, AbsInfo(value=0, min=0, max=self.screen_h, fuzz=0, flat=0, resolution=0))
            ]
        }
        self.ui = UInput(cap, name="xshouyan-pointer")
        
        # 3. State & Filter Variables
        self.curr_x: float = 0.0
        self.curr_y: float = 0.0
        self.is_first_move: bool = True
        
        self.deadzone_px: float = 1.0 
        self.min_dist: float = 5.0    
        self.max_dist: float = 80.0   
        self.min_alpha: float = 0.15  
        self.max_alpha: float = 1.0   

    def _calculate_dynamic_alpha(self, distance: float) -> float:
        """Calculates kinematic filter weight."""
        if distance >= self.max_dist: return self.max_alpha
        if distance <= self.min_dist: return self.min_alpha
        
        ratio = (distance - self.min_dist) / (self.max_dist - self.min_dist)
        return self.min_alpha + ratio * (self.max_alpha - self.min_alpha)

    def move_absolute(self, cam_x: float, cam_y: float) -> None:
        """Maps coordinates and dispatches direct memory writes to the kernel."""
        # Removed the (1.0 - cam_x) inversion here
        target_x = cam_x * self.screen_w
        target_y = cam_y * self.screen_h

        if self.is_first_move:
            self.curr_x, self.curr_y = target_x, target_y
            self.is_first_move = False
            return

        distance = math.hypot(target_x - self.curr_x, target_y - self.curr_y)
        
        if distance < self.deadzone_px:
            return 
            
        alpha = self._calculate_dynamic_alpha(distance)

        self.curr_x += (target_x - self.curr_x) * alpha
        self.curr_y += (target_y - self.curr_y) * alpha

        # Zero-Latency Event Dispatch
        self.ui.write(e.EV_ABS, e.ABS_X, int(self.curr_x))
        self.ui.write(e.EV_ABS, e.ABS_Y, int(self.curr_y))
        self.ui.syn()

    def reset(self) -> None:
        self.is_first_move = True

    def left_click(self) -> None:
        """Simulates physical hardware interrupts for click down, then click up."""
        self.ui.write(e.EV_KEY, e.BTN_LEFT, 1)
        self.ui.syn()
        self.ui.write(e.EV_KEY, e.BTN_LEFT, 0)
        self.ui.syn()

    def right_click(self) -> None:
        self.ui.write(e.EV_KEY, e.BTN_RIGHT, 1)
        self.ui.syn()
        self.ui.write(e.EV_KEY, e.BTN_RIGHT, 0)
        self.ui.syn()