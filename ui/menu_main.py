from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QSlider, QHBoxLayout
from PySide6.QtCore import Qt
from utils.music import music

class MainMenu(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        container.setFixedWidth(550)
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        title = QLabel("Metal soul")
        title.setObjectName("menu_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.continue_button = QPushButton("Continue")
        self.new_game_button = QPushButton("New game")
        self.exit_button = QPushButton("Exit the game")
        for button in (self.continue_button, self.new_game_button, self.exit_button):  
            self.set_button_style(button)
            layout.addWidget(button)
        self.continue_button.clicked.connect(self.main_window.continue_game)
        self.new_game_button.clicked.connect(self.handle_new_game)
        self.exit_button.clicked.connect(self.close_app)

        self.difficulty_label = QLabel("Select Difficulty:")
        self.difficulty_label.setObjectName("difficulty_label")
        self.difficulty_selector = QComboBox()
        self.difficulty_selector.addItems(["Easy", "Normal", "Hard", "Nightmare", "Senya"])
        self.difficulty_selector.setObjectName("difficulty_selector")
        layout.addWidget(self.difficulty_label)
        layout.addWidget(self.difficulty_selector)

        music_layout = QHBoxLayout()
        music_label = QLabel("Music Volume")
        music_label.setFixedWidth(100)

        self.music_slider = QSlider(Qt.Horizontal)
        self.music_slider.setRange(0, 100)
        self.music_slider.setValue(int(music.music_volume * 100))
        self.music_slider.setFixedWidth(250)
        self.music_slider.valueChanged.connect(lambda v: music.set_volume(music_volume=v / 100))

        music_layout.addWidget(music_label)
        music_layout.addWidget(self.music_slider)
        layout.addLayout(music_layout)

        sfx_layout = QHBoxLayout()
        sfx_label = QLabel("SFX Volume")
        sfx_label.setFixedWidth(100)

        self.sfx_slider = QSlider(Qt.Horizontal)
        self.sfx_slider.setRange(0, 100)
        self.sfx_slider.setValue(int(music.sfx_volume * 100))
        self.sfx_slider.setFixedWidth(250)
        self.sfx_slider.valueChanged.connect(lambda v: music.set_volume(sfx_volume=v / 100))

        sfx_layout.addWidget(sfx_label)
        sfx_layout.addWidget(self.sfx_slider)
        layout.addLayout(sfx_layout)

        self.continue_button.setEnabled(False)
        self.set_button_style(self.continue_button)

        outer_layout.addWidget(container)

    def close_app(self):
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
        
    def set_button_style(self, button):
        button.setObjectName("menu_button")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.style().unpolish(button)
        button.style().polish(button)
        button.update()

    def handle_new_game(self):
        selected_difficulty = self.difficulty_selector.currentText()
        self.main_window.new_game(selected_difficulty)