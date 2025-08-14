from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, Qt

class WinMenu(QWidget):
    restartRequested = Signal()
    exitRequested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("win_menu")
        self.setFixedSize(400, 400)
        
        self.setup_ui()
        
        self.restartButton.clicked.connect(self.restartRequested.emit)
        self.exitButton.clicked.connect(self.exitRequested.emit)
    
    def setup_ui(self):
        title = QLabel("Victory!", self)
        title.setObjectName("win_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.scoreLabel = QLabel(self)
        self.scoreLabel.setObjectName("win_score")
        self.scoreLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timeLabel = QLabel(self)
        self.timeLabel.setObjectName("win_time")
        self.timeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.restartButton = QPushButton("Start new run", self)
        self.exitButton = QPushButton("Exit to menu", self)
        self.restartButton.setObjectName("win_button")
        self.exitButton.setObjectName("win_button")
        
        for btn in (self.restartButton, self.exitButton):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.addWidget(title)
        layout.addWidget(self.scoreLabel)
        layout.addWidget(self.timeLabel)
        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(self.restartButton)
        layout.addWidget(self.exitButton)
        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    
    def set_score(self, score):
        self.scoreLabel.setText(f"Total score: {score}")

    def set_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        self.timeLabel.setText(f"Total time: {m:02}:{s:02}")
