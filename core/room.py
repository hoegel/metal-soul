class Room:
    def __init__(self, x, y, room_type="normal"):
        self.x = x
        self.y = y
        self.room_type = room_type  # "start", "fight", "treasure", "boss"
        self.visited = False
        self.enemies = []
        self.cleared = False

    def position(self):
        return (self.x, self.y)
