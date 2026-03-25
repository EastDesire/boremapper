from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QDoubleSpinBox, QFormLayout, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from boremapper import commands, const


class InsertPositionsRangeWindow(QWidget):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__(document_window)

        self.dw = document_window

        self.setWindowTitle('Insert Positions Range')
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setFixedSize(220, 180)

        self.layout = QVBoxLayout()

        range_max = float(self.dw.app.build_length_output(const.SPINBOX_MAX_RANGE_MM))

        self.spinbox_start = sb = QDoubleSpinBox(self)
        sb.setRange(-range_max, range_max)
        sb.setSingleStep(self.dw.app.length_step() * 10)
        sb.setDecimals(self.dw.app.length_display_decimals())
        sb.setValue(float(self.dw.app.build_length_output(0))) # TODO: save in settings
        sb.returnPressed.connect(self.on_submit)

        self.spinbox_end = sb = QDoubleSpinBox(self)
        sb.setRange(-range_max, range_max)
        sb.setSingleStep(self.dw.app.length_step() * 10)
        sb.setDecimals(self.dw.app.length_display_decimals())
        sb.setValue(float(self.dw.app.build_length_output(500))) # TODO: save in settings
        sb.returnPressed.connect(self.on_submit)

        self.spinbox_step = sb = QDoubleSpinBox(self)
        sb.setRange(-range_max, range_max)
        sb.setSingleStep(self.dw.app.length_step())
        sb.setDecimals(self.dw.app.length_display_decimals())
        sb.setValue(float(self.dw.app.build_length_output(20))) # TODO: save in settings
        sb.returnPressed.connect(self.on_submit)

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
        positions = self.dw.app.lengths_range(
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
