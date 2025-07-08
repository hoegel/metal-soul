from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

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

        self.continue_button = QPushButton("Продолжить")
        self.new_game_button = QPushButton("Новая игра")
        self.exit_button = QPushButton("Выйти из игры")
        for button in (self.continue_button, self.new_game_button, self.exit_button):  
            self.set_button_style(button)
            layout.addWidget(button)
        self.continue_button.clicked.connect(self.main_window.continue_game)
        self.new_game_button.clicked.connect(self.main_window.new_game)
        self.exit_button.clicked.connect(self.close_app)

        self.continue_button.setEnabled(False)
        self.set_disabled_button_style(self.continue_button)
        self.setLayout(layout)

    def close_app(self):
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
        
    def set_button_style(self, button):
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedHeight(40)
        button.setStyleSheet("""
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
        
    def set_disabled_button_style(self, button):
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedHeight(40)
        button.setStyleSheet("""
        QPushButton {
            background-color: #a0a0a0;
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