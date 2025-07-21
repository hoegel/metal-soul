import json
import random
import math
import time
from queue import PriorityQueue
from config import *
from PySide6.QtGui import QColor
from core.projectile import Projectile

class Enemy:
    def __init__(self, x, y, damage, hp, max_hp, speed, size, is_flying, current_room):
        self.x = x
        self.y = y
        self.damage = damage
        self.hp = hp
        self.max_hp = max_hp
        self.base_speed = speed
        self.speed = speed
        self.size = size
        self.room = current_room

        self.is_flying = is_flying

        self.path = []
        self.path_index = 0

        self.dot = {"active": False, "damage": 0, "timer": 0}
        self.stun = {"active": False, "timer": 0, "cooldown": 0}
        self.slow = {"active": False, "factor": 1.0, "timer": 0}
        self.knock_x = 0
        self.knock_y = 0
        self.knock_timer = 0
        self.last_chain_time = 0

    def update(self, player_x, player_y, projectiles):
        self.update_effects()
        if self.stun["active"]:
            return

        if not self.is_flying and self.room.tiles:
            self.move_smart_towards(player_x, player_y)
        else:
            self.move_towards(player_x, player_y)

    def move_towards(self, target_x, target_y):
        if self.stun["active"]:
            return
        
        dx = target_x - (self.x + self.size // 2)
        dy = target_y - (self.y + self.size // 2)
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
        self.x = max(self.x, BORDER_SIZE)
        self.x = min(self.x, ROOM_SIZE[0] - BORDER_SIZE - self.size)
        self.y = max(self.y, BORDER_SIZE)
        self.y = min(self.y, ROOM_SIZE[1] - BORDER_SIZE - self.size)

    def can_walk(self, x, y):
        tile_x = int((x - BORDER_SIZE) // TILE_SIZE)
        tile_y = int((y - BORDER_SIZE) // TILE_SIZE)
        if 0 <= tile_y < len(self.room.tiles) and 0 <= tile_x < len(self.room.tiles[0]):
            return self.room.tiles[tile_y][tile_x].is_walkable(self)
        return False
    
    def move_smart_towards(self, target_x, target_y):
        if self.stun["active"] or self.is_flying:
            return

        if not hasattr(self, 'path') or not self.path or random.random() < 0.01:
            start = (
                int((self.x + self.size // 2 - BORDER_SIZE) // TILE_SIZE),
                int((self.y + self.size // 2 - BORDER_SIZE) // TILE_SIZE)
            )
            goal = (
                int((target_x - BORDER_SIZE) // TILE_SIZE),
                int((target_y - BORDER_SIZE) // TILE_SIZE)
            )

            self.path = a_star(start, goal, self.room.tiles, self)
            self.path_index = 0

        if hasattr(self, 'path') and self.path and self.path_index < len(self.path):
            tx, ty = self.path[self.path_index]
            target_px = tx * TILE_SIZE + BORDER_SIZE + TILE_SIZE // 2
            target_py = ty * TILE_SIZE + BORDER_SIZE + TILE_SIZE // 2

            dx = target_px - (self.x + self.size // 2)
            dy = target_py - (self.y + self.size // 2)
            dist = math.hypot(dx, dy)

            if dist < 2:
                self.path_index += 1
            else:
                self.x += self.speed * dx / dist
                self.y += self.speed * dy / dist


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

    def check_contact_with_player(self, player_x, player_y, player_size):
        dx = (self.x + self.size / 2) - (player_x + player_size / 2)
        dy = (self.y + self.size / 2) - (player_y + player_size / 2)
        distance = math.hypot(dx, dy)
        return distance < (self.size + player_size) / 2


class ShooterEnemy(Enemy):
    def __init__(self, x, y, cooldown=90, damage=5, hp=30, max_hp=30, speed=0.6, size=24, is_flying=False, current_room=None):
        super().__init__(x, y, damage, hp, max_hp, speed, size, is_flying, current_room)
        self.shoot_cooldown = cooldown
        self.shoot_timer = cooldown

    def update(self, player_x, player_y, projectiles):
        super().update(player_x, player_y, projectiles)

        if self.stun["active"]:
            return

        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        else:
            proj = Projectile(
                source="enemy", target_type="player",
                x=self.x + self.size / 2, y=self.y + self.size / 2,
                tx=player_x, ty=player_y,
                damage=self.damage, speed=4, range_=500,
                color=QColor(255, 0, 0), radius=5
            )
            projectiles.append(proj)
            self.shoot_timer = self.shoot_cooldown

class CrossShooterEnemy(Enemy):
    def __init__(self, x, y, cooldown=150, damage=4, hp=40, max_hp=40, speed=0.4, size=26, is_flying=False, current_room=None):
        super().__init__(x, y, damage, hp, max_hp, speed, size, is_flying, current_room)
        self.shoot_cooldown = cooldown
        self.shoot_timer = cooldown
        self.rotation = False

    def update(self, player_x, player_y, projectiles):
        self.update_effects()

        if self.stun["active"]:
            return

        self.move_randomly()
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        else:
            if not self.rotation:
                dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            else:
                dirs = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
            for dx, dy in dirs:
                proj = Projectile(
                    source="enemy", target_type="player",
                    x=self.x + self.size / 2, y=self.y + self.size / 2,
                    tx=self.x + dx * 100, ty=self.y + dy * 100,
                    damage=self.damage, speed=3, range_=400,
                    color=QColor(255, 128, 0), radius=5
                )
                projectiles.append(proj)
            self.shoot_timer = self.shoot_cooldown
            self.rotation = not self.rotation

    def move_randomly(self):
        if random.random() < 0.02:
            angle = random.uniform(0, 2 * math.pi)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed

            new_x = self.x + dx
            new_y = self.y + dy

            if self.is_flying:
                self.x = new_x
                self.y = new_y
            else:
                # Проверяем тайлы по центру врага
                center_new_x = new_x + self.size // 2
                center_new_y = new_y + self.size // 2

                tile_x = int((center_new_x - BORDER_SIZE) // TILE_SIZE)
                tile_y = int((center_new_y - BORDER_SIZE) // TILE_SIZE)

                if (
                    0 <= tile_y < len(self.room.tiles)
                    and 0 <= tile_x < len(self.room.tiles[0])
                    and self.room.tiles[tile_y][tile_x].is_walkable(self)
                ):
                    self.x = new_x
                    self.y = new_y

        # Границы комнаты
        self.x = max(self.x, BORDER_SIZE)
        self.x = min(self.x, ROOM_SIZE[0] - BORDER_SIZE - self.size)
        self.y = max(self.y, BORDER_SIZE)
        self.y = min(self.y, ROOM_SIZE[1] - BORDER_SIZE - self.size)



def load_enemies_from_json(path, hp_multiplier, damage_multiplier, current_room):
    with open(path, 'r') as f:
        data = json.load(f)

    enemies = []
    for entry in data.get("enemies", []):
        enemy_type = entry.get("type", "base")
        x = entry.get("x", random.randint(100, 700))
        y = entry.get("y", random.randint(100, 500))
        damage = int(entry.get("damage", 10) * damage_multiplier)
        hp = int(entry.get("hp", 20) * hp_multiplier)
        max_hp = int(entry.get("max_hp", 20) * hp_multiplier)
        speed = entry.get("speed", 1.5)
        size = entry.get("size", 20)
        is_flying = entry.get("is_flying", False)

        if enemy_type == "shooter":
            cooldown = entry.get("cooldown", 90)
            enemies.append(ShooterEnemy(x, y, cooldown, damage, hp, max_hp, speed, size, is_flying, current_room))
        elif enemy_type == "cross_shooter":
            cooldown = entry.get("cooldown", 90)
            enemies.append(CrossShooterEnemy(x, y, cooldown, damage, hp, max_hp, speed, size, is_flying, current_room))
        else:
            enemies.append(Enemy(x, y, damage, hp, max_hp, speed, size, is_flying, current_room))

    return enemies


def a_star(start, goal, tiles, entity):
    width = len(tiles[0])
    height = len(tiles)
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        _, current = frontier.get()

        if current == goal:
            break

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = current[0] + dx, current[1] + dy
            if 0 <= nx < width and 0 <= ny < height:
                if tiles[ny][nx].is_walkable(entity):
                    new_cost = cost_so_far[current] + 1
                    if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                        cost_so_far[(nx, ny)] = new_cost
                        priority = new_cost + abs(goal[0]-nx) + abs(goal[1]-ny)
                        frontier.put((priority, (nx, ny)))
                        came_from[(nx, ny)] = current

    path = []
    current = goal
    while current and current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path