from core.tiles.base import Tile
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtCore import Qt
from config import *

class RockTile(Tile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.rock_pixmap = QPixmap("resources/images/backgrounds/rock.webp")
        self.scaled_pixmap = self.rock_pixmap.scaled(TILE_SIZE, TILE_SIZE, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    def is_walkable(self, entity=None):
        return False

    def is_projectile_passable(self, projectile=None):
        if projectile and getattr(projectile, 'spectral', False):
            return True
        return False

    def draw(self, painter, tile_size):
        painter.drawPixmap(self.x * tile_size + BORDER_SIZE, self.y * tile_size + BORDER_SIZE, self.scaled_pixmap)
