from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent
from PySide6.QtCore import QTimer, Qt, QPoint
from ui.hud import HUD
from core.player import Player
from config import *

class GameView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.player = Player()

        self.player_x = 100
        self.player_y = 100
        self.player_size = 20
        self.speed = 4
        self.pressed_keys = set()

        self.bounds = [10, 10, ROOM_SIZE[0] - 10 - self.player_size, ROOM_SIZE[0] - 10 - self.player_size]  # границы: left, top, right, bottom

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.hud = HUD(self)
        self.layout.addWidget(self.hud)
        self.layout.setAlignment(self.hud, Qt.AlignBottom)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.attack_effects = []

    def keyPressEvent(self, event: QKeyEvent):
        self.pressed_keys.add(event.key())

        if event.key() in (Qt.Key_1, Qt.Key_2, Qt.Key_3):
            self.player.set_attack_type(int(event.text()))

    def keyReleaseEvent(self, event):
        self.pressed_keys.discard(event.key())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.perform_attack(event.globalPos())

    def perform_attack(self, point):
        atk = self.player.attack_type
        if atk == 1:
            self.attack_effects.append(('melee', self.player_x, self.player_y, point.x(), point.y()))
        elif atk == 2:
            self.attack_effects.append(('beam', self.player_x, self.player_y, point.x(), point.y()))
        elif atk == 3:
            self.attack_effects.append(('bomb', self.player_x, self.player_y, point.x(), point.y()))

    def update_game(self):
        dx = dy = 0
        if Qt.Key_W in self.pressed_keys:
            dy -= self.player.speed
        if Qt.Key_S in self.pressed_keys:
            dy += self.player.speed
        if Qt.Key_A in self.pressed_keys:
            dx -= self.player.speed
        if Qt.Key_D in self.pressed_keys:
            dx += self.player.speed

        new_x = self.player_x + dx
        new_y = self.player_y + dy

        if self.bounds[0] <= new_x <= self.bounds[2]:
            self.player_x = new_x
        if self.bounds[1] <= new_y <= self.bounds[3]:
            self.player_y = new_y

        hp, max_hp, mana, max_mana = self.player.get_stats()
        self.hud.update_stats(hp, max_hp, mana, max_mana)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        painter.setBrush(QColor(255, 100, 100))
        painter.drawEllipse(self.player_x, self.player_y, self.player_size, self.player_size)

        painter.setBrush(QColor(100, 100, 100))
        painter.setPen(QColor(0, 0, 0, 0))
        painter.drawRect(0, 0, ROOM_SIZE[0], 10)
        painter.drawRect(0, 0, 10, ROOM_SIZE[1])
        painter.drawRect(0, ROOM_SIZE[1] - 10, ROOM_SIZE[0], 10)
        painter.drawRect(ROOM_SIZE[0] - 10, 0, 10, ROOM_SIZE[1])

        for atk_type, x, y, px, py in self.attack_effects:
            if atk_type == 'melee':
                painter.setBrush(QColor(255, 255, 0))
                painter.drawEllipse(x - 10, y - 10, 40, 40)
            elif atk_type == 'beam':
                painter.setPen(QColor(0, 255, 255))
                painter.drawLine(x + 10, y + 10, px, py)
            elif atk_type == 'bomb':
                painter.setBrush(QColor(255, 0, 255))
                painter.drawEllipse(px - 10, py - 10, 20, 20)
