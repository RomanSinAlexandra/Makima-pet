from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPainter

class PetLabel(QLabel):
    """Кастомный виджет для анимации персонажа с поддержкой разворота"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.flipped = False

    def set_flipped(self, flipped):
        if self.flipped != flipped:
            self.flipped = flipped
            self.update()

    def paintEvent(self, event):
        movie = self.movie()
        if movie and movie.currentPixmap():
            painter = QPainter(self)
            if self.flipped:
                painter.translate(self.width(), 0)
                painter.scale(-1, 1)
            painter.drawPixmap(0, 0, movie.currentPixmap())
        else:
            super().paintEvent(event)