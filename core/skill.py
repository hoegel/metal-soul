class Skill:
    def __init__(self, name, cooldown, range_, damage, slot_type):
        self.name = name
        self.cooldown = cooldown
        self.range = range_
        self.damage = damage
        self.slot_type = slot_type
        self.last_used = 0
