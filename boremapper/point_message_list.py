from PySide6.QtGui import QIcon, QBrush, QPalette
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QAbstractItemView

from boremapper.utils import text_color_to_red


class PointMessageList(QListWidget):

    def __init__(self, parent: QWidget|None = None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        
    def set_data(self, data: list):
        self.clear()
        red_foreground_brush = QBrush(text_color_to_red(QPalette().color(QPalette.ColorRole.Text)))
        for i, text in enumerate(data):
            item = QListWidgetItem(text)
            item.setIcon(QIcon.fromTheme('dialog-warning'))
            item.setForeground(red_foreground_brush)
            self.addItem(item)