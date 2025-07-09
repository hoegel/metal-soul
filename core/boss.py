import json
import random
import math
import time
from PySide6.QtGui import QColor
from core.projectile import Projectile
from core.enemy import *

class BossEnemy(Enemy):
    def __init__(self, x, y, hp=500, speed=0.7, size=60):
        super().__init__(x, y, damage=15, hp=hp, max_hp=hp, speed=speed, size=size)
        self.attack_timer = 120

    def update_effects(self):
        # Боссы получают меньше урона от эффектов
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
    def update(self, player_x, player_y, projectiles):
        super().update(player_x, player_y, projectiles)
        if self.stun["active"]:
            return
        
        self.attack_timer -= 1
        if self.attack_timer <= 0:
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                tx = self.x + math.cos(rad) * 100
                ty = self.y + math.sin(rad) * 100
                projectiles.append(Projectile("enemy", "player", self.x + self.size / 2, self.y + self.size / 2, tx, ty, 8, 3, 600, QColor(200, 0, 200), 6))
            self.attack_timer = 180

class BossCharger(BossEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=600, speed=1.5, size=70)
        self.charge_cooldown = 300
        self.charging = False
        self.charge_target = None

    def update(self, player_x, player_y, projectiles):
        self.update_effects()
        if self.stun["active"]:
            return

        if self.charging:
            dx = self.charge_target[0] - self.x
            dy = self.charge_target[1] - self.y
            dist = math.hypot(dx, dy)
            if dist > 10:
                self.x += dx / dist * self.speed * 2
                self.y += dy / dist * self.speed * 2
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
    def __init__(self, x, y):
        super().__init__(x, y, hp=450, speed=0.3, size=80)
        self.spawn_timer = 180

    def update(self, player_x, player_y, enemies):
        self.update_effects()
        if self.stun["active"]:
            return

        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            for _ in range(2):
                spawn_x = self.x + random.randint(-40, 40)
                spawn_y = self.y + random.randint(-40, 40)
                enemies.append(Enemy(spawn_x, spawn_y, 5, 15, 15, 1.0, 18))
            self.spawn_timer = 300

        self.move_towards(player_x, player_y)