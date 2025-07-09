import time

class Ultimate:
    def __init__(self, duration=10, cooldown=60):
        self.duration = duration
        self.cooldown = cooldown
        self.start_time = 0
        # self.last_used = time.time()
        self.last_used = 0

    def can_activate(self):
        return time.time() - self.last_used >= self.cooldown

    def activate(self):
        if self.can_activate():
            self.start_time = time.time()
            self.last_used = self.start_time
            return True
        return False

    def is_active(self):
        return time.time() - self.start_time < self.duration

    def remaining_cooldown(self):
        remaining = self.cooldown - (time.time() - self.last_used)
        return max(0, int(remaining))
