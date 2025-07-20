class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_walkable(self, entity=None) -> bool:
        return False

    def is_projectile_passable(self, projectile=None) -> bool:
        return True

    def draw(self, painter, tile_size):
        raise NotImplementedError()