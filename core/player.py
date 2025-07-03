class Player:
    def __init__(self):
        self.damage = 30
        self.max_hp = 100
        self.hp = 100
        self.speed = 4

        self.attack_type = 1  # 1 - ближняя, 2 - луч, 3 - бомба

    def set_attack_type(self, number):
        if number in (1, 2, 3):
            self.attack_type = number

    def get_stats(self):
        return self.damage, self.hp, self.max_hp, self.speed