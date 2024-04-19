import os
import sys
import shutil
import random
from queue import Queue
from PyQt5.QtCore import Qt, QTimer, QDateTime, QPoint, QRect, QPropertyAnimation, QEasingCurve, QFileSystemWatcher, QDir,QStandardPaths, QUrl, QThread, pyqtSignal, QCoreApplication, QTime
from PyQt5.QtGui import QMovie, QIcon, QPixmap, QFont, QPainter, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, QAction, QLabel, QVBoxLayout, QDesktopWidget, QDialog, QTimeEdit, QPushButton, QMessageBox, QSpinBox, QActionGroup, QMainWindow, QFileDialog, QMessageBox, QCheckBox, QFrame, QGridLayout, QHBoxLayout, QSlider, QListWidget, QStackedWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist

class ConfigWindow(QMainWindow):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setWindowTitle("Configuration window")
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon('resources\\icon\\app.ico'))
        # Для хранения разницы между положением мыши и положением окна
        self.drag_pos = QPoint()

        # Создаем основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Создаем сеточный макет
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        # Загружаем изображения из файла config.txt
        images_info = self.load_images_from_config("config.txt")

        # Добавляем четыре изображения с подписями
        for i, (label_text, image_path) in enumerate(images_info.items()):
            self.add_image_with_label(image_path, label_text, i // 2, i % 2)

        # Добавляем кнопки Save и Cancel
        self.add_buttons()

        self.setStyleSheet(f"""
            QFrame{{
                border: solid; 
            }}                   
            ConfigWindow{{           
                background-color: #474747;
            }}   
            QLabel{{     
                color: white;               
                font-size: 15px;
                font: Garamond;
                font-weight: bold;  
            }}  
            QPushButton {{
                color: white;           
                font-size: 15px;
                font: Garamond;
                font-weight: bold;       
                border: solid; 
                border-radius: 10px;
                padding: 5px 10px; /* Adjust padding to control button width */
                min-width: 50px; /* Set minimum width for the button */
                background-color: rgba(236, 151, 156, 150); /* Set button background color */
            }}
            QPushButton:hover {{
                background-color: rgba(255, 0, 0, 150); /* Change button background color on hover */
            }}
        """)

    def load_images_from_config(self, config_file):
        images_info = {}
        try:
            with open(config_file, 'r') as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line.startswith("#background audio player"):
                        images_info["background audio player"] = lines[i + 1].strip()
                    if line.startswith("#background night audio player"):
                        images_info["background night audio player"] = lines[i + 1].strip()
                    elif line.startswith("#background popup/tray menu"):
                        images_info["background popup/tray menu"] = lines[i + 1].strip()
                    elif line.startswith("#background timer"):
                        images_info["background timer"] = lines[i + 1].strip()
                    elif line.startswith("#background alarm"):
                        images_info["background alarm"] = lines[i + 1].strip()
        except FileNotFoundError:
            print("Config file not found.")
        return images_info

    def add_image_with_label(self, image_path, label_text, row, col):
        # Создаем фрейм для изображения
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setLineWidth(2)
        frame.setFixedSize(250, 250)  # Устанавливаем фиксированный размер фрейма

        # Создаем метку для подписи
        label = QLabel(label_text)

        # Создаем метку и загружаем изображение
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(frame.size(), aspectRatioMode=True)
        image_label.setPixmap(pixmap)

        # Устанавливаем выравнивание по центру в метке
        image_label.setAlignment(Qt.AlignCenter)

        # Создаем вертикальный макет для фрейма и метки с изображением
        layout = QVBoxLayout()
        frame.setLayout(layout)
        layout.addWidget(image_label)
        layout.addWidget(label, alignment=Qt.AlignCenter)

        # Добавляем фрейм в основной макет
        self.layout.addWidget(frame, row, col)       

        # Подключаем событие клика по изображению
        frame.mousePressEvent = lambda event, label=label_text, image_label=image_label: self.image_clicked(event, label, image_label)


    def add_buttons(self):
        # Создаем кнопку Save
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_clicked)

        # Reset Config
        reset_button = QPushButton("Reset Config")
        reset_button.clicked.connect(self.reset_config_clicked)

        # Создаем кнопку Cancel
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_clicked)

        # Создаем горизонтальный макет для кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(reset_button)
        buttons_layout.addWidget(cancel_button)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем виджет и добавляем в него горизонтальный макет с кнопками
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        # Добавляем виджет с кнопками в основной макет
        self.layout.addWidget(buttons_widget, 2, 0, 1, 2, Qt.AlignBottom | Qt.AlignRight)

    def show_reply_message(self):
        msg = DraggableMessageBox()  # используем наше кастомное QMessageBox
        msg.setIcon(QMessageBox.Information)
        msg.setText("Are you sure you want to reset the configuration file?")

        # Добавляем кнопки
        ok_button = msg.addButton(QPushButton("Yes"), QMessageBox.AcceptRole)
        no_button = msg.addButton(QPushButton("No"), QMessageBox.RejectRole)

        # Применяем стили
        msg.setStyleSheet("""
            QMessageBox {
                background-color: rgba(236, 151, 156, 150);
                border: 2px solid white;
                border-radius: 10px;
            }
            QLabel {
                font-family: Garamond;
                color: white;
                font-weight: bold;
            }
            QPushButton {
                background-color: rgba(236, 151, 156, 150);
                font-family: Garamond;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px;
                min-width: 70px; 
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 150);
            }                         
        """)

        reply = msg.exec_()
    
        # Обрабатываем ответ
        if reply == QMessageBox.Accepted:
            pass
        else:
            try:
                with open("config.txt", "w") as f:
                    f.write("""#time alarm
00:00:00
#repeat alarm count
3
#play alarm
0
#media alarm path
resources\sound\i_can't_believe_youre_clowning_around_at_a_time_like_this_Makima.mp3
#background alarm
resources/background/background_alarm.jpg
#background timer
resources/background/Makima_timer.jpg
#background popup/tray menu
resources/background/MakimaBackground.png
#background audio player
resources/background/background_audio.jpg
#background night audio player
resources/background/Calm.jpg""")
            except FileNotFoundError:
                pass    
            

    def reset_config_clicked(self):
        # Вызываем функцию для показа сообщения
        user_response = self.show_reply_message()

    def save_clicked(self):
        self.hide()
        self.parent_window.show_options_action.setChecked(False)
        self.parent_window.show_options_tray_action.setChecked(False)  

    def cancel_clicked(self):
        self.hide()
        self.parent_window.show_options_action.setChecked(False)
        self.parent_window.show_options_tray_action.setChecked(False)  

    def image_clicked(self, event, label_text, image_label):
        # Отображаем надпись в консоли при клике на фрейм
        print(f"Frame clicked: {label_text}")

        # Открываем диалоговое окно для выбора файла
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file in selected_files:
                # Выводим название файла в консоль (только название и формат)
                file_name = os.path.basename(file)
                print(f"Selected file: {file_name}")

                # Формируем путь для сохранения файла в папке resources/background
                destination_path = os.path.join("resources", "background", file_name)

                # Копируем выбранный файл в папку resources/background
                shutil.copy2(file, destination_path)

                # Выводим полный путь к скопированному файлу в консоль
                print(f"Saved as: {destination_path}")

                # Обновляем изображение в QLabel
                pixmap = QPixmap(destination_path)
                pixmap = pixmap.scaled(image_label.size(), aspectRatioMode=True)
                image_label.setPixmap(pixmap)

                # Ищем соответствующую строку в файле config.txt и заменяем ее на новый путь
                try:
                    with open("config.txt", 'r') as config_file:
                        lines = config_file.readlines()
                    with open("config.txt", 'w') as config_file:
                        replace_next_line = False
                        for line in lines:
                            if replace_next_line:  
                                config_file.write(f"{destination_path.replace(os.sep, '/')}\n")
                                replace_next_line = False
                            elif line.strip().startswith("#" + label_text):
                                replace_next_line = True
                                config_file.write(line)
                            else:
                                config_file.write(line)
                except FileNotFoundError:
                    print("Config file not found.")

       
    def mousePressEvent(self, event):
        # Запоминаем текущее положение мыши при нажатии
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        # Перемещаем окно при перемещении мыши с нажатой левой кнопкой
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
        event.accept()

class DraggableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.offset = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() & Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = None

