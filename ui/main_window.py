from PySide6.QtWidgets import QMainWindow, QStackedWidget
from ui.menu_main import MainMenu
from ui.game_view import GameView
from ui.menu_tutorial import TutorialMenu
from config import *
from utils.music import music

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metal soul")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main_menu = MainMenu(self)

        self.tutorial_menu = TutorialMenu(self)

        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.tutorial_menu)

        self.stack.setCurrentWidget(self.main_menu)
        
        self.isStarted = False

        music.play_music("menu", loop=True)

    def new_game(self, difficulty="Normal"):
        self.isStarted = True
        self.main_menu.continue_button.setEnabled(True)
        self.main_menu.set_button_style(self.main_menu.continue_button)
        self.game = GameView(self, difficulty)
        self.stack.addWidget(self.game)
        self.stack.setCurrentWidget(self.game)
        self.game.game_starts()
        
    def continue_game(self):
        if self.isStarted:
            self.stack.setCurrentWidget(self.game)
            self.game.game_starts()
        
    def go_to_main_menu(self):
        self.stack.setCurrentWidget(self.main_menu)
        music.play_music("menu", loop=True)

    def show_tutorial(self):
        self.stack.setCurrentWidget(self.tutorial_menu)

    def show_main_menu(self):
        self.stack.setCurrentWidget(self.main_menu)
