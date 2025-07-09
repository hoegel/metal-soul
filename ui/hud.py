# ui/hud.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt
from config import *
from resources.colors import *

class HUD(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(WINDOW_HEIGHT - ROOM_SIZE[0])
        self.setFixedWidth(WINDOW_WIDTH)
        #self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)

        weapon_row = QHBoxLayout()
        hp_row = QHBoxLayout()
        
        # Скилы        
        self.power_chord_label = QLabel("Power chord")
        self.major_chord_label = QLabel("Major chord")
        self.minor_chord_label = QLabel("Minor chord")
        
        self.power_chord_label.setObjectName("power_chord_label")
        self.major_chord_label.setObjectName("major_chord_label")
        self.minor_chord_label.setObjectName("minor_chord_label")

        # self.power_chord_label.setStyleSheet(f"background-color: {CHOSEN_WEAPON_COLOR}; font-size: 16px;")
        # self.major_chord_label.setStyleSheet(f"background-color: {NOT_CHOSEN_WEAPON_COLOR}; font-size: 16px;")
        # self.minor_chord_label.setStyleSheet(f"background-color: {NOT_CHOSEN_WEAPON_COLOR}; font-size: 16px;")
            
        weapon_row.addWidget(self.power_chord_label)
        weapon_row.addWidget(self.major_chord_label)
        weapon_row.addWidget(self.minor_chord_label)

        # Жизнь
        self.hp_bar = QProgressBar()
        self.hp_bar.setMinimum(0)
        self.hp_bar.setMaximum(100)
        self.hp_bar.setValue(100)
        self.hp_bar.setTextVisible(True)
        self.hp_bar.setAlignment(Qt.AlignCenter)
        self.hp_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #000;
                background-color: #444;
                height: 40px;
                text-align: center;
                color: white;
                font-size: 15px;
                font-family: monospace;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: red;
            }
        """)

        hp_row.addWidget(self.hp_bar) 

        main_layout.addLayout(weapon_row)
        main_layout.addLayout(hp_row)
    
    def update_stats(self, hp, max_hp):
        self.hp_bar.setFormat(f"HP: {hp}/{max_hp} ({int(hp * 100 // max_hp)}%)")
        self.hp_bar.setMaximum(max_hp)
        self.hp_bar.setValue(hp)

        percent = hp / max_hp if max_hp > 0 else 0

        if percent > 0.7:
            color = GOOD_HP_BAR
        elif percent > 0.3:
            color = MID_HP_BAR
        else:
            color = LOW_HP_BAR

        self.hp_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #000;
                background-color: #444;
                height: 40px;
                text-align: center;
                color: white;
                font-size: 15px;
                font-family: monospace;
                font-weight: bold;
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

