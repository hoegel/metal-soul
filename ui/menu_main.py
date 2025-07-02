from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt

class MainMenu(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Roguelike Guitar Game")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        layout.addWidget(title)

        start_button = QPushButton("Start game")
        start_button.clicked.connect(self.main_window.start_game)
        layout.addWidget(start_button)

        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close_app)
        layout.addWidget(exit_button)

        self.setLayout(layout)

    def close_app(self):
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
