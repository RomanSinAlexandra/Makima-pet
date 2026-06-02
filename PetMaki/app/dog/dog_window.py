# dog_window.py
import os
from PyQt6.QtWidgets import QMainWindow, QMenu
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize, QUrl
from PyQt6.QtGui import QMovie, QAction
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer 

from app.widgets.widgets import PetLabel
from app.dog.dog_logic import DogLogic

class DogPet(QMainWindow):
    """Оконная часть: создание интерфейса, регистрация событий мыши и ресурсов"""
    def __init__(self, start_pos):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Указывает прямо на папку app/resource
        self.script_dir = os.path.join(os.path.dirname(current_dir), "resource")
        
        # Привязываем логическую часть к окну
        self.logic = DogLogic(self)
        
        # --- ОПТИМИЗАЦИЯ ПУТЕЙ: изолируем ресурсы собаки в app/resource/dog/ ---
        dog_res_dir = os.path.join(self.script_dir, "dog")
        
        self.idle_path = os.path.join(dog_res_dir, "dog_idle.gif")
        self.walk_path = os.path.join(dog_res_dir, "dog_walk.gif")
        self.run_path = os.path.join(dog_res_dir, "dog_run.gif") 
        self.bark_sound = os.path.join(dog_res_dir, "sound", "bark.mp3")
        
        # Инициализация звука
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8)

        # Настройки безрамочного прозрачного окна
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Размеры и анимации
        self.label = PetLabel(self)
        self.movie_idle = QMovie(self.idle_path)
        self.movie_walk = QMovie(self.walk_path)
        self.movie_run = QMovie(self.run_path) 
        
        self.base_movie_size = QSize(150, 150) 
        
        if self.movie_idle.isValid(): self.movie_idle.setScaledSize(self.base_movie_size)
        if self.movie_walk.isValid(): self.movie_walk.setScaledSize(self.base_movie_size)
        if self.movie_run.isValid(): self.movie_run.setScaledSize(self.base_movie_size)
            
        self.resize(self.base_movie_size)
        self.label.setGeometry(0, 0, self.base_movie_size.width(), self.base_movie_size.height())

        self.was_dragged = False
        self.drag_start_position = QPoint()

        # Стартовая позиция появления
        self.move(start_pos.x() + 100, start_pos.y())

        # Запуск начального состояния
        self.set_state('idle', 1)
        
        # Таймеры (вызывают методы из dog_logic)
        self.physics_timer = QTimer()
        self.physics_timer.timeout.connect(self.logic.apply_physics)
        self.physics_timer.start(20)

        self.decision_timer = QTimer()
        self.decision_timer.timeout.connect(self.logic.decide_action)
        self.decision_timer.start(3000)

        self.show()

    def play_bark(self):
        if os.path.exists(self.bark_sound):
            self.media_player.setSource(QUrl.fromLocalFile(self.bark_sound))
            self.media_player.play()

    # --- ИСПРАВЛЕНИЕ ДРАГ-ОФФСЕТА: стабильное перемещение без джиттера ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.logic.dragging = True
            self.was_dragged = False
            # Запоминаем глобальную позицию клика относительно левого верхнего угла окна
            self.drag_start_position = event.globalPosition().toPoint() - self.pos()
            self.set_state('idle', self.logic.direction)

    def mouseMoveEvent(self, event):
        if self.logic.dragging:
            self.was_dragged = True
            # Перемещаем окно по чистым глобальным координатам мыши
            self.move(event.globalPosition().toPoint() - self.drag_start_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.logic.dragging:
            self.logic.dragging = False
            if not self.was_dragged:
                self.play_bark()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        # Стилизуем меню собаки под общую эстетику приложения, если нужно
        menu.setStyleSheet("QMenu { border: 1px solid #5c1d1d; padding: 5px; }")
        quit_action = QAction("Убрать собаку", self)
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)
        menu.exec(event.globalPos())

    def set_state(self, new_state, direction=1):
        """Визуальное переключение гифок и отражение текстуры"""
        if self.logic.state == new_state and self.logic.direction == direction: return 
        
        # Синхронизируем состояние в логику
        self.logic.state = new_state
        self.logic.direction = direction

        self.movie_idle.stop()
        self.movie_walk.stop()
        self.movie_run.stop()

        if new_state == 'idle':
            active_movie = self.movie_idle
            self.logic.current_speed = 0
        elif new_state == 'walk':
            active_movie = self.movie_walk
            self.logic.current_speed = self.logic.walk_speed
        elif new_state == 'run':
            active_movie = self.movie_run
            self.logic.current_speed = self.logic.run_speed

        self.label.setMovie(active_movie)
        active_movie.start()
        self.label.set_flipped(self.logic.direction == -1)