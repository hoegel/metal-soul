# ui/hud.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt
from config import *
from resources.colors import *
from utils.styles_loader import update_style_property

class HUD(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(WINDOW_HEIGHT - ROOM_SIZE[0])
        self.setFixedWidth(WINDOW_WIDTH)

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
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
    
    def update_chord(self, number):
        update_style_property(self.power_chord_label, "background-color", str(NOT_CHOSEN_WEAPON_COLOR))
        update_style_property(self.major_chord_label, "background-color", str(NOT_CHOSEN_WEAPON_COLOR))
        update_style_property(self.minor_chord_label, "background-color", str(NOT_CHOSEN_WEAPON_COLOR))
        match number:
            case 1:
                update_style_property(self.power_chord_label, "background-color", str(CHOSEN_WEAPON_COLOR))
            case 2:
                update_style_property(self.major_chord_label, "background-color", str(CHOSEN_WEAPON_COLOR))
            case 3:
                update_style_property(self.minor_chord_label, "background-color", str(CHOSEN_WEAPON_COLOR))

