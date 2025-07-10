# ui/hud.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt
from config import *
from resources.colors import *
from PySide6.QtGui import QPainter, QPixmap

class HUD(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(WINDOW_HEIGHT - ROOM_SIZE[0])
        self.setFixedWidth(WINDOW_WIDTH)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")
        
        self.power_chord_pixmap = QPixmap("resources/images/icons/axe_guitar.png")
        self.major_chord_pixmap = QPixmap("resources/images/icons/blaster_guitar.png")
        self.minor_chord_pixmap = QPixmap("resources/images/icons/bomb_amp.png")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)

        weapon_row = QHBoxLayout()
        hp_row = QHBoxLayout()
        
        # Скилы        
        self.power_chord_widget = QWidget()
        self.power_chord_layout = QHBoxLayout(self.power_chord_widget)
        self.power_chord_layout.setContentsMargins(0, 0, 0, 0)
        self.power_chord_text = QLabel()
        self.power_chord_icon = QLabel()
        self.power_chord_icon.setPixmap(self.power_chord_pixmap)
        self.power_chord_text.setText("1")
        self.power_chord_layout.addWidget(self.power_chord_icon)
        self.power_chord_layout.addWidget(self.power_chord_text)
        self.set_chosen_skill_style(self.power_chord_widget)
        
        self.major_chord_widget = QWidget()
        self.major_chord_layout = QHBoxLayout(self.major_chord_widget)
        self.major_chord_layout.setContentsMargins(0, 0, 0, 0)
        self.major_chord_text = QLabel()
        self.major_chord_icon = QLabel()
        self.major_chord_icon.setPixmap(self.major_chord_pixmap)
        self.major_chord_text.setText("2")
        self.major_chord_layout.addWidget(self.major_chord_icon)
        self.major_chord_layout.addWidget(self.major_chord_text)
        self.set_not_chosen_skill_style(self.major_chord_widget)
        
        self.minor_chord_widget = QWidget()
        self.minor_chord_layout = QHBoxLayout(self.minor_chord_widget)
        self.minor_chord_layout.setContentsMargins(0, 0, 0, 0)
        self.minor_chord_text = QLabel()
        self.minor_chord_icon = QLabel()
        self.minor_chord_icon.setPixmap(self.minor_chord_pixmap)
        self.minor_chord_text.setText("3")
        self.minor_chord_layout.addWidget(self.minor_chord_icon)
        self.minor_chord_layout.addWidget(self.minor_chord_text)
        self.set_not_chosen_skill_style(self.minor_chord_widget)
        
        weapon_row.addWidget(self.power_chord_widget)
        weapon_row.addWidget(self.major_chord_widget)
        weapon_row.addWidget(self.minor_chord_widget)

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
            self.set_chosen_skill_style(self.power_chord_widget)
            self.set_not_chosen_skill_style(self.major_chord_widget)
            self.set_not_chosen_skill_style(self.minor_chord_widget)
        elif(number == 2):
            self.set_not_chosen_skill_style(self.power_chord_widget)
            self.set_chosen_skill_style(self.major_chord_widget)
            self.set_not_chosen_skill_style(self.minor_chord_widget)
        elif(number == 3):
            self.set_not_chosen_skill_style(self.power_chord_widget)
            self.set_not_chosen_skill_style(self.major_chord_widget)
            self.set_chosen_skill_style(self.minor_chord_widget)
            
    def set_chosen_skill_style(self, widget):
        widget.setFixedSize(240, 130)
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {CHOSEN_WEAPON_COLOR};
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
            }}
            QLabel {{
                color: white;
                font-size: 48px;
                font-weight: bold;
            }}
        """)
        
    def set_not_chosen_skill_style(self, widget):
        widget.setFixedSize(230, 120)
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {NOT_CHOSEN_WEAPON_COLOR};
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
            }}
            QLabel {{
                color: white;
                font-size: 48px;
                font-weight: bold;
            }}
        """)
