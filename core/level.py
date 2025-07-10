import random
from core.room import Room

class Level:
    def __init__(self, room_count=11, width=5, height=5):
        self.room_count = room_count
        self.width = width
        self.height = height
        self.rooms = {}
        self.start_pos = (width // 2, height // 2)
        self.generate_level()

    def generate_level(self):
        cx, cy = self.start_pos
        self.rooms[(cx, cy)] = Room(cx, cy, "start")

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        queue = [(cx, cy)]

        # 1. Создаём основной остов комнат
        while len(self.rooms) < self.room_count:
            x, y = random.choice(queue)
            dx, dy = random.choice(directions)
            nx, ny = x + dx, y + dy

            if (nx, ny) not in self.rooms:
                self.rooms[(nx, ny)] = Room(nx, ny, "fight")
                queue.append((nx, ny))

        # 2. Находим возможные тупиковые места (ещё не занятые)
        candidates = []
        for (x, y) in list(self.rooms.keys()):
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (nx, ny) in self.rooms:
                    continue

                # Подсчитать, сколько соседей будет у новой комнаты
                neighbor_count = 0
                for ddx, ddy in directions:
                    adj_x, adj_y = nx + ddx, ny + ddy
                    if (adj_x, adj_y) in self.rooms:
                        neighbor_count += 1

                if neighbor_count == 1:
                    candidates.append((nx, ny))

        random.shuffle(candidates)

        # 3. Создаём комнату босса
        if candidates:
            bx, by = candidates.pop()
            self.rooms[(bx, by)] = Room(bx, by, "boss")
            for dx, dy in directions:
                nx, ny = bx + dx, by + dy
                if (nx, ny) in candidates:
                    candidates.remove((nx, ny))

        # 4. Создаём до 3 комнат-сокровищниц
        for _ in range(3):
            if candidates:
                tx, ty = candidates.pop()
                self.rooms[(tx, ty)] = Room(tx, ty, "treasure")
                for dx, dy in directions:
                    nx, ny = tx + dx, ty + dy
                    if (nx, ny) in candidates:
                        candidates.remove((nx, ny))

        for dx, dy in directions:
            nx, ny = bx + dx, by + dy
            if (nx, ny) in self.rooms:
                continue

            neighbor_count = 0
            for ddx, ddy in directions:
                adj_x, adj_y = nx + ddx, ny + ddy
                if (adj_x, adj_y) in self.rooms:
                    neighbor_count += 1

            if neighbor_count == 1:
                candidates.append((nx, ny))
        if candidates:
            sx, sy = candidates.pop()
            self.rooms[(sx, sy)] = Room(sx, sy, "next_level")
        else:
            for dx, dy in directions:
                nx, ny = bx + dx, by + dy
                if (nx, ny) in self.rooms:
                    continue
                self.rooms[(nx, ny)] = Room(nx, ny, "next_level")
                break



    def get_room(self, x, y):
        return self.rooms.get((x, y), None)
