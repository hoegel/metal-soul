from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from pathlib import Path

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
        title = QLabel("Пауза", self)
        title.setObjectName("pause_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.resumeButton = QPushButton("Продолжить", self)
        self.exitButton = QPushButton("Выйти в меню", self)
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