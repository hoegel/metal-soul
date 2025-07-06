import json
import random
import math
import time

class Enemy:
    def __init__(self, x, y, damage, hp, max_hp, speed, size):
        self.x = x
        self.y = y
        self.damage = damage
        self.hp = hp
        self.max_hp = max_hp
        self.base_speed = speed
        self.speed = speed
        self.size = size

        self.dot = {"active": False, "damage": 0, "timer": 0}
        self.stun = {"active": False, "timer": 0, "cooldown": 0}
        self.slow = {"active": False, "factor": 1.0, "timer": 0}
        self.knock_x = 0
        self.knock_y = 0
        self.knock_timer = 0
        self.last_chain_time = 0

    def move_towards(self, target_x, target_y):
        self.update_effects()

        if self.stun["active"]:
            return
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        if self.knock_timer > 0:
            self.x += self.knock_x
            self.y += self.knock_y
            self.knock_timer -= 1
            return

        speed = self.speed
        self.x += speed * dx / dist
        self.y += speed * dy / dist

    def update_effects(self):
        # DOT
        if self.dot["active"]:
            self.dot["timer"] -= 1
            if self.dot["timer"] % 20 == 0:
                self.hp -= self.dot["damage"]
            if self.dot["timer"] <= 0:
                self.dot["active"] = False

        # Stun
        if self.stun["cooldown"] > 0:
            self.stun["cooldown"] -= 1

        if self.stun["active"]:
            self.stun["timer"] -= 1
            if self.stun["timer"] <= 0:
                self.stun["active"] = False

        # Slow
        if self.slow["active"]:
            self.slow["timer"] -= 1
            if self.slow["timer"] <= 0:
                self.slow["active"] = False
                self.speed = self.base_speed

    def take_damage(self, dmg):
        self.hp -= dmg
        return self.hp <= 0

    def rect(self):
        return (self.x, self.y, self.size, self.size)
    
    # --- ЭФФЕКТЫ ---

    def apply_dot(self, damage=1, duration=3):
        self.dot = {"active": True, "damage": damage, "timer": duration * 60}

    def apply_stun(self, duration=2):
        if self.stun["cooldown"] <= 0:
            self.stun = {"active": True, "timer": duration * 60, "cooldown": 420}

    def apply_slow(self, factor=0.67, duration=4):
        self.slow = {"active": True, "factor": factor, "timer": duration * 60}
        self.speed = self.base_speed * factor

    def apply_chain_damage(self, damage=2, all_enemies=None, chain_radius=300, max_chains=3):
        now = time.time()
        if now - self.last_chain_time < 0.5:
            return  # защита от многократного повторного применения цепи
        self.last_chain_time = now

        self.hp -= damage
        if not all_enemies:
            return

        chains = 0
        for other in all_enemies:
            if other is self:
                continue
            if time.time() - other.last_chain_time < 0.5:
                continue
            dist = math.hypot(self.x - other.x, self.y - other.y)
            if dist < chain_radius:
                other.last_chain_time = now
                other.hp -= damage
                chains += 1
                if chains >= max_chains:
                    break

    def knockback(self, force=10):
        self.knock_timer = 5
        angle = random.uniform(0, 2 * math.pi)
        self.knock_x = force * math.cos(angle)
        self.knock_y = force * math.sin(angle)


def load_enemies_from_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    enemies = []
    for entry in data.get("enemies", []):
        x = entry.get("x", random.randint(100, 700))
        y = entry.get("y", random.randint(100, 500))
        damage = entry.get("damage", 10)
        hp = entry.get("hp", 20)
        max_hp = entry.get("max_hp", 20)
        speed = entry.get("speed", 1.5)
        size = entry.get("size", 20)
        enemies.append(Enemy(x, y, damage, hp, max_hp, speed, size))
    return enemies