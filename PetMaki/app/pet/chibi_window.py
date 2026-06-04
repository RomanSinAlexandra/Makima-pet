import os
import random
import json
from PyQt6.QtWidgets import (QMainWindow, QLabel, QGraphicsColorizeEffect, QInputDialog, QApplication)
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize, QDateTime, QUrl, QTime
from PyQt6.QtGui import QMovie, QPainter, QColor, QPixmap
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

from app.widgets.widgets import PetLabel
from app.dog.dog_window import DogPet
from app.pet.chibi_logic import ChibiLogic
from app.widgets.menu import PetMenu 

class ChibiPet(QMainWindow):

    def __init__(self):
        super().__init__()
        
        # Инстанцируем логический контроллер
        self.logic = ChibiLogic(self)
        
        self.bubble_path = os.path.join(self.logic.script_dir, "cloud.png")
        self.base_movie_size = QSize(150, 230)

        self.dogs = []

        # Инициализируем переменные для анимаций злости, чтобы они существовали в контексте класса
        self.movie_angry = None
        self.movie_demon_angry = None

        # Медиаплеер звуков
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)

        self.last_click_time = QTime()
        self.is_double_click = False
        self.was_dragged = False 

        # Настройки прозрачного окна без рамок
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Текстовое облако (таймер / часы)
        self.time_label = QLabel(self)
        self.time_label.hide() 
        
        if os.path.exists(self.bubble_path):
            self.bubble_pixmap = QPixmap(self.bubble_path)
            if self.bubble_pixmap.width() > 160:
                self.bubble_pixmap = self.bubble_pixmap.scaledToWidth(160, Qt.TransformationMode.SmoothTransformation)
        else:
            self.bubble_pixmap = None
        
        self.time_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 11px;
                font-family: 'Courier New', 'Lucida Console', monospace;
                font-weight: bold;
                qproperty-alignment: 'AlignCenter';
                background-color: transparent;
                padding-bottom: 18px; 
            }
        """)

        self.label = PetLabel(self)

        # Точка для безрывкового перетаскивания окна
        self.drag_start_position = QPoint()

        # Служебные таймеры обновления интерфейса
        self.time_update_timer = QTimer()
        self.time_update_timer.timeout.connect(self.update_time_text)
        
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.tick_timer)

        # Инициализация первого скина (Загрузит Макиму по умолчанию)
        saved_skin = self.load_config()
        self.load_skin(saved_skin)
        self.update_widget_geometries()
        
        # Анимация появления
        self.set_state('start', 1)
        QTimer.singleShot(2000, lambda: self.set_state('idle', 1) if self.logic.state == 'start' else None)
        QTimer.singleShot(100, self.adjust_size_to_movie)

        # Процедурные таймеры физики и принятия решений
        self.physics_timer = QTimer()
        self.physics_timer.timeout.connect(self.logic.apply_physics)
        self.physics_timer.start(20)

        self.decision_timer = QTimer()
        self.decision_timer.timeout.connect(self.logic.decide_action)
        self.decision_timer.start(3000)

        self.show()


    def load_config(self):
        """Загрузка сохраненного скина и настроек из файла config.json"""
        self.config_path = os.path.join(self.logic.script_dir, "config.json")
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Восстанавливаем режим демона
                    self.logic.demon_mode = config.get("demon_mode", False)
                    # Возвращаем имя сохраненного скина
                    return config.get("current_skin", "Makima")
            except Exception as e:
                print(f"Ошибка при чтении конфига: {e}")
        
        # Если файла нет или он поврежден, возвращаем дефолтную Макиму
        return "Makima"

    def save_config(self):
        """Сохранение текущего скина и состояния в файл config.json"""
        try:
            config = {
                "current_skin": self.logic.current_skin_name,
                "demon_mode": self.logic.demon_mode
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении конфига: {e}")

    def load_skin(self, skin_name):
        """Загрузка конфигурации текстур и звуков из директории скина"""
        self.logic.current_skin_name = skin_name
        paths = self.logic.get_skin_paths(skin_name)

        print(f"Проверка пути idle.gif для {skin_name}: {paths['idle']} -> Существует: {os.path.exists(paths['idle'])}")
        
        self.movie_start = QMovie(paths["start"]) if os.path.exists(paths["start"]) else QMovie(paths["idle"])
        self.movie_idle = QMovie(paths["idle"])
        self.movie_walk = QMovie(paths["walk"])
        self.movie_demon_start = QMovie(paths["demon_start"]) if os.path.exists(paths["demon_start"]) else QMovie(paths["idle"])
        self.movie_demon_idle = QMovie(paths["demon_idle"]) if os.path.exists(paths["demon_idle"]) else self.movie_idle
        self.movie_demon_walk = QMovie(paths["demon_walk"]) if os.path.exists(paths["demon_walk"]) else self.movie_walk
        
        self.movie_jump = QMovie(paths["jump"]) if os.path.exists(paths["jump"]) else QMovie(paths["idle"])
        self.movie_demon_jump = QMovie(paths["demon_jump"]) if os.path.exists(paths["demon_jump"]) else self.movie_jump
        
        self.movie_angry = QMovie(paths["angry"]) if os.path.exists(paths["angry"]) else QMovie(paths["idle"])
        self.movie_demon_angry = QMovie(paths["demon_angry"]) if os.path.exists(paths["demon_angry"]) else self.movie_angry
        
        self.menu_bg_path = paths["menu_bg"]
        
        self.all_movies = [
            self.movie_start, self.movie_idle, self.movie_walk, 
            self.movie_demon_start, self.movie_demon_idle, self.movie_demon_walk,
            self.movie_jump, self.movie_demon_jump,
            self.movie_angry, self.movie_demon_angry
        ]
        
        for m in self.all_movies:
            if m and m.isValid(): 
                m.setScaledSize(self.base_movie_size)

        # === ИЗМЕНЕНО: Анимация СТАРТА при смене скина ===
        # Сбрасываем старое состояние, чтобы принудительно обновить анимацию
        self.logic.state = None 
        
        # Определяем, какой старт включать (обычный или демонический)
        target_start = 'demon_start' if self.logic.demon_mode else 'start'
        self.set_state(target_start, self.logic.direction)
        
        # Через 2 секунды (2000 мс) плавно переводим в idle
        QTimer.singleShot(2000, lambda: self.set_state('idle', self.logic.direction) if self.logic.state in ['start', 'demon_start'] else None)
        
        # Подгоняем размеры окна под новый скин (на случай, если разрешения гифок разные)
        QTimer.singleShot(100, self.adjust_size_to_movie)
        # ================================================

        if hasattr(self, 'menu') and self.menu:
            self.menu.menu_bg_path = self.menu_bg_path
            self.menu.init_stylesheet()

        self.save_config()

    def play_random_sound(self):
        if self.logic.sound_files:
            chosen_sound = random.choice(self.logic.sound_files)
            self.media_player.setSource(QUrl.fromLocalFile(chosen_sound))
            self.media_player.play()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.logic.is_click_on_pet(event.pos()):
                self.logic.dragging = True
                self.was_dragged = False
                self.drag_start_position = event.globalPosition().toPoint() - self.pos()
                
                current_time = QTime.currentTime()
                
                if self.last_click_time.isValid() and self.last_click_time.msecsTo(current_time) < 250:
                    self.is_double_click = True
                    self.set_state('angry', self.logic.direction)
                    
                    QTimer.singleShot(3000, lambda: self.set_state('idle', self.logic.direction) if self.logic.state == 'angry' else None)
                else:
                    self.is_double_click = False
                    if self.logic.state not in ['start', 'demon_start', 'fall', 'angry']:
                        self.set_state('idle', self.logic.direction)
                
                self.last_click_time = current_time
                event.accept()

    def mouseMoveEvent(self, event):
        if self.logic.dragging:
            self.was_dragged = True 
            self.move(event.globalPosition().toPoint() - self.drag_start_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.logic.dragging:
            self.logic.dragging = False
            if not self.was_dragged and not self.is_double_click:
                self.play_random_sound()

    def toggle_time_bubble(self, enabled):
        self.logic.show_time = enabled
        old_bottom = self.pos().y() + self.height()
        
        if enabled:
            self.time_update_timer.start(1000)
            self.update_time_text()
            self.time_label.show()
        else:
            self.time_update_timer.stop()
            self.time_label.hide()
            
        self.update_widget_geometries()
        self.move(self.pos().x(), old_bottom - self.height())

    def update_time_text(self):
        if self.logic.timer_seconds_left > 0:
            m, s = divmod(self.logic.timer_seconds_left, 60)
            self.time_label.setText(f"Таймер:\n{m:02d}:{s:02d}")
        else:
            current_dt = QDateTime.currentDateTime().toString("yyyy.MM.dd\n HH:mm:ss")
            self.time_label.setText(current_dt)

    def start_timer(self, minutes):
        self.logic.timer_seconds_left = minutes * 60
        self.toggle_time_bubble(True)
        self.update_time_text()
        self.countdown_timer.start(1000)

    def start_custom_timer(self):
        minutes, ok = QInputDialog.getInt(self, "Таймер", "Введите минуты:", 10, 1, 1440)
        if ok:
            self.start_timer(minutes)

    def stop_timer(self):
        self.logic.timer_seconds_left = 0
        self.countdown_timer.stop()
        self.update_time_text()

    def tick_timer(self):
        if self.logic.timer_seconds_left > 0:
            self.logic.timer_seconds_left -= 1
            self.update_time_text()
            if self.logic.timer_seconds_left <= 0:
                self.countdown_timer.stop()
                self.play_random_sound()

    def update_widget_geometries(self):
        w_movie = self.base_movie_size.width()
        h_movie = self.base_movie_size.height()
        
        if self.logic.show_time and self.bubble_pixmap:
            b_width = self.bubble_pixmap.width()
            b_height = self.bubble_pixmap.height()
            max_w = max(w_movie, b_width)
            overlap = 15 
            total_h = h_movie + b_height - overlap
            self.resize(max_w, total_h)
            
            self.time_label.setGeometry(max_w - b_width, 0, b_width, b_height)
            self.label.setGeometry((max_w - w_movie) // 2, b_height - overlap, w_movie, h_movie)
            self.time_label.raise_()
        else:
            self.resize(w_movie, h_movie)
            self.label.setGeometry(0, 0, w_movie, h_movie)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.logic.show_time and self.bubble_pixmap:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawPixmap(self.time_label.geometry(), self.bubble_pixmap)

    def adjust_size_to_movie(self):
        size = self.movie_idle.currentImage().size()
        if not size.isEmpty():
            self.base_movie_size = size
            for m in self.all_movies:
                if m and m.isValid(): m.setScaledSize(size)
            self.update_widget_geometries()

    def toggle_demon_mode(self, enabled):
        self.logic.demon_mode = enabled
        if enabled:
            self.set_state('demon_start', self.logic.direction)
            QTimer.singleShot(2000, lambda: self.set_state('idle', self.logic.direction) if self.logic.state == 'demon_start' else None)
        else: 
            self.set_state('idle', self.logic.direction)

        self.save_config()

    def set_state(self, new_state, direction=1):
        if self.logic.state == new_state and self.logic.direction == direction: return 

        self.logic.state = new_state
        self.logic.direction = direction

        for m in self.all_movies: 
            if m: m.stop()

        if new_state == 'start': active_movie = self.movie_start
        elif new_state == 'demon_start': active_movie = self.movie_demon_start
        elif new_state == 'idle': active_movie = self.movie_demon_idle if self.logic.demon_mode else self.movie_idle
        elif new_state == 'walk': active_movie = self.movie_demon_walk if self.logic.demon_mode else self.movie_walk
        elif new_state == 'fall': active_movie = self.movie_demon_jump if self.logic.demon_mode else self.movie_jump
        elif new_state == 'angry': active_movie = self.movie_angry
        elif new_state == 'demon_angry': active_movie = self.movie_demon_angry

        if active_movie:
            self.label.setMovie(active_movie)
            active_movie.start()
            self.label.set_flipped(self.logic.direction == -1)
        
    def spawn_dog(self) -> None:
        dog = DogPet(self.pos()) 
        self.dogs.append(dog) 

    def contextMenuEvent(self, event):
        menu = PetMenu(self)
        menu.exec(event.globalPos())