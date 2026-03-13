from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QDoubleSpinBox, QFormLayout, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from boremapper import commands, const
from boremapper.utils import lengths_range


class InsertPositionsRangeWindow(QWidget):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__(document_window)

        self.dw = document_window

        self.setWindowTitle('Insert Positions Range')
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setFixedSize(220, 180)

        self.layout = QVBoxLayout()

        self.spinbox_start = QDoubleSpinBox(self)
        self.spinbox_start.setRange(const.INSERT_POSITIONS_RANGE_MIN, const.INSERT_POSITIONS_RANGE_MAX)
        self.spinbox_start.setSingleStep(10)
        self.spinbox_start.setValue(0) # TODO
        self.spinbox_start.setDecimals(const.LENGTH_DISPLAY_DECIMALS)
        self.spinbox_start.returnPressed.connect(self.on_submit)

        self.spinbox_end = QDoubleSpinBox(self)
        self.spinbox_end.setRange(const.INSERT_POSITIONS_RANGE_MIN, const.INSERT_POSITIONS_RANGE_MAX)
        self.spinbox_end.setSingleStep(10)
        self.spinbox_end.setValue(500) # TODO
        self.spinbox_end.setDecimals(const.LENGTH_DISPLAY_DECIMALS)
        self.spinbox_end.returnPressed.connect(self.on_submit)

        self.spinbox_step = QDoubleSpinBox(self)
        self.spinbox_step.setRange(const.INSERT_POSITIONS_RANGE_MIN, const.INSERT_POSITIONS_RANGE_MAX)
        self.spinbox_step.setSingleStep(1)
        self.spinbox_step.setValue(10) # TODO
        self.spinbox_step.setDecimals(const.LENGTH_DISPLAY_DECIMALS)
        self.spinbox_step.returnPressed.connect(self.on_submit)

        form = QFormLayout()
        form.addRow('Start:', self.spinbox_start)
        form.addRow('End:', self.spinbox_end)
        form.addRow('Step:', self.spinbox_step)
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

    def on_close_click(self):
        self.close()

    def on_submit(self):
        positions = lengths_range(
            self.spinbox_start.value(),
            self.spinbox_end.value(),
            self.spinbox_step.value()
        )
        # TODO: do this only if there is any position that doesn't yet exist
        self.dw.do_command(commands.InsertPositions(self.dw, positions))
        self.close()

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()
