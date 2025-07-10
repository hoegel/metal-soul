import time

class Shield:
    def __init__(self):
        self.max_charges = 2
        self.cooldown = 20  # seconds
        self.active_duration = 7  # seconds
        self.charges = self.max_charges
        self.last_used_times = []
        self.active_until = 0

    def activate(self):
        if self.charges > 0 and not self.is_active():
            self.charges -= 1
            self.active_until = time.time() + self.active_duration
            self.last_used_times.append(time.time())
            return True
        return False

    def is_active(self):
        return time.time() < self.active_until

    def update(self):
        now = time.time()
        self.last_used_times = [t for t in self.last_used_times if now - t < self.cooldown]
        self.charges = self.max_charges - len(self.last_used_times)

    def absorb_hit(self):
        if self.is_active():
            self.active_until = 0
            return True
        return False

    def get_cooldown(self):
        return self.cooldown
    
    def get_next_cooldown(self):
        now = time.time()
        if self.charges < self.max_charges:
            remaining_times = [self.cooldown - (now - t) for t in self.last_used_times]
            remaining_times = [rt for rt in remaining_times if rt > 0]
            if remaining_times:
                return min(remaining_times)
        return 0