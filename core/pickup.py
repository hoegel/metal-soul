from PySide6.QtGui import QColor, QPainter
import math

class Pickup:
    def __init__(self, x, y, size=10):
        self.x = x
        self.y = y
        self.size = size
        self.collected = False

    def check_collision(self, player_x, player_y, player_size):
        dx = (self.x + self.size/2) - (player_x + player_size/2)
        dy = (self.y + self.size/2) - (player_y + player_size/2)
        distance = math.hypot(dx, dy)
        return distance < (self.size + player_size) / 2

    def apply(self, player):
        raise NotImplementedError()

    def draw(self, painter: QPainter):
        raise NotImplementedError()
    

class HealthPickup(Pickup):
    def __init__(self, x, y):
        super().__init__(x, y, size=10)

    def apply(self, player):
        player.heal_percent(10)

    def draw(self, painter):
        painter.setBrush(QColor(100, 255, 100))
        painter.drawEllipse(self.x, self.y, self.size, self.size)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.x + 4, self.y + 15, "+HP")


class KeyPickup(Pickup):
    def __init__(self, x, y):
        super().__init__(x, y, size=10)

    def apply(self, player):
        player.keys += 1

    def draw(self, painter):
        painter.setBrush(QColor(255, 255, 100))
        painter.drawEllipse(self.x, self.y, self.size, self.size)
        painter.setPen(QColor(50, 50, 0))
        painter.drawText(self.x + 2, self.y + 14, "🔑")

class BombPickup(Pickup):
    def __init__(self, x, y):
        super().__init__(x, y, size=10)

    def apply(self, player):
        player.bombs += 5

    def draw(self, painter):
        painter.setBrush(QColor(10, 10, 10))
        painter.drawEllipse(self.x, self.y, self.size, self.size)
        painter.setPen(QColor(50, 50, 0))
        painter.drawText(self.x + 2, self.y + 14, "bombx5")
