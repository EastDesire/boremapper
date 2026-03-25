from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton

from boremapper import commands, const


class InsertPositionWindow(QWidget):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__(document_window)

        self.dw = document_window

        self.setWindowTitle('Insert Position')
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setFixedSize(220, 120)

        self.layout = QVBoxLayout()

        self.spinbox_at = QDoubleSpinBox(self)
        self.spinbox_at.setRange(const.INSERT_POSITIONS_RANGE_MIN, const.INSERT_POSITIONS_RANGE_MAX)
        self.spinbox_at.setSingleStep(self.dw.app.length_step())
        self.spinbox_at.setValue(0)
        self.spinbox_at.setDecimals(self.dw.app.length_display_decimals())
        self.spinbox_at.returnPressed.connect(self.on_submit)

        form = QFormLayout()
        form.addRow('At:', self.spinbox_at)
        self.layout.addLayout(form)

        buttons = QHBoxLayout()

        self.button_close = QPushButton('Close', self)
        self.button_close.clicked.connect(self.on_close_click)
        buttons.addWidget(self.button_close)

        self.button_submit = QPushButton('Insert', self)
        self.button_submit.setDefault(True)
        self.button_submit.clicked.connect(self.on_submit)
        buttons.addWidget(self.button_submit)

        self.layout.addLayout(buttons)

        self.setLayout(self.layout)

        self.spinbox_at.selectAll()

    def on_close_click(self):
        self.close()

    def on_submit(self):
        # TODO: do this only if the position doesn't yet exist
        self.dw.do_command(commands.InsertPositions(self.dw, [self.spinbox_at.value()]))

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()