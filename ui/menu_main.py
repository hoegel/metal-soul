from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class MainMenu(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Metal soul")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 20px;")
        layout.addWidget(title)

        start_button = QPushButton("Start game")
        start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        start_button.setFixedHeight(40)
        start_button.setStyleSheet("""
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
        start_button.clicked.connect(self.main_window.start_game)
        layout.addWidget(start_button)

        exit_button = QPushButton("Exit")
        exit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_button.setFixedHeight(40)
        exit_button.setStyleSheet("""
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
        exit_button.clicked.connect(self.close_app)
        layout.addWidget(exit_button)

        self.setLayout(layout)

    def close_app(self):
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
