from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QWidget


class PixmapLabel(QLabel):
    
    def __init__(self, pixmap: QPixmap, parent: QWidget|None = None):
        super().__init__(parent)
        self._pixmap = pixmap
        
    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        self.update_pixmap()

    def update_pixmap(self):
        self.size()
        self.setPixmap(self._pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))