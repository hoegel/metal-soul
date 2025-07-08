from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor

class PauseMenu(QWidget):
    resumeRequested = Signal()
    exitRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 250)
        self.setStyleSheet("""
            background-color: #2c2f33;
            border-radius: 15px;
        """)

        # Тень для меню
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0)
        self.setGraphicsEffect(shadow)

        # Заголовок
        title = QLabel("Пауза", self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 20px;")

        # Кнопки
        self.resumeButton = QPushButton("Продолжить", self)
        self.exitButton = QPushButton("Выйти в меню", self)

        for btn in (self.resumeButton, self.exitButton):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #7289da;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 8px 15px;
                }
                QPushButton:hover {
                    background-color: #5b6eae;
                }
                QPushButton:pressed {
                    background-color: #4a5a8e;
                }
            """)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(self.resumeButton)
        layout.addWidget(self.exitButton)
        layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.setLayout(layout)

        self.hide()

        # Сигналы кнопок
        self.resumeButton.clicked.connect(self.resumeRequested)
        self.exitButton.clicked.connect(self.exitRequested)
