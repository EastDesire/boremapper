from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QDoubleSpinBox, QFormLayout, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from boremapper import const
from boremapper.utils import lengths_range, coalesce


class InsertPositionsRangeWindow(QWidget):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__(document_window)

        self.dw = document_window

        self.setWindowTitle('Insert Positions Range')
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setFixedSize(300, 180)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        range_max = float(self.dw.app.build_length_output(const.SPINBOX_MAX_RANGE_MM))
        settings_group = 'insert_positions_range_feature'
        settings = {
            'start': self.dw.app.settings.load(settings_group, 'start'),
            'end': self.dw.app.settings.load(settings_group, 'end'),
            'step': self.dw.app.settings.load(settings_group, 'step'),
        }
        
        self.spinbox_start = sb = QDoubleSpinBox(self)
        sb.setRange(-range_max, range_max)
        sb.setSingleStep(self.dw.app.current_length_units().step * 10)
        sb.setDecimals(self.dw.app.current_length_units().display_decimals)
        sb.setValue(float(self.dw.app.build_length_output(coalesce(settings['start'], 0))))
        sb.valueChanged.connect(self.on_form_change)
        sb.returnPressed.connect(self.on_form_return)

        self.spinbox_end = sb = QDoubleSpinBox(self)
        sb.setRange(-range_max, range_max)
        sb.setSingleStep(self.dw.app.current_length_units().step * 10)
        sb.setDecimals(self.dw.app.current_length_units().display_decimals)
        sb.setValue(float(self.dw.app.build_length_output(coalesce(settings['end'], 0))))
        sb.valueChanged.connect(self.on_form_change)
        sb.returnPressed.connect(self.on_form_return)

        self.spinbox_step = sb = QDoubleSpinBox(self)
        sb.setRange(-range_max, range_max)
        sb.setSingleStep(self.dw.app.current_length_units().step)
        sb.setDecimals(self.dw.app.current_length_units().display_decimals)
        sb.setValue(float(self.dw.app.build_length_output(coalesce(settings['step'], 0))))
        sb.valueChanged.connect(self.on_form_change)
        sb.returnPressed.connect(self.on_form_return)

        form = QFormLayout()
        form.addRow('Start:', self.spinbox_start)
        form.addRow('End:', self.spinbox_end)
        form.addRow('Step:', self.spinbox_step)
        self.layout.addLayout(form)

        buttons = QHBoxLayout()
        self.layout.addLayout(buttons)

        self.button_close = QPushButton('Close', self)
        self.button_close.clicked.connect(self.on_close_click)
        buttons.addWidget(self.button_close)

        self.button_submit = QPushButton('Insert', self)
        self.button_submit.setDefault(True)
        self.button_submit.clicked.connect(self.on_submit)
        buttons.addWidget(self.button_submit)

        self.update_buttons()

    def form_value_start(self):
        return round(self.spinbox_start.value(), self.dw.app.current_length_units().display_decimals)

    def form_value_end(self):
        return round(self.spinbox_end.value(), self.dw.app.current_length_units().display_decimals)

    def form_value_step(self):
        return round(self.spinbox_step.value(), self.dw.app.current_length_units().display_decimals)
    
    def update_buttons(self):
        self.button_submit.setEnabled(self.is_form_valid())
        
    def is_form_valid(self):
        return (
            (self.form_value_start() <= self.form_value_end() and self.form_value_step() > 0) or
            (self.form_value_start() > self.form_value_end() and self.form_value_step() < 0)
        )

    def on_close_click(self):
        self.close()
    
    def on_form_change(self):
        self.update_buttons()

    def on_form_return(self):
        self.button_submit.click()

    def on_submit(self):
        start = self.form_value_start()
        end = self.form_value_end()
        step = self.form_value_step()
        
        positions = lengths_range(start, end, step, self.dw.app.current_length_units().display_decimals)
        
        if len(positions) > const.MAX_POSITIONS_TO_INSERT:
            self.dw.app.show_error('This range and step would create too many positions')
            return
            
        self.dw.try_insert_positions_command(positions)

        self.dw.app.settings.write({
            'insert_positions_range_feature': {
                'start': self.dw.app.parse_length_input(str(start)),
                'end': self.dw.app.parse_length_input(str(end)),
                'step': self.dw.app.parse_length_input(str(step)),
            },
        })
        
        self.close()

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()
