from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent
from PySide6.QtCore import QTimer, Qt, QPoint, QRect, QRectF
from ui.hud import HUD
from core.player import Player
from config import *
from core.enemy import load_enemies_from_json
import math
from core.weapon import *

class GameView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.player = Player()

        self.player_x = 100
        self.player_y = 100
        self.player_size = 20
        self.speed = 4
        self.pressed_keys = set()

        self.bounds = [BORDER_SIZE, BORDER_SIZE, ROOM_SIZE[0] - BORDER_SIZE - self.player_size, ROOM_SIZE[1] - BORDER_SIZE - self.player_size]  # границы: left, top, right, bottom
                                                                                                                                                # self.player_size for hitbox
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.hud = HUD(self)
        self.layout.addWidget(self.hud)
        self.layout.setAlignment(self.hud, Qt.AlignBottom)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.attack_effects = []
        for weapon in self.player.weapons.values():
            weapon.subscribe(self.on_enemies_hit)

        self.enemies = load_enemies_from_json("resources/data/enemies.json")

    def on_enemies_hit(self, enemies):
        for e in enemies:
            if e in self.enemies:
                self.enemies.remove(e)


    def keyPressEvent(self, event: QKeyEvent):
        self.pressed_keys.add(event.key())

        if event.key() in (Qt.Key_1, Qt.Key_2, Qt.Key_3):
            self.player.set_attack_type(int(event.text()))
            self.hud.update_chord(int(event.text()))

    def keyReleaseEvent(self, event):
        self.pressed_keys.discard(event.key())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if QRect(BORDER_SIZE, BORDER_SIZE, ROOM_SIZE[0] - 2 * BORDER_SIZE, ROOM_SIZE[1] - 2 * BORDER_SIZE).contains(event.pos()):
                self.perform_attack(event.pos()) #XXX

    def perform_attack(self, mouse_pos):
        player_pos = (self.player_x, self.player_y) #XXX
        target_pos = (mouse_pos.x(), mouse_pos.y())

        self.attack_effects.append({
            'type': ['melee', 'beam', 'bomb'][self.player.attack_type - 1],
            'x': player_pos[0], 'y': player_pos[1],
            'px': target_pos[0], 'py': target_pos[1],
            'ttl': 10
        })

    def update_game(self):
        dx = dy = 0
        if Qt.Key_W in self.pressed_keys:
            dy -= self.player.speed
        if Qt.Key_S in self.pressed_keys:
            dy += self.player.speed
        if Qt.Key_A in self.pressed_keys:
            dx -= self.player.speed
        if Qt.Key_D in self.pressed_keys:
            dx += self.player.speed

        new_x = self.player_x + dx
        new_y = self.player_y + dy

        if self.bounds[0] <= new_x <= self.bounds[2]:
            self.player_x = new_x
        if self.bounds[1] <= new_y <= self.bounds[3]:
            self.player_y = new_y

        damage, hp, max_hp, speed = self.player.get_stats()
        #self.hud.update_stats(hp, max_hp)

        for enemy in self.enemies:
            enemy.move_towards(self.player_x, self.player_y)

        self.resolve_collisions()

        for effect in self.attack_effects:
            effect['ttl'] -= 1
        self.attack_effects = [e for e in self.attack_effects if e['ttl'] > 0]

        self.update()

    def resolve_collisions(self):
        to_remove = set()
        damaged_enemies = set()

        for effect in self.attack_effects:
            atk_type = effect['type']
            x = effect['x']
            y = effect['y']
            px = effect['px']
            py = effect['py']

            if atk_type == 'melee':
                damage = 8
                radius = 40
                for enemy in self.enemies:
                    if enemy in damaged_enemies:
                        continue
                    ex, ey, _, _ = enemy.rect()
                    dist = ((ex - x) ** 2 + (ey - y) ** 2) ** 0.5
                    if dist < radius:
                        if enemy.take_damage(damage):
                            to_remove.add(enemy)
                        damaged_enemies.add(enemy)

            elif atk_type == 'beam':
                damage = 12
                beam_threshold = 10  # расстояние до линии для попадания
                dx = px - x
                dy = py - y
                length_squared = dx**2 + dy**2 if dx or dy else 1
                for enemy in self.enemies:
                    if enemy in damaged_enemies:
                        continue
                    ex, ey, _, _ = enemy.rect()

                    # расстояние от врага до линии атаки
                    t = max(0, min(1, ((ex - x) * dx + (ey - y) * dy) / length_squared))
                    closest_x = x + t * dx
                    closest_y = y + t * dy
                    dist = ((closest_x - ex) ** 2 + (closest_y - ey) ** 2) ** 0.5

                    if dist < beam_threshold:
                        if enemy.take_damage(damage):
                            to_remove.add(enemy)
                        damaged_enemies.add(enemy)

            elif atk_type == 'bomb':
                damage = 18
                radius = 50
                for enemy in self.enemies:
                    if enemy in damaged_enemies:
                        continue
                    ex, ey, _, _ = enemy.rect()
                    dist = ((ex - px) ** 2 + (ey - py) ** 2) ** 0.5
                    if dist < radius:
                        if enemy.take_damage(damage):
                            to_remove.add(enemy)
                        damaged_enemies.add(enemy)

        self.enemies = [e for e in self.enemies if e not in to_remove]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        painter.setBrush(QColor(255, 100, 100))
        painter.drawEllipse(self.player_x, self.player_y, self.player_size, self.player_size)

        painter.setBrush(QColor(100, 100, 100))
        painter.setPen(QColor(0, 0, 0, 0))
        painter.drawRect(0, 0, ROOM_SIZE[0], 10)
        painter.drawRect(0, 0, 10, ROOM_SIZE[1])
        painter.drawRect(0, ROOM_SIZE[1] - 10, ROOM_SIZE[0], 10)
        painter.drawRect(ROOM_SIZE[0] - 10, 0, 10, ROOM_SIZE[1])

        for effect in self.attack_effects:
            atk_type = effect['type']
            x, y = effect['x'], effect['y']
            px, py = effect['px'], effect['py']

            if atk_type == 'melee':
                angle = math.degrees(math.atan2(py - y, px - x))
                start_angle = int((angle - 45) * 16)
                span_angle = int(90 * 16)

                painter.setBrush(QColor(255, 255, 0, 180))
                painter.setPen(Qt.NoPen)
                painter.drawPie(QRectF(x - 40, y - 40, 80, 80), start_angle, span_angle)

            elif atk_type == 'beam':
                # Вычисляем конец луча до столкновения со стеной
                end = Beam()._compute_wall_intersection(x, y, px, py)
                if end:
                    bx, by = end
                    painter.setPen(QColor(0, 255, 255))
                    painter.drawLine(x + 10, y + 10, bx, by)

            elif atk_type == 'bomb':
                painter.setBrush(QColor(255, 0, 255, 160))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(px - 25, py - 25, 50, 50)


        for enemy in self.enemies:
            painter.setBrush(QColor(200, 50, 50))
            painter.drawEllipse(enemy.x, enemy.y, enemy.size, enemy.size)

            painter.setPen(QColor(255, 255, 255))
            painter.drawText(enemy.x, enemy.y - 5, f"{enemy.hp}/{enemy.max_hp}")
