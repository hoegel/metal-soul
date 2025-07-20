from core.tiles.base import Tile
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from config import *

class PitTile(Tile):
    def is_walkable(self, entity=None):
        return getattr(entity, 'is_flying', False)

    def draw(self, painter, tile_size):
        painter.setBrush(QColor(10, 10, 10))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.x * tile_size + BORDER_SIZE, self.y * tile_size + BORDER_SIZE, tile_size, tile_size)
