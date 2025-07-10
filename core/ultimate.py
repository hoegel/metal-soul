import time

class Ultimate:
    def __init__(self, duration=10, cooldown=60):
        self.duration = duration
        self.cooldown = cooldown
        self.start_time = 0
        # self.last_used = time.time()
        self.last_used = 0
        self.pause_start = 0
        self.dtime = 0

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

    def get_cooldown(self):
        return self.cooldown
    
    def on_pause_on(self):
        self.pause_start = time.time()
        
    def on_pause_off(self):
        self.dtime = time.time() - self.pause_start

        # Если в момент паузы ролл был активен — корректируем start_time
        if self.is_active:
            self.start_time += self.dtime
        else:
            # Если не активен, то значит cooldown идет — нужно поправить last_end_time
            self.last_used += self.dtime