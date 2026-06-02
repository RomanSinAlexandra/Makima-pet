import os
from PyQt6.QtWidgets import QMenu, QApplication
from PyQt6.QtGui import QAction, QActionGroup

class PetMenu(QMenu):
    """Класс контекстного меню для управления питомцем"""
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.pet = parent_window
        self.logic = parent_window.logic
        self.menu_bg_path = os.path.join(self.logic.skins_dir, "Makima", "MakimaBackground.png")
        
        self.init_stylesheet()
        self.build_menu()

    def init_stylesheet(self):
        """Настройка стилей и заднего фона меню"""
        if os.path.exists(self.pet.menu_bg_path):
            bg_path_qss = self.pet.menu_bg_path.replace("\\", "/")
            self.setStyleSheet(f"""
                QMenu {{
                    border-image: url("{bg_path_qss}") 0 0 0 0 stretch stretch;
                    border: 1px solid #5c1d1d;
                    padding: 10px;             
                }}
                QMenu::item {{
                    background-color: rgba(255, 255, 255, 0.6); 
                    color: #2b0000;                                                                            
                    padding: 6px 25px 6px 20px;
                    margin: 2px 0px;
                    border-radius: 4px;
                }}
                QMenu::item:selected {{
                    background-color: rgba(230, 0, 0, 0.4);   
                    color: #ffffff;                                                                            
                }}
                QMenu::separator {{
                    height: 1px;
                    background: rgba(92, 29, 29, 0.4);
                    margin: 5px 5px;
                }}
            """)

    def build_menu(self):
        """Сборка структуры контекстного меню"""
        # --- Меню скинов ---
        skins_menu = self.addMenu("🎨 Сменить скин")
        
        # Группа для скинов, чтобы активным визуально был только один
        skin_group = QActionGroup(self)
        
        default_skin_action = QAction("Makima", self)
        default_skin_action.setCheckable(True)
        default_skin_action.setChecked(self.logic.current_skin_name == "Makima")
        default_skin_action.triggered.connect(lambda: self.pet.load_skin("Makima"))
        skins_menu.addAction(default_skin_action)
        skin_group.addAction(default_skin_action)
        
        if os.path.exists(self.logic.skins_dir):
            for folder_name in os.listdir(self.logic.skins_dir):
                if folder_name == "Makima":
                    continue
                if os.path.isdir(os.path.join(self.logic.skins_dir, folder_name)):
                    skin_action = QAction(folder_name, self)
                    skin_action.setCheckable(True)
                    skin_action.setChecked(self.logic.current_skin_name == folder_name)
                    skin_action.triggered.connect(lambda checked, name=folder_name: self.pet.load_skin(name))
                    skins_menu.addAction(skin_action)
                    skin_group.addAction(skin_action)
                    
        self.addSeparator()

        # --- Режимы поведения (с исправленным вызовом и радио-выбором) ---
        behavior_group = QActionGroup(self)
        
        mode_random_action = QAction("Режим: Случайная ходьба", self)
        mode_random_action.setCheckable(True)
        mode_random_action.setChecked(self.logic.behavior_mode == 'random')
        # ИСПРАВЛЕНО: вызываем метод set_behavior_mode, а не переменную
        mode_random_action.triggered.connect(lambda: self.logic.set_behavior_mode('random'))
        self.addAction(mode_random_action)
        behavior_group.addAction(mode_random_action)
        
        mode_follow_action = QAction("Режим: За курсором", self)
        mode_follow_action.setCheckable(True)
        mode_follow_action.setChecked(self.logic.behavior_mode == 'follow')
        # ИСПРАВЛЕНО: вызываем метод set_behavior_mode
        mode_follow_action.triggered.connect(lambda: self.logic.set_behavior_mode('follow'))
        self.addAction(mode_follow_action)
        behavior_group.addAction(mode_follow_action)
        
        self.addSeparator()
        
        # --- Таймер ---
        timer_menu = self.addMenu("⏱️ Таймер")
        
        t_5m = QAction("5 минут", self)
        t_5m.triggered.connect(lambda: self.pet.start_timer(5))
        timer_menu.addAction(t_5m)
        
        t_15m = QAction("15 минут", self)
        t_15m.triggered.connect(lambda: self.pet.start_timer(15))
        timer_menu.addAction(t_15m)
        
        t_custom = QAction("Задать свое время...", self)
        t_custom.triggered.connect(self.pet.start_custom_timer)
        timer_menu.addAction(t_custom)
        
        if self.logic.timer_seconds_left > 0:
            timer_menu.addSeparator()
            t_stop = QAction("❌ Остановить таймер", self)
            t_stop.triggered.connect(self.pet.stop_timer)
            timer_menu.addAction(t_stop)

        self.addSeparator()
        
        # --- Спавн питомцев ---
        dog_action = QAction("🐕 Вызвать собаку", self)
        dog_action.triggered.connect(self.pet.spawn_dog)
        self.addAction(dog_action)
        
        self.addSeparator()

        # --- Переключатели состояния интерфейса ---
        time_action = QAction("💬 Показывать время/таймер", self)
        time_action.setCheckable(True)
        time_action.setChecked(self.logic.show_time)
        time_action.triggered.connect(self.pet.toggle_time_bubble)
        self.addAction(time_action)

        demon_action = QAction("😈 Демонический режим", self)
        demon_action.setCheckable(True)
        demon_action.setChecked(self.logic.demon_mode)
        demon_action.triggered.connect(self.pet.toggle_demon_mode)
        self.addAction(demon_action)

        self.addSeparator()

        # --- Системные действия ---
        autostart_action = QAction("Автозапуск с Windows", self)
        autostart_action.setCheckable(True)
        autostart_action.setChecked(self.logic.is_autostart_enabled())
        autostart_action.triggered.connect(self.logic.toggle_autostart)
        self.addAction(autostart_action)

        self.addSeparator()
        
        quit_action = QAction("Закрыть питомца", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        self.addAction(quit_action)