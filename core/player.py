from core.weapon import Melee, Beam, Bomb
from core.shield import Shield
from core.dash import DodgeRoll
from core.ultimate import Ultimate
from core.heal import HealFragment

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
        self.score = 0
        self.keys = 0

        self.attack_type = 1
        self.weapons = {
            1: Melee(self),
            2: Beam(self),
            3: Bomb(self)
        }
        self.weapon = self.weapons[self.attack_type]

        self.shield = Shield()
        self.dodge = DodgeRoll()

        self.ultimate = Ultimate()
        self.ult_active_multiplier = 1

        self.heal_fragments = HealFragment()

        self.enemies = []

    def update(self):
        self.shield.update()
        self.dodge.update()
        
    def on_pause_on(self):
        self.shield.on_pause_on()
        self.dodge.on_pause_on()
        
    def on_pause_off(self):
        self.shield.on_pause_off()
        self.dodge.on_pause_off()

    def start_roll(self, direction):
        return self.dodge.start_roll((self.x, self.y), direction)

    def is_dodging(self):
        return self.dodge.active

    def get_position(self):
        if self.dodge.active:
            return self.dodge.get_position()
        return (self.x, self.y)

    def set_attack_type(self, atk_id):
        if atk_id in self.weapons:
            self.attack_type = atk_id
            self.weapon = self.weapons[self.attack_type]

    def attack(self, player_pos, target_pos, enemies):
        self.weapon = self.weapons[self.attack_type]
        self.weapon.attack(player_pos, target_pos, enemies)

    def get_stats(self):
        if self.ultimate.is_active():
            self.ult_active_multiplier = 2
        else:
            self.ult_active_multiplier = 1
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