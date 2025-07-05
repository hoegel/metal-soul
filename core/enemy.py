import json
import random

class Enemy:
    def __init__(self, x, y, damage, hp, max_hp, speed, size):
        self.x = x
        self.y = y
        self.damage = damage
        self.hp = hp
        self.max_hp = max_hp
        self.speed = speed
        self.size = size

    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = max((dx**2 + dy**2) ** 0.5, 0.01)
        self.x += self.speed * dx / distance
        self.y += self.speed * dy / distance

    def take_damage(self, dmg):
        self.hp -= dmg
        return self.hp <= 0

    def rect(self):
        return (self.x, self.y, self.size, self.size)


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