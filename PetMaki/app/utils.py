import ctypes

APP_NAME = "MakimaPet" 
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

# Инициализация WinAPI функций для физики окон
user32 = ctypes.windll.user32
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)