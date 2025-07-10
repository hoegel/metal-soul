from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt
from config import *
from resources.colors import *
from utils.styles_loader import update_style_property
from PySide6.QtGui import QPixmap
from ui.countdown_circle import CountdownCircle

class HUD(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(WINDOW_HEIGHT // 1.3)
        self.setFixedWidth(WINDOW_WIDTH)
        
        self.power_chord_pixmap = QPixmap("resources/images/icons/axe_guitar.png")
        self.major_chord_pixmap = QPixmap("resources/images/icons/blaster_guitar.png")
        self.minor_chord_pixmap = QPixmap("resources/images/icons/bomb_amp.png")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)

        weapon_row = QHBoxLayout()
        hp_row = QHBoxLayout()
        
        # Weapons        
        self.power_chord_widget = QWidget()
        self.power_chord_widget.setObjectName("power_chord_label")
        self.power_chord_layout = QHBoxLayout(self.power_chord_widget)
        self.power_chord_icon = QLabel()
        self.power_chord_text = CountdownCircle(0.1)
        self.power_chord_icon.setPixmap(self.power_chord_pixmap)
        self.power_chord_layout.addWidget(self.power_chord_icon)
        self.power_chord_layout.addWidget(self.power_chord_text)

        self.major_chord_widget = QWidget()
        self.major_chord_widget.setObjectName("major_chord_label")
        self.major_chord_layout = QHBoxLayout(self.major_chord_widget)
        self.major_chord_icon = QLabel()
        self.major_chord_text = CountdownCircle(0.1)
        self.major_chord_icon.setPixmap(self.major_chord_pixmap)
        self.major_chord_layout.addWidget(self.major_chord_icon)
        self.major_chord_layout.addWidget(self.major_chord_text)
        
        self.minor_chord_widget = QWidget()
        self.minor_chord_widget.setObjectName("minor_chord_label")
        self.minor_chord_layout = QHBoxLayout(self.minor_chord_widget)
        self.minor_chord_icon = QLabel()
        self.minor_chord_text = CountdownCircle(0.1)
        self.minor_chord_icon.setPixmap(self.minor_chord_pixmap)
        self.minor_chord_layout.addWidget(self.minor_chord_icon)
        self.minor_chord_layout.addWidget(self.minor_chord_text)
        
        weapon_row.addWidget(self.power_chord_widget)
        weapon_row.addWidget(self.major_chord_widget)
        weapon_row.addWidget(self.minor_chord_widget)

        self.update_chord(1)

        # Health
        self.hp_bar = QProgressBar()
        self.hp_bar.setMinimum(0)
        self.hp_bar.setMaximum(100)
        self.hp_bar.setValue(100)
        self.hp_bar.setTextVisible(True)
        self.hp_bar.setAlignment(Qt.AlignCenter)

        hp_row.addWidget(self.hp_bar) 

        # Skills
        vbox = QVBoxLayout()
        
        def create_cooldown_widget(label_text: str) -> QWidget:
            widget = QWidget()
            widget.setObjectName("skill_widget")
            layout = QHBoxLayout(widget)
            
            label = QLabel(label_text)
            label.setObjectName("skill_label")
            widget.circle = CountdownCircle(0.1)

            layout.addWidget(label)
            layout.addStretch()
            layout.addWidget(widget.circle)

            return widget

        self.dodge_widget = create_cooldown_widget("Dash")
        self.shield_widget = create_cooldown_widget("Shield")
        self.ult_widget = create_cooldown_widget("Utimate")
        # self.potion_widget = create_cooldown_widget("Heal")

        vbox.addWidget(self.dodge_widget)
        vbox.addWidget(self.shield_widget)
        vbox.addWidget(self.ult_widget)
        # vbox.addWidget(self.potion_widget)
        vbox.addStretch()
        
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addLayout(vbox)
        hbox.setContentsMargins(0, 0, 0, 0)

        self.resize(400, 300)
        
        main_layout.addLayout(hbox)
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
        update_style_property(self.power_chord_widget, "background-color", str(NOT_CHOSEN_WEAPON_COLOR))
        update_style_property(self.major_chord_widget, "background-color", str(NOT_CHOSEN_WEAPON_COLOR))
        update_style_property(self.minor_chord_widget, "background-color", str(NOT_CHOSEN_WEAPON_COLOR))
        match number:
            case 1:
                update_style_property(self.power_chord_widget, "background-color", str(CHOSEN_WEAPON_COLOR))
            case 2:
                update_style_property(self.major_chord_widget, "background-color", str(CHOSEN_WEAPON_COLOR))
            case 3:
                update_style_property(self.minor_chord_widget, "background-color", str(CHOSEN_WEAPON_COLOR))