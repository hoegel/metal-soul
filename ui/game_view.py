from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent, QPen, QLinearGradient, QPixmap
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent, QPen, QLinearGradient
from PySide6.QtCore import QTimer, Qt, QPoint, QRect, QRectF, Signal, qDebug
import math, os, random
from config import *
from ui.hud import HUD
from ui.menu_pause import PauseMenu
from ui.menu_death import DeathMenu
from ui.menu_win import WinMenu
from core.player import Player
from core.enemy import load_enemies_from_json
from core.weapon import *
from core.level import Level
from core.elemental import *
from core.artifact_pool import get_random_artifact, create_artifact_pool
from core.effect_registry import load_unlocked_effects, unlock_effect
from core.boss import *
from core.pickup import *
from utils.music import music

class GameView(QWidget):
    def __init__(self, main_window, difficulty_name):
        super().__init__()
        self.main_window = main_window

        self.pixmap_init()

        self.set_difficulty(difficulty_name)

        self.player_init()
                                                                                                                            
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

        self.bounds = [BORDER_SIZE, BORDER_SIZE, ROOM_SIZE[0] - BORDER_SIZE - self.player.size, ROOM_SIZE[1] - BORDER_SIZE - self.player.size]

        self.floor = 0
        self.level = Level(self.difficulty_config["room_count"])
        self.current_room = self.level.get_room(*self.level.start_pos)
        self.current_room.visited = True
        self.current_room.cleared = True
        self.room_coords = self.level.start_pos

        self.current_room.artifact = None
        self.artifact_pos = QPoint(ROOM_SIZE[0]//2 - 10, ROOM_SIZE[1]//2 - 10)
        create_artifact_pool()

        self.current_room.pickups = []

        self.ult_music_plays = False

        self.pressed_keys = set()

        self.projectiles = []


        self.effect_choices = []
        self.load_unlocked_effects()

        self.menus_init()
        
        self.load_room()

    def pixmap_init(self):
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

    def player_init(self):
        self.player = Player()
        self.player.size = 20
        self.player.x = ROOM_SIZE[0] // 2 - self.player.size // 2
        self.player.y = ROOM_SIZE[1] // 2 - self.player.size // 2
        self.player.speed = 4
        
        self.attack_effects = []
        for weapon in self.player.weapons.values():
            weapon.subscribe(self.on_enemies_hit)

        self.player.enemies = []

    def menus_init(self):
        #pause_menu
        self.isPaused = False

        self.pauseMenu = PauseMenu(self)
        self.pauseMenu.setGeometry(100, 100, 200, 100)

        self.pauseMenu.resumeRequested.connect(self.resume_game)
        self.pauseMenu.exitRequested.connect(self.main_window.go_to_main_menu)

        #death_menu
        self.isDead = False
        self.deathMenu = DeathMenu(self)
        self.deathMenu.setGeometry(100, 100, 200, 100)
        self.deathMenu.hide()
  
        self.deathMenu.reviveRequested.connect(self.revive_player)
        self.deathMenu.exitRequested.connect(self.main_window.go_to_main_menu)

        #win menu
        self.winMenu = WinMenu(self)
        self.winMenu.setGeometry(100, 100, 300, 200)
        self.winMenu.hide()
        self.winMenu.restartRequested.connect(self.restart_game)
        self.winMenu.exitRequested.connect(self.main_window.go_to_main_menu)

    def set_difficulty(self, difficulty_name):
        self.difficulty_name = difficulty_name
        self.difficulty_config = DIFFICULTY_SETTINGS[difficulty_name]
      
    def load_unlocked_effects(self):
        self.effect_choices = []
        if self.room_coords == self.level.start_pos:
            unlocked = load_unlocked_effects()
            if unlocked:
                self.effect_choices = random.sample(unlocked, min(3, len(unlocked)))
            else:
                self.effect_choices = []

    def play_music_(self):
        if self.player.ultimate.is_active():
            if self.ult_music_plays:
                ...
            else:
                music.play_music("ultimate", loop=False, temporary=True)
                self.ult_music_plays = True
        else:
            match self.current_room.room_type:
                case "boss":
                    if not self.player.enemies:
                        music.play_music(f"background", loop=True, temporary=True)
                    else:
                        music.play_music(f"boss/boss{self.floor}", loop=True, temporary=True)
                case _:
                    music.play_music(f"background", loop=True, temporary=True)

    def pause_game(self):
        self.isPaused = True
        self.hud.pause()
        self.pauseMenu.show()
        self.pauseMenu.move(270, 200)
        self.timer.stop()
        music.play_music("menu", loop=True, temporary=True)
        self.player.on_pause_on()
        
    def resume_game(self):
        self.isPaused = False
        self.hud.resume()
        self.pauseMenu.hide()
        self.timer.start()
        self.play_music_()
        self.player.on_pause_off()

    def game_starts(self):
        self.pauseMenu.hide()
        self.isPaused = False
        self.timer.start(16)
        music.play_music("background", loop=True)

    def check_player_death(self):
        if self.player.hp <= 0:
            self.player_death()
        else:
            self.isDead = False

    def player_death(self):
        self.isDead = True
        self.isPaused = True
        self.timer.stop()
        self.deathMenu.show()
        self.deathMenu.move(270, 200)
        music.play_music("death", loop=True)

    def revive_player(self):
        self.player.hp = self.player.max_hp
        self.isDead = False
        self.isPaused = False
        self.floor = 0
        self.level = Level(self.difficulty_config["room_count"])
        self.current_room = self.level.get_room(*self.level.start_pos)
        self.current_room.visited = True
        self.current_room.cleared = True
        self.room_coords = self.level.start_pos
        self.load_unlocked_effects()
        self.player = Player()
        for weapon in self.player.weapons.values():
            weapon.subscribe(self.on_enemies_hit)
        create_artifact_pool()
        self.deathMenu.hide()
        self.timer.start(16)
        
        self.room_coords = self.level.start_pos
        self.current_room = self.level.get_room(*self.room_coords)
        self.player.x = ROOM_SIZE[0] // 2 - self.player.size // 2
        self.player.y = ROOM_SIZE[1] // 2 - self.player.size // 2
        self.load_room()

        music.play_music("background", loop=True)

    
    def check_win_condition(self):
        if (self.current_room.room_type == "next_level" and 
            self.floor == MAX_FLOORS - 1 and 
            not self.player.enemies):
            self.player_win()

    def player_win(self):
        self.isPaused = True
        self.timer.stop()
        self.winMenu.set_score(self.player.score)
        self.winMenu.show()
        self.winMenu.move(250, 200)
        music.play_music("win", loop=True)

    def restart_game(self):
        self.winMenu.hide()
        self.revive_player()

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
                self.player.enemies.extend(load_enemies_from_json(path, self.difficulty_config["hp_multiplier"], self.difficulty_config["damage_multiplier"]))
            else:
                print(path)
                self.player.enemies.extend(load_enemies_from_json("resources/data/enemies.json", self.difficulty_config["hp_multiplier"], self.difficulty_config["damage_multiplier"]))
            room.enemies = self.player.enemies
        elif room.room_type == "boss" and not room.cleared:
            music.play_music(f"boss/boss{self.floor}", loop=True, temporary=True)
            self.current_room.artifact = None
            match self.floor:
                case 0:
                    self.player.enemies.append(BossCharger(ROOM_SIZE[0] // 2 - 40, ROOM_SIZE[1] // 2 - 40, self.difficulty_config["hp_multiplier"], self.difficulty_config["damage_multiplier"]))
                case 1:
                    self.player.enemies.append(BossShooter(ROOM_SIZE[0] // 2 - 40, ROOM_SIZE[1] // 2 - 40, self.difficulty_config["hp_multiplier"], self.difficulty_config["damage_multiplier"]))
                case _:
                    self.player.enemies.append(BossSpawner(ROOM_SIZE[0] // 2 - 40, ROOM_SIZE[1] // 2 - 40, self.difficulty_config["hp_multiplier"], self.difficulty_config["damage_multiplier"]))
        elif room.room_type == "treasure" and not room.cleared and self.current_room.artifact == None:
            self.current_room.artifact = get_random_artifact()

    def on_enemies_hit(self, enemies):
        for e in enemies:
            if e in self.player.enemies:
                self.player.enemies.remove(e)
        if not self.player.enemies and not self.current_room.cleared:
            if self.current_room.room_type == "fight":
                self.player.score += 10

                if random.random() < 0.3:
                    self.current_room.pickups.append(HealthPickup((self.player.x + 30), self.player.y))
                    
                if random.random() < 0.15:
                    self.current_room.pickups.append(KeyPickup((self.player.x - 30), self.player.y))
                
                if random.random() < self.difficulty_config["heart_drop_chance"]:
                    if self.player.heal_fragments.add():
                        ...
            elif self.current_room.room_type == "boss":
                self.play_music_()
                self.player.score += 40
                if random.random() < self.difficulty_config["heart_drop_chance_boss"]:
                    if self.player.heal_fragments.add():
                        ...
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
                    if self.player.start_roll(direction):
                        self.hud.dodge_widget.circle.start_countdown(self.player.dodge.get_cooldown())

            # if event.key() == Qt.Key_E and self.current_room.artifact:
            #     dist = math.hypot(self.player.x - self.artifact_pos.x(), self.player.y - self.artifact_pos.y())
            #     if dist < 40:
            #         artifact = self.current_room.artifact

            #         if hasattr(artifact, "effect_cls"):
            #             if artifact.apply(self.player):
            #                 unlock_effect(artifact.effect_cls.__name__)
            #                 QMessageBox.information(self, "New effect", f"New effect unlocked: {artifact.effect_cls.__name__}")
            #             else:
            #                 QMessageBox.warning(self, "No space", "No free slots for effect!")
            #         else:
            #             artifact.apply(self.player)
            #             QMessageBox.information(self, "Artifact", f"Artifact received: {artifact.name}")

            #         self.current_room.artifact = None
            #         self.current_room.cleared = True

            if event.key() == Qt.Key_Q:
                if self.player.ultimate.activate():
                    music.play_music("ultimate", loop=False, temporary=True)
                    self.ult_music_plays = True
                    self.hud.ult_widget.circle.start_countdown(self.player.ultimate.get_cooldown())

            if event.key() == Qt.Key_C:
                if self.player.heal_fragments.use(self.player):
                    self.hud.update_heal(self.player.heal_fragments.get_count(), self.player.heal_fragments.get_max_count())
                else:
                    ...#XXX
            if event.key() in (Qt.Key_1, Qt.Key_2, Qt.Key_3):
                self.player.set_attack_type(int(event.text()))
                self.hud.update_chord(int(event.text()))

    def keyReleaseEvent(self, event):
        self.pressed_keys.discard(event.key())

    def mousePressEvent(self, event: QMouseEvent):
        if not self.isPaused:
            if event.button() == Qt.MouseButton.LeftButton:
                if QRect(0, 0, ROOM_SIZE[0], ROOM_SIZE[1]).contains(event.pos()):
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
                    
                    if self.player.shield.activate():
                        self.hud.shield_widget.circle.start_countdown(self.player.shield.get_cooldown())
                    
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
                    self.hud.power_chord_text.start_countdown(self.player.weapon.cooldown)
                elif atk_type == 'beam':
                    self.hud.major_chord_text.start_countdown(self.player.weapon.cooldown)
                elif atk_type == 'bomb':
                    self.hud.minor_chord_text.start_countdown(self.player.weapon.cooldown)

            music.play_sfx(f"sfx{self.player.attack_type}.mp3", duration=(self.player.attack_type * 0.5))

    def update_game(self):
        music.update()

        self.check_player_death()
        self.check_win_condition() 
        if self.isDead:
            _, hp, max_hp, _ = self.player.get_stats()
            self.hud.update_stats(hp, max_hp)
            return
        self.player.update()

        _, hp, max_hp, _ = self.player.get_stats()

        if not self.player.ultimate.is_active():
            if self.ult_music_plays:
                self.play_music_()
                self.ult_music_plays = False
        
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

        blocked_x = False
        blocked_y = False

        if new_y <= wall_thickness:
            if not (neighbors['up'] and abs(cx - ROOM_SIZE[0] // 2) <= door_width // 2 and not self.player.enemies):
                blocked_y = True
        if new_y + self.player.size >= ROOM_SIZE[1] - wall_thickness:
            if not (neighbors['down'] and abs(cx - ROOM_SIZE[0] // 2) <= door_width // 2 and not self.player.enemies):
                blocked_y = True
        if new_x <= wall_thickness:
            if not (neighbors['left'] and abs(cy - ROOM_SIZE[1] // 2) <= door_width // 2 and not self.player.enemies):
                blocked_x = True
        if new_x + self.player.size >= ROOM_SIZE[0] - wall_thickness:
            if not (neighbors['right'] and abs(cy - ROOM_SIZE[1] // 2) <= door_width // 2 and not self.player.enemies):
                blocked_x = True

        if not blocked_x:
            self.player.x = new_x
        if not blocked_y:
            self.player.y = new_y

        if self.player.y <= BORDER_SIZE // 2:
            self.try_move_room(0, -1)
        elif self.player.y + self.player.size >= FIELD_SIZE[1] + BORDER_SIZE // 2:
            self.try_move_room(0, 1)
        elif self.player.x <= BORDER_SIZE // 2:
            self.try_move_room(-1, 0)
        elif self.player.x + self.player.size >= FIELD_SIZE[0] + BORDER_SIZE // 2:
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
                    self.player.score += 10
                    if random.random() < self.difficulty_config["heart_drop_chance"]:
                        if self.player.heal_fragments.add():
                            self.hud.update_heal(self.player.heal_fragments.get_count(), self.player.heal_fragments.get_max_count())
                elif self.current_room.room_type == "boss":
                    self.play_music_()
                    self.player.score += 40
                    if random.random() < self.difficulty_config["heart_drop_chance_boss"]:
                        if self.player.heal_fragments.add():
                            self.hud.update_heal(self.player.heal_fragments.get_count(), self.player.heal_fragments.get_max_count())
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

        if self.current_room.artifact:
            dist = math.hypot(self.player.x - self.artifact_pos.x(), self.player.y - self.artifact_pos.y())
            if dist < 40:
                self.current_room.artifact.apply(self.player)
                self.current_room.artifact = None
                self.current_room.cleared = True

        for pickup in self.current_room.pickups:
            if not pickup.collected and pickup.check_collision(self.player.x, self.player.y, self.player.size):
                pickup.apply(self.player)
                pickup.collected = True

        self.current_room.pickups = [p for p in self.current_room.pickups if not p.collected]

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
                if self.floor < MAX_FLOORS - 1:
                    self.floor += 1
                    self.level = Level(self.difficulty_config["room_count"])  # Generate new floor
                    self.current_room = self.level.get_room(*self.level.start_pos)
                    self.current_room.visited = True
                    self.current_room.cleared = True
                    self.room_coords = self.level.start_pos
                    self.player.x = ROOM_SIZE[0] // 2 - self.player.size // 2
                    self.player.y = ROOM_SIZE[1] // 2 - self.player.size // 2
                    self.load_room()
                    return
                else:
                    self.player_win()
                    return
            else:
                self.room_coords = (new_x, new_y)
                self.current_room = next_room
                
                if dx == 1:
                    self.player.x = BORDER_SIZE
                    self.player.y = ROOM_SIZE[1] // 2 - self.player.size // 2
                elif dx == -1:
                    self.player.x = ROOM_SIZE[0] - BORDER_SIZE - self.player.size
                    self.player.y = ROOM_SIZE[1] // 2 - self.player.size // 2
                elif dy == 1:
                    self.player.y = BORDER_SIZE
                    self.player.x = ROOM_SIZE[0] // 2 - self.player.size // 2
                elif dy == -1:
                    self.player.y = ROOM_SIZE[1] - BORDER_SIZE - self.player.size
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

        door_w, door_h = 100, BORDER_SIZE

        painter.setPen(QColor(0, 0, 0, 0))

        
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
        # painter.drawText(20, 20, f"Floor: {self.floor} Room: {self.room_coords} ({self.current_room.room_type})")


        effect_colors = {
            'delay': QColor(255, 100, 0),
            'fuzz': QColor(150, 0, 255),
            'overdrive': QColor(0, 200, 255),
            'wah': QColor(0, 255, 0),
            'tremolo': QColor(255, 255, 0),
            'distortion': QColor(255, 0, 0),
        }

        painter.setPen(Qt.NoPen)
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
            painter.drawText(40, 70, self.current_room.artifact.description)

        for pickup in self.current_room.pickups:
            pickup.draw(painter)

        if self.room_coords == self.level.start_pos and self.effect_choices:
            for i, eff_class in enumerate(self.effect_choices):
                painter.setPen(QColor(255, 255, 255))
                painter.setBrush(QColor(80 + i*60, 80, 255 - i*60))
                painter.drawRect(100 + i*140, 100, 120, 40)
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(110 + i*140, 125, eff_class.__name__)


        minimap_scale = 8
        minimap_offset_x = WINDOW_WIDTH - 125
        minimap_offset_y = 85
        room_size = 20

        for (rx, ry), room in self.level.rooms.items():
            color = QColor(100, 100, 100)
            if room == self.current_room:
                color = QColor(0, 255, 0)
            elif room.room_type == "boss":
                color = QColor(255, 0, 0)
            elif room.room_type == "treasure":
                color = QColor(255, 215, 0)
            elif room.visited:
                color = QColor(200, 200, 200)
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
            painter.fillRect(QRect(0, 0, *ROOM_SIZE), QColor(255, 0, 0, 50))
            painter.setOpacity(1.0)

        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)

        score_text = f"Score: {self.player.score}"
        text_rect = painter.fontMetrics().boundingRect(score_text)
        text_x = ROOM_SIZE[0] // 2 - text_rect.width() // 2
        text_y = 40

        painter.drawText(text_x, text_y, score_text)
