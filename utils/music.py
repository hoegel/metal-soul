import os
import pygame
import random
import threading
import time

class MusicManager:
    def __init__(self, base_path="resources/sounds"):
        self.base_path = base_path
        self.current_category = None
        self.previous_categories = []
        self.track_queue = []
        self.current_track = None
        self.loop_enabled = True
        self.last_check_time = time.time()

        self.music_volume = 0.1
        self.sfx_volume = 0.0

        pygame.mixer.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        pygame.mixer.music.set_volume(self.music_volume)

    def _build_track_queue(self, category):
        folder = os.path.join(self.base_path, category)
        if not os.path.isdir(folder):
            print(f"[MusicManager] No folder: {folder}")
            return []

        tracks = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith((".ogg", ".mp3", ".wav"))]
        random.shuffle(tracks)
        return tracks

    def play_music(self, category, loop=True, temporary=False):
        if temporary and self.current_category:
            self.previous_categories.append(self.current_category)

        if self.current_category != category or not self.track_queue:
            self.current_category = category
            self.track_queue = self._build_track_queue(category)

        # print("Currently playing:", self.current_category)

        self.loop_enabled = loop
        self._play_next_in_queue()

    def _play_next_in_queue(self):
        if not self.track_queue:
            self.track_queue = self._build_track_queue(self.current_category)

        if self.track_queue:
            next_track = self.track_queue.pop(0)

            # while next_track == self.current_track and len(self.track_queue) > 0:
            #     self.track_queue.append(next_track)
            #     next_track = self.track_queue.pop(0)

            self.current_track = next_track
            pygame.mixer.music.load(next_track)
            pygame.mixer.music.play()
        else:
            print("[MusicManager] No tracks to play.")

    def update(self):
        if time.time() - self.last_check_time > 3:
            self.last_check_time = time.time()
            if not pygame.mixer.music.get_busy():
                if self.loop_enabled:
                    self._play_next_in_queue()

    def stop_music(self):
        pygame.mixer.music.stop()
        self.track_queue = []

    def play_sfx(self, name, duration=0.1):
        path = os.path.join(self.base_path, "sfx", name)
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.sfx_volume)
            sound.play()


            channel = sound.play()

            if duration is not None:
                def stop():
                    if channel.get_busy():
                        channel.stop()
                threading.Timer(duration, stop).start()

    def resume_previous_music(self):
        if self.previous_categories:
            previous = self.previous_categories.pop()
            self.play_music(previous)

    def set_volume(self, music_volume=None, sfx_volume=None):
        if music_volume is not None:
            self.music_volume = music_volume
            pygame.mixer.music.set_volume(music_volume)
        if sfx_volume is not None:
            self.sfx_volume = sfx_volume

    def play_effect(self, effect_name):
        path = os.path.join(self.base_path, "sfx", effect_name)
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.sfx_volume)
            sound.play()

music = MusicManager()