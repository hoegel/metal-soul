# ui/hud.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from config import *

class HUD(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(WINDOW_HEIGHT - ROOM_SIZE[0])
        self.setFixedWidth(WINDOW_WIDTH)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)

        top_row = QHBoxLayout()
        bottom_row = QHBoxLayout()
        weapon_row = QHBoxLayout()

        # Жизнь
        self.hp_label = QLabel("HP: 100/100")
        self.hp_label.setStyleSheet("color: red; font-size: 16px;")
        top_row.addWidget(self.hp_label)

        # Мана
        self.mana_label = QLabel("Mana: 50/50")
        self.mana_label.setStyleSheet("color: cyan; font-size: 16px;")
        top_row.addWidget(self.mana_label)

        # Умения
        for i in range(1, 5):
            skill = QLabel(f"Skill {i}")
            skill.setFixedSize(60, 20)
            skill.setStyleSheet("background: gray; color: white; border: 1px solid white;")
            bottom_row.addWidget(skill)

        # Оружие
        for i in range(1, 4):
            weapon = QLabel(f"Weapon {i}")
            weapon.setFixedSize(80, 20)
            weapon.setStyleSheet("background: black; color: white; border: 1px solid white;")
            weapon_row.addWidget(weapon)

        main_layout.addLayout(top_row)
        main_layout.addLayout(bottom_row)
        main_layout.addLayout(weapon_row)
    
    def update_stats(self, hp, max_hp, mana, max_mana):
        self.hp_label.setText(f"HP: {hp}/{max_hp}")
        self.mana_label.setText(f"Mana: {mana}/{max_mana}")
