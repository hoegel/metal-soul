# ui/hud.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QProgressBar
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

        weapon_row = QHBoxLayout()
        hp_row = QHBoxLayout()
        
        # Скилы        
        self.power_chord_label = QLabel("Power chord")
        self.major_chord_label = QLabel("Major chord")
        self.minor_chord_label = QLabel("Minor chord")
        
        self.power_chord_label.setStyleSheet(f"background-color: {CHOSEN_WEAPON_COLOR}; font-size: 16px;")
        self.major_chord_label.setStyleSheet(f"background-color: {NOT_CHOSEN_WEAPON_COLOR}; font-size: 16px;")
        self.minor_chord_label.setStyleSheet(f"background-color: {NOT_CHOSEN_WEAPON_COLOR}; font-size: 16px;")
            
        weapon_row.addWidget(self.power_chord_label)
        weapon_row.addWidget(self.major_chord_label)
        weapon_row.addWidget(self.minor_chord_label)

        # Жизнь
        self.hp_label = QLabel("HP: 100/100")
        self.hp_label.setStyleSheet("""
            color: red;
            font-size: 16px;
            font-family: monospace;                               
        """)
        self.hp_label.setAlignment(Qt.AlignCenter)
        self.hp_label.setMinimumWidth(100) 

        self.hp_bar = QProgressBar()
        self.hp_bar.setMinimum(0)
        self.hp_bar.setMaximum(100)
        self.hp_bar.setValue(100)
        self.hp_bar.setTextVisible(False)
        self.hp_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #000;
                background-color: #444;
                height: 40px;
            }
            QProgressBar::chunk {
                background-color: red;
            }
        """)

        hp_row.addWidget(self.hp_label)
        hp_row.addWidget(self.hp_bar)

        main_layout.addLayout(weapon_row)
        main_layout.addLayout(hp_row)
    
    def update_stats(self, hp, max_hp):
        self.hp_label.setText(f"HP: {hp}/{max_hp}")
        self.hp_bar.setMaximum(max_hp)
        self.hp_bar.setValue(hp)

        percent = hp / max_hp if max_hp > 0 else 0

        if percent > 0.7:
            color = "#579a33"
        elif percent > 0.3:
            color = "#ffea00"
        else:
            color = "#ee1c25"

        self.hp_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #000;
                background-color: #444;
                height: 40px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
    
    def update_chord(self, number):
        if(number == 1):
            self.power_chord_label.setStyleSheet(f"background-color: {CHOSEN_WEAPON_COLOR}; font-size: 16px;")
            self.major_chord_label.setStyleSheet(f"background-color: {NOT_CHOSEN_WEAPON_COLOR}; font-size: 16px;")
            self.minor_chord_label.setStyleSheet(f"background-color: {NOT_CHOSEN_WEAPON_COLOR}; font-size: 16px;")
        elif(number == 2):
            self.power_chord_label.setStyleSheet(f"background-color: {NOT_CHOSEN_WEAPON_COLOR}; font-size: 16px;")
            self.major_chord_label.setStyleSheet(f"background-color: {CHOSEN_WEAPON_COLOR}; font-size: 16px;")
            self.minor_chord_label.setStyleSheet(f"background-color: {NOT_CHOSEN_WEAPON_COLOR}; font-size: 16px;")
        elif(number == 3):
            self.power_chord_label.setStyleSheet(f"background-color: {NOT_CHOSEN_WEAPON_COLOR}; font-size: 16px;")
            self.major_chord_label.setStyleSheet(f"background-color: {NOT_CHOSEN_WEAPON_COLOR}; font-size: 16px;")
            self.minor_chord_label.setStyleSheet(f"background-color: {CHOSEN_WEAPON_COLOR}; font-size: 16px;")

