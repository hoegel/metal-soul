import math
from PySide6.QtGui import QColor
from config import *

class Projectile:
    def __init__(self, source, target_type, x, y, tx, ty, damage=10, speed=5, range_=500, color=QColor(255, 255, 255), radius=5):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.damage = damage
        self.speed = speed
        self.range = range_
        self.color = color
        self.radius = radius
        self.source = source
        self.target_type = target_type
        self.spectral = False

        dx = tx - x
        dy = ty - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dx, dy = 1, 0
            dist = 1
        self.dir_x = dx / dist
        self.dir_y = dy / dist

        self.alive = True

    def update(self, current_room):
        if not self.alive:
            return

        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed

        traveled = math.hypot(self.x - self.start_x, self.y - self.start_y)
        if traveled >= self.range:
            self.alive = False

        if self.x < BORDER_SIZE // 2 or self.x > ROOM_SIZE[0] - BORDER_SIZE:
            self.alive = False
        if self.y < BORDER_SIZE // 2 or self.y > ROOM_SIZE[1] - BORDER_SIZE:
            self.alive = False

        tile_x = int((self.x - BORDER_SIZE) // TILE_SIZE)
        tile_y = int((self.y - BORDER_SIZE) // TILE_SIZE)
        if (
            0 <= tile_y < len(current_room.tiles) and
            0 <= tile_x < len(current_room.tiles[0])
        ):
            tile = current_room.tiles[tile_y][tile_x]
            if not tile.is_projectile_passable(self):
                self.alive = False

    def check_collision(self, targets):
        if not self.alive:
            return []

        hit_targets = []
        for target in targets:
            if self.target_type == "enemy" and hasattr(target, 'rect'):
                tx, ty, tw, th = target.rect()
            elif self.target_type == "player":
                tx, ty = target.x, target.y
                tw, th = target.size, target.size
            else:
                continue

            dist = math.hypot(self.x - (tx + tw/2), self.y - (ty + th/2))
            if dist <= self.radius + tw / 2:
                hit_targets.append(target)

        if hit_targets:
            self.alive = False

        return hit_targets

    def draw(self, painter):
        painter.setBrush(self.color)
        painter.setPen(QColor(0, 0, 0, 0))
        painter.drawEllipse(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
