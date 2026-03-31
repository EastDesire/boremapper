from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton

from boremapper import const, commands


class OffsetPositionsWindow(QWidget):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__(document_window)

        self.dw = document_window

        self.setWindowTitle('Offset Positions')
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setFixedSize(300, 120)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        range_max = float(self.dw.app.build_length_output(const.SPINBOX_MAX_RANGE_MM))

        self.spinbox_offset = sb = QDoubleSpinBox(self)
        sb.setRange(-range_max, range_max)
        sb.setSingleStep(self.dw.app.current_length_units().step)
        sb.setDecimals(self.dw.app.current_length_units().display_decimals)
        sb.setValue(0)
        sb.valueChanged.connect(self.on_form_change)
        sb.returnPressed.connect(self.on_form_return)

        form = QFormLayout()
        form.addRow('Offset All Positions by:', self.spinbox_offset)
        self.layout.addLayout(form)

        buttons = QHBoxLayout()
        self.layout.addLayout(buttons)

        self.button_close = QPushButton('Close', self)
        self.button_close.clicked.connect(self.on_close_click)
        buttons.addWidget(self.button_close)

        self.button_submit = QPushButton('OK', self)
        self.button_submit.setDefault(True)
        self.button_submit.clicked.connect(self.on_submit)
        buttons.addWidget(self.button_submit)

        self.update_buttons()
        self.spinbox_offset.selectAll()

    def form_value_offset(self):
        return round(self.spinbox_offset.value(), self.dw.app.current_length_units().display_decimals)

    def update_buttons(self):
        self.button_submit.setEnabled(self.is_form_valid())

    def is_form_valid(self):
        return self.form_value_offset() != 0

    def on_close_click(self):
        self.close()

    def on_form_change(self):
        self.update_buttons()

    def on_form_return(self):
        self.button_submit.click()

    def on_submit(self):
        offset = self.dw.app.parse_length_input(str(self.form_value_offset()))
        self.dw.do_command(commands.OffsetPositions(self.dw, offset))
        self.close()

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()