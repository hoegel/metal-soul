from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.styles_loader import apply_app_styles
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_app_styles(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())