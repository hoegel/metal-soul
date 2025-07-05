from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent
from PySide6.QtCore import QTimer, Qt, QPoint, QRect, QRectF
from ui.hud import HUD
from core.player import Player
from config import *
from core.enemy import load_enemies_from_json
import math
from core.weapon import *
from core.level import Level

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
        self.timer.stop()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.hud = HUD(self)
        self.layout.addWidget(self.hud)
        self.layout.setAlignment(self.hud, Qt.AlignBottom)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.attack_effects = []
        for weapon in self.player.weapons.values():
            weapon.subscribe(self.on_enemies_hit)

        # self.enemies = load_enemies_from_json("resources/data/enemies.json")

        self.level = Level()
        self.current_room = self.level.get_room(*self.level.start_pos)
        self.room_coords = self.level.start_pos
        self.load_room()

    def game_starts(self):
        self.timer.start(16)

    def load_room(self):
        self.enemies = []
        room = self.current_room

        if room.room_type == "fight" and not room.cleared:
            self.enemies = load_enemies_from_json("resources/data/enemies.json")
            room.enemies = self.enemies
        elif room.room_type == "boss":
            # load boss logic
            ...

    def on_enemies_hit(self, enemies):
        for e in enemies:
            if e in self.enemies:
                self.enemies.remove(e)
        if not self.enemies:
            self.current_room.cleared = True


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
            'time': 10
        })
        self.player.attack(player_pos, target_pos, self.enemies)

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

        door_width = 40
        wall_thickness = BORDER_SIZE  # 10 по умолчанию

        # Центр игрока
        # cx = new_x + self.player_size // 2
        # cy = new_y + self.player_size // 2
        cx = new_x
        cy = new_y

        cx_room, cy_room = self.room_coords
        neighbors = {
            'up':    self.level.get_room(cx_room, cy_room - 1),
            'down':  self.level.get_room(cx_room, cy_room + 1),
            'left':  self.level.get_room(cx_room - 1, cy_room),
            'right': self.level.get_room(cx_room + 1, cy_room)
        }

        # Стены с учётом дверей
        blocked_x = False
        blocked_y = False

        # Верх
        if new_y <= wall_thickness:
            if not (neighbors['up'] and abs(cx - ROOM_SIZE[0] // 2) <= door_width // 2 and not self.enemies):
                blocked_y = True
        # Низ
        if new_y + self.player_size >= ROOM_SIZE[1] - wall_thickness:
            if not (neighbors['down'] and abs(cx - ROOM_SIZE[0] // 2) <= door_width // 2 and not self.enemies):
                blocked_y = True
        # Лево
        if new_x <= wall_thickness:
            if not (neighbors['left'] and abs(cy - ROOM_SIZE[1] // 2) <= door_width // 2 and not self.enemies):
                blocked_x = True
        # Право
        if new_x + self.player_size >= ROOM_SIZE[0] - wall_thickness:
            if not (neighbors['right'] and abs(cy - ROOM_SIZE[1] // 2) <= door_width // 2 and not self.enemies):
                blocked_x = True

        # Разрешённое движение
        if not blocked_x:
            self.player_x = new_x
        if not blocked_y:
            self.player_y = new_y

        # Переход в соседнюю комнату
        if self.player_y <= 0:
            self.try_move_room(0, -1)
        elif self.player_y + self.player_size >= ROOM_SIZE[1]:
            self.try_move_room(0, 1)
        elif self.player_x <= 0:
            self.try_move_room(-1, 0)
        elif self.player_x + self.player_size >= ROOM_SIZE[0]:
            self.try_move_room(1, 0)



        damage, hp, max_hp, speed = self.player.get_stats()
        #self.hud.update_stats(hp, max_hp)

        for enemy in self.enemies:
            enemy.move_towards(self.player_x, self.player_y)

        # self.resolve_collisions()

        for effect in self.attack_effects:
            effect['time'] -= 1
        self.attack_effects = [e for e in self.attack_effects if e['time'] > 0]

        self.update()

    def try_move_room(self, dx, dy):
        if self.enemies:
            return

        new_x = self.room_coords[0] + dx
        new_y = self.room_coords[1] + dy
        next_room = self.level.get_room(new_x, new_y)

        if next_room:
            self.room_coords = (new_x, new_y)
            self.current_room = next_room
            self.player_x = ROOM_SIZE[0] // 2
            self.player_y = ROOM_SIZE[1] // 2
            self.load_room()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        painter.setBrush(QColor(255, 100, 100))
        painter.drawEllipse(self.player_x, self.player_y, self.player_size, self.player_size)

        cx, cy = self.room_coords
        neighbors = {
            'up':    self.level.get_room(cx, cy - 1),
            'down':  self.level.get_room(cx, cy + 1),
            'left':  self.level.get_room(cx - 1, cy),
            'right': self.level.get_room(cx + 1, cy)
        }

        door_w, door_h = 40, BORDER_SIZE  # размеры двери

        painter.setBrush(QColor(100, 100, 100))
        painter.setPen(QColor(0, 0, 0, 0))
        if not neighbors['up']:
            painter.drawRect(0, 0, ROOM_SIZE[0], BORDER_SIZE)  # обычная стена
        else:
            # левая часть
            painter.drawRect(0, 0, ROOM_SIZE[0] // 2 - door_w // 2, BORDER_SIZE)
            # правая часть
            painter.drawRect(ROOM_SIZE[0] // 2 + door_w // 2, 0, ROOM_SIZE[0] // 2 - door_w // 2, BORDER_SIZE)

        if not neighbors['down']:
            painter.drawRect(0, ROOM_SIZE[1] - BORDER_SIZE, ROOM_SIZE[0], BORDER_SIZE)  # обычная стена
        else:
            # левая часть
            painter.drawRect(0, ROOM_SIZE[1] - BORDER_SIZE, ROOM_SIZE[0] // 2 - door_w // 2, BORDER_SIZE)
            # правая часть
            painter.drawRect(ROOM_SIZE[0] // 2 + door_w // 2, ROOM_SIZE[1] - BORDER_SIZE, ROOM_SIZE[0] // 2 - door_w // 2, BORDER_SIZE)

        if not neighbors['left']:
            painter.drawRect(0, 0, BORDER_SIZE, ROOM_SIZE[1])  # обычная стена
        else:
            # верхняя часть
            painter.drawRect(0, 0, BORDER_SIZE, ROOM_SIZE[1] // 2 - door_w // 2)
            # нижняя часть
            painter.drawRect(0, ROOM_SIZE[1] // 2 + door_w // 2, BORDER_SIZE, ROOM_SIZE[1] // 2 - door_w // 2)

        if not neighbors['right']:
            painter.drawRect(ROOM_SIZE[0] - BORDER_SIZE, 0, BORDER_SIZE, ROOM_SIZE[1])  # обычная стена
        else:
            # верхняя часть
            painter.drawRect(ROOM_SIZE[0] - BORDER_SIZE, 0, BORDER_SIZE, ROOM_SIZE[1] // 2 - door_w // 2)
            # нижняя часть
            painter.drawRect(ROOM_SIZE[0] - BORDER_SIZE, ROOM_SIZE[1] // 2 + door_w // 2, BORDER_SIZE, ROOM_SIZE[1] // 2 - door_w // 2)


        painter.setBrush(QColor(180, 180, 180))  # цвет двери

        # Вверх
        if neighbors['up']:
            painter.drawRect(ROOM_SIZE[0] // 2 - door_w // 2, 0, door_w, door_h)
        # Вниз
        if neighbors['down']:
            painter.drawRect(ROOM_SIZE[0] // 2 - door_w // 2, ROOM_SIZE[1] - door_h, door_w, door_h)
        # Влево
        if neighbors['left']:
            painter.drawRect(0, ROOM_SIZE[1] // 2 - door_w // 2, door_h, door_w)
        # Вправо
        if neighbors['right']:
            painter.drawRect(ROOM_SIZE[0] - door_h, ROOM_SIZE[1] // 2 - door_w // 2, door_h, door_w)


        painter.setPen(QColor(255, 255, 255))
        painter.drawText(20, 20, f"Room: {self.room_coords} ({self.current_room.room_type})")

        for effect in self.attack_effects:
            atk_type = effect['type']
            x, y = effect['x'], effect['y']
            px, py = effect['px'], effect['py']

            if atk_type == 'melee':
                dx = px - x
                dy = py - y
                angle = math.degrees(math.atan2(-dy, dx))
                angle = (angle + 360) % 360

                start_angle = int((angle - 45) * 16)
                span_angle = int(90 * 16)

                painter.setBrush(QColor(255, 255, 0, 180))
                painter.setPen(Qt.NoPen)
                painter.drawPie(QRectF(x - 30, y - 30, 80, 80), start_angle, span_angle)


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
