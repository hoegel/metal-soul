from core.weapon import Melee, Beam, Bomb

class Player:
    def __init__(self):
        self.damage = 30
        self.max_hp = 100
        self.hp = 100
        self.speed = 4

        self.attack_type = 1
        self.weapons = {
            1: Melee(),
            2: Beam(),
            3: Bomb()
        }

    def set_attack_type(self, atk_id):
        if atk_id in self.weapons:
            self.attack_type = atk_id

    def attack(self, player_pos, target_pos, enemies):
        weapon = self.weapons[self.attack_type]
        weapon.attack(player_pos, target_pos, enemies)

    def get_stats(self):
        return self.damage, self.hp, self.max_hp, self.speed