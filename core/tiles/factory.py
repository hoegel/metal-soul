from core.tiles.floor import FloorTile
from core.tiles.rock import RockTile
from core.tiles.pit import PitTile

TILE_TYPES = {
    "F": FloorTile,
    "R": RockTile,
    "P": PitTile
}

def create_tile(char, x, y):
    tile_class = TILE_TYPES.get(char)
    if tile_class:
        return tile_class(x, y)
    raise ValueError(f"Unknown tile type: {char}")