from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.styles_loader import stylesheet
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())