class AudioPlayer(DraggableWindow):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setWindowTitle("Audio Player")
        self.media_player = QMediaPlayer()
        self.media_player.stateChanged.connect(self.state_changed)
        self.playlist = QMediaPlaylist()
        self.media_player.setPlaylist(self.playlist)
        self.current_index = 0
        self.is_slider_pressed = False  # Флаг для определения нажатия на слайдер
        self.state = False
        self.init_ui()
        self.playlist.currentIndexChanged.connect(self.update_image)
        self.is_playing = False
        
    def init_ui(self):
        self.setWindowIcon(QIcon('resources\\icon\\app.ico'))
        self.setStyleSheet(f"""               
            
            QSlider::groove:horizontal {{
                border: none;
                background: transparent;
                height: 4px;  /* Уменьшаем высоту слайдера */
                border-radius: 2px; /* Уменьшаем радиус границы */
            }}

            QSlider::handle:horizontal {{
                background: #ffa500;
                border: 1px solid #5c5c5c;
                width: 14px; /* Уменьшаем ширину ручки */
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 7px; /* Уменьшаем радиус границы */
            }}

            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF0000, stop:0.5 #ffa500, stop:1 #00FF00 );
                border: none;
                height: 4px; /* Уменьшаем высоту слайдера */
                border-radius: 5px; /* Уменьшаем радиус границы */
            }}

            QSlider::add-page:horizontal {{
                background: #000000;
                border: none;
                height: 6px; /* Уменьшаем высоту слайдера */
                border-radius: 2px; /* Уменьшаем радиус границы */
            }}                                   
              
            QLabel{{
                border: none; /* Устанавливаем границу для QLabel как 'none' */
                font: Garamond;
                color: white;           
                font-size: 15px;           
            }}  
            QPushButton {{
                color: white;           
                font-size: 15px;
                font: Garamond;
                font-weight: bold;       
                border: solid; 
                border-radius: 10px;
                padding: 5px 10px; /* Adjust padding to control button width */
            }}
            QPushButton:hover {{
                background-color: rgba(255, 0, 0, 150); /* Change button background color on hover */
            }}     
            AudioPlayer{{           
                background-color: #474747;
                font: Garamond;
                color: white;           
                font-size: 15px;                    
            }}""")
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint)
        layout = QVBoxLayout()

        # Stacked widget to hold multiple pages
        self.stacked_widget = QStackedWidget()

        # Page 1: Audio Player Controls
        self.page1 = QWidget()
        layout_page1 = QVBoxLayout()
        self.list_widget = QListWidget()
        layout_page1.addWidget(self.list_widget)

        self.load_files()

        # Установка указателя на первый элемент списка
        self.list_widget.setCurrentRow(0)

        # Scrubber slider
        scrubber_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        scrubber_layout.addWidget(self.current_time_label)

        self.scrubber_slider = QSlider()
        self.scrubber_slider.setOrientation(Qt.Horizontal)
        self.scrubber_slider.sliderMoved.connect(self.set_position)
        self.scrubber_slider.sliderPressed.connect(self.slider_pressed)  # Обработчик нажатия на слайдер
        self.scrubber_slider.sliderReleased.connect(self.slider_released)  # Обработчик отпускания слайдера
        scrubber_layout.addWidget(self.scrubber_slider)

        self.total_time_label = QLabel("00:00")
        scrubber_layout.addWidget(self.total_time_label)

        layout_page1.addLayout(scrubber_layout)

        # Volume slider
        self.volume_slider = QSlider()
        self.volume_slider.setOrientation(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)  # Default volume
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.minimize_button = QPushButton("Minimize")
        self.minimize_button.clicked.connect(self.hide_window)


        # Page 2: Placeholder Page
        self.page2 = QWidget()
        layout_page2 = QVBoxLayout()
        layout_page2_buttons = QHBoxLayout()        
        # Создаем фрейм для изображения
        image_frame = QFrame()
        image_frame.setFrameShape(QFrame.Box)  # Устанавливаем форму рамки
        image_frame.setLineWidth(2)  # Устанавливаем толщину линии рамки

        # Добавляем QLabel для отображения изображения во внутреннюю часть фрейма
        self.image_label = QLabel()
        image_path = self.get_background_image_path()  # Укажите путь к вашему изображению
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(500, 400, Qt.KeepAspectRatio)  # Устанавливаем размер изображения
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.image_label)
        image_frame.setLayout(image_layout)

        layout_page2.addWidget(self.image_label)
        
        # Добавляем scrubber_slider на вторую страницу
        scrubber_layout_page2 = QHBoxLayout()
        self.current_time_label_page2 = QLabel("00:00")
        scrubber_layout_page2.addWidget(self.current_time_label_page2)

        self.scrubber_slider_page2 = QSlider()
        self.scrubber_slider_page2.setOrientation(Qt.Horizontal)
        self.scrubber_slider_page2.sliderMoved.connect(self.set_position)
        self.scrubber_slider_page2.sliderPressed.connect(self.slider_pressed)  # Обработчик нажатия на слайдер
        self.scrubber_slider_page2.sliderReleased.connect(self.slider_released)  # Обработчик отпускания слайдера
        scrubber_layout_page2.addWidget(self.scrubber_slider_page2)

        self.total_time_label_page2 = QLabel("00:00")
        scrubber_layout_page2.addWidget(self.total_time_label_page2)
        
        layout_page2.addLayout(scrubber_layout_page2)

        # Добавляем volume_slider на вторую страницу
        self.volume_slider_page2 = QSlider()
        self.volume_slider_page2.setOrientation(Qt.Horizontal)
        self.volume_slider_page2.setMinimum(0)
        self.volume_slider_page2.setMaximum(100)
        self.volume_slider_page2.setValue(50)  # Default volume
        self.volume_slider_page2.valueChanged.connect(self.set_volume)
        
        volume_and_switch_page2_layout = QHBoxLayout()
        
        self.minimize_button_page2 = QPushButton()
        self.minimize_button_page2.clicked.connect(self.hide_window)
        volume_and_switch_page2_layout.addWidget(self.minimize_button_page2)
        self.minimize_button_page2.setStyleSheet("QPushButton { border-image: url(resources/icon/close-window.png); }")
        self.minimize_button_page2.setFixedSize(40, 40)
        volume_and_switch_page2_layout.addWidget(self.volume_slider_page2)
        
        # Добавление кнопки для перехода на первую страницу
        self.switch_page_button_page2 = QPushButton()
        self.switch_page_button_page2.setStyleSheet("QPushButton { border-image: url(resources/icon/playlist.png); }")
        self.switch_page_button_page2.clicked.connect(self.switch_page)
        self.switch_page_button_page2.setFixedSize(40, 40)
        volume_and_switch_page2_layout.addWidget(self.switch_page_button_page2)
        
        layout_page2.addLayout(volume_and_switch_page2_layout)

        # Добавление кнопки "Add" на вторую страницу
        self.add_button_page2 = QPushButton()
        self.add_button_page2.setStyleSheet("QPushButton { border-image: url(resources/icon/download.png); }")
        self.add_button_page2.clicked.connect(self.add_files)
        self.add_button_page2.setFixedSize(40, 40)
        layout_page2_buttons.addWidget(self.add_button_page2)

        # Добавление кнопки "Previous" на вторую страницу
        self.previous_button_page2 = QPushButton()
        self.previous_button_page2.setStyleSheet("QPushButton { border-image: url(resources/icon/rewind-button.png); }")
        self.previous_button_page2.clicked.connect(self.previous_clicked)
        self.previous_button_page2.setFixedSize(40, 40)
        layout_page2_buttons.addWidget(self.previous_button_page2)

        # Добавление кнопки "Play" на вторую страницу
        self.play_button_page2 = QPushButton()
        self.play_button_page2.setStyleSheet("QPushButton { border-image: url(resources/icon/play.png); }")
        self.play_button_page2.clicked.connect(self.play_clicked)
        self.play_button_page2.setFixedSize(40, 40)
        layout_page2_buttons.addWidget(self.play_button_page2)

        # Добавление кнопки "Next" на вторую страницу
        self.next_button_page2 = QPushButton()
        self.next_button_page2.setStyleSheet("QPushButton { border-image: url(resources/icon/next-button.png); }")
        self.next_button_page2.clicked.connect(self.next_clicked)
        self.next_button_page2.setFixedSize(40, 40)
        layout_page2_buttons.addWidget(self.next_button_page2)

        # Добавление кнопки "Repeat" на вторую страницу
        self.repeat_button_page2 = QPushButton()
        self.repeat_button_page2.setStyleSheet("QPushButton { border-image: url(resources/icon/repeat.png); }")
        self.repeat_button_page2.clicked.connect(lambda: self.set_repeat_state(self.state))
        self.repeat_button_page2.setFixedSize(40, 40)
        layout_page2_buttons.addWidget(self.repeat_button_page2)

        # Добавляем горизонтальный контейнер с кнопками на вторую страницу
        layout_page2.addLayout(layout_page2_buttons)

        self.page2.setLayout(layout_page2)
        self.stacked_widget.addWidget(self.page2)
        layout.addWidget(self.stacked_widget)

        # Buttons for controlling playback
        button_layout = QHBoxLayout()

        # Добавляем кнопку "Add"
        self.add_button = QPushButton()
        self.add_button.setStyleSheet("QPushButton { border-image: url(resources/icon/download.png); }")
        self.add_button.clicked.connect(self.add_files)
        self.add_button.setFixedSize(40, 40) 
        button_layout.addWidget(self.add_button)

        # Добавляем кнопку "Previous"
        self.previous_button = QPushButton()
        self.previous_button.setStyleSheet("QPushButton { border-image: url(resources/icon/rewind-button.png); }")
        self.previous_button.clicked.connect(self.previous_clicked)
        self.previous_button.setFixedSize(40, 40)
        button_layout.addWidget(self.previous_button)

        # Остальные кнопки "Play" и "Next"
        self.play_button = QPushButton()
        self.play_button.setStyleSheet("QPushButton { border-image: url(resources/icon/play.png); }")
        self.play_button.clicked.connect(self.play_clicked)
        self.play_button.setFixedSize(40, 40) 
        button_layout.addWidget(self.play_button)

        self.next_button = QPushButton()
        self.next_button.setStyleSheet("QPushButton { border-image: url(resources/icon/next-button.png); }")        
        self.next_button.clicked.connect(self.next_clicked)
        self.next_button.setFixedSize(40, 40) 
        button_layout.addWidget(self.next_button)
        
        self.repeat_button = QPushButton()
        self.repeat_button.setStyleSheet("QPushButton { border-image: url(resources/icon/repeat.png); }")
        self.repeat_button.clicked.connect(lambda: self.set_repeat_state(self.state))
        self.repeat_button.setFixedSize(40, 40) 
        button_layout.addWidget(self.repeat_button)

        volume_and_switch_layout = QHBoxLayout()
        
        self.minimize_button = QPushButton()
        self.minimize_button.clicked.connect(self.hide_window)
        volume_and_switch_layout.addWidget(self.minimize_button)
        self.minimize_button.setStyleSheet("QPushButton { border-image: url(resources/icon/close-window.png); }")
        self.minimize_button.setFixedSize(40, 40)
        volume_and_switch_layout.addWidget(self.volume_slider)

        # Add a button to switch between pages
        self.switch_page_button = QPushButton()
        self.switch_page_button.setStyleSheet("QPushButton { border-image: url(resources/icon/playlist.png); }")
        self.switch_page_button.clicked.connect(self.switch_page)
        self.switch_page_button.setFixedSize(40, 40)
        volume_and_switch_layout.addWidget(self.switch_page_button)

        layout_page1.addLayout(volume_and_switch_layout)

        self.page1.setLayout(layout_page1)
        self.stacked_widget.addWidget(self.page1)
    
        # Добавляем горизонтальный контейнер с кнопками в вертикальный layout_page1
        layout_page1.addLayout(button_layout)


        self.setLayout(layout)

        # Timer for updating scrubber position
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scrubber)
        self.timer.start(1000)  # Update every second

        # Обработчик сигнала изменения статуса медиафайла
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)
        
        self.stacked_widget.setCurrentIndex(0)

    def get_background_image_path(config_file):
        config_file_path = "config.txt"
        background_image_path = None
        with open(config_file_path, 'r') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if line.strip() == '#background audio player':
                    # Ищем следующую строку после заголовка
                    if i + 1 < len(lines):
                        background_image_path = lines[i + 1].strip()
                        break  # Нашли путь, выходим из цикла
        return background_image_path
        
    def hide_window(self):
        self.hide()
        self.parent_window.show_audio_player_action.setChecked(False)
        self.parent_window.show_audio_player_tray_action.setChecked(False)           
        
    def set_repeat_state(self, state):
        if self.state == True:
            self.state = False
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)
            # Устанавливаем стиль кнопок при self.state == True
            self.repeat_button.setStyleSheet("QPushButton { border-image: url(resources/icon/repeat.png); }")
            self.repeat_button_page2.setStyleSheet("QPushButton { border-image: url(resources/icon/repeat.png); }")
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
            self.state = True
            # Устанавливаем стиль кнопок при self.state == False
            self.repeat_button.setStyleSheet("QPushButton { background-color: rgba(255, 0, 0, 150); border-image: url(resources/icon/repeat.png); }")  # Очищаем стиль, чтобы вернуть его к изначальному
            self.repeat_button_page2.setStyleSheet("QPushButton { background-color: rgba(255, 0, 0, 150); border-image: url(resources/icon/repeat.png); }")  # Очищаем стиль, чтобы вернуть его к изначальному
        
    def add_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Audio Files (*.mp3 *.wav)")
        if file_dialog.exec_():
            file_names = file_dialog.selectedFiles()
            for file_name in file_names:
                # Определяем целевой путь для копирования файла
                target_path = os.path.join(os.getcwd(), "resources", "music", os.path.basename(file_name))
                # Копируем файл в целевую папку
                try:
                    shutil.copy(file_name, target_path)
                except Exception as e:
                    print("Error copying file:", e)
                    continue
                # Добавляем скопированный файл в плейлист и список
                media = QMediaContent(QUrl.fromLocalFile(target_path))
                self.playlist.addMedia(media)
                self.list_widget.addItem(os.path.basename(target_path))

    def slider_pressed(self):
        self.is_slider_pressed = True
        # При нажатии на слайдер останавливаем воспроизведение
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        
    def slider_released(self):
        # Устанавливаем флаг нажатия на слайдер в False
        self.is_slider_pressed = False

        # При отпускании слайдера возобновляем воспроизведение, если ранее было воспроизведение
        if self.media_player.state() == QMediaPlayer.PausedState:
            self.media_player.play()

    def media_status_changed(self, status):
        if self.repeat_button.isChecked():
            pass
        if self.repeat_button_page2.isChecked():
            pass
        else:
            if status == QMediaPlayer.EndOfMedia:
                # Если достигнут конец медиафайла, переместить указатель списка
                if self.current_index < self.playlist.mediaCount() - 1:
                    self.list_widget.setCurrentRow(self.current_index + 1)

    def switch_page(self):
        # Switch between pages
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0:
            self.stacked_widget.setCurrentIndex(1)
        else:
            self.stacked_widget.setCurrentIndex(0)

    def set_volume(self, value):
        self.volume_slider.setValue(value)
        self.volume_slider_page2.setValue(value)
        self.media_player.setVolume(value)

    def load_files(self):
        music_folder = os.path.join(os.getcwd(), "resources", "music")
        if not os.path.exists(music_folder):
            print("Music folder does not exist!")
            return

        files = os.listdir(music_folder)
        for file in files:
            if file.endswith(".mp3") or file.endswith(".wav"):
                file_name = os.path.splitext(file)[0]  # Получить только имя файла без расширения
                media = QMediaContent(QUrl.fromLocalFile(os.path.join(music_folder, file)))
                self.playlist.addMedia(media)
                self.list_widget.addItem(file_name)
        self.list_widget.setStyleSheet("""
            QListWidget::item {
                font: Garamond;
                background-color: #474747;
                color: white;
                font-weight: bold;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 0, 0, 150); /* Change background color on hover */
            }
            QListWidget::item:selected {
                background-color: rgba(236, 151, 156, 150); /* Change background color when selected */
            }
            QListWidget {
                selection-color: white; /* Text color of selected item */
                selection-background-color: rgba(0, 0, 255, 150); /* Background color of selected item */
                background-color: #474747;    
                font: Garamond;
                font-weight: bold;                
                font-size: 15px;
            }
        """)
        if self.playlist.mediaCount() > 0:
            self.playlist.setCurrentIndex(0)
            self.list_widget.setCurrentRow(0)  # Set list widget pointer to the first item

        self.list_widget.itemClicked.connect(self.list_item_clicked)

    def play_clicked(self):
        if not self.playlist.mediaCount():
            print("No files in the playlist!")
            return

        # Сохраняем текущий индекс перед вызовом play_clicked()
        current_index = self.current_index
        # Если музыка не воспроизводится, начинаем воспроизведение и меняем иконку кнопки
        if not self.is_playing:
            # Устанавливаем текущую позицию плейлиста перед воспроизведением
            self.playlist.setCurrentIndex(current_index)
            self.media_player.play()
            self.play_button.setStyleSheet("QPushButton { border-image: url(resources/icon/pause-button.png); }")
            self.play_button_page2.setStyleSheet("QPushButton { border-image: url(resources/icon/pause-button.png); }")
            self.is_playing = True
        # Если музыка воспроизводится, останавливаем воспроизведение и меняем иконку кнопки
        else:
            self.media_player.stop()
            self.play_button.setStyleSheet("QPushButton { border-image: url(resources/icon/play.png); }")
            self.play_button_page2.setStyleSheet("QPushButton { border-image: url(resources/icon/play.png); }")
            self.is_playing = False

        # Восстанавливаем текущий индекс после play_clicked()
        self.update_current_index_and_row(current_index)

    def list_item_clicked(self, item):
        index = self.list_widget.currentRow()
        if index != self.current_index:
            self.update_current_index_and_row(index)
            self.playlist.setCurrentIndex(index)
            self.update_image(index)

    def next_clicked(self):
        if self.playlist.mediaCount() > 0:
            next_index = (self.current_index + 1) % self.playlist.mediaCount()
            self.update_current_index_and_row(next_index)
            self.playlist.setCurrentIndex(next_index)

    def previous_clicked(self):
        if self.playlist.mediaCount() > 0:
            prev_index = (self.current_index - 1) % self.playlist.mediaCount()
            self.update_current_index_and_row(prev_index)
            self.playlist.setCurrentIndex(prev_index)

    def state_changed(self, state):  
        if state == QMediaPlayer.StoppedState:
            if self.current_index < self.playlist.mediaCount() - 1:
                self.next_clicked()
            else:
                self.update_current_index_and_row(0)
                self.playlist.setCurrentIndex(0)
        elif state == QMediaPlayer.PausedState:
            if not self.is_slider_pressed:
                self.media_player.play()

    def update_current_index_and_row(self, index):
        self.current_index = index
        self.list_widget.setCurrentRow(index)

    def update_scrubber(self):
        if not self.is_slider_pressed:
            # Обновление только при не нажатии на слайдер
            if self.media_player.duration() > 0:
                position = self.media_player.position()
                duration = self.media_player.duration()
                self.scrubber_slider.setMaximum(duration)
                self.scrubber_slider.setValue(position)
                self.scrubber_slider_page2.setMaximum(duration)  # Установка максимального значения на странице 2
                self.scrubber_slider_page2.setValue(position)  # Установка значения на странице 2

                current_time = self.format_time(position)
                total_time = self.format_time(duration)
                self.current_time_label.setText(current_time)
                self.total_time_label.setText(total_time)
                self.current_time_label_page2.setText(current_time)  # Установка текущего времени на странице 2
                self.total_time_label_page2.setText(total_time)  # Установка общего времени на странице 2

    def set_position(self, position):
        self.media_player.setPosition(position)

    def format_time(self, milliseconds):
        seconds = milliseconds // 1000
        minutes, seconds = divmod(seconds, 60)
        return "{:02}:{:02}".format(minutes, seconds)
    
    def update_image(self, index):
        # Определите путь к файлу конфигурации
        config_file_path = "config.txt"  # Путь к файлу конфигурации

        # Определите заголовки для поиска в файле конфигурации
        header1 = "#background audio player"
        header2 = "#background night audio player"

        # Переменная для хранения пути к изображению
        image_path = ""

        # Чтение файла конфигурации
        with open(config_file_path, "r") as file:
            lines = file.readlines()
            for i in range(len(lines)):
                if lines[i].strip() == header1 and index < self.playlist.mediaCount() / 2:
                    image_path = lines[i+1].strip()
                    break
                elif lines[i].strip() == header2 and index >= self.playlist.mediaCount() / 2:
                    image_path = lines[i+1].strip()
                    break

        # Проверяем, что путь к изображению был найден
        if image_path:
            # Создаем абсолютный путь к файлу изображения
            image_path = os.path.join(os.getcwd(), image_path)

            # Обновляем изображение
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setAlignment(Qt.AlignCenter)

class Ziegfied(QMainWindow):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.media_player = QMediaPlayer(self)
        self.media_content = QMediaContent(QUrl.fromLocalFile("resources/sound/bark.mp3"))        

        self.sound_queue = Queue()
        self.sound_queue.put("resources/sound/bark.mp3")
        self.sound_queue.put("resources/sound/Good_boy_Makima.wav")
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 95, 104)
        self.label.setAlignment(Qt.AlignCenter)
        self.movie = None  
        
        # Remove system menu and window frame
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Make the window transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 900, 95, 104)
        
     
        self.cursor_timer = self.startTimer(50)        

        self.is_left_button_held_long = False
        self.left_button_hold_timer = QTimer(self)
        self.left_button_hold_timer.timeout.connect(self.handle_left_button_hold_timeout)

        self.central_widget = QLabel(self)
        self.central_widget.setGeometry(0, 0, 95, 104)
        self.central_widget.setAlignment(Qt.AlignCenter)

        self.standing_gifs = ['resources/gif/dogs_stay_unscreen.gif', 'resources/gif/dogs_sit_unscreen.gif', 'resources/gif/dogs_sitdown_unscreen.gif']

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_behaviour)
        self.timer.start(2000)  # Update behaviour every 3 seconds

        self.current_state = "Standing"
        self.old_pos = self.pos()

        self.dx = 0
        self.speed = 5
        self.steps_remaining = 0  # Number of steps remaining in the current direction

        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.move_window)

        # Get desktop size
        self.desktop_rect = QDesktopWidget().screenGeometry()
        self.desktop_width = self.desktop_rect.width()

        # Flags to control window behavior
        self.should_attract_to_taskbar = True
        self.is_dragging = False
        self.is_shift_pressed = False

        # Additional setup for attraction
        self.desktop_rect = QApplication.desktop().availableGeometry()
        self.attraction_strength = 0.1  # You may adjust this value as needed
        self.animation = QPropertyAnimation(self, b'pos')
        self.desktop_watcher = QFileSystemWatcher()
        desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        self.desktop_watcher.addPath(desktop_path)

        # Connect signals
        self.desktop_watcher.fileChanged.connect(self.attract_to_taskbar)

        # Timer to periodically check and update the window position
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.attract_to_taskbar)
        self.timer.start(100)  # Adjust the interval as needed (milliseconds)

        # Create a menu for choosing move mode
        self.move_mode_menu = QMenu(self)
        def get_background_image_path_from_config():
            config_file = "config.txt"
            background_image_path = None

            with open(config_file, 'r') as f:
                lines = f.readlines()
                found_header = False

                for line in lines:
                    if line.strip() == "#background popup/tray menu":
                        found_header = True
                    elif found_header:
                        # Assuming the path is specified after the header on the same line
                        background_image_path = line.strip()
                        break

            return background_image_path

        # Get the background image path from config.txt
        background_image_path = get_background_image_path_from_config()

        # Create a menu for choosing move mode
        self.move_mode_menu = QMenu(self)
        self.move_mode_menu.setStyleSheet(        
            f"""
            QMenu {{
                background-image: url('{background_image_path}');
                background-repeat: no-repeat; 
                background-position: center; 
                border: 1px solid #707070; 
                font-family: Garamond; 
                font-weight: bold;
            }}
            QMenu::item {{
                padding: 5px 20px; 
                color: white; 
            }}
            QMenu::item:selected {{
                background-color: rgba(236, 151, 156, 150);
            }}
            """
        )
        self.move_mode_menu.clear()  # Clear existing actions if any
        self.move_mode_menu.addAction("Ziegfried")  # Add the label "Ziegfried"
        self.move_mode_menu.addSeparator()  # Add a separator        
        self.random_move_action = QAction("Random", self)
        self.cursor_move_action = QAction("Cursor", self)
        self.hide_window_action = QAction("Hide", self)
        self.random_move_action.setCheckable(True)  # Make actions checkable
        self.random_move_action.setChecked(True)  # Set the default action to checked
        self.cursor_move_action.setCheckable(True)
        self.move_mode_menu.addAction(self.random_move_action)
        self.move_mode_menu.addAction(self.cursor_move_action)
        self.move_mode_menu.addSeparator()
        self.move_mode_menu.addAction(self.hide_window_action)
        self.random_move_action.triggered.connect(self.set_random_move_mode)
        self.cursor_move_action.triggered.connect(self.set_cursor_move_mode)
        self.hide_window_action.triggered.connect(self.hide_window)

        self.should_random_move = True  # Default to random movement
        
    def hide_window(self):
        self.parent_window.toggle_show_ziegfied_action_popup.setText("Show Ziegfried")
        self.parent_window.toggle_show_ziegfied_action_tray.setText("Show Ziegfried")
        self.parent_window.toggle_show_ziegfied_action_tray.setChecked(False)
        self.parent_window.toggle_show_ziegfied_action_popup.setChecked(False) 
        self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Start a timer to track long press
            self.left_button_hold_timer.start(500)  # 5 seconds
            self.is_left_button_held_long = False

            self.is_dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.is_dragging:
            return
        if self.is_dragging:
            self.move(event.globalPos() - self.offset)
        if not self.should_random_move:
            self.move_to_cursor()  # Move window to cursor position
        else:
            super().mouseMoveEvent(event)  

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
        
         
            if not self.is_left_button_held_long:
                self.media_player.setMedia(self.media_content)
                self.media_player.play()

            self.left_button_hold_timer.stop()

            # Check if window left the taskbar and update state accordingly
            if self.is_touching_taskbar and not self.should_attract_to_taskbar:
                self.current_state = "Standing"
                self.start_standing()

            self.is_touching_taskbar = False
            
    def handle_left_button_hold_timeout(self):
        # Timeout for long press of the left mouse button
        self.is_left_button_held_long = True
        # Stop the timer
        self.left_button_hold_timer.stop()

    def attract_to_taskbar(self):
        # Skip attraction if the left mouse button is being dragged or Shift key is pressed
        if not self.should_attract_to_taskbar or self.is_dragging or self.is_shift_pressed:
            return
        
        # Calculate distance to the taskbar
        distance_to_taskbar = self.desktop_rect.bottom() - self.height() - self.y() + 48

        # Check if in the specified zone (approximately 50 pixels in height from attract_to_taskbar)
        in_zone = distance_to_taskbar < 50

        # If not already touching taskbar and in zone, set touching taskbar flag and stop attraction
        if in_zone and not self.is_touching_taskbar:
            self.is_touching_taskbar = True
            self.animation.stop()
            return

        # If not in zone anymore, unset touching taskbar flag
        if not in_zone:
            self.is_touching_taskbar = False

        # If touching taskbar, skip attraction
        if self.is_touching_taskbar:
            return

        # Adjust the window's position based on the attraction strength
        new_y = self.y() + self.attraction_strength * distance_to_taskbar

        # Ensure the window stays within the desktop bounds
        new_y = max(self.desktop_rect.top(), min(new_y, self.desktop_rect.bottom() - self.height()))

        # Animate the window's position smoothly
        self.animation.stop()  # Stop any ongoing animations
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(self.x(), int(new_y)))
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.start()

        # If in the specified zone, activate the function to return to the previous state
        if in_zone:
            self.restore_previous_state()

    def restore_previous_state(self):
        # Implement your logic to restore the previous state of the window here
        pass

    def update_behaviour(self):
        if self.should_random_move:
            # Randomly choose between Standing and Walking only if should_attract_to_taskbar is True
            if self.should_attract_to_taskbar:
                # Calculate distance to the taskbar
                distance_to_taskbar = self.desktop_rect.bottom() - self.height() - self.y() + 48

                # Check if in the specified zone (approximately 50 pixels in height from attract_to_taskbar)
                in_zone = distance_to_taskbar < 50

                if in_zone:
                    # If in the zone, proceed with random behavior selection
                    self.current_state = random.choice(["Standing", "Walking"])
                else:
                    # If not in the zone, stick to Standing until in the zone
                    self.current_state = "Standing"
            else:
                # If not attracting to the taskbar, proceed with normal behavior
                self.current_state = random.choice(["Standing", "Walking"])
        else:
            # If cursor movement mode is active, do not change the behavior
            return

        if self.current_state == "Standing":
            self.start_standing()
            self.move_timer.stop()  # Stop window movement
        else:
            self.start_walking()
            self.move_timer.start(50)  # Start window movement

    def start_standing(self):
        # Randomly choose a standing gif
        standing_gif = random.choice(self.standing_gifs)
        self.playAnimation(standing_gif)

    def start_walking(self):
        # If steps remaining, continue in the current direction
        if self.steps_remaining > 0:
            self.move_window()
            return

        # Randomly choose a walking gif and direction
        walking_gif = random.choice(['resources/gif/dogs_walk_left_unscreen.gif', 'resources/gif/dog_run_left_unscreen.gif', 
                                     'resources/gif/dogs_walk_right_unscreen.gif', 'resources/gif/dog_run_right_unscreen.gif'])
        self.playAnimation(walking_gif)

        # Set direction based on chosen gif
        if 'left' in walking_gif:
            self.dx = -1
        else:
            self.dx = 1

        # Set number of steps to move in the current direction
        self.steps_remaining = random.randint(8, 10)

    def set_movie(self, movie_name):
        movie = QMovie(movie_name)
        self.central_widget.setMovie(movie)
        movie.start()
        # Connect the signal for when the movie ends to restart it
        movie.finished.connect(movie.start)

    def move_window(self):
        if QApplication.mouseButtons() == Qt.LeftButton:
            return
        new_x = self.x() + self.dx * self.speed
        if new_x < 0 or new_x + self.width() > self.desktop_width:
            self.dx *= -1
            self.steps_remaining = random.randint(8, 10)
            self.playAnimation('resources/gif/dogs_walk_left_unscreen.gif' if self.dx == -1 else 'resources/gif/dogs_walk_right_unscreen.gif')
            return
        self.move(new_x, self.y())  # Updated to only change x-coordinate
        self.steps_remaining -= 1

        # Call the function to check distance between windows
        self.check_distance_between_windows(nobara_window)

    def resume_movement(self):
        # Resume movement after staying
        self.start_walking()
        self.move_timer.start(50)  # Start window movement

    def check_distance_between_windows(self, nobara_window):
        # Check if both windows are visible
        if self.isVisible() and nobara_window.isVisible():
            # Calculate the distance between this window and the other window
            distance = self.geometry().center().x() - nobara_window.geometry().center().x()
            if random.random() < 0.005:  # Adjust the probability as needed
                self.check_distance_between_windows(nobara_window)
                # If the distance is less than 100 pixels, stop movement and play staying animation
                if abs(distance) < 100:
                    # Stop movement for Ziegfied window
                    self.move_timer.stop()
                    # Stop movement for Nobara window
                    nobara_window.move_timer.stop()
                
                    # Play staying animation for Ziegfied window
                    self.start_standing()
                    # Play staying animation for Nobara window
                    nobara_window.start_standing()

                    # Start playing sounds from the queue
                    self.play_next_sound()

                    # Start a timer to resume movement after 5 seconds
                    QTimer.singleShot(5000, self.resume_movement)
        else:
            # One or both windows are not visible, handle this case if needed
            pass  # You may add your handling logic here

    def play_next_sound(self):
        if not self.sound_queue.empty():
            sound_file = self.sound_queue.get()
            media_content = QMediaContent(QUrl.fromLocalFile(sound_file))
            self.media_player.setMedia(media_content)
            self.media_player.play()

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.play_next_sound()

    def set_random_move_mode(self):
        if self.cursor_move_action.isChecked(): 
            self.cursor_move_action.setChecked(False)
        self.should_random_move = True
        self.move_timer.start(50)

    def set_cursor_move_mode(self):
        if self.random_move_action.isChecked():  
            self.random_move_action.setChecked(False)
        self.should_random_move = False
        self.move_timer.stop()

        cursor_pos = QCursor.pos()
        current_pos = self.pos()

        if current_pos.y() <= 0 and cursor_pos.y() < current_pos.y():

            new_y = max(0, current_pos.y() - 50)
            self.move(current_pos.x(), new_y)

            self.playAnimation("resources/gif/dog_wall_unscreen.gif")

    def contextMenuEvent(self, event):
        self.move_mode_menu.exec_(event.globalPos())
        
    def timerEvent(self, event):
        if event.timerId() == self.cursor_timer:
            if not self.is_dragging and not self.should_random_move:
                self.move_to_cursor() 

    def move_to_cursor(self):
        cursor_pos = QCursor.pos()
        current_pos = self.pos()


        center_pos = QPoint(current_pos.x() + self.width() // 2, current_pos.y() + self.height() // 2)

        if cursor_pos.x() > current_pos.x():
            animation_file = "resources/gif/dog_run_right_unscreen.gif"
        else:
            animation_file = "resources/gif/dog_run_left_unscreen.gif"

        if current_pos.x() < cursor_pos.x() < current_pos.x() + self.height():
            self.playAnimation("resources/gif/dogs_stay_unscreen.gif")
            return
        
        self.playAnimation(animation_file)
    

        dx = cursor_pos.x() - center_pos.x()
        dy = cursor_pos.y() - center_pos.y()
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > self.speed:

            step_dx = dx / distance * self.speed
            step_dy = dy / distance * self.speed

            new_pos = QPoint(int(current_pos.x() + step_dx), int(current_pos.y()))

            self.move(new_pos)
        else:

            self.killTimer(self.cursor_timer)
            self.cursor_timer = 0
            self.reached_target = True


    def playAnimation(self, filename):
        if self.movie and self.movie.fileName() == filename:
            return
        self.movie = QMovie(filename)
        self.label.setMovie(self.movie) 
        self.movie.start()

        self.movie.finished.connect(self.restartAnimation)

    def restartAnimation(self):

        if self.movie:
            self.movie.start()
            
    def toggle_show_nobara_window(self):
        if self.timer_window.isHidden():
            self.timer_window.show()
        else:
            self.timer_window.hide()

    def toggle_show_ziegfied_window(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

class Nobara(QMainWindow):
    def __init__(self, parent_window):
        super().__init__()

        self.parent_window = parent_window
        
        self.media_player = QMediaPlayer(self)
        self.media_content = QMediaContent(QUrl.fromLocalFile("resources/sound/bark.mp3"))

        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 95, 104)
        self.label.setAlignment(Qt.AlignCenter)
        self.movie = None  
        
        # Remove system menu and window frame
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.media_content = QMediaContent(QUrl.fromLocalFile("resources/sound/bark.mp3"))
        # Make the window transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(300, 900, 95, 104)
        

        self.cursor_timer = self.startTimer(50)         

        self.is_left_button_held_long = False
        self.left_button_hold_timer = QTimer(self)
        self.left_button_hold_timer.timeout.connect(self.handle_left_button_hold_timeout)

        self.central_widget = QLabel(self)
        self.central_widget.setGeometry(0, 0, 95, 104)
        self.central_widget.setAlignment(Qt.AlignCenter)

        self.standing_gifs = ['resources/gif/dogs_stay_unscreen.gif', 'resources/gif/dogs_sit_unscreen.gif', 'resources/gif/dogs_sitdown_unscreen.gif']

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_behaviour)
        self.timer.start(2000)  # Update behaviour every 3 seconds

        self.current_state = "Standing"
        self.old_pos = self.pos()

        self.dx = 0
        self.speed = 5
        self.steps_remaining = 0  # Number of steps remaining in the current direction

        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.move_window)

        # Get desktop size
        self.desktop_rect = QDesktopWidget().screenGeometry()
        self.desktop_width = self.desktop_rect.width()

        # Flags to control window behavior
        self.should_attract_to_taskbar = True
        self.is_dragging = False
        self.is_shift_pressed = False

        # Additional setup for attraction
        self.desktop_rect = QApplication.desktop().availableGeometry()
        self.attraction_strength = 0.1  # You may adjust this value as needed
        self.animation = QPropertyAnimation(self, b'pos')
        self.desktop_watcher = QFileSystemWatcher()
        desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        self.desktop_watcher.addPath(desktop_path)

        # Connect signals
        self.desktop_watcher.fileChanged.connect(self.attract_to_taskbar)

        # Timer to periodically check and update the window position
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.attract_to_taskbar)
        self.timer.start(100)  # Adjust the interval as needed (milliseconds)
        
        def get_background_image_path_from_config():
            config_file = "config.txt"
            background_image_path = None

            with open(config_file, 'r') as f:
                lines = f.readlines()
                found_header = False

                for line in lines:
                    if line.strip() == "#background popup/tray menu":
                        found_header = True
                    elif found_header:
                        # Assuming the path is specified after the header on the same line
                        background_image_path = line.strip()
                        break

            return background_image_path

        # Get the background image path from config.txt
        background_image_path = get_background_image_path_from_config()

        # Create a menu for choosing move mode
        self.move_mode_menu = QMenu(self)
        self.move_mode_menu.setStyleSheet(        
            f"""
            QMenu {{
                background-image: url('{background_image_path}');
                background-repeat: no-repeat; 
                background-position: center; 
                border: 1px solid #707070; 
                font-family: Garamond; 
                font-weight: bold;
            }}
            QMenu::item {{
                padding: 5px 20px; 
                color: white; 
            }}
            QMenu::item:selected {{
                background-color: rgba(236, 151, 156, 150);
            }}
            """
        )        
        self.move_mode_menu.clear()  # Clear existing actions if any
        self.move_mode_menu.addAction("Nobara")  # Add the label "Ziegfried"
        self.move_mode_menu.addSeparator()  # Add a separator        
        self.random_move_action = QAction("Random", self)
        self.cursor_move_action = QAction("Cursor", self)
        self.hide_window_action = QAction("Hide", self)
        self.random_move_action.setCheckable(True)  # Make actions checkable
        self.random_move_action.setChecked(True)  # Set the default action to checked
        self.cursor_move_action.setCheckable(True)
        self.move_mode_menu.addAction(self.random_move_action)
        self.move_mode_menu.addAction(self.cursor_move_action)
        self.move_mode_menu.addSeparator()
        self.move_mode_menu.addAction(self.hide_window_action)
        self.random_move_action.triggered.connect(self.set_random_move_mode)
        self.cursor_move_action.triggered.connect(self.set_cursor_move_mode)
        self.hide_window_action.triggered.connect(self.hide_window)

        self.should_random_move = True  # Default to random movement
        
    def hide_window(self):
        self.parent_window.toggle_show_nobara_action_popup.setText("Show Nobara")
        self.parent_window.toggle_show_nobara_action_tray.setText("Show Nobara")
        self.parent_window.toggle_show_nobara_action_tray.setChecked(False)
        self.parent_window.toggle_show_nobara_action_popup.setChecked(False)        
        self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Start a timer to track long press
            self.left_button_hold_timer.start(500)  # 5 seconds
            self.is_left_button_held_long = False

            self.is_dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.is_dragging:
            return
        if self.is_dragging:
            self.move(event.globalPos() - self.offset)
        if not self.should_random_move:
            self.move_to_cursor()  # Move window to cursor position
        else:
            super().mouseMoveEvent(event)  

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
        
      
            if not self.is_left_button_held_long:
                
                self.media_player.setMedia(self.media_content)
                self.media_player.play()
    
            self.left_button_hold_timer.stop()

            # Check if window left the taskbar and update state accordingly
            if self.is_touching_taskbar and not self.should_attract_to_taskbar:
                self.current_state = "Standing"
                self.start_standing()

            self.is_touching_taskbar = False
            
    def handle_left_button_hold_timeout(self):
        # Timeout for long press of the left mouse button
        self.is_left_button_held_long = True
        # Stop the timer
        self.left_button_hold_timer.stop()

    def attract_to_taskbar(self):
        # Skip attraction if the left mouse button is being dragged or Shift key is pressed
        if not self.should_attract_to_taskbar or self.is_dragging or self.is_shift_pressed:
            return
        
        # Calculate distance to the taskbar
        distance_to_taskbar = self.desktop_rect.bottom() - self.height() - self.y() + 48

        # Check if in the specified zone (approximately 50 pixels in height from attract_to_taskbar)
        in_zone = distance_to_taskbar < 50

        # If not already touching taskbar and in zone, set touching taskbar flag and stop attraction
        if in_zone and not self.is_touching_taskbar:
            self.is_touching_taskbar = True
            self.animation.stop()
            return

        # If not in zone anymore, unset touching taskbar flag
        if not in_zone:
            self.is_touching_taskbar = False

        # If touching taskbar, skip attraction
        if self.is_touching_taskbar:
            return

        # Adjust the window's position based on the attraction strength
        new_y = self.y() + self.attraction_strength * distance_to_taskbar

        # Ensure the window stays within the desktop bounds
        new_y = max(self.desktop_rect.top(), min(new_y, self.desktop_rect.bottom() - self.height()))

        # Animate the window's position smoothly
        self.animation.stop()  # Stop any ongoing animations
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(self.x(), int(new_y)))
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.start()

        # If in the specified zone, activate the function to return to the previous state
        if in_zone:
            self.restore_previous_state()

    def restore_previous_state(self):
        # Implement your logic to restore the previous state of the window here
        pass

    def update_behaviour(self):
        if self.should_random_move:
            # Randomly choose between Standing and Walking only if should_attract_to_taskbar is True
            if self.should_attract_to_taskbar:
                # Calculate distance to the taskbar
                distance_to_taskbar = self.desktop_rect.bottom() - self.height() - self.y() + 48

                # Check if in the specified zone (approximately 50 pixels in height from attract_to_taskbar)
                in_zone = distance_to_taskbar < 50

                if in_zone:
                    # If in the zone, proceed with random behavior selection
                    self.current_state = random.choice(["Standing", "Walking"])
                else:
                    # If not in the zone, stick to Standing until in the zone
                    self.current_state = "Standing"
            else:
                # If not attracting to the taskbar, proceed with normal behavior
                self.current_state = random.choice(["Standing", "Walking"])
        else:
            # If cursor movement mode is active, do not change the behavior
            return

        if self.current_state == "Standing":
            self.start_standing()
            self.move_timer.stop()  # Stop window movement
        else:
            self.start_walking()
            self.move_timer.start(50)  # Start window movement

    def start_standing(self):
        # Randomly choose a standing gif
        standing_gif = random.choice(self.standing_gifs)
        self.playAnimation(standing_gif)

    def start_walking(self):
        # If steps remaining, continue in the current direction
        if self.steps_remaining > 0:
            self.move_window()
            return

        # Randomly choose a walking gif and direction
        walking_gif = random.choice(['resources/gif/dogs_walk_left_unscreen.gif', 'resources/gif/dog_run_left_unscreen.gif', 
                                     'resources/gif/dogs_walk_right_unscreen.gif', 'resources/gif/dog_run_right_unscreen.gif'])
        self.playAnimation(walking_gif)

        # Set direction based on chosen gif
        if 'left' in walking_gif:
            self.dx = -1
        else:
            self.dx = 1

        # Set number of steps to move in the current direction
        self.steps_remaining = random.randint(8, 10)

    def set_movie(self, movie_name):
        movie = QMovie(movie_name)
        self.central_widget.setMovie(movie)
        movie.start()
        # Connect the signal for when the movie ends to restart it
        movie.finished.connect(movie.start)

    def resume_movement(self):
        # Resume movement after staying
        self.start_walking()
        self.move_timer.start(50)  # Start window movement

    def set_random_move_mode(self):
        if self.cursor_move_action.isChecked():  
            self.cursor_move_action.setChecked(False)
        self.should_random_move = True
        self.move_timer.start(50)

    def set_cursor_move_mode(self):
        if self.random_move_action.isChecked():  
            self.random_move_action.setChecked(False)
        self.should_random_move = False
        self.move_timer.stop

    def contextMenuEvent(self, event):
        self.move_mode_menu.exec_(event.globalPos())
        
    def timerEvent(self, event):
        if event.timerId() == self.cursor_timer:
            if not self.is_dragging and not self.should_random_move:
                self.move_to_cursor()  

    def move_window(self):
        if QApplication.mouseButtons() == Qt.LeftButton:
            return
        new_x = self.x() + self.dx * self.speed
        if new_x < 0 or new_x + self.width() > self.desktop_width:
            self.dx *= -1
            self.steps_remaining = random.randint(8, 10)
            self.playAnimation('resources/gif/dogs_walk_left_unscreen.gif' if self.dx == -1 else 'resources/gif/dogs_walk_right_unscreen.gif')
            return
        self.move(new_x, self.y())  # Updated to only change x-coordinate
        self.steps_remaining -= 1
        
    def playAnimation(self, filename):
        if self.movie and self.movie.fileName() == filename:
            return
        self.movie = QMovie(filename)
        self.label.setMovie(self.movie)  
        self.movie.start()
        

        self.movie.finished.connect(self.restartAnimation)

    def restartAnimation(self):
        
        if self.movie:
            self.movie.start()
            
    def move_to_cursor(self):
        cursor_pos = QCursor.pos()
        current_pos = self.pos()


        center_pos = QPoint(current_pos.x() + self.width() // 2, current_pos.y() + self.height() // 2)


        if cursor_pos.x() > current_pos.x():
            animation_file = "resources/gif/dog_run_right_unscreen.gif"
        else:
            animation_file = "resources/gif/dog_run_left_unscreen.gif"

        if current_pos.x() < cursor_pos.x() < current_pos.x() + self.height():
            self.playAnimation("resources/gif/dogs_stay_unscreen.gif")
            return

        self.playAnimation(animation_file)
    
        dx = cursor_pos.x() - center_pos.x()
        dy = cursor_pos.y() - center_pos.y()
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > self.speed:

            step_dx = dx / distance * self.speed
            step_dy = dy / distance * self.speed


            new_pos = QPoint(int(current_pos.x() + step_dx), int(current_pos.y()))

            self.move(new_pos)
        else:

            self.killTimer(self.cursor_timer)
            self.cursor_timer = 0
            self.reached_target = True

class TimerWindow(QDialog):
    
    def __init__(self, parent_window):
        super().__init__()

        self.parent_window = parent_window
        self.setWindowIcon(QIcon('resources\\icon\\app.ico'))
        self.setWindowTitle("Timer")
        self.setGeometry(100, 100, 200, 200)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint )
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Time:", self)
        self.time_display = QLabel("00:00:00", self)
        self.start_button = QPushButton("Start", self)
        self.stop_button = QPushButton("Stop", self)
        self.reset_button = QPushButton("Reset", self)
        self.exit_button = QPushButton("Exit", self)
        
        layout.addWidget(self.label)
        layout.addWidget(self.time_display)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.exit_button)
        
        self.start_button.clicked.connect(self.start_timer)
        self.stop_button.clicked.connect(self.stop_timer)
        self.reset_button.clicked.connect(self.reset_timer)
        self.exit_button.clicked.connect(self.hide_timer)  # Connect exit_button to hide_timer() method
        
        self.timer_running = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # Initially, disable the Stop and Reset buttons
        self.stop_button.setEnabled(False)
        self.reset_button.setEnabled(False)

        self.load_settings()  # Load settings including background image
        self.set_background_image()  # Set background image

        # Variables for mouse dragging
        self.draggable = False
        self.offset = QPoint()

    def load_settings(self):
        try:
            with open("config.txt", "r") as file:
                lines = file.readlines()
                settings = {}
                label = None  # Initialize label
                for line in lines:
                    if line.startswith("#"):  # Check if the line is a comment (indicating a label)
                        label = line.strip("#").strip().lower()  # Extract the label and convert to lowercase
                    else:
                        if label and line.strip():  # Check if a label exists and the line is not empty
                            settings[label] = line.strip()  # Store the data with its label in the dictionary

                # Check if all necessary settings are present
                if len(settings) >= 6:  # Assuming there are 6 settings in total
                    background_image_path_str = settings.get('background timer')
                    self.background_image_path = background_image_path_str.strip()

        except FileNotFoundError:
            print("Config file not found.")
        except ValueError:
            print("Error parsing config file.")

    def set_background_image(self):
        if hasattr(self, 'background_image_path'):
            self.setStyleSheet(f"""
                TimerWindow {{background-image: url({self.background_image_path}); background-repeat: no-repeat; background-position: center}}
                QLabel, QPushButton {{  
                    font-family: Garamond;
                    font-size: 15px;       
                    color: white;
                    font-weight: bold;
                }}         
                QPushButton {{
                    border: solid; 
                    border-radius: 10px;
                    padding: 5px 10px; /* Adjust padding to control button width */
                    min-width: 50px; /* Set minimum width for the button */
                    background-color: rgba(236, 151, 156, 150); /* Set button background color */
                }}
                QPushButton:disabled {{
                   background-color: rgba(210, 99, 106, 150);
                }}           
                QPushButton:hover {{
                    background-color: rgba(255, 0, 0, 150); /* Change button background color on hover */
                }}
            """)

    def mousePressEvent(self, event):
        # Check if the left mouse button is pressed
        if event.button() == Qt.LeftButton:
            self.draggable = True
            # Save the position of the mouse cursor relative to the window's top-left corner
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        # Check if the left mouse button is pressed and the window is draggable
        if self.draggable and event.buttons() & Qt.LeftButton:
            # Move the window by the difference between the current mouse position and the saved offset
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        # Reset the draggable flag when the left mouse button is released
        if event.button() == Qt.LeftButton:
            self.draggable = False

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.time_display.setEnabled(True)
            self.timer.start(1000)  # Trigger timeout every 1000 ms (1 second)
            self.reset_button.setEnabled(False)
            # Enable the Stop button and disable the Start button
            self.stop_button.setEnabled(True)
            self.start_button.setEnabled(False)

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.timer.stop()
            self.start_button.setEnabled(True)
            # Enable the Reset button and disable the Stop button
            self.reset_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def reset_timer(self):
        self.stop_timer()
        self.time_display.setText("00:00:00")

        # Disable the Reset button and enable the Start button
        self.reset_button.setEnabled(False)
        self.start_button.setEnabled(True)

    def update_timer(self):
        current_time = QTime.fromString(self.time_display.text(), "HH:mm:ss")
        current_time = current_time.addSecs(1)  # Add one second to the current time
        self.time_display.setText(current_time.toString("HH:mm:ss"))
        
    def hide_timer(self):
        self.parent_window.toggle_timer_action.setText("Show Timer")
        self.parent_window.toggle_alarm_action_tray.setText("Show Timer")
        self.parent_window.toggle_timer_action.setChecked(False)
        self.parent_window.toggle_alarm_action_tray.setChecked(False)  
        self.hide()

