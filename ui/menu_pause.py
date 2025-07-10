from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QSlider
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from pathlib import Path
from utils.music import music

class PauseMenu(QWidget):
    resumeRequested = Signal()
    exitRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pause_menu")
        self.setFixedSize(400, 350)

        self.setup_ui()

        self.resumeButton.clicked.connect(self.resumeRequested)
        self.exitButton.clicked.connect(self.exitRequested)

    def setup_ui(self):
        title = QLabel("Pause", self)
        title.setObjectName("pause_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.resumeButton = QPushButton("Continue", self)
        self.exitButton = QPushButton("Exit to menu", self)
        self.resumeButton.setObjectName("pause_button")
        self.exitButton.setObjectName("pause_button")
        for btn in (self.resumeButton, self.exitButton):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.addWidget(title)
        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(self.resumeButton)
        layout.addWidget(self.exitButton)
        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.music_slider = QSlider(Qt.Horizontal)
        self.music_slider.setRange(0, 100)
        self.music_slider.setValue(int(music.music_volume * 100))
        self.music_slider.valueChanged.connect(lambda v: music.set_volume(music_volume=v / 100))

        self.sfx_slider = QSlider(Qt.Horizontal)
        self.sfx_slider.setRange(0, 100)
        self.sfx_slider.setValue(int(music.sfx_volume * 100))
        self.sfx_slider.valueChanged.connect(lambda v: music.set_volume(sfx_volume=v / 100))

        music_label = QLabel("Music Volume")
        sfx_label = QLabel("SFX Volume")

        layout.addWidget(music_label)
        layout.addWidget(self.music_slider)
        layout.addWidget(sfx_label)
        layout.addWidget(self.sfx_slider)