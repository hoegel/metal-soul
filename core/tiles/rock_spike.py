from core.tiles.base import Tile
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtCore import Qt
from config import *
from core.player import Player

class RockSpikeTile(Tile):
    def __init__(self, x, y, damage=10):
        super().__init__(x, y)
        self.damage = damage
        self.spike_rock_pixmap = QPixmap("resources/images/backgrounds/spike_rock.webp")
        self.scaled_pixmap = self.spike_rock_pixmap.scaled(TILE_SIZE, TILE_SIZE, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    def is_walkable(self, entity=None):
        if entity and hasattr(entity, "take_damage") and isinstance(entity, Player):
            entity.take_damage(self.damage)
        return False

    def is_projectile_passable(self, projectile=None):
        return False

    def draw(self, painter, tile_size):
        painter.drawPixmap(self.x * tile_size + BORDER_SIZE, self.y * tile_size + BORDER_SIZE, self.scaled_pixmap)