class DraggableMessageBox(QMessageBox):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool)

        # Variables for dragging the window
        self.old_pos = QPoint(self.pos())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        pass

class AlarmClock(QDialog):
    def __init__(self, parent_window):
        super().__init__()
        
        self.setWindowIcon(QIcon('resources\\icon\\app.ico'))

        self.parent_window = parent_window
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint )
        
        self.setWindowTitle("Alarm")
        self.setFixedSize(200, 250)
        
        # Set font for the entire widget
        font = QFont("Garamond", 10, QFont.Bold)
        self.setFont(font)
        
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.cancel_alarm)
        self.cancel_button.setFixedHeight(30)
        
        self.set_sound_button = QPushButton("Set Sound", self)
        self.set_sound_button.clicked.connect(self.set_sound)
        self.set_sound_button.setFixedHeight(30)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Set alarm time:", self)
        self.time_edit = QTimeEdit(self)
        self.time_edit.setDisplayFormat("HH:mm:ss")
        
        self.repeat_label = QLabel("Repeat count:", self)
        self.repeat_spinbox = QSpinBox(self)
        self.repeat_spinbox.setMinimum(0)
        self.repeat_spinbox.setMaximum(10)        
        self.play_checkbox = QCheckBox("Play Alarm", self)
        
        self.set_button = QPushButton("Set Alarm", self)
        self.set_button.clicked.connect(self.set_alarm)
        self.set_button.setFixedHeight(30)
        
        layout.addWidget(self.label)
        layout.addWidget(self.time_edit)
        layout.addWidget(self.repeat_label)
        layout.addWidget(self.repeat_spinbox)
        layout.addWidget(self.play_checkbox)
        layout.addWidget(self.set_button)
        layout.addWidget(self.set_sound_button)
        layout.addWidget(self.cancel_button)
        
        self.alarm_timer = QTimer(self)
        self.alarm_timer.timeout.connect(self.check_alarm)
        self.media_player = QMediaPlayer()
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)

        # Load settings from config.txt
        self.load_settings()
        
        self.repeat_count = self.repeat_spinbox.value()  # Инициализация repeat_count
        
        self.alarm_timer = QTimer(self)
        self.alarm_timer.timeout.connect(self.check_alarm)
        self.alarm_timer.start(1000)  # изменение здесь, чтобы таймер запускался каждую секунду

        # Variables for dragging the window
        self.old_pos = QPoint(self.pos())

    def load_settings(self):
        try:
            with open("config.txt", "r") as file:
                lines = file.readlines()
                settings = {}
                label = None  # Initialize label
                for line in lines:
                    if line.startswith("#"):  # Check if the line is a comment (indicating a label)
                        label = line.strip("#").strip().lower()  # Extract the label and convert to lowercase
                    else:
                        if label and line.strip():  # Check if a label exists and the line is not empty
                            settings[label] = line.strip()  # Store the data with its label in the dictionary

                # Check if all necessary settings are present
                if len(settings) >= 5:
                    time_str = settings.get('time alarm')
                    repeat_count_str = settings.get('repeat alarm count')
                    play_alarm_str = settings.get('play alarm')
                    media_path_str = settings.get('media alarm path')
                    background_image_path_str = settings.get('background alarm')

                    self.time_edit.setTime(QTime.fromString(time_str.strip(), "HH:mm:ss"))
                    self.repeat_spinbox.setValue(int(repeat_count_str.strip()))
                    self.play_checkbox.setChecked(bool(int(play_alarm_str.strip())))
                    self.media_path = media_path_str.strip()
                    self.setStyleSheet("""
                        AlarmClock {background-image: url(%s); background-repeat: no-repeat; background-position: center}
                        QLabel, QPushButton {  
                            font-family: Garamond;
                            color: white;
                            font-weight: bold;
                        }

                        QCheckBox {
                            font-family: Garamond;
                            color: white;
                            font-weight: bold;
                        }

                        QCheckBox::indicator {
                            width: 20px; /* Ширина индикатора */
                            height: 20px; /* Высота индикатора */
                            border: 2px solid white; /* Граница индикатора */
                            border-radius: 10px; /* Скругление углов индикатора (делает его круглым) */
                            background-color: rgba(255, 255, 255, 100); /* Цвет индикатора */
                        }

                        QCheckBox::indicator:checked {
                            image: url(%s);               
                            background-color: rgba(255, 0, 0, 100); /* Цвет индикатора при выборе */
                        }

                        QCheckBox::indicator:hover {
                            border: 2px solid red; /* Граница индикатора при наведении */
                        }

                        QSpinBox, QTimeEdit {
                            font-family: Garamond;
                            color: white;
                            font-weight: bold;   
                            background-color: rgba(236, 151, 156, 150); /* Прозрачный белый фон */
                        }   

                        QSpinBox:hover, QTimeEdit:hover {
                            background-color: rgba(255, 0, 0, 150); /* Цвет при наведении */
                        }               

                        QPushButton {
                            border-radius: 10px;               
                            background-color: rgba(236, 151, 156, 150); /* Цвет кнопки */
                        }

                        QPushButton:hover {
                            background-color: rgba(255, 0, 0, 150); /* Цвет при наведении */
                        }
                    """ % (background_image_path_str.strip(), "resources/icon/checkmark.png"))  # Update the background image path
        except FileNotFoundError:
            print("Config file not found.")
        except ValueError:
            print("Error parsing config file.")

    def set_alarm(self):
        self.save_settings()
        self.parent_window.toggle_alarm_action.setText("Show Alarm")
        self.parent_window.toggle_alarm_action_tray.setText("Show Alarm")
        self.parent_window.toggle_alarm_action.setChecked(False)
        self.parent_window.toggle_alarm_action_tray.setChecked(False)   
        alarm_time = self.time_edit.time().toString("HH:mm:ss")
        self.label.setText(f"Alarm set for {alarm_time}")
        self.repeat_count = self.repeat_spinbox.value()  # Установка repeat_count
        self.alarm_timer.start(1000)
        self.hide()

    def check_alarm(self):
        current_time = QTime.currentTime()
        alarm_time = self.time_edit.time()
        if self.play_checkbox.isChecked():
            # Сравниваем только часы, минуты и секунды
            if current_time.hour() == alarm_time.hour() and \
                        current_time.minute() == alarm_time.minute() and \
                        current_time.second() == alarm_time.second():
                    self.alarm_timer.stop()
                    self.label.setText("Time's up! Wake up!")
                    if self.play_checkbox.isChecked():
                        self.play_alarm_sound()
                    self.show_alarm_message()

    def play_alarm_sound(self):
        self.playback_count = 0
        self.play_next_iteration()

    def play_next_iteration(self):
        if self.playback_count < self.repeat_count:
            self.playback_count += 1
            media_content = QMediaContent(QUrl.fromLocalFile(self.media_path))
            self.media_player.setMedia(media_content)
            self.media_player.play()
        else:
            pass

    def media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.play_next_iteration()

    def cancel_alarm(self):
        self.parent_window.toggle_alarm_action.setText("Show Alarm")
        self.parent_window.toggle_alarm_action_tray.setText("Show Alarm")
        self.parent_window.toggle_alarm_action.setChecked(False)
        self.parent_window.toggle_alarm_action_tray.setChecked(False)     
        self.hide()  
        
    def save_settings(self):
        try:
            # Read existing settings
            settings = {}
            with open("config.txt", "r") as file:
                current_label = None
                for line in file:
                    line = line.strip()
                    if line.startswith("#"):
                        current_label = line.strip("#").strip().lower()
                        settings[current_label] = []  # Initialize empty list for label
                    elif current_label:
                        settings[current_label].append(line)

            # Update specific settings
            settings['time alarm'] = [self.time_edit.time().toString("HH:mm:ss")]
            settings['repeat alarm count'] = [str(self.repeat_spinbox.value())]
            settings['play alarm'] = ['1' if self.play_checkbox.isChecked() else '0']
            settings['media alarm path'] = [os.path.relpath(self.media_path, os.path.dirname(__file__))]

            # Write updated settings
            new_lines = []
            with open("config.txt", "w") as file:
                for label, lines in settings.items():
                    new_lines.append(f"#{label}\n")  # Write the label
                    if lines:  # If there are lines associated with this label, write them
                        for line in lines:
                            new_lines.append(f"{line}\n")

                file.writelines(new_lines)

        except FileNotFoundError:
            print("Config file not found.")
        except ValueError:
            print("Error parsing config file.")


    def set_sound(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Sound File", "", "Sound Files (*.wav *.mp3)", options=options)
        if file_path:
            # Определяем путь к папке resources/sound/
            sound_folder = os.path.join(os.path.dirname(__file__), 'resources/sound')
            # Создаем папку, если ее нет
            if not os.path.exists(sound_folder):
                os.makedirs(sound_folder)
            # Получаем только имя файла без пути
            file_name = os.path.basename(file_path)
            # Формируем путь к файлу в папке resources/sound/
            destination_path = os.path.join(sound_folder, file_name)
            # Копируем выбранный звуковой файл в папку resources/sound/
            shutil.copyfile(file_path, destination_path)

            # Записываем относительный путь в конфигурационный файл
            relative_path = os.path.join("resources", "sound", file_name)
            with open("config.txt", "r") as file:
                lines = file.readlines()
            with open("config.txt", "w") as file:
                for line in lines:
                    if line.startswith("# Media timer Path"):
                        file.write(f"# Media timer Path\n{relative_path}\n")
                    else:
                        file.write(line)

            self.media_path = destination_path
            self.save_settings()


    def show_alarm_message(self):
        msg = DraggableMessageBox()  # используем наше кастомное QMessageBox
        msg.setIcon(QMessageBox.Information)
        msg.setText("Time's up! Wake up!")
        msg.setWindowTitle("Alarm")

        ok_button = msg.addButton("OK", QMessageBox.ButtonRole.AcceptRole)

        msg.setStyleSheet("""
            DraggableMessageBox {
                background-color: rgba(236, 151, 156, 150);
                border: 2px solid white;
                border-radius: 10px;
            }
            DraggableMessageBox QLabel {
                font-family: Garamond;
                color: white;
                font-weight: bold;
            }
            DraggableMessageBox QPushButton {
                background-color: rgba(236, 151, 156, 150);
                font-family: Garamond;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px;
                min-width: 70px; 
            }
            DraggableMessageBox QPushButton:hover {
                background-color: rgba(255, 0, 0, 150);
            }                         
        """)
        msg.exec_()
        msg.hide()

    # Methods for dragging the window
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        pass

class ClockWidget(QWidget):
    def __init__(self, font_family="Garamond", time_font_size=9, label_font_size=9):
        super().__init__()      

        # Load the pre-processed "background_image.png" with desired transparency
        background_image = QPixmap("background_image.png")

        # Create label to display the "Time" text
        self.time_label = QLabel("Time", self)
        self.time_label.setAlignment(Qt.AlignCenter)

        # Create label to display the clock
        self.clock_label = QLabel(self)
        self.clock_label.setAlignment(Qt.AlignTop)  # Align to the top

        # Set the font for the labels
        font = QFont(font_family, time_font_size)
        self.time_label.setFont(font)
        self.clock_label.setFont(font)

        # Create timer to update the clock every second
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every 1000 milliseconds (1 second)

        # Initial clock update
        self.update_clock()

        # Set window flags to make it frameless
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Make the window background fully transparent
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create a vertical layout for the time, "Date," and clock labels
        layout = QVBoxLayout(self)
        layout.addWidget(self.time_label, alignment=Qt.AlignCenter)

        layout.addWidget(self.clock_label, alignment=Qt.AlignCenter)

        # Set layout alignment and spacing
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(2)  # Adjust the spacing as needed

        # Set the size of the window
        self.resize(100, 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the background image with transparency
        background_image = QPixmap("resources/background/background_image.png")
        painter.drawPixmap(self.rect(), background_image)

    def update_clock(self):
        # Update the clock label with the current time
        current_time = QDateTime.currentDateTime()
        formatted_time = current_time.toString("hh:mm:ss")

        # Update the date label with the current date
        formatted_date = current_time.toString("MMM dd, yyyy")

        # Concatenate time, "Date," and date strings
        display_text = f"{formatted_time}\nDate\n{formatted_date}"

        # Set the text for the labels
        self.clock_label.setText(display_text)

    def toggle_visibility(self):
        # Toggle the visibility of the clock widget
        self.setVisible(not self.isVisible())

class GifPlayerThread(QThread):
    gif_finished = pyqtSignal()

    def __init__(self, label, gif_file):
        super().__init__()
        self.label = label
        self.gif_file = gif_file

    def run(self):
        movie = QMovie(self.gif_file)
        self.label.setMovie(movie)
        movie.finished.connect(self.gif_finished.emit)
        movie.start()
        self.exec_()
        
class MyWindow(QWidget):
    # Rest timer signal
    stop_rest_timer = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.nobara_window = Nobara(self)
        self.ziegfied_window = Ziegfied(self)
        
        self.is_touching_taskbar = False

        self.timer_window = TimerWindow(self)
        
        self.audio_player = AudioPlayer(self)

        self.config_window = ConfigWindow(self)
        
        # Create QMediaPlayer instance for playing MP3
        self.media_player = QMediaPlayer()
        
        # Create AlarmClock instance
        self.alarm_clock = AlarmClock(self)
        
        # Create ClockWidget instance
        self.clock_widget = ClockWidget()
        
        self.clock_widget.hide()
        self.target_pos = QPoint(400, 400)
        self.reached_target = False
        self.click_count = 0
        self.click_timer = QTimer(self)
        self.click_timer.timeout.connect(self.reset_click_count)
        self.click_timer.setSingleShot(True)
        self.movie = None
        self.prev_pos = QCursor.pos()

        # Start cursor follower timer
        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self.updateCursorFollowing)
        self.cursor_timer.start(50)  # Update cursor following every 50 milliseconds
        self.cursor_timer = self.startTimer(50)
        self.is_left_button_held_long = False
        self.left_button_hold_timer = QTimer(self)
       
        self.clock_widget.setParent(self)

        # Add the rest timer to the __init__ function
        self.rest_timer = QTimer(self)
        self.rest_timer.timeout.connect(self.rest_complete)

        self.movement_counter = 0
        self.step_size = 3
        self.continuous_move_timer = QTimer(self)
        self.continuous_move_timer.timeout.connect(self.continuous_move)
        self.continuous_move_timer.start(20)       
        self.movie_standing = QMovie("resources/gif/stay.gif")
        # Create window with GIF
        self.movie_idle = QMovie("resources/gif/stay.gif")
        self.movie_walk_left = QMovie("resources/gif/makima_walk_left_unscreen.gif")
        self.movie_walk_right = QMovie("resources/gif/makima_walk_right_unscreen.gif")
        self.label = QLabel()
        self.label.setMovie(self.movie_idle)
        self.movie_idle.start()
        self.sound_player = QMediaPlayer()
        self.sound_files = [
            "resources/sound/i_can't_believe_youre_clowning_around_at_a_time_like_this_Makima.mp3",
            "resources/sound/Good_boy_Makima.wav",
            "resources/sound/Makima13.wav",
            "resources/sound/Makima21.wav",
            "resources/sound/Makima33.wav",
            "resources/sound/Makima42.wav",
            "resources/sound/English_Makima.mp3"
        ]
        self.last_click_time = QDateTime.currentDateTime()

        # Set window size based on GIF dimensions
        self.resize(self.movie_idle.frameRect().size())

        # Remove system menu and window frame
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint)

        # Make the window transparent
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create System tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("resources\\icon\\app.ico"))
        
        self.movement_group = QActionGroup(self)
        self.movement_group.setExclusive(True)
        
        self.popup_menu = QMenu()
        
        def get_background_image_path_from_config():
            config_file = "config.txt"
            background_image_path = None

            with open(config_file, 'r') as f:
                lines = f.readlines()
                found_header = False

                for line in lines:
                    if line.strip() == "#background popup/tray menu":
                        found_header = True
                    elif found_header:
                        # Assuming the path is specified after the header on the same line
                        background_image_path = line.strip()
                        break

            return background_image_path

        # Get the background image path from config.txt
        background_image_path = get_background_image_path_from_config()

        # Assuming self.popup_menu is your QMenu instance
        self.popup_menu.setStyleSheet(
            f"""
            QMenu {{
                background-image: url('{background_image_path}');
                background-repeat: no-repeat; 
                background-position: center; 
                border: 1px solid #707070; 
                font-family: Garamond; 
                font-weight: bold;
            }}
            QMenu::item {{
                padding: 5px 20px; 
                color: white; 
            }}
            QMenu::item:selected {{
                background-color: rgba(236, 151, 156, 150);
            }}
            """
        )

        
        self.toggle_show_ziegfied_action_popup = QAction("Show Ziegfried", self)
        self.toggle_show_ziegfied_action_popup.setCheckable(True)
        self.toggle_show_ziegfied_action_popup.setChecked(False)
        self.toggle_show_ziegfied_action_popup.triggered.connect(self.toggle_show_ziegfied_window)
        self.popup_menu.addAction(self.toggle_show_ziegfied_action_popup)
        
        self.toggle_show_nobara_action_popup = QAction("Show Nobara", self)
        self.toggle_show_nobara_action_popup.setCheckable(True)
        self.toggle_show_nobara_action_popup.setChecked(False)
        self.toggle_show_nobara_action_popup.triggered.connect(self.toggle_show_nobara_window)
        self.popup_menu.addAction(self.toggle_show_nobara_action_popup)

        self.popup_menu.addSeparator()
        
        self.resume_movement_action = QAction("Resume Movement", self)
        self.resume_movement_action.setCheckable(True)
        self.resume_movement_action.setChecked(True)
        self.popup_menu.addAction(self.resume_movement_action)
        self.movement_group.addAction(self.resume_movement_action)  
        self.resume_movement_action.triggered.connect(self.resume_movement)

        # Создание действия "Stop Movement" для popup_menu
        self.stop_movement_popup_action = QAction("Stop Movement", self)
        self.stop_movement_popup_action.setCheckable(True)
        self.stop_movement_popup_action.setChecked(False)
        self.popup_menu.addAction(self.stop_movement_popup_action)
        self.stop_movement_popup_action.triggered.connect(self.stop_movement)


        self.popup_menu.addSeparator()
        # Create menu actions for movement modes
        self.random_move_action = QAction("Random Movement", self)
        self.random_move_action.setCheckable(True)        
        self.popup_menu.addAction(self.random_move_action)
        self.random_move_action.setChecked(True)  # Set random movement as the default mode
        self.random_move_action.triggered.connect(self.set_random_movement)
        self.follow_cursor_action = QAction("Follow Cursor", self)
        self.follow_cursor_action.setCheckable(True)     
        self.follow_cursor_action.setChecked(False)
        self.follow_cursor_action.triggered.connect(self.set_follow_cursor_movement)
        self.popup_menu.addAction(self.follow_cursor_action)
        self.popup_menu.addSeparator()  # Add a separator
        
        # Create a toggle action for showing/hiding the clock
        self.toggle_clock_action = QAction("Show Clock", self)
        self.toggle_clock_action.setCheckable(True)
        self.toggle_clock_action.setChecked(False)  # Set to "Show Clock" by default
        self.popup_menu.addAction(self.toggle_clock_action)
        self.toggle_clock_action.triggered.connect(self.toggle_clock)

        # Create a toggle action for showing/hiding the timer
        self.toggle_timer_action = QAction("Show Timer", self)
        self.toggle_timer_action.setCheckable(True)
        self.toggle_timer_action.setChecked(False)  # Set to "Show Timer" by default
        self.popup_menu.addAction(self.toggle_timer_action)
        self.toggle_timer_action.triggered.connect(self.toggle_timer_window)

        # Create a toggle action for showing/hiding the alarm
        self.toggle_alarm_action = QAction("Show Alarm", self)
        self.toggle_alarm_action.setCheckable(True)
        self.toggle_alarm_action.setChecked(False)  # Set to "Set Alarm" by default
        self.popup_menu.addAction(self.toggle_alarm_action)
        self.toggle_alarm_action.triggered.connect(self.toggle_alarm_dialog)
        
        self.popup_menu.addSeparator()
        
        self.show_audio_player_action = QAction("Show Audio Player", self)
        self.show_audio_player_action.setCheckable(True)
        self.show_audio_player_action.setChecked(False)        
        self.show_audio_player_action.triggered.connect(self.show_audio_player)
        self.popup_menu.addAction(self.show_audio_player_action)

        self.show_options_action = QAction("Show Options", self)
        self.show_options_action.setCheckable(True)
        self.show_options_action.setChecked(False)         
        self.show_options_action.triggered.connect(self.show_options)
        self.popup_menu.addAction(self.show_options_action)

        self.popup_menu.addSeparator()  # Add a separator        
        self.hide_action_popup = QAction("Hide Shimeji", self) 
        self.popup_menu.addAction(self.hide_action_popup)        
        self.hide_action_popup.triggered.connect(self.toggle_show_tray)        
        self.close_action_popup = QAction("Exit", self)     
        self.popup_menu.addAction(self.close_action_popup)
        self.close_action_popup.triggered.connect(self.close_application)
        # Modify the existing popup menu and add new actions
        self.popup_menu.addAction(self.hide_action_popup)        
        self.popup_menu.addAction(self.close_action_popup)

        # Set flag for dragging
        self.is_dragging = False
        # Set flag for Shift key pressed
        self.is_shift_pressed = False

        self.tray_menu = QMenu()
        
        self.tray_menu.setStyleSheet(
            f"""
            QMenu {{
                background-image: url('{background_image_path}');
                background-repeat: no-repeat; 
                background-position: center; 
                border: 1px solid #707070; 
                font-family: Garamond; 
                font-weight: bold;
            }}
            QMenu::item {{
                padding: 5px 20px; 
                color: white; 
            }}
            QMenu::item:selected {{
                background-color: rgba(236, 151, 156, 150);
            }}
            """
        )   
        
        self.toggle_show_ziegfied_action_tray = QAction("Show Ziegfried", self)
        self.toggle_show_ziegfied_action_tray.setCheckable(True)
        self.toggle_show_ziegfied_action_tray.setChecked(False)
        self.toggle_show_ziegfied_action_tray.triggered.connect(self.toggle_show_ziegfied_window)
        self.tray_menu.addAction(self.toggle_show_ziegfied_action_tray)
        
        self.toggle_show_nobara_action_tray = QAction("Show Nobara", self)
        self.toggle_show_nobara_action_tray.setCheckable(True)
        self.toggle_show_nobara_action_tray.setChecked(False)
        self.toggle_show_nobara_action_tray.triggered.connect(self.toggle_show_nobara_window)
        self.tray_menu.addAction(self.toggle_show_nobara_action_tray)

        self.tray_menu.addSeparator()
        
        self.resume_movement_action_tray = QAction("Resume Movement", self)
        self.resume_movement_action_tray.setCheckable(True)
        self.resume_movement_action_tray.setChecked(True)
        self.tray_menu.addAction(self.resume_movement_action_tray)
    
        self.resume_movement_action_tray.triggered.connect(self.resume_movement)

        # Создание действия "Stop Movement" для tray_menu
        self.stop_movement_action_tray = QAction("Stop Movement", self)
        self.stop_movement_action_tray.setCheckable(True)
        self.stop_movement_action_tray.setChecked(False)
        self.tray_menu.addAction(self.stop_movement_action_tray)
        self.movement_group.addAction(self.stop_movement_action_tray)
        self.stop_movement_action_tray.triggered.connect(self.stop_movement)


        self.tray_menu.addSeparator()  # Add a separator
        # Create and add actions to the tray menu
        self.random_move_action_tray = QAction("Random Movement", self)
        self.random_move_action_tray.setCheckable(True)
        self.random_move_action_tray.setChecked(True)
        self.tray_menu.addAction(self.random_move_action_tray)
        self.follow_cursor_action_tray = QAction("Follow Cursor", self)
        self.follow_cursor_action_tray.setCheckable(True)
        self.follow_cursor_action_tray.setChecked(False)
        self.tray_menu.addAction(self.follow_cursor_action_tray)
        self.tray_menu.addSeparator()  # Add a separator  
        self.toggle_clock_action_tray = QAction("Show Clock", self)
        self.toggle_clock_action_tray.setCheckable(True)
        self.toggle_clock_action_tray.setChecked(False)
        self.tray_menu.addAction(self.toggle_clock_action)
        self.tray_menu.addAction(self.toggle_timer_action)
        # Create a toggle action for showing/hiding the alarm in the system tray
        self.toggle_alarm_action_tray = QAction("Set Alarm", self)
        self.toggle_alarm_action_tray.setCheckable(True)
        self.toggle_alarm_action_tray.setChecked(False)
        self.tray_menu.addAction(self.toggle_alarm_action)
        self.toggle_alarm_action_tray.triggered.connect(self.toggle_alarm_dialog)
    
        self.tray_menu.addSeparator()
        
        self.show_audio_player_tray_action = QAction("Show Audio Player", self)
        self.show_audio_player_tray_action.setCheckable(True)
        self.show_audio_player_tray_action.setChecked(False)        
        self.show_audio_player_tray_action.triggered.connect(self.show_audio_player)
        self.tray_menu.addAction(self.show_audio_player_tray_action)

        self.show_options_tray_action = QAction("Show Options", self)
        self.show_options_tray_action.setCheckable(True)
        self.show_options_tray_action.setChecked(False)         
        self.show_options_tray_action.triggered.connect(self.show_options)
        self.tray_menu.addAction(self.show_options_tray_action)
        
        self.tray_menu.addSeparator()
        self.toggle_show_action_tray = QAction("Hide Shimeji", self)
        self.tray_menu.addAction(self.toggle_show_action_tray)
        self.toggle_show_action_tray.triggered.connect(self.toggle_show_tray)        
        self.close_action_tray = QAction("Exit", self)
        self.tray_menu.addAction(self.close_action_tray)

        self.toggle_clock_action_tray.triggered.connect(self.toggle_clock)
        self.random_move_action_tray.triggered.connect(self.set_random_movement)
        self.follow_cursor_action_tray.triggered.connect(self.set_follow_cursor_movement)
        self.close_action_tray.triggered.connect(self.close_application)
 
        # Additional properties for automatic attraction
        self.attraction_timer = QTimer(self)
        self.attraction_timer.timeout.connect(self.attract_to_taskbar)
        self.attraction_timer.start(50)  # Adjust the interval as needed
        self.attraction_strength = 0.1  # Adjust the strength of the attraction
        self.animation_duration = 50  # Animation duration in milliseconds
        self.animation = QPropertyAnimation(self, b'pos')
        self.should_attract_to_taskbar = True

        # Get information about the size of the desktop
        desktop_rect = QDesktopWidget().screenGeometry()
        self.desktop_rect = QRect(desktop_rect)

        # Set menu for System tray
        self.tray_icon.setContextMenu(self.tray_menu)

        # Create layout manager and set widgets
        layout = QVBoxLayout(self)
        layout.addWidget(self.label, alignment=Qt.AlignTop | Qt.AlignLeft)
        
    def show_audio_player(self):
        if self.audio_player.isHidden():
            self.audio_player.show() 
            self.show_audio_player_action.setChecked(True)
            self.show_audio_player_tray_action.setChecked(True)
        else:
            self.audio_player.hide() 
            self.show_audio_player_action.setChecked(False)
            self.show_audio_player_tray_action.setChecked(False)            

    def show_options(self):
        if self.config_window.isHidden():
            self.config_window.show() 
            self.show_options_tray_action.setChecked(True)
            self.show_options_action.setChecked(True)
        else:
            self.config_window.hide() 
            self.show_options_tray_action.setChecked(False)
            self.show_options_action.setChecked(False)

    def toggle_show_tray(self):
        if self.isVisible():
            self.toggle_show_action_tray.setText("Show Shimeji")                                   
            self.hide_window()
        else:
            self.toggle_show_action_tray.setText("Hide Shimeji")         
            self.show_window()

    def attract_to_taskbar(self):
        # Skip attraction if the left mouse button is being dragged or Shift key is pressed
        if not self.should_attract_to_taskbar or self.is_dragging or self.is_shift_pressed:
            return
    
        # Calculate distance to the taskbar
        distance_to_taskbar = self.desktop_rect.bottom() - self.height() - self.y() + 48

        # Check if in the specified zone (approximately 50 pixels in height from attract_to_taskbar)
        in_zone = distance_to_taskbar < 50

        # Adjust the window's position based on the attraction strength
        new_y = self.y() + self.attraction_strength * distance_to_taskbar

        # Ensure the window stays within the desktop bounds
        new_y = max(self.desktop_rect.top(), min(new_y, self.desktop_rect.bottom() - self.height()))

        # If not already touching taskbar and in zone, set touching taskbar flag and stop attraction
        if in_zone and not self.is_touching_taskbar:
            self.is_touching_taskbar = True
            # Stop animation only if not touching the taskbar
            if not self.is_shimeji_on_taskbar():
                self.restore_previous_state()
            return

        # If not in zone anymore, unset touching taskbar flag
        if not in_zone:
            self.is_touching_taskbar = False

        # If touching taskbar, skip attraction
        if self.is_touching_taskbar:
            return

        # Animate the window's position smoothly
        self.animation.setStartValue(self.pos())  # Set the start value to the current position
        self.animation.setEndValue(QPoint(self.x(), int(new_y)))
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.setKeyValueAt(0, self.pos())
        self.animation.setKeyValueAt(1, QPoint(self.x(), int(new_y)))
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.start()

        # Additional property for desktop icons monitoring
        self.desktop_watcher = QFileSystemWatcher()
        desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        self.desktop_watcher.addPath(desktop_path)

        # Remove taskbar icon by setting appropriate window flags
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.show()

        # If in the specified zone, activate the function to return to the previous state
        if in_zone:
            self.restore_previous_state()


    def close_application(self):
        # Handler for closing the application
        QCoreApplication.exit()

    def hide_window(self):
        # Handler for hiding the window and creating a shortcut in System tray
        self.should_attract_to_taskbar = False  # Disable attraction when hiding
        self.toggle_show_action_tray.setText("Show Shimeji")
        # Hide the window
        self.setVisible(False)

    def mousePressEvent(self, event):
        current_time = QDateTime.currentDateTime()

        if event.button() == Qt.LeftButton:
            time_difference = self.last_click_time.msecsTo(current_time)
            self.left_button_hold_timer.start(500)  # 5 seconds
            self.is_left_button_held_long = False
            if time_difference < 7000:  # Check if the time difference is less than 2 seconds
                # Increment the click count
                self.click_count += 1

                # Start the timer to reset the click count after a delay
                self.click_timer.start(2000)  # 2 seconds delay

                # Check if the click count reaches 15 and switch to evil.gif
                if self.click_count == 7:
                    self.switch_to_evil_gif()

            self.last_click_time = current_time

            self.is_dragging = True
            self.offset = event.pos()

        elif event.button() == Qt.RightButton:
            # Show the popup menu at the click point
            self.popup_menu.exec_(event.globalPos())

        # Check if the Shift key is pressed
        if event.modifiers() & Qt.ShiftModifier:
            self.is_shift_pressed = True
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
        
            if not self.is_left_button_held_long:
                time_difference = self.last_click_time.msecsTo(QDateTime.currentDateTime())
                if time_difference < 500:  # Check if the time difference is less than 0.5 seconds
                    sound_file = random.choice(self.sound_files)
                    self.sound_player.setMedia(QMediaContent(QUrl.fromLocalFile(sound_file)))
                    self.sound_player.setPosition(0)
                    self.sound_player.play()

            self.left_button_hold_timer.start(500)  # 5 seconds
            self.is_left_button_held_long = False
        
            if self.direction == 'left' and self.y() <= self.desktop_rect.top() + self.desktop_rect.height() / 2:
                if not hasattr(self, 'movie_alternate'):
                    self.movie_alternate = QMovie("resources/gif/stay.gif")

                self.label.setMovie(self.movie_alternate)
                self.movie_alternate.start()

                # Stop playing the animation in the thread if it is running
                if hasattr(self, 'gif_thread'):
                    self.gif_thread.quit()
                    self.gif_thread.wait()
                self.direction = None  # Reset the movement direction

                # Restart the animation in the thread with the new gif
                self.start_gif_thread("resources/gif/stay.gif")
            self.is_touching_taskbar = False
            
    def show_window(self):
        self.toggle_show_action_tray.setText("Hide Shimeji")
        # Handler for showing the hidden window
        self.should_attract_to_taskbar = True  # Enable attraction when showing
        self.attraction_timer.start()  # Start the attraction animation timer
        self.setVisible(True)          

    def switch_to_evil_gif(self):
        # Switch to evil.gif
        self.start_gif_thread("resources/gif/evil.gif")
        self.click_count = 0  # Reset click count after switching

    def reset_click_count(self):
        # Reset the click count after the timer expires
        self.click_count = 0

    def mouseMoveEvent(self, event):
        if not event.buttons() & Qt.LeftButton:
            return

        if self.is_dragging:
            if self.random_move_action.isChecked():                
                new_pos = event.globalPos() - self.offset
                new_pos.setX(max(self.desktop_rect.left(), min(new_pos.x(), self.desktop_rect.right() - self.width())))

                zone_top = -100 
                zone_bottom = self.desktop_rect.bottom() - 280

                in_zone = zone_top <= new_pos.y() <= zone_bottom

                if in_zone and not hasattr(self, 'in_zone'):
                    self.in_zone = True
                elif not in_zone and hasattr(self, 'in_zone'):
                    self.in_zone = False

                if zone_top <= new_pos.y() <= zone_bottom:
                    if not hasattr(self, 'movie_alternate'):
                        self.movie_alternate = QMovie("resources/gif/stay.gif")

                    if not hasattr(self, 'previous_movie'):
                        self.previous_movie = self.label.movie()

                    self.label.setMovie(self.movie_alternate)
                    self.movie_alternate.start()

                    self.continuous_move_timer.stop()

                    self.in_zone = True
                else:

                    if hasattr(self, 'in_zone') and self.in_zone:

                        if hasattr(self, 'previous_movie'):
                            self.label.setMovie(self.previous_movie)
                            self.previous_movie.start()
                            delattr(self, 'previous_movie')

                        self.continuous_move_timer.start(20)
                        delattr(self, 'in_zone')

                new_pos.setX(max(self.desktop_rect.left(), min(new_pos.x(), self.desktop_rect.right() - self.width())))
                new_pos.setY(max(self.desktop_rect.top(), min(new_pos.y(), self.desktop_rect.bottom() - self.height())))
                self.move(new_pos)

                if event.modifiers() & Qt.ShiftModifier:
                    self.is_shift_pressed = True
                    
        if self.follow_cursor_action.isChecked():
            # Move the window to follow the cursor along the X-axis
            new_pos_x = event.globalX() - self.offset.x()
            new_pos_x = max(self.desktop_rect.left(), min(new_pos_x, self.desktop_rect.right() - self.width()))
            new_pos_y = event.globalY() - self.offset.y()  # Assign new_pos_y here
            new_pos_y = max(self.desktop_rect.top(), min(new_pos_y, self.desktop_rect.bottom() - self.height()))
            self.move(new_pos_x, new_pos_y)  # Keep the same Y position
        else:
            # Regular dragging behavior
            new_pos = event.globalPos() - self.offset
            new_pos.setX(max(self.desktop_rect.left(), min(new_pos.x(), self.desktop_rect.right() - self.width())))
            new_pos.setY(max(self.desktop_rect.top(), min(new_pos.y(), self.desktop_rect.bottom() - self.height())))
            self.move(new_pos)

        # Check if the Shift key is pressed
        if event.modifiers() & Qt.ShiftModifier:
            self.is_shift_pressed = True

    def show_tray_icon(self):
        # Display the icon in the System Tray
        self.tray_icon.show()
        self.clock_widget.raise_()

    def move_in_steps(self, direction, steps):
        # Move the window in steps in the specified direction
        current_pos = self.pos()

        if direction == 'left':
            new_pos_x = -self.step_size * (steps / 2)
            new_pos = current_pos + QPoint(new_pos_x, 0)
        elif direction == 'right':
            new_pos_x = self.step_size * (steps / 2)
            new_pos = current_pos + QPoint(new_pos_x, 0)
        else:
            return

        # Ensure the window stays within the desktop bounds
        new_pos.setX(max(self.desktop_rect.left(), min(new_pos.x(), self.desktop_rect.right() - self.width())))
        new_pos.setY(max(self.desktop_rect.top(), min(new_pos.y(), self.desktop_rect.bottom() - self.height())))
        self.move(new_pos)

    def continuous_move(self):
        if self.isVisible() and not self.is_dragging:
            if self.animation.state() == QPropertyAnimation.Running:
                return  # Wait for the current animation to finish before starting a new one

            if self.is_shimeji_on_taskbar():
                self.movement_counter = 0  # Reset counter if Shimeji is on the taskbar
                self.rest_timer.start(10000)  # 10 seconds rest timer
                self.restore_previous_state()  # Restore previous state when reaching taskbar
            elif self.movement_counter == 0:
                # Randomly choose the direction (left or right)
                self.direction = random.choice(['left', 'right'])

                # Randomly choose the number of steps between 5 and 20
                self.steps = random.randint(130, 160)

                # Set the appropriate movie based on the direction
                if self.direction == 'left':
                    self.start_gif_thread("resources/gif/makima_walk_left_unscreen.gif")
                elif self.direction == 'right':
                    self.start_gif_thread("resources/gif/makima_walk_right_unscreen.gif")
                else:
                    self.start_gif_thread("resources/gif/stay.gif")

                # No immediate move here, only set the direction and steps
                self.movement_counter += 1
            elif 1 <= self.movement_counter <= self.steps:
                # Continue moving in the chosen direction
                self.move_in_steps(self.direction, 1)
                self.movement_counter += 1

                # Check if reached the edge of the window
                if self.at_window_edge():
                    # Reverse direction and move back for 10 steps
                    self.direction = 'left' if self.direction == 'right' else 'right'
                    self.movement_counter = self.steps - 9  # Move back for 10 steps
            elif self.movement_counter == self.steps + 1:
                # Start the rest timer after completing the steps
                self.rest_timer.start(10000)  # 10 seconds rest timer
                self.movement_counter += 1
            elif self.movement_counter > self.steps + 1:
                # Reset the counter and choose a new direction after the rest period
                self.movement_counter = 0
            
    def rest_complete(self):
        # Stop the rest timer and reset the movement counter
        self.rest_timer.stop()
        self.movement_counter = 0
        self.continuous_move()
        # Emit stop_rest_timer signal when rest is complete
        self.stop_rest_timer.emit()

    def is_shimeji_on_taskbar(self):
        shimeji_rect = self.geometry()
        taskbar_rect = QDesktopWidget().availableGeometry()

        # Check if the Shimeji window is leaving the taskbar and the specified zone in the y-axis
        leaving_taskbar = not taskbar_rect.contains(shimeji_rect, Qt.IntersectsItemBoundingRect)
        leaving_zone = shimeji_rect.y() + shimeji_rect.height() + 30 < taskbar_rect.y()
        
        return leaving_taskbar and leaving_zone
    
    def start_gif_thread(self, gif_file):
        self.gif_thread = GifPlayerThread(self.label, gif_file)
        self.gif_thread.gif_finished.connect(self.handle_gif_finished)
        self.gif_thread.start()

    def handle_gif_finished(self):
        # Stop the rest timer and reset the movement counter
        self.rest_timer.stop()
        self.movement_counter = 0
        self.continuous_move()
        
    def at_window_edge(self):
        # Check if the window is at the left or right edge
        return self.x() <= 0 or self.x() + self.width() >= self.desktop_rect.right()
    
    def restore_previous_state(self):
        if hasattr(self, 'in_zone') and self.in_zone:
            # Switch back to the previous movie
            if hasattr(self, 'previous_movie'):
                self.label.setMovie(self.previous_movie)
                self.previous_movie.start()
                delattr(self, 'previous_movie')

            # Resume continuous movement
            self.continuous_move_timer.start(20)
            delattr(self, 'in_zone')

    def stop_movement(self):
        # Stop the continuous movement and switch to standing gif
        self.continuous_move_timer.stop()
        self.label.setMovie(self.movie_standing)
        self.movie_standing.start()
        if self.stop_movement_popup_action.isChecked() or self.stop_movement_action_tray.isChecked():
            self.resume_movement_action.setChecked(False)
            self.resume_movement_action_tray.setChecked(False)
            self.stop_movement_popup_action.setChecked(True)
            self.stop_movement_action_tray.setChecked(True)
            self.random_move_action.setEnabled(False)
            self.follow_cursor_action.setEnabled(False)
            self.random_move_action_tray.setEnabled(False)
            self.follow_cursor_action_tray.setEnabled(False)             

    def resume_movement(self):
        # Resume the continuous movement
        self.continuous_move_timer.start(20)
        gif_file = "resources/gif/makima_walk_right_unscreen.gif" if self.direction == 'right' else "resources/gif/makima_walk_left_unscreen.gif"
        self.start_gif_thread(gif_file)  
        if self.resume_movement_action.isChecked() or self.resume_movement_action_tray.isChecked():
            self.resume_movement_action.setChecked(True)
            self.resume_movement_action_tray.setChecked(True)
            self.stop_movement_popup_action.setChecked(False)
            self.stop_movement_action_tray.setChecked(False)
            self.random_move_action.setEnabled(True)
            self.follow_cursor_action.setEnabled(True)
            self.random_move_action_tray.setEnabled(True)
            self.follow_cursor_action_tray.setEnabled(True)

    def set_random_movement(self):
        # Set the window to random movement mode
        self.random_move_action.setChecked(True)
        self.follow_cursor_action.setChecked(False)
        self.random_move_action_tray.setChecked(True)
        self.follow_cursor_action_tray.setChecked(False)
        self.attraction_timer.start()  # Start the attraction animation timer for random movement
        self.resume_movement()  # Resume movement when selecting random movement
        # After changing the state, update the menu
        self.update_menu()

    def set_follow_cursor_movement(self):
        # Set the window to follow cursor mode
        self.random_move_action.setChecked(False)
        self.follow_cursor_action.setChecked(True)
        self.attraction_timer.start()  # Start the attraction animation timer for random movement
        self.stop_movement()  # Stop movement when selecting follow cursor
        # After changing the state, update the menu
        self.update_menu()  
        
    def update_menu(self):
        self.random_move_action_tray.setChecked(self.random_move_action.isChecked())
        self.follow_cursor_action_tray.setChecked(self.follow_cursor_action.isChecked())
        self.toggle_show_action_tray.setChecked(self.isVisible())
        
    def show_clock(self):
        # Show the clock widget
        self.clock_widget.setVisible(True)
        self.show_clock_action.setChecked(True)
        self.hide_clock_action.setChecked(False)
        self.update_menu()

    def hide_clock(self):
        # Hide the clock widget
        self.clock_widget.setVisible(False)
        self.show_clock_action.setChecked(False)
        self.hide_clock_action.setChecked(True)
        self.show_clock_action_tray.setChecked(False)
        self.hide_clock_action_tray.setChecked(True)
        self.update_menu()        
        
    def restore_previous_state(self):
        if hasattr(self, 'in_zone') and self.in_zone:
            # Switch back to the previous movie
            if hasattr(self, 'previous_movie'):
                self.label.setMovie(self.previous_movie)
                self.previous_movie.start()
                delattr(self, 'previous_movie')

            # Resume continuous movement
            self.continuous_move_timer.start(20)
            delattr(self, 'in_zone')

    def show_alarm_dialog(self):
        self.alarm_clock.show()
        
    def toggle_timer_window(self):
        if self.toggle_timer_action.isChecked():
            self.show_timer_window()
            self.toggle_timer_action.setText("Hide Timer")
        else:
            self.hide_timer_window()
            self.toggle_timer_action.setText("Show Timer")
        
    def show_timer_window(self):
        self.timer_window.show()
       
    def hide_timer_window(self):
        self.timer_window.hide()
        
    def toggle_clock(self):
        if self.toggle_clock_action.isChecked():
            self.show_clock()
            self.toggle_clock_action.setText("Hide Clock")
        else:
            self.hide_clock()
            self.toggle_clock_action.setText("Show Clock")

    def show_clock(self):
        self.clock_widget.show()

    def hide_clock(self):
        self.clock_widget.hide()
        
    def toggle_alarm_dialog(self):
        if self.toggle_alarm_action.isChecked():
            self.show_alarm_dialog()
            self.toggle_alarm_action.setText("Hide Alarm")
        else:
            self.hide_alarm_dialog()
            self.toggle_alarm_action.setText("Show Alarm")

    def show_alarm_dialog(self):
        self.alarm_clock.show()
        
    def hide_alarm_dialog(self):
        self.alarm_clock.hide()

    def updateCursorFollowing(self):
        if not self.follow_cursor_action.isChecked():
            return

        cursor_pos = QCursor.pos()
        current_pos = self.pos()

        # Calculate movement direction based on cursor movement
        if cursor_pos.x() > current_pos.x():
            animation_file = "resources/gif/makima_walk_right_unscreen.gif"
        else:
            animation_file = "resources/gif/makima_walk_left_unscreen.gif"
        self.prev_pos = cursor_pos


        # Calculate window center
        center_pos = QPoint(current_pos.x() + self.width() // 2, current_pos.y() + self.height() // 2)

        # Check if cursor is inside the window
        if self.underMouse():
            self.playAnimation("resources/gif/stay.gif")
            return

        # Check if the window is on the same line as the cursor on the Y-axis
        if current_pos.x() < cursor_pos.x() < current_pos.x() + self.height():
            self.playAnimation("resources/gif/stay.gif")
            return
        # Play the GIF animation cyclically, only if there is animation to play
        if animation_file:
            self.playAnimation(animation_file)

        if not self.reached_target:
            # Calculate direction and distance to the target position
            dx = cursor_pos.x() - center_pos.x()
            dy = cursor_pos.y() - center_pos.y()
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance > self.step_size:
                # Normalize the vector and multiply by the step size
                step_dx = dx / distance * self.step_size
                step_dy = dy / distance * self.step_size

                # Calculate new position only on the X-axis
                new_pos = QPoint(current_pos.x() + step_dx, current_pos.y())

                self.move(new_pos)

            else:
                self.reached_target = True

    def playAnimation(self, filename):
        if self.movie and self.movie.fileName() == filename:
            return
        self.movie = QMovie(filename)
        self.label.setMovie(self.movie)
        self.movie.start()
        
    def toggle_show_nobara_window(self):
        if self.nobara_window.isHidden():
            self.nobara_window.show()
            self.toggle_show_nobara_action_popup.setText("Hide Nobara")
            self.toggle_show_nobara_action_tray.setText("Hide Nobara")
            self.toggle_show_nobara_action_popup.setChecked(True)
            self.toggle_show_nobara_action_tray.setChecked(True)
        else:
            self.nobara_window.hide()
            self.toggle_show_nobara_action_popup.setText("Show Nobara")
            self.toggle_show_nobara_action_tray.setText("Show Nobara")
            self.toggle_show_nobara_action_tray.setChecked(False)
            self.toggle_show_nobara_action_popup.setChecked(False)

    def toggle_show_ziegfied_window(self):
        if self.ziegfied_window.isHidden():
            self.ziegfied_window.show()
            self.toggle_show_ziegfied_action_popup.setText("Hide Ziegfried")
            self.toggle_show_ziegfied_action_tray.setText("Hide Ziegfried")
            self.toggle_show_ziegfied_action_popup.setChecked(True)
            self.toggle_show_ziegfied_action_tray.setChecked(True)
        else:
            self.ziegfied_window.hide()
            self.toggle_show_ziegfied_action_popup.setText("Show Ziegfried")
            self.toggle_show_ziegfied_action_tray.setText("Show Ziegfried")
            self.toggle_show_ziegfied_action_tray.setChecked(False)
            self.toggle_show_ziegfied_action_popup.setChecked(False)  
           
if __name__ == '__main__':  
    try:       
        app = QApplication(sys.argv)
        window = MyWindow()
        initial_x = window.x() + 1600  
        initial_y = window.y() + 870   
        # Use a timer to delay the display of the icon in System Tray
        timer = QTimer()
        timer.timeout.connect(window.show_tray_icon)
        timer.start(1000)  # Delayed start after 1 second
        # Check if Shimeji is on the taskbar and adjust the initial position accordingly
        if not window.is_shimeji_on_taskbar():
            # Randomly choose the direction (left or right)
            initial_direction = random.choice(['left', 'right'])

            # Randomly choose the number of steps between 5 and 20
            initial_steps = random.randint(130, 160)

            # Ensure initial_steps is within the range of a 32-bit signed integer
            initial_steps = max(-2147483648, min(initial_steps, 2147483647))

            window.move_in_steps(initial_direction, initial_steps)

        ziegfied_window = Ziegfied(window)
        nobara_window = Nobara(window)         
        window.move(initial_x, initial_y)
        window.show()
        window.raise_()  
        app.setQuitOnLastWindowClosed(False)
        sys.exit(app.exec_())

    except Exception as e:
        print("An error occurred:", e)
