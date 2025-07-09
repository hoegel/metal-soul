from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent, QPen, QLinearGradient, QPixmap
from PySide6.QtCore import QTimer, Qt, QPoint, QRect, QRectF, Signal
from ui.hud import HUD
from core.player import Player
from config import *
from core.enemy import load_enemies_from_json
import math
from core.weapon import *
from core.level import Level
from core.elemental import *
from ui.menu_pause import PauseMenu

import os
print(os.path.exists("resources/images/backgrounds/level_background1.png"))

class GameView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        self.background_pixmap = QPixmap("resources/images/backgrounds/level_background1.png")
        self.doors_up = QPixmap("resources/images/backgrounds/doors_up.png")
        self.doors_down = QPixmap("resources/images/backgrounds/doors_down.png")
        self.doors_right = QPixmap("resources/images/backgrounds/doors_right.png")
        self.doors_left = QPixmap("resources/images/backgrounds/doors_left.png")

        self.player = Player()

        self.player_size = 20
        self.player_x = ROOM_SIZE[0] // 2 - self.player_size // 2
        self.player_y = ROOM_SIZE[1] // 2 - self.player_size // 2
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

        self.enemies = []

        self.floor = 0
        self.level = Level()
        self.current_room = self.level.get_room(*self.level.start_pos)
        self.current_room.visited = True
        self.room_coords = self.level.start_pos
        self.load_room()

        # effect tests
        self.player.weapons[1].add_effect(Overdrive())
        self.player.weapons[1].add_effect(Tremolo(self.enemies))
        self.player.weapons[2].add_effect(Delay())
        self.player.weapons[2].add_effect(Fuzz())
        self.player.weapons[3].add_effect(Wah(self.player))
        self.player.weapons[3].add_effect(Distortion())
        
        #pause_menu
        self.isPaused = False

        self.pauseMenu = PauseMenu(self)
        self.pauseMenu.setGeometry(100, 100, 200, 100)

        self.pauseMenu.resumeRequested.connect(self.resume_game)
        self.pauseMenu.exitRequested.connect(self.main_window.go_to_main_menu)
        
    def pause_game(self):
        self.isPaused = True
        self.pauseMenu.show()
        self.pauseMenu.move(270, 200)
        self.timer.stop()
        
    def resume_game(self):
        self.isPaused = False
        self.pauseMenu.hide()
        self.timer.start()

    def game_starts(self):
        self.pauseMenu.hide()
        self.isPaused = False
        self.timer.start(16)

    def load_room(self):
        self.enemies.clear
        room = self.current_room

        if room.room_type == "fight" and not room.cleared:
            self.enemies.extend(load_enemies_from_json("resources/data/enemies.json"))
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
        if event.key() == Qt.Key.Key_Escape:
            if not self.isPaused:
                self.pause_game()
            else:
                self.resume_game()
        else:
            super().keyPressEvent(event)
        
        if not self.isPaused:
            self.pressed_keys.add(event.key())

            if event.key() in (Qt.Key_1, Qt.Key_2, Qt.Key_3):
                self.player.set_attack_type(int(event.text()))
                self.hud.update_chord(int(event.text()))

    def keyReleaseEvent(self, event):
        self.pressed_keys.discard(event.key())

    def mousePressEvent(self, event: QMouseEvent):
        if not self.isPaused:
            if event.button() == Qt.MouseButton.LeftButton:
                if QRect(BORDER_SIZE, BORDER_SIZE, ROOM_SIZE[0] - 2 * BORDER_SIZE, ROOM_SIZE[1] - 2 * BORDER_SIZE).contains(event.pos()):
                    self.perform_attack(event.pos()) #XXX

    def perform_attack(self, mouse_pos):
        if self.player.weapon.can_attack():
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

        door_width = 100
        wall_thickness = BORDER_SIZE

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
        if self.player_y <= 70:
            self.try_move_room(0, -1)
        elif self.player_y + self.player_size >= FIELD_SIZE[1]:
            self.try_move_room(0, 1)
        elif self.player_x <= 70:
            self.try_move_room(-1, 0)
        elif self.player_x + self.player_size >= FIELD_SIZE[0]:
            self.try_move_room(1, 0)

        damage, hp, max_hp, speed = self.player.get_stats()
        self.hud.update_stats(hp, max_hp)

        for enemy in self.enemies:
            enemy.move_towards(self.player_x, self.player_y)
            if enemy.hp <= 0:
                self.enemies.remove(enemy)

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
            if next_room.room_type == "next_level":
                self.floor += 1
                self.level = Level()  # Сгенерировать новый этаж
                self.room_coords = self.level.start_pos
                self.current_room = self.level.get_room(*self.room_coords)
                self.player_x = ROOM_SIZE[0] // 2 - self.player_size // 2
                self.player_y = ROOM_SIZE[1] // 2 - self.player_size // 2
            else:
                self.room_coords = (new_x, new_y)
                self.current_room = next_room
                # Расчёт позиции игрока у входа в новую комнату
                if dx == 1:  # пришёл слева → появиться у левой двери
                    self.player_x = 70
                    self.player_y = ROOM_SIZE[1] // 2 - self.player_size // 2
                elif dx == -1:  # пришёл справа → появиться у правой двери
                    self.player_x = ROOM_SIZE[0] - 70 - self.player_size
                    self.player_y = ROOM_SIZE[1] // 2 - self.player_size // 2
                elif dy == 1:  # пришёл сверху → появиться у верхней двери
                    self.player_y = 70
                    self.player_x = ROOM_SIZE[0] // 2 - self.player_size // 2
                elif dy == -1:  # пришёл снизу → появиться у нижней двери
                    self.player_y = ROOM_SIZE[1] - 70 - self.player_size
                    self.player_x = ROOM_SIZE[0] // 2 - self.player_size // 2
            self.current_room.visited = True
            self.load_room()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if not self.background_pixmap.isNull():
            scaled_pixmap = self.background_pixmap.scaled(600, 600, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled_pixmap)
        else:
            painter.fillRect(QRect(0, 0, 600, 600), Qt.lightGray)

        painter.setBrush(QColor(255, 100, 100))
        painter.drawEllipse(self.player_x, self.player_y, self.player_size, self.player_size)

        cx, cy = self.room_coords
        neighbors = {
            'up':    self.level.get_room(cx, cy - 1),
            'down':  self.level.get_room(cx, cy + 1),
            'left':  self.level.get_room(cx - 1, cy),
            'right': self.level.get_room(cx + 1, cy)
        }

        door_w, door_h = 100, BORDER_SIZE  # размеры двери

        painter.setPen(QColor(0, 0, 0, 0))

        # Вверх
        if neighbors['up']:
            match self.level.get_room(cx, cy - 1).room_type:
                case "boss":
                    painter.setBrush(self.doors_up)
                case "treasure":
                    painter.setBrush(self.doors_up)
                case "next_level":
                    painter.setBrush(self.doors_up)
                case _:
                    painter.setBrush(self.doors_up)
            painter.drawRect(ROOM_SIZE[0] // 2 - door_w // 2, 0, door_w, door_h)
        # Вниз
        if neighbors['down']:
            match self.level.get_room(cx, cy + 1).room_type:
                case "boss":
                    painter.setBrush(self.doors_down)
                case "treasure":
                    painter.setBrush(self.doors_down)
                case "next_level":
                    painter.setBrush(self.doors_down)
                case _:
                    painter.setBrush(self.doors_down)
            painter.drawRect(ROOM_SIZE[0] // 2 - door_w // 2, ROOM_SIZE[1] - door_h, door_w, door_h)
        # Влево
        if neighbors['left']:
            match self.level.get_room(cx - 1, cy).room_type:
                case "boss":
                    painter.setBrush(self.doors_left)
                case "treasure":
                    painter.setBrush(self.doors_left)
                case "next_level":
                    painter.setBrush(self.doors_left)
                case _:
                    painter.setBrush(self.doors_left)
            painter.drawRect(0, ROOM_SIZE[1] // 2 - door_w // 2, door_h, door_w)
        # Вправо
        if neighbors['right']:
            match self.level.get_room(cx + 1, cy).room_type:
                case "boss":
                    painter.setBrush(self.doors_right)
                case "treasure":
                    painter.setBrush(self.doors_right)
                case "next_level":
                    painter.setBrush(self.doors_right)
                case _:
                    painter.setBrush(self.doors_right)
            painter.drawRect(ROOM_SIZE[0] - door_h, ROOM_SIZE[1] // 2 - door_w // 2, door_h, door_w)


        painter.setPen(QColor(255, 255, 255))
        painter.drawText(20, 20, f"Floor: {self.floor} Room: {self.room_coords} ({self.current_room.room_type})")

        # Отрисовка игрока с учетом эффектов
        effect_colors = {
            'delay': QColor(255, 100, 0),
            'fuzz': QColor(150, 0, 255),
            'overdrive': QColor(0, 200, 255),
            'wah': QColor(0, 255, 0),
            'tremolo': QColor(255, 255, 0),
            'distortion': QColor(255, 0, 0),
        }

        # Соберем цвета эффектов текущего оружия
        current_effects = self.player.weapon.effect
        if current_effects:
            gradient = QLinearGradient(self.player_x, self.player_y, self.player_x + self.player_size, self.player_y + self.player_size)
            for i, eff in enumerate(current_effects):
                color = effect_colors.get(eff.name, QColor(255, 255, 255, 180))
                gradient.setColorAt(i / max(1, len(current_effects) - 1), color)
            painter.setBrush(gradient)
        else:
            gradient = QColor(255, 255, 255, 180)

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

                painter.setBrush(gradient)
                painter.setPen(Qt.NoPen)
                painter.drawPie(QRectF(x - 30, y - 30, 80, 80), start_angle, span_angle)


            elif atk_type == 'beam':
                # Вычисляем конец луча до столкновения со стеной
                end = Beam(Player)._compute_wall_intersection(x, y, px, py)
                if end:
                    bx, by = end
                    if self.player.weapon.effect:
                        painter.setPen(effect_colors.get(self.player.weapon.effect[-1].name, QColor(255, 255, 255, 180)))
                    else:
                        painter.setPen(QColor(255, 255, 255, 180))
                    painter.drawLine(x + 10, y + 10, bx, by)

            elif atk_type == 'bomb':
                painter.setBrush(gradient)
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(px - 25, py - 25, 50, 50)


        for enemy in self.enemies:
            painter.setBrush(QColor(200, 50, 50))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(enemy.x, enemy.y, enemy.size, enemy.size)

            # Эффекты врага (пример по dot/stun/slow)
            outline_color = None
            if enemy.dot["active"]:
                outline_color = QColor(255, 100, 0)
            elif enemy.stun["active"]:
                outline_color = QColor(150, 0, 255)
            elif enemy.slow["active"]:
                outline_color = QColor(0, 200, 255)

            if outline_color:
                pen = QPen(outline_color, 3)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(enemy.x - 3, enemy.y - 3, enemy.size + 6, enemy.size + 6)

            painter.setPen(QColor(255, 255, 255))
            painter.drawText(enemy.x, enemy.y - 5, f"{enemy.hp}/{enemy.max_hp}")


        # Рисуем миникарту
        minimap_scale = 8
        minimap_offset_x = WINDOW_WIDTH - 100
        minimap_offset_y = 100
        room_size = 16

        for (rx, ry), room in self.level.rooms.items():
            color = QColor(100, 100, 100)
            if room == self.current_room:
                color = QColor(0, 255, 0)  # Текущая комната
            elif room.room_type == "boss":
                color = QColor(255, 0, 0)
            elif room.room_type == "treasure":
                color = QColor(255, 215, 0)
            elif room.visited:
                color = QColor(200, 200, 200)  # Пройденные комнаты
            elif room.room_type == "next_level":
                continue

            painter.setBrush(color)
            painter.setPen(QPen(Qt.black))
            painter.drawRect(
                minimap_offset_x + (rx - self.level.start_pos[0]) * room_size,
                minimap_offset_y + (ry - self.level.start_pos[1]) * room_size,
                room_size, room_size
            )
        painter.end