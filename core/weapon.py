from abc import ABC, abstractmethod
from config import ROOM_SIZE
import math
import time

class Weapon(ABC):
    def __init__(self, player):
        self.observers = []
        self.effect = []
        self.last_attack_time = 0
        self.cooldown = 1.0
        self.player = player

    def add_effect(self, effect):
        if len(self.effect) < 3:
            self.effect.append(effect)
            return True
        return False

    def subscribe(self, callback):
        self.observers.append(callback)

    def notify(self, hit_enemies):
        for callback in self.observers:
            callback(hit_enemies)

    def can_attack(self):
        return (time.time() - self.last_attack_time) >= self.cooldown
    
    def reset_cooldown(self):
        self.last_attack_time = time.time()

    def get_stats(self):
        return {
            "cooldown": self.cooldown,
            "effects": [e.name for e in self.effect]
        }
    
    @abstractmethod
    def attack(self, player_pos, target_pos, enemies):
        pass

class Melee(Weapon):
    def __init__(self, player):
        super().__init__(player)
        self.damage = 8
        self.radius = 40
        self.angle_range = math.pi / 2
        self.cooldown = 0.3

    def attack(self, player_pos, target_pos, enemies):
        if not self.can_attack():
            return
        
        self.reset_cooldown()

        px, py = player_pos
        tx, ty = target_pos

        hit = []

        dx = tx - px
        dy = ty - py
        main_angle = math.atan2(dy, dx)

        for enemy in enemies:
            ex, ey, esize, _ = enemy.rect()
            ex += esize / 2
            ey += esize / 2
            vec_x = ex - px
            vec_y = ey - py
            dist = math.hypot(vec_x, vec_y)

            if dist > self.radius + esize:
                continue

            angle_to_enemy = math.atan2(vec_y, vec_x)
            angle_diff = abs(self.normalize_angle(angle_to_enemy - main_angle))

            if angle_diff <= self.angle_range:
                if enemy.take_damage(self.damage):
                    hit.append(enemy)
                elif self.effect:
                    for eff in self.effect:
                        if eff.name != "wah":
                            eff.apply(enemy)
                        else:
                            eff.apply(self.player)
        
        self.notify(hit)

    @staticmethod
    def normalize_angle(angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

class Beam(Weapon):
    def __init__(self, player):
        super().__init__(player)
        self.damage = 12
        self.threshold = 10
        self.cooldown = 1.0

    def attack(self, player_pos, target_pos, enemies): 
        if not self.can_attack():
            return
        
        self.reset_cooldown()
        
        px, py = player_pos
        tx, ty = target_pos

        # Вычисление конечной точки на границе комнаты
        beam_end = self._compute_wall_intersection(px, py, tx, ty)
        if not beam_end:
            return

        bx, by = beam_end
        hit = []

        # Вектор луча
        dx = bx - px
        dy = by - py
        len_sq = dx ** 2 + dy ** 2 if dx or dy else 1

        for enemy in enemies:
            ex, ey, esize, _ = enemy.rect()
            ex += esize / 2
            ey += esize / 2

            # проекция точки врага на луч
            t = max(0, min(1, ((ex - px) * dx + (ey - py) * dy) / len_sq))
            closest_x = px + t * dx
            closest_y = py + t * dy

            dist = math.hypot(closest_x - ex, closest_y - ey)
            if dist < self.threshold + esize:
                if enemy.take_damage(self.damage):
                    hit.append(enemy)
                elif self.effect:
                    for eff in self.effect:
                        if eff.name != "wah":
                            eff.apply(enemy)
                        else:
                            eff.apply(self.player)

        self.notify(hit)

    def _compute_wall_intersection(self, px, py, tx, ty):
        from PySide6.QtCore import QRectF
        rect = QRectF(0, 0, *ROOM_SIZE)

        dx = tx - px
        dy = ty - py

        if dx == 0 and dy == 0:
            return None

        t_values = []

        # левая и правая границы (x = const)
        if dx != 0:
            for x_edge in (rect.left(), rect.right()):
                t = (x_edge - px) / dx
                if t > 0:
                    y = py + t * dy
                    if rect.top() <= y <= rect.bottom():
                        t_values.append((t, x_edge, y))

        # верхняя и нижняя границы (y = const)
        if dy != 0:
            for y_edge in (rect.top(), rect.bottom()):
                t = (y_edge - py) / dy
                if t > 0:
                    x = px + t * dx
                    if rect.left() <= x <= rect.right():
                        t_values.append((t, x, y_edge))

        if not t_values:
            return None

        # вернуть ближайшую точку пересечения
        t_values.sort(key=lambda v: v[0])
        _, bx, by = t_values[0]
        return bx, by

class Bomb(Weapon):
    def __init__(self, player):
        super().__init__(player)
        self.damage = 18
        self.radius = 50
        self.tod = 10

    def attack(self, player_pos, target_pos, enemies):
        if not self.can_attack():
            return
        
        self.reset_cooldown()

        tx, ty = target_pos
        hit = []

        for enemy in enemies:
            ex, ey, esize, _ = enemy.rect()
            ex += esize / 2
            ey += esize / 2
            dist = math.hypot(ex - tx, ey - ty)
            if dist < self.radius + esize:
                if enemy.take_damage(self.damage):
                    hit.append(enemy)
                elif self.effect:
                    for eff in self.effect:
                        if eff.name != "wah":
                            eff.apply(enemy)
                        else:
                            eff.apply(self.player)
        px, py = player_pos
        dist = math.hypot(px - tx, py - ty)
        if dist < self.radius:
            if self.player.take_damage(self.damage):
                pass

        self.notify(hit)