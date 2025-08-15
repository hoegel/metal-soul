from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class TutorialMenu(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.setWindowTitle("Tutorial")
        self.setFixedSize(800, 600)

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.image_label = QLabel("")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.text_label = QLabel("")
        self.text_label.setAlignment(Qt.AlignTop)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.text_label)

        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Назад")
        self.next_button = QPushButton("Далее")
        self.exit_button = QPushButton("Выйти")
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.exit_button)
        self.layout.addLayout(nav_layout)

        self.steps = [
            (
                "Добро пожаловать!",
                "В этой игре вы спускаетесь по этажам подземелий, сражаясь с врагами и боссами. "
                "Ваша цель — пройти все этажи и победить финального босса.",
                "resources/images/tutorial/goal.webp"
            ),
            (
                "Управление",
                "Перемещение: W, A, S, D\n"
                "Атака: ЛКМ\n"
                "Щит: ПКМ\n"
                "Уклонение: Пробел (направление — кнопками движения)\n"
                "Использовать ультимейт: Q\n"
                "Лечение: C",
                "resources/images/tutorial/controls.gif"
            ),
            (
                "Оружие",
                "В игре есть три типа атак: ближний бой (1), луч (2), бомба (3).\n"
                "Каждое оружие можно усиливать эффектами, найденными в подземельях.",
                "resources/images/tutorial/weapons.png"
            ),
            (
                "Артефакты и эффекты",
                "Артефакты дают особые бонусы. Эффекты могут усиливать атаки, замедлять врагов, наносить урон с течением времени и т.д.\n"
                "Собирайте их, чтобы становиться сильнее.",
                "resources/images/tutorial/artifacts.png"
            ),
            (
                "Этажи и боссы",
                "В игре несколько этажей (по умолчанию 3–5). На каждом этаже вас ждут обычные комнаты, комнаты с сокровищами и босс.\n"
                "Победа над боссом открывает дверь на следующий этаж.",
                "resources/images/tutorial/floors.webp"
            ),
            (
                "Удачи!",
                "Теперь вы готовы к приключению. Помните — внимательность и тактика помогут выжить.\n"
                "Желаем удачи в сражении!",
                "resources/images/tutorial/good_luck.png"
            ),
        ]

        self.current_step = 0
        self.update_step()

        # Подключаем кнопки
        self.prev_button.clicked.connect(self.prev_step)
        self.next_button.clicked.connect(self.next_step)
        self.exit_button.clicked.connect(self.exit_tutorial)

    def update_step(self):
        title, text, image_path = self.steps[self.current_step]
        self.title_label.setText(title)
        self.text_label.setText(text)

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio))
        else:
            self.image_label.clear()

        self.prev_button.setEnabled(self.current_step > 0)
        self.next_button.setEnabled(self.current_step < len(self.steps) - 1)

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_step()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step()

    def exit_tutorial(self):
        self.main_window.show_main_menu()