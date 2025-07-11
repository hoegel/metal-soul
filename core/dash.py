# core/dodge_roll.py
import time
from config import *

class DodgeRoll:
    def __init__(self, duration=0.2, cooldown=1.0, distance=120):
        self.active = False
        self.duration = duration
        self.cooldown = cooldown
        self.distance = distance
        self.start_time = 0
        self.last_end_time = -cooldown
        self.direction = (0, 0)
        self.start_pos = (0, 0)
        self.start_time = 0
        self.dtime = 0

    def can_roll(self):
        return not self.active and (time.time() - self.last_end_time) >= self.cooldown

    def start_roll(self, current_pos, direction):
        if not self.can_roll():
            return False
        self.start_time = time.time()
        self.start_pos = current_pos
        self.direction = direction
        self.active = True
        return True

    def update(self):
        if self.active and (time.time() - self.start_time) >= self.duration:
            self.active = False
            self.last_end_time = time.time()

    def get_position(self):
        if not self.active:
            return self.start_pos
        t = (time.time() - self.start_time) / self.duration
        dx = self.direction[0] * self.distance * t
        dy = self.direction[1] * self.distance * t
        x = max(self.start_pos[0] + dx, BORDER_SIZE)
        x = min(self.start_pos[0] + dx, ROOM_SIZE[0] - BORDER_SIZE - 20)
        y = max(self.start_pos[1] + dy, BORDER_SIZE)
        y = min(self.start_pos[1] + dy, ROOM_SIZE[1] - BORDER_SIZE - 20)
        
        return (x, y)
    
    def get_cooldown(self):
        return self.cooldown + self.duration
    
    def on_pause_on(self):
        self.pause_start = time.time()
        
    def on_pause_off(self):
        self.dtime = time.time() - self.pause_start

        if self.active:
            self.start_time += self.dtime
        else:
            self.last_end_time += self.dtime
