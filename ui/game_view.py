from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import QTimer, Qt

class GameView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.player_x = 100
        self.player_y = 100
        self.player_size = 20
        self.speed = 3
        self.pressed_keys = set()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event):
        self.pressed_keys.add(event.key())

    def keyReleaseEvent(self, event):
        self.pressed_keys.discard(event.key())

    def update_game(self):
        if Qt.Key_W in self.pressed_keys:
            self.player_y -= self.speed
        if Qt.Key_S in self.pressed_keys:
            self.player_y += self.speed
        if Qt.Key_A in self.pressed_keys:
            self.player_x -= self.speed
        if Qt.Key_D in self.pressed_keys:
            self.player_x += self.speed

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(0, 150, 255))
        painter.drawEllipse(self.player_x, self.player_y, self.player_size, self.player_size)
