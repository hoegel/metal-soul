import json
import random
import math
import time
from PySide6.QtGui import QColor
from core.projectile import Projectile
from core.enemy import *

class BossEnemy(Enemy):
    def __init__(self, x, y, hp_multiplier, damage_multiplier, hp=500, speed=0.7, size=60, current_room=None):
        super().__init__(x, y, damage=int(15 * damage_multiplier), hp=int(hp * hp_multiplier), max_hp=int(hp * hp_multiplier), speed=speed, size=size, is_flying=True, current_room=current_room)
        self.attack_timer = 120

    def update_effects(self):
        if self.dot["active"]:
            self.dot["timer"] -= 1
            if self.dot["timer"] % 30 == 0:
                self.hp -= self.dot["damage"]
            if self.dot["timer"] <= 0:
                self.dot["active"] = False

        if self.stun["cooldown"] > 0:
            self.stun["cooldown"] -= 1
        if self.stun["active"]:
            self.stun["timer"] -= 2
            if self.stun["timer"] <= 0:
                self.stun["active"] = False

        if self.slow["active"]:
            self.slow["timer"] -= 1
            if self.slow["timer"] <= 0:
                self.slow["active"] = False
                self.speed = self.base_speed

class BossShooter(BossEnemy):
    def __init__(self, x, y, hp_multiplier, damage_multiplier, current_room):
        super().__init__(x, y, hp_multiplier, damage_multiplier, hp=500, speed=0.3, size=60, current_room=current_room)

    def update(self, player_x, player_y, projectiles):
        super().update(player_x, player_y, projectiles)
        if self.stun["active"]:
            return
        
        self.attack_timer -= 1
        if self.attack_timer <= 0:
            for angle in range(0, 360, 20):
                rad = math.radians(angle)
                tx = self.x + self.size / 2 + math.cos(rad) * 100
                ty = self.y + self.size / 2 + math.sin(rad) * 100
                projectiles.append(Projectile("enemy", "player", self.x + self.size / 2, self.y + self.size / 2, tx, ty, 8, 3, 600, QColor(200, 0, 200), 6))
            self.attack_timer = 180

class BossCharger(BossEnemy):
    def __init__(self, x, y, hp_multiplier, damage_multiplier, current_room):
        super().__init__(x, y, hp_multiplier, damage_multiplier, hp=600, speed=1.5, size=70, current_room=current_room)
        self.charge_cooldown = 300
        self.charging = False
        self.charge_target = None

    def update(self, player_x, player_y, projectiles):
        self.update_effects()
        if self.stun["active"]:
            return

        if self.charging:
            dx = self.charge_target[0] - (self.x + self.size // 2)
            dy = self.charge_target[1] - (self.y + self.size // 2)
            dist = math.hypot(dx, dy)
            if dist > self.size // 2:
                self.x += dx / dist * self.speed * 2
                self.y += dy / dist * self.speed * 2
                self.x = max(self.x, BORDER_SIZE)
                self.x = min(self.x, ROOM_SIZE[0] - BORDER_SIZE - self.size)
                self.y = max(self.y, BORDER_SIZE)
                self.y = min(self.y, ROOM_SIZE[1] - BORDER_SIZE - self.size)
            else:
                self.charging = False
                self.charge_cooldown = 240
        else:
            self.move_towards(player_x, player_y)
            self.charge_cooldown -= 1
            if self.charge_cooldown <= 0:
                self.charging = True
                self.charge_target = (player_x, player_y)

class BossSpawner(BossEnemy):
    def __init__(self, x, y, hp_multiplier, damage_multiplier, current_room):
        super().__init__(x, y, hp_multiplier, damage_multiplier, hp=450, speed=0.3, size=80, current_room=current_room)
        self.spawn_timer = 180

    def update(self, player_x, player_y, enemies):
        self.update_effects()
        if self.stun["active"]:
            return

        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            for _ in range(2):
                spawn_x = self.x + random.randint(-60, 60)
                spawn_y = self.y + random.randint(-60, 60)
                spawn_x = max(spawn_x, BORDER_SIZE)
                spawn_x = min(spawn_x, ROOM_SIZE[0] - BORDER_SIZE - 18)
                spawn_y = max(spawn_y, BORDER_SIZE)
                spawn_y = min(spawn_y, ROOM_SIZE[1] - BORDER_SIZE - 18)
                enemies.append(Enemy(spawn_x, spawn_y, 5, 15, 15, 1.0, 18))
            for _ in range(2):
                spawn_x = self.x + random.randint(-60, 60)
                spawn_y = self.y + random.randint(-60, 60)
                spawn_x = max(spawn_x, BORDER_SIZE)
                spawn_x = min(spawn_x, ROOM_SIZE[0] - BORDER_SIZE - 18)
                spawn_y = max(spawn_y, BORDER_SIZE)
                spawn_y = min(spawn_y, ROOM_SIZE[1] - BORDER_SIZE - 18)
                enemies.append(ShooterEnemy(spawn_x, spawn_y, 80, 5, 15, 15, 1.0, 18))
            self.spawn_timer = 300

        self.move_towards(player_x, player_y)