from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QFont
from PySide6.QtCore import Qt, QTimer
import math

class CountdownCircle(QWidget):
    def __init__(self, total_time=5, text = "", parent=None):
        super().__init__(parent)
        self.hide()
        self.is_paused = False  # флаг для паузы
        QTimer.singleShot(100, self.show)  # показать виджет через 100 мс
        self.text = text  # текст, отображаемый при окончании таймера
        
        self.total_time = total_time  # общее время в секундах
        self.remaining_time = total_time
        self.setFixedSize(80, 80)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(100)  # обновлять каждые 100 мс

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def update_timer(self):
        if self.is_paused:
            return
        
        self.remaining_time -= 0.1
        if self.remaining_time <= 0:
            self.remaining_time = 0
            self.timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.remaining_time > 0:
            # Радиус и центр
            radius = min(self.width(), self.height()) // 2 - 7
            center = self.rect().center()

            # Фон круга (серый)
            pen = QPen(Qt.gray, 10)
            painter.setPen(pen)
            painter.drawEllipse(center, radius, radius)

            # Активная дуга (синяя)
            percent = self.remaining_time / self.total_time
            angle_span = 360 * percent

            pen = QPen(Qt.white, 10)
            painter.setPen(pen)
            painter.drawArc(
                center.x() - radius, center.y() - radius,
                radius * 2, radius * 2,
                90 * 16,  # старт с верхней точки (12 часов)
                -angle_span * 16  # по часовой стрелке
            )

            # Текст (остаток времени, округлённый)
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", 20, QFont.Bold))
            text = f"{self.remaining_time:.1f}"
            painter.drawText(self.rect(), Qt.AlignCenter, text)
        else:
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", 20, QFont.Bold))
            text = f"{self.text}"
            painter.drawText(self.rect(), Qt.AlignCenter, text)
            
        
    def start_countdown(self, seconds):
        self.total_time = seconds
        self.remaining_time = seconds
        self.timer.start(100)
        self.update()

    def set_progress(self, remaining, total):
        self.total_time = total
        self.remaining_time = remaining
        self.update()