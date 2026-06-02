import sys
from PyQt6.QtWidgets import QApplication
from app.pet.chibi_window import ChibiPet

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = ChibiPet()
    sys.exit(app.exec())