from core.tiles.base import Tile
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from config import *
from core.player import Player

class RockSpikeTile(Tile):
    def __init__(self, x, y, damage=10):
        super().__init__(x, y)
        self.damage = damage

    def is_walkable(self, entity=None):
        if entity and hasattr(entity, "take_damage") and (entity is Player):
            entity.take_damage(self.damage)
        return False

    def is_projectile_passable(self, projectile=None):
        return False

    def draw(self, painter, tile_size):
        painter.setBrush(QColor(80, 80, 80))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.x * tile_size + BORDER_SIZE, self.y * tile_size + BORDER_SIZE, tile_size, tile_size)

        painter.setBrush(QColor(200, 0, 0))
        center_x = self.x * tile_size + BORDER_SIZE + tile_size // 2
        center_y = self.y * tile_size + BORDER_SIZE + tile_size // 2
        size = tile_size // 3
        painter.drawEllipse(center_x - size // 2, center_y - size // 2, size, size)
