from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QBrush
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QAbstractItemView


class PointMessageList(QListWidget):

    def __init__(self, parent: QWidget|None = None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        
    def set_data(self, data: list):
        self.clear()
        for i, text in enumerate(data):
            item = QListWidgetItem(text)
            item.setIcon(QIcon.fromTheme('dialog-warning'))
            item.setForeground(QBrush(Qt.GlobalColor.red))
            self.addItem(item)