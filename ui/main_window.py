from PySide6.QtWidgets import QMainWindow, QStackedWidget
from ui.menu_main import MainMenu
from ui.game_view import GameView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Roguelike Game")
        self.resize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu = MainMenu(self)
        self.game_view = GameView(self)

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.game_view)

        self.stack.setCurrentWidget(self.menu)

    def start_game(self):
        self.stack.setCurrentWidget(self.game_view)