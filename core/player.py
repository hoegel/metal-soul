from core.weapon import Melee, Beam, Bomb

class Player:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.size = 20
        self.damage = 30
        self.max_hp = 100
        self.hp = 100
        self.speed = 4
        self.invincible = False
        self.invincible_timer = 0

        self.attack_type = 1
        self.weapons = {
            1: Melee(self),
            2: Beam(self),
            3: Bomb(self)
        }
        self.weapon = self.weapons[self.attack_type]

        self.enemies = []

    def set_attack_type(self, atk_id):
        if atk_id in self.weapons:
            self.attack_type = atk_id

    def attack(self, player_pos, target_pos, enemies):
        self.weapon = self.weapons[self.attack_type]
        self.weapon.attack(player_pos, target_pos, enemies)

    def get_stats(self):
        return self.damage, self.hp, self.max_hp, self.speed
    
    def take_damage(self, damage):
        if self.invincible:
            return
        self.hp = self.hp - damage if self.hp > damage else 0
        self.invincible = True
        self.invincible_timer = 60

    def update_invincibility(self):
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def heal_percent(self, percent):
        self.hp = min(self.hp + int(self.max_hp * percent / 100), self.max_hp)