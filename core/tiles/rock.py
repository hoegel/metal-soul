from core.tiles.base import Tile
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from config import *

class RockTile(Tile):
    def is_walkable(self, entity=None):
        return False

    def is_projectile_passable(self, projectile=None):
        if projectile and getattr(projectile, 'spectral', False):
            return True
        return False

    def draw(self, painter, tile_size):
        painter.setBrush(QColor(80, 80, 80))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.x * tile_size + BORDER_SIZE, self.y * tile_size + BORDER_SIZE, tile_size, tile_size)
