from core.weapon import Melee, Beam, Bomb

class Player:
    def __init__(self):
        self.damage = 30
        self.max_hp = 100
        self.hp = 100
        self.speed = 4

        self.attack_type = 1
        self.weapons = {
            1: Melee(self),
            2: Beam(self),
            3: Bomb(self)
        }
        self.weapon = self.weapons[self.attack_type]

    def set_attack_type(self, atk_id):
        if atk_id in self.weapons:
            self.attack_type = atk_id

    def attack(self, player_pos, target_pos, enemies):
        self.weapon = self.weapons[self.attack_type]
        self.weapon.attack(player_pos, target_pos, enemies)

    def get_stats(self):
        return self.damage, self.hp, self.max_hp, self.speed
    
    def take_damage(self, damage):
        self.hp = self.hp - damage if self.hp > damage else 0

    def heal_percent(self, percent):
        self.hp = min(self.hp + int(self.max_hp * percent / 100), self.max_hp)