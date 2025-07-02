from PySide6.QtWidgets import QMainWindow, QStackedWidget
from ui.menu_main import MainMenu
from ui.game_view import GameView
from config import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Roguelike Guitar Game")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu = MainMenu(self)
        self.game = GameView(self)

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.game)

        self.stack.setCurrentWidget(self.menu)

    def start_game(self):
        self.stack.setCurrentWidget(self.game)