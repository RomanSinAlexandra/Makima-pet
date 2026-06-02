# chibi_logic.py
import os
import sys
import random
import winreg 
import ctypes
from ctypes import wintypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer  # Добавили QTimer для отслеживания кликов
from PyQt6.QtGui import QCursor

from app.utils import user32, EnumWindowsProc, APP_NAME, REG_PATH

class ChibiLogic:
    """Логика поведения питомца: физика, WinAPI, режимы работы и автозапуск"""
    def __init__(self, window):
        self.w = window  # Ссылка на графическое окно ChibiPet
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_dir = os.path.join(os.path.dirname(current_dir), "resource")
        self.skins_dir = os.path.join(self.script_dir, "skins")
        
        self.current_skin_name = "Makima"
        self.sound_files = []
        
        # Состояния поведения и флаги
        self.state = None 
        self.direction = 1  
        self.behavior_mode = 'random' 
        self.demon_mode = False 
        self.show_time = False 
        self.walk_speed = 2
        self.dragging = False
        self.timer_seconds_left = 0

        # --- Система комбо-кликов для злости ---
        self.click_count = 0
        
        # Таймер сброса серии кликов (если игрок перестал кликать, комбо обнуляется через 1.2 сек)
        self.click_reset_timer = QTimer()
        self.click_reset_timer.setSingleShot(True)
        self.click_reset_timer.timeout.connect(self.reset_clicks)
        
        # Таймер длительности злости (питомец злится 3 секунды, затем остывает)
        self.angry_timer = QTimer()
        self.angry_timer.setSingleShot(True)
        self.angry_timer.timeout.connect(self.reset_angry)

    def get_skin_paths(self, skin_name):
        """Определяет пути к ресурсам выбранного скина"""
        self.current_skin_name = skin_name
        
        if skin_name == "Makima":
            skin_path = os.path.join(self.script_dir, "skins/Makima")
            sound_dir = os.path.join(skin_path, "sound")
        else:
            skin_path = os.path.join(self.skins_dir, skin_name)
            sound_dir = os.path.join(skin_path, "sound")

        self.sound_files = []
        if os.path.exists(sound_dir):
            for file in os.listdir(sound_dir):
                if file.endswith(('.wav', '.mp3')):
                    self.sound_files.append(os.path.join(sound_dir, file))
                    
        return {
            "start": os.path.join(skin_path, "start.gif"),
            "idle": os.path.join(skin_path, "idle.gif"),
            "walk": os.path.join(skin_path, "walk.gif"),
            "demon_start": os.path.join(skin_path, "demon_start.gif"),
            "demon_idle": os.path.join(skin_path, "demon_idle.gif"),
            "demon_walk": os.path.join(skin_path, "demon_walk.gif"),
            "menu_bg": os.path.join(skin_path, "Background.png"),
            "jump": os.path.join(skin_path, "jump.gif"),
            "demon_jump": os.path.join(skin_path, "demon_jump.gif"),
            # ДОБАВИЛИ: Пути к анимациям злости
            "angry": os.path.join(skin_path, "angry.gif"),
            "demon_angry": os.path.join(skin_path, "demon_angry.gif"),
        }

    def decide_action(self):
        """Выбор случайного действия в режиме 'random'"""
        # ИСПРАВЛЕНИЕ: Если злится, не прерываем анимацию случайным действием
        if self.state in ['start', 'demon_start', 'angry', 'demon_angry'] or self.dragging or self.behavior_mode == 'follow': 
            return 
            
        floor_y = self.get_floor_y()
        pet_bottom = self.w.pos().y() + self.w.height()
        if pet_bottom < floor_y: return 

        # ИСПРАВЛЕНИЕ: Сделали темп выбора действий одинаковым (убрали демоническую спешку)
        actions = ['idle', 'idle', 'walk_left', 'walk_right']
        action = random.choice(actions)

        if action == 'idle': self.w.set_state('idle', self.direction)
        elif action == 'walk_left': self.w.set_state('walk', direction=-1)
        elif action == 'walk_right': self.w.set_state('walk', direction=1)
            
        # Скорость смены решений теперь всегда умеренная
        self.w.decision_timer.setInterval(random.randint(2000, 5000))

    def get_floor_y(self):
        """Поиск под питомцем верхней границы других окон или низа экрана"""
        screen_geometry = QApplication.primaryScreen().geometry()
        floor_y = screen_geometry.height()
        pet_x_center = self.w.pos().x() + self.w.width() // 2
        pet_bottom = self.w.pos().y() + self.w.height()
        
        def enum_windows_proc(hwnd, lParam):
            nonlocal floor_y
            if hwnd == int(self.w.winId()): return True
            if user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
                if user32.GetWindowTextLengthW(hwnd) > 0:
                    rect = wintypes.RECT()
                    user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    if rect.left <= pet_x_center <= rect.right:
                        if pet_bottom - 10 <= rect.top <= floor_y:
                            floor_y = rect.top
            return True

        user32.EnumWindows(EnumWindowsProc(enum_windows_proc), 0)
        return floor_y

    def apply_physics(self):
        """Расчет падения (гравитации) и алгоритмов перемещения"""
        if self.dragging: return
            
        floor_y = self.get_floor_y()
        pet_bottom = self.w.pos().y() + self.w.height()
        
        # Симуляция падения
        if pet_bottom < floor_y:
            # ИСПРАВЛЕНИЕ: Скорость падения теперь всегда равна 5 (убрали 10 у демона)
            fall_speed = 5 
            new_y = self.w.pos().y() + fall_speed
            
            if new_y + self.w.height() > floor_y: 
                new_y = floor_y - self.w.height()
                
            self.w.move(self.w.pos().x(), new_y)
            self.w.set_state('fall', self.direction)
            return 
        else:
            if self.state == 'fall':
                self.w.set_state('idle', self.direction)
                
        # ИСПРАВЛЕНИЕ: Блокируем движение, пока проигрывается злость
        if self.state in ['start', 'demon_start', 'angry', 'demon_angry']: return

        # Движение за курсором
        if self.behavior_mode == 'follow':
            cursor_x = QCursor.pos().x()
            pet_center_x = self.w.pos().x() + self.w.width() // 2
            dist_x = cursor_x - pet_center_x
            
            if abs(dist_x) > self.walk_speed * 2: 
                direction = 1 if dist_x > 0 else -1
                self.w.set_state('walk', direction)
                new_x = self.w.pos().x() + (self.walk_speed * direction)
                self.w.move(new_x, self.w.pos().y())
            else:
                self.w.set_state('idle', self.direction)
                
        # Случайное блуждание с отскоком от краев экрана
        elif self.behavior_mode == 'random' and self.state == 'walk':
            new_x = self.w.pos().x() + (self.walk_speed * self.direction)
            screen_width = QApplication.primaryScreen().geometry().width()
            if new_x < 0:
                new_x = 0
                self.w.set_state('walk', direction=1) 
            elif new_x + self.w.width() > screen_width:
                new_x = screen_width - self.w.width()
                self.w.set_state('walk', direction=-1) 
                
            self.w.move(new_x, self.w.pos().y())

    # --- Новые методы для обработки злости при кликах ---
    def register_click(self):
        """Вызывать этот метод из pet.py при каждом успешном клике по питомцу!"""
        # Не злимся, если питомец падает или только запускается
        if self.state in ['start', 'demon_start', 'fall']: 
            return
            
        self.click_count += 1
        self.click_reset_timer.start(1200) # Если пауза между кликами больше 1.2 сек — комбо сбросится
        
        if self.click_count >= 3:  # Третий клик подряд активирует злость
            self.click_count = 0
            self.click_reset_timer.stop()
            
            # Переключаем состояние
            target_state = 'demon_angry' if self.demon_mode else 'angry'
            self.w.set_state(target_state, self.direction)
            
            # Запускаем таймер злости на 3000 мс (3 секунды)
            self.angry_timer.start(3000)

    def reset_clicks(self):
        """Сброс счетчика кликов по таймауту"""
        self.click_count = 0

    def reset_angry(self):
        """Возврат в обычное состояние после того, как питомец позлился"""
        if self.state in ['angry', 'demon_angry']:
            self.w.set_state('idle', self.direction)

    def is_click_on_pet(self, pos):
        """Проверка клика: игнорирует прозрачные пиксели на GIF-анимации"""
        if self.show_time and self.w.time_label.geometry().contains(pos): return True
        current_movie = self.w.label.movie()
        if not current_movie: return True
        image = current_movie.currentImage()
        if image.isNull(): return True
        image_pos = self.w.label.mapFromParent(pos)
        if not self.w.label.rect().contains(image_pos): return False
        if image.size() != self.w.label.size():
            image = image.scaled(self.w.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        if image_pos.x() < 0 or image_pos.y() < 0 or image_pos.x() >= image.width() or image_pos.y() >= image.height():
            return False
        pixel_color = image.pixelColor(image_pos.x(), image_pos.y())
        return pixel_color.alpha() > 10 

    def is_autostart_enabled(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except OSError:
            return False

    def set_behavior_mode(self, mode):
        """Меняет режим поведения питомца и обновляет его состояние"""
        if mode in ['random', 'follow']:
            self.behavior_mode = mode
            if mode == 'follow':
                self.apply_physics()
            else:
                self.w.decision_timer.setInterval(100)

    def toggle_autostart(self, state):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
            if state:
                if getattr(sys, 'frozen', False):
                    cmd = f'"{sys.executable}"'
                else:
                    pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
                    script_path = os.path.abspath(sys.argv[0])
                    cmd = f'"{pythonw_path}" "{script_path}"'
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                winreg.DeleteValue(key, APP_NAME)
            winreg.CloseKey(key)
        except OSError:
            pass