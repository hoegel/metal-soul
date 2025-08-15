from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, Qt

class DeathMenu(QWidget):
    reviveRequested = Signal()
    exitRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("death_menu")
        self.setFixedSize(400, 400)

        self.setup_ui()

        self.reviveButton.clicked.connect(self.reviveRequested)
        self.exitButton.clicked.connect(self.exitRequested)

    def setup_ui(self):
        title = QLabel("You Died", self)
        title.setObjectName("death_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scoreLabel = QLabel(self)
        self.scoreLabel.setObjectName("death_score")
        self.scoreLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timeLabel = QLabel(self)
        self.timeLabel.setObjectName("death_time")
        self.timeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.reviveButton = QPushButton("Revive", self)
        self.exitButton = QPushButton("Exit to menu", self)
        self.reviveButton.setObjectName("death_button")
        self.exitButton.setObjectName("death_button")
        for btn in (self.reviveButton, self.exitButton):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.addWidget(title)
        layout.addWidget(self.scoreLabel)
        layout.addWidget(self.timeLabel)
        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(self.reviveButton)
        layout.addWidget(self.exitButton)
        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def set_score(self, score):
        self.scoreLabel.setText(f"Total score: {score}")

    def set_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        self.timeLabel.setText(f"Total time: {m:02}:{s:02}")
