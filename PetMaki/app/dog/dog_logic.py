# dog_logic.py
import random
from ctypes import wintypes
import ctypes
from PyQt6.QtWidgets import QApplication
from app.utils import user32, EnumWindowsProc

class DogLogic:
    """Функциональная часть: логика поведения, расчет физики и WinAPI взаимодействия"""
    def __init__(self, window):
        self.w = window  # Ссылка на окно для изменения его позиции и вызова графических методов
        
        # Состояния и физические параметры
        self.state = None
        self.direction = 1
        self.walk_speed = 3
        self.run_speed = 7      
        self.current_speed = 0   
        self.dragging = False

    def decide_action(self):
        """Принятие решения о следующем действии на основе положения на экране"""
        if self.dragging: return
        floor_y = self.get_floor_y()
        if self.w.pos().y() + self.w.height() < floor_y: return 

        action = random.choice(['idle', 'idle', 'walk_left', 'walk_right', 'run_left', 'run_right'])
        
        if action == 'idle':
            self.w.set_state('idle', self.direction)
        elif action == 'walk_left':
            self.w.set_state('walk', -1)
        elif action == 'walk_right':
            self.w.set_state('walk', 1)
        elif action == 'run_left':
            self.w.set_state('run', -1)
        elif action == 'run_right':
            self.w.set_state('run', 1)
            
        # Обновляем интервал таймера в окне
        self.w.decision_timer.setInterval(random.randint(2000, 4000))

    def get_floor_y(self):
        """Вычисление уровня ближайшего окна или низа экрана"""
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
        """Гравитация и перемещение по горизонтали"""
        if self.dragging: return
        floor_y = self.get_floor_y()
        pet_bottom = self.w.pos().y() + self.w.height()
        
        # Физика падения (гравитация)
        if pet_bottom < floor_y:
            new_y = self.w.pos().y() + 6
            if new_y + self.w.height() > floor_y: new_y = floor_y - self.w.height()
            self.w.move(self.w.pos().x(), new_y)
            if self.state in ['walk', 'run']: self.w.set_state('idle', self.direction)
            return 
                
        # Горизонтальное движение внутри границ экрана
        if self.state in ['walk', 'run']:
            new_x = self.w.pos().x() + (self.current_speed * self.direction)
            screen_width = QApplication.primaryScreen().geometry().width()
            
            if new_x < 0:
                new_x = 0
                self.w.set_state(self.state, 1) 
            elif new_x + self.w.width() > screen_width:
                new_x = screen_width - self.w.width()
                self.w.set_state(self.state, -1) 
                
            self.w.move(new_x, self.w.pos().y())