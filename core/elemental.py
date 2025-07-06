class Element:
    def __init__(self, name):
        self.name = name

    def apply(self, enemy):
        pass

class Delay(Element):
    def __init__(self):
        super().__init__("delay")

    def apply(self, enemy):
        enemy.apply_dot(damage=1, duration=3)

class Fuzz(Element):
    def __init__(self):
        super().__init__("fuzz")

    def apply(self, enemy):
        enemy.apply_stun(duration=2)

class Overdrive(Element):
    def __init__(self):
        super().__init__("overdrive")

    def apply(self, enemy):
        enemy.apply_slow(factor=0.67, duration=4)

class Wah(Element):
    def __init__(self, player):
        super().__init__("wah")
        self.player = player

    def apply(self, enemy):
        self.player.heal_percent(3)

class Tremolo(Element):
    def __init__(self, all_enemies):
        super().__init__("tremolo")
        self.all_enemies = all_enemies

    def apply(self, enemy):
        enemy.apply_chain_damage(damage=2, all_enemies=self.all_enemies)

class Distortion(Element):
    def __init__(self):
        super().__init__("distortion")

    def apply(self, enemy):
        enemy.knockback(force=10)
