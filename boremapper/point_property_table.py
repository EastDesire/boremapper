from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem, QWidget

# <text>, <italic>
COLUMNS = (
    ('Property', False),
    ('Value', False),
    ('Note', True),
)

class PointPropertyTable(QTableWidget):

    def __init__(self, parent: QWidget|None = None):
        super().__init__(parent)
        
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setShowGrid(False)

        header = QHeaderView(Qt.Orientation.Horizontal)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setHorizontalHeader(header)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        
    def set_data(self, data: list):
        self.setColumnCount(len(COLUMNS))
        self.setRowCount(len(data))

        for r, row in enumerate(data):
            for c, column in enumerate(COLUMNS):
                col_text, col_italic = column
                item = QTableWidgetItem(str(row[c]))
                item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled |
                    Qt.ItemFlag.ItemIsSelectable
                )
                font: QFont = item.font()
                if col_italic:
                    font.setItalic(True)
                item.setFont(font)
                self.setItem(r, c, item)