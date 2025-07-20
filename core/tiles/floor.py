from core.tiles.base import Tile
from PySide6.QtGui import QColor
from config import *

class FloorTile(Tile):
    def is_walkable(self, entity=None):
        return True

    def draw(self, painter, tile_size):
        # painter.setBrush(QColor(200, 200, 200, 256))
        # painter.drawRect(self.x * tile_size + BORDER_SIZE, self.y * tile_size + BORDER_SIZE, tile_size, tile_size)
        ...