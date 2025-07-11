class HealFragment:
    MAX_FRAGMENTS = 3

    def __init__(self):
        self.count = 1

    def can_use(self):
        return self.count > 0

    def use(self, player):
        if self.can_use():
            healed = int(player.max_hp * 0.6)
            player.hp = min(player.hp + healed, player.max_hp)
            self.count -= 1
            return True
        return False

    def add(self):
        if self.count < self.MAX_FRAGMENTS:
            self.count += 1
            return True
        return False
    
    def get_count(self):
        return self.count
    
    def get_max_count(self):
        return self.MAX_FRAGMENTS
