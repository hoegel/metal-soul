import json
from core.tiles.floor import *
from core.tiles.pit import *
from core.tiles.rock import *

class Room:
    def __init__(self, x, y, room_type="normal"):
        self.x = x
        self.y = y
        self.room_type = room_type  # "start", "fight", "treasure", "boss"
        self.visited = False
        self.enemies = []
        self.cleared = False
        self.artifact = None
        self.pickups = []
        self.tiles = []

    def position(self):
        return (self.x, self.y)

    def load_layout_from_json(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
            self.tiles = []
            for y, row in enumerate(data.get("tiles", [])):
                tile_row = []
                for x, char in enumerate(row):
                    match char:
                        case 'F': tile = FloorTile(x, y)
                        case 'P': tile = PitTile(x, y)
                        case 'R': tile = RockTile(x, y)
                        case _:   tile = FloorTile(x, y)
                    tile_row.append(tile)
                self.tiles.append(tile_row)