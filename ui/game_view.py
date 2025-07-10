from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent, QPen, QLinearGradient, QPixmap
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent, QPen, QLinearGradient
from PySide6.QtCore import QTimer, Qt, QPoint, QRect, QRectF, Signal
import math, os, random
from config import *
from ui.hud import HUD
from ui.menu_pause import PauseMenu
from core.player import Player
from core.enemy import load_enemies_from_json, Enemy, ShooterEnemy, CrossShooterEnemy
from core.weapon import *
from core.level import Level
from core.elemental import *
from core.projectile import Projectile
from core.artifact_pool import get_random_artifact, create_artifact_pool
from core.effect_registry import load_unlocked_effects, unlock_effect
from core.boss import *
from ui.countdown_circle import CountdownCircle

class GameView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        self.background_pixmap = QPixmap("resources/images/backgrounds/level_background1.png")
        self.doors_up = QPixmap("resources/images/backgrounds/doors_up.png")
        self.doors_down = QPixmap("resources/images/backgrounds/doors_down.png")
        self.doors_right = QPixmap("resources/images/backgrounds/doors_right.png")
        self.doors_left = QPixmap("resources/images/backgrounds/doors_left.png")
        self.doors_up_treasure = QPixmap("resources/images/backgrounds/doors_up_treasure.png")
        self.doors_down_treasure = QPixmap("resources/images/backgrounds/doors_down_treasure.png")
        self.doors_right_treasure = QPixmap("resources/images/backgrounds/doors_right_treasure.png")
        self.doors_left_treasure = QPixmap("resources/images/backgrounds/doors_left_treasure.png")
        self.doors_up_next_level = QPixmap("resources/images/backgrounds/doors_up_next_level.png")
        self.doors_down_next_level = QPixmap("resources/images/backgrounds/doors_down_next_level.png")
        self.doors_right_next_level = QPixmap("resources/images/backgrounds/doors_right_next_level.png")
        self.doors_left_next_level = QPixmap("resources/images/backgrounds/doors_left_next_level.png")
        self.doors_up_boss = QPixmap("resources/images/backgrounds/doors_up_boss.png")
        self.doors_down_boss = QPixmap("resources/images/backgrounds/doors_down_boss.png")
        self.doors_right_boss = QPixmap("resources/images/backgrounds/doors_right_boss.png")
        self.doors_left_boss = QPixmap("resources/images/backgrounds/doors_left_boss.png")

        self.player = Player()

        self.player.size = 20
        self.player.x = ROOM_SIZE[0] // 2 - self.player.size // 2
        self.player.y = ROOM_SIZE[1] // 2 - self.player.size // 2
        self.player.speed = 4
        self.pressed_keys = set()

        self.bounds = [BORDER_SIZE, BORDER_SIZE, ROOM_SIZE[0] - BORDER_SIZE - self.player.size, ROOM_SIZE[1] - BORDER_SIZE - self.player.size]  # границы: left, top, right, bottom
                                                                                                                                                # self.player.size for hitbox
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

        self.player.enemies = []

        self.floor = 0
        self.level = Level()
        self.current_room = self.level.get_room(*self.level.start_pos)
        self.current_room.visited = True
        self.room_coords = self.level.start_pos

        self.projectiles = []

        self.load_room()


        self.current_room.artifact = None
        self.artifact_pos = QPoint(ROOM_SIZE[0]//2 - 10, ROOM_SIZE[1]//2 - 10)
        create_artifact_pool()

        self.effect_choices = []
        if self.room_coords == self.level.start_pos:
            unlocked = load_unlocked_effects()
            if unlocked:
                self.effect_choices = random.sample(unlocked, min(3, len(unlocked)))
            else:
                self.effect_choices = []
        
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
        self.player.enemies.clear()
        self.projectiles.clear()
        room = self.current_room

        if room.room_type == "fight" and not room.cleared:
            self.current_room.artifact = None
            # room_id = f"floor{self.floor}_x{self.room_coords[0]}_y{self.room_coords[1]}"
            room_id = f"floor{self.floor}_{(self.room_coords[0] + self.room_coords[1]) % 4}"
            path = f"resources/data/enemies/{room_id}.json"
            if os.path.exists(path):
                self.player.enemies.extend(load_enemies_from_json(path))
            else:
                print(path)
                self.player.enemies.extend(load_enemies_from_json("resources/data/enemies.json"))
            room.enemies = self.player.enemies
        elif room.room_type == "boss" and not room.cleared:
            self.current_room.artifact = None
            match self.floor:
                case 0:
                    self.player.enemies.append(BossCharger(ROOM_SIZE[0] // 2 - 40, ROOM_SIZE[1] // 2 - 40))
                case 1:
                    self.player.enemies.append(BossShooter(ROOM_SIZE[0] // 2 - 40, ROOM_SIZE[1] // 2 - 40))
                case _:
                    self.player.enemies.append(BossSpawner(ROOM_SIZE[0] // 2 - 40, ROOM_SIZE[1] // 2 - 40))
        elif room.room_type == "treasure" and not room.cleared and self.current_room.artifact == None:
            self.current_room.artifact = get_random_artifact()

    def on_enemies_hit(self, enemies):
        for e in enemies:
            if e in self.player.enemies:
                self.player.enemies.remove(e)
        if not self.player.enemies:
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

            if event.key() == Qt.Key_Space:
                dx, dy = 0, 0
                if Qt.Key_W in self.pressed_keys: dy -= 1
                if Qt.Key_S in self.pressed_keys: dy += 1
                if Qt.Key_A in self.pressed_keys: dx -= 1
                if Qt.Key_D in self.pressed_keys: dx += 1
                if dx or dy:
                    length = math.hypot(dx, dy)
                    direction = (dx / length, dy / length)
                    self.player.start_roll(direction)

            if event.key() == Qt.Key_E and self.current_room.artifact:
                # Подбор артефакта, если рядом
                dist = math.hypot(self.player.x - self.artifact_pos.x(), self.player.y - self.artifact_pos.y())
                if dist < 40:
                    artifact = self.current_room.artifact

                    if hasattr(artifact, "effect_cls"):
                        if artifact.apply(self.player):
                            unlock_effect(artifact.effect_cls.__name__)
                            QMessageBox.information(self, "Новый эффект", f"Новый эффект разблокирован: {artifact.effect_cls.__name__}")
                        else:
                            QMessageBox.warning(self, "Нет места", "Нет свободных слотов для эффекта!")
                    else:
                        artifact.apply(self.player)
                        QMessageBox.information(self, "Артефакт", f"Получен артефакт: {artifact.name}")

                    self.current_room.artifact = None
                    self.current_room.cleared = True

            if event.key() == Qt.Key_Q:
                if self.player.ultimate.activate():
                    # self.music.play()
                    print("ULTIMATE ACTIVATED!")
                else:
                    print(f"Ульта на перезарядке: {self.player.ultimate.remaining_cooldown()} сек")

            if event.key() == Qt.Key_C:
                if self.player.heal_fragments.use(self.player):
                    print("🎵 Хилочка использована!")
                else:
                    print("❌ Нет хилок!")

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
                    
                    if self.room_coords == self.level.start_pos and self.effect_choices:
                        for i, eff_class in enumerate(self.effect_choices):
                            rect = QRect(100 + i*140, 100, 120, 40)
                            if rect.contains(event.pos()):
                                weapon = self.player.weapon
                                if issubclass(eff_class, Tremolo):
                                    effect_instance = eff_class(self.player.enemies)
                                elif issubclass(eff_class, Wah):
                                    effect_instance = eff_class(self.player)
                                else:
                                    effect_instance = eff_class()
                                if weapon.add_effect(effect_instance):
                                    print(f"Effect {eff_class.__name__} added to current weapon")
                                else:
                                    print("Cannot add more effects")
                                self.effect_choices.clear()

            if event.button() == Qt.MouseButton.RightButton:
                if QRect(BORDER_SIZE, BORDER_SIZE, ROOM_SIZE[0] - 2 * BORDER_SIZE, ROOM_SIZE[1] - 2 * BORDER_SIZE).contains(event.pos()):
                    
                    self.player.shield.activate()
                    
    def perform_attack(self, mouse_pos):
        if self.player.weapon.can_attack():
            player_pos = (self.player.x, self.player.y) #XXX
            target_pos = (mouse_pos.x(), mouse_pos.y())

            self.attack_effects.append({
                'type': ['melee', 'beam', 'bomb'][self.player.attack_type - 1],
                'x': player_pos[0], 'y': player_pos[1],
                'px': target_pos[0], 'py': target_pos[1],
                'time': 10
            })
            self.player.attack(player_pos, target_pos, self.player.enemies)
            
            for effect in self.attack_effects:
                atk_type = effect['type']
                
                if atk_type == 'melee':
                    self.hud.power_chord_text.start_countdown(0.3)
                elif atk_type == 'beam':
                    self.hud.major_chord_text.start_countdown(1)
                elif atk_type == 'bomb':
                    self.hud.minor_chord_text.start_countdown(1.5)

    def update_game(self):
        self.player.update()
        _, hp, max_hp, _ = self.player.get_stats()
        # if not self.player.ultimate.is_active():
        #     self.music.stop()
        if self.player.is_dodging():
            new_x, new_y = self.player.get_position()
        else:
            dx = dy = 0
            if Qt.Key_W in self.pressed_keys:
                dy -= self.player.speed * self.player.ult_active_multiplier
            if Qt.Key_S in self.pressed_keys:
                dy += self.player.speed * self.player.ult_active_multiplier
            if Qt.Key_A in self.pressed_keys:
                dx -= self.player.speed * self.player.ult_active_multiplier
            if Qt.Key_D in self.pressed_keys:
                dx += self.player.speed * self.player.ult_active_multiplier

            new_x = self.player.x + dx
            new_y = self.player.y + dy

        door_width = 100
        
        wall_thickness = BORDER_SIZE

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
            if not (neighbors['up'] and abs(cx - ROOM_SIZE[0] // 2) <= door_width // 2 and not self.player.enemies):
                blocked_y = True
        # Низ
        if new_y + self.player.size >= ROOM_SIZE[1] - wall_thickness:
            if not (neighbors['down'] and abs(cx - ROOM_SIZE[0] // 2) <= door_width // 2 and not self.player.enemies):
                blocked_y = True
        # Лево
        if new_x <= wall_thickness:
            if not (neighbors['left'] and abs(cy - ROOM_SIZE[1] // 2) <= door_width // 2 and not self.player.enemies):
                blocked_x = True
        # Право
        if new_x + self.player.size >= ROOM_SIZE[0] - wall_thickness:
            if not (neighbors['right'] and abs(cy - ROOM_SIZE[1] // 2) <= door_width // 2 and not self.player.enemies):
                blocked_x = True

        # Разрешённое движение
        if not blocked_x:
            self.player.x = new_x
        if not blocked_y:
            self.player.y = new_y

        # Переход в соседнюю комнату
        if self.player.y <= 70:
            self.try_move_room(0, -1)
        elif self.player.y + self.player.size >= FIELD_SIZE[1]:
            self.try_move_room(0, 1)
        elif self.player.x <= 70:
            self.try_move_room(-1, 0)
        elif self.player.x + self.player.size >= FIELD_SIZE[0]:
            self.try_move_room(1, 0)

        damage, hp, max_hp, speed = self.player.get_stats()

        self.hud.update_stats(hp, max_hp)
        self.player.update_invincibility()

        for enemy in self.player.enemies:
            if isinstance(enemy, BossSpawner):
                enemy.update(self.player.x + self.player.size // 2, self.player.y + self.player.size // 2, self.player.enemies)
            else:
                enemy.update(self.player.x + self.player.size // 2, self.player.y + self.player.size // 2, self.projectiles)
            if enemy.hp <= 0:
                self.player.enemies.remove(enemy)
            elif enemy.check_contact_with_player(self.player.x, self.player.y, self.player.size):
                if self.player.is_dodging():
                    continue
                if self.player.shield.absorb_hit():
                    continue
                self.player.take_damage(enemy.damage)

        if not self.player.enemies:
            if not self.current_room.cleared:
                if self.current_room.room_type == "fight":
                    if random.random() < 0.15:  # 15%
                        if self.player.heal_fragments.add():
                            print("🎶 Найдена хилочка!")
                elif self.current_room.room_type == "boss":
                    if random.random() < 0.5:  # 50%
                        if self.player.heal_fragments.add():
                            print("🎶 Найдена хилочка после босса!")
                self.current_room.cleared = True


        for effect in self.attack_effects:
            effect['time'] -= 1
        self.attack_effects = [e for e in self.attack_effects if e['time'] > 0]

        for proj in self.projectiles:
            proj.update()
            hits = proj.check_collision(self.player.enemies if proj.target_type == "enemy" else [self.player])
            for h in hits:
                if h == self.player:
                    if self.player.is_dodging():
                        continue
                    if self.player.shield.absorb_hit():
                        continue
                h.take_damage(proj.damage)

        self.projectiles = [p for p in self.projectiles if p.alive]

        self.update()

    def try_move_room(self, dx, dy):
        if self.player.enemies:
            return

        new_x = self.room_coords[0] + dx
        new_y = self.room_coords[1] + dy
        next_room = self.level.get_room(new_x, new_y)

        if next_room:
            if next_room.room_type == "next_level":
                if self.current_room.room_type != "boss":
                    return
                self.floor += 1
                self.level = Level()  # Сгенерировать новый этаж
                self.room_coords = self.level.start_pos
                self.current_room = self.level.get_room(*self.room_coords)
                self.player.x = ROOM_SIZE[0] // 2 - self.player.size // 2
                self.player.y = ROOM_SIZE[1] // 2 - self.player.size // 2
            else:
                self.room_coords = (new_x, new_y)
                self.current_room = next_room
                # Расчёт позиции игрока у входа в новую комнату
                if dx == 1:  # пришёл слева → появиться у левой двери
                    self.player.x = 70
                    self.player.y = ROOM_SIZE[1] // 2 - self.player.size // 2
                elif dx == -1:  # пришёл справа → появиться у правой двери
                    self.player.x = ROOM_SIZE[0] - 70 - self.player.size
                    self.player.y = ROOM_SIZE[1] // 2 - self.player.size // 2
                elif dy == 1:  # пришёл сверху → появиться у верхней двери
                    self.player.y = 70
                    self.player.x = ROOM_SIZE[0] // 2 - self.player.size // 2
                elif dy == -1:  # пришёл снизу → появиться у нижней двери
                    self.player.y = ROOM_SIZE[1] - 70 - self.player.size
                    self.player.x = ROOM_SIZE[0] // 2 - self.player.size // 2
            self.current_room.visited = True
            self.load_room()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if not self.background_pixmap.isNull():
            scaled_pixmap = self.background_pixmap.scaled(600, 600, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled_pixmap)
        else:
            painter.fillRect(QRect(0, 0, 600, 600), Qt.lightGray)

        if self.player.shield.is_active():
            painter.setPen(QPen(QColor(0, 255, 255), 4))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(self.player.x - 5, self.player.y - 5, self.player.size + 10, self.player.size + 10)

        if self.player.dodge.active:
            painter.setPen(QPen(QColor(100, 180, 255), 4))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(self.player.x - 5, self.player.y - 5, self.player.size + 10, self.player.size + 10)

        if self.player.shield.is_active():
            painter.setPen(QPen(QColor(0, 255, 255), 4))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(self.player.x - 5, self.player.y - 5, self.player.size + 10, self.player.size + 10)

        if self.player.dodge.active:
            painter.setPen(QPen(QColor(100, 180, 255), 4))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(self.player.x - 5, self.player.y - 5, self.player.size + 10, self.player.size + 10)

        painter.setBrush(QColor(255, 100, 100))
        painter.setPen(QColor(255, 120, 120))
        if self.player.invincible:
            painter.setBrush(QColor(255, 100, 100, 100))
        painter.drawEllipse(self.player.x, self.player.y, self.player.size, self.player.size)

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
                    painter.setBrush(self.doors_up_boss)
                case "treasure":
                    painter.setBrush(self.doors_up_treasure)
                case "next_level":
                    painter.setBrush(self.doors_up_next_level)
                case _:
                    painter.setBrush(self.doors_up)
            painter.drawRect(ROOM_SIZE[0] // 2 - door_w // 2, 0, door_w, door_h)
        # Вниз
        if neighbors['down']:
            match self.level.get_room(cx, cy + 1).room_type:
                case "boss":
                    painter.setBrush(self.doors_down_boss)
                case "treasure":
                    painter.setBrush(self.doors_down_treasure)
                case "next_level":
                    painter.setBrush(self.doors_down_next_level)
                case _:
                    painter.setBrush(self.doors_down)
            painter.drawRect(ROOM_SIZE[0] // 2 - door_w // 2, ROOM_SIZE[1] - door_h, door_w, door_h)
        # Влево
        if neighbors['left']:
            match self.level.get_room(cx - 1, cy).room_type:
                case "boss":
                    painter.setBrush(self.doors_left_boss)
                case "treasure":
                    painter.setBrush(self.doors_left_treasure)
                case "next_level":
                    painter.setBrush(self.doors_left_next_level)
                case _:
                    painter.setBrush(self.doors_left)
            painter.drawRect(0, ROOM_SIZE[1] // 2 - door_w // 2, door_h, door_w)
        # Вправо
        if neighbors['right']:
            match self.level.get_room(cx + 1, cy).room_type:
                case "boss":
                    painter.setBrush(self.doors_right_boss)
                case "treasure":
                    painter.setBrush(self.doors_right_treasure)
                case "next_level":
                    painter.setBrush(self.doors_right_next_level)
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
            gradient = QLinearGradient(self.player.x, self.player.y, self.player.x + self.player.size, self.player.y + self.player.size)
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
                painter.drawPie(QRectF(x - self.player.weapon.radius + 10, y - self.player.weapon.radius + 10, self.player.weapon.radius * 2, self.player.weapon.radius * 2), start_angle, span_angle)
                

            elif atk_type == 'beam':
                # Вычисляем конец луча до столкновения со стеной
                end = Beam(Player)._compute_wall_intersection(x, y, px, py)
                if end:
                    bx, by = end
                    if self.player.weapon.effect:
                        painter.setPen(QPen(effect_colors.get(self.player.weapon.effect[-1].name, QColor(255, 255, 255, 180)), self.player.weapon.radius * 2))
                    else:
                        painter.setPen(QPen(QColor(255, 255, 255, 180), self.player.weapon.radius * 2))
                    painter.drawLine(x + 10, y + 10, bx, by)

            elif atk_type == 'bomb':
                painter.setBrush(gradient)
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(px - self.player.weapon.radius, py - self.player.weapon.radius, self.player.weapon.radius * 2, self.player.weapon.radius * 2)


        for enemy in self.player.enemies:
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

        for proj in self.projectiles:
            proj.draw(painter)

        if self.current_room.artifact:
            painter.setBrush(QColor(100, 255, 100))
            painter.setPen(QColor(255, 255, 255))
            x, y = self.artifact_pos.x(), self.artifact_pos.y()
            painter.drawEllipse(x, y, 20, 20)
            painter.drawText(x - 10, y - 10, self.current_room.artifact.name)
            painter.drawText(40, 40, self.current_room.artifact.description)

        if self.room_coords == self.level.start_pos and self.effect_choices:
            for i, eff_class in enumerate(self.effect_choices):
                painter.setBrush(QColor(80 + i*60, 80, 255 - i*60))
                painter.drawRect(100 + i*140, 100, 120, 40)
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(110 + i*140, 125, eff_class.__name__)

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

        if self.player.ultimate.is_active():
            painter.setOpacity(0.25)
            painter.fillRect(QRect(0, 0, *ROOM_SIZE), QColor(255, 0, 0))  # красный фильтр
            painter.setOpacity(1.0)
        painter.end
