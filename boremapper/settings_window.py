from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QTabWidget, \
    QGroupBox, QCheckBox, QComboBox

from boremapper import const


class SettingsWindow(QWidget):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__()

        self.dw = document_window

        self.units_combobox = None
        self.correction_spinboxes = {}
        self.checkbox_beep_hints = None
        self.checkbox_voice_hints = None

        self.setWindowTitle('Settings')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setFixedSize(400, 500)

        self.layout = QVBoxLayout()

        self.general_tab = self.create_general_tab()

        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.general_tab, 'General')
        self.layout.addWidget(self.tabs)

        buttons = QHBoxLayout()

        self.button_cancel = QPushButton('Cancel', self)
        self.button_cancel.clicked.connect(self.on_cancel_click)
        buttons.addWidget(self.button_cancel)

        self.button_ok = QPushButton('OK', self)
        self.button_ok.setDefault(True)
        self.button_ok.clicked.connect(self.on_ok_click)
        buttons.addWidget(self.button_ok)

        self.layout.addLayout(buttons)

        self.setLayout(self.layout)

    def create_general_tab(self):
        widget = QWidget(self)
        
        layout = QVBoxLayout()
        layout.setSpacing(const.GROUPS_SPACING)

        # Group

        self.units_combobox = cb = QComboBox(self)
        for units_symbol, units_def in const.UNITS.items():
            cb.addItem(units_symbol)
        cb.setCurrentText(self.dw.app.length_units_symbol())

        form = QFormLayout()
        form.addRow('Length Units:', self.units_combobox)

        group = QGroupBox(self)
        group.setTitle('Basic')
        group.setLayout(form)
        layout.addWidget(group)

        # Group

        correction_range_min = -1000
        correction_range_max = 1000

        for p in const.BORE_PARTS:
            self.correction_spinboxes[p] = {}
            for dim in ('width', 'height'):
                val = self.dw.app.settings.load('default_corrections', p + '_groove_' + dim)
                sb = self.correction_spinboxes[p]['groove_' + dim] = QDoubleSpinBox(self)
                sb.setRange(correction_range_min, correction_range_max)
                sb.setSingleStep(self.dw.app.length_step() / 10)
                sb.setValue(float(self.dw.app.build_length_output(val)))
                sb.setDecimals(self.dw.app.length_display_decimals())

        form = QFormLayout()
        for dim in ('width', 'height'):
            for p in const.BORE_PARTS:
                form.addRow(
                    p.capitalize() + ' ' + dim.capitalize() + ':',
                    self.correction_spinboxes[p]['groove_' + dim]
                )

        group = QGroupBox(self)
        group.setTitle('Default Groove Corrections')
        group.setLayout(form)
        layout.addWidget(group)

        # Group

        self.checkbox_beep_hints = QCheckBox('Beep', self)
        self.checkbox_beep_hints.setChecked(self.dw.app.settings.load('audio', 'beep_hints'))
        self.checkbox_voice_hints = QCheckBox('Voice Hints', self)
        self.checkbox_voice_hints.setChecked(self.dw.app.settings.load('audio', 'voice_hints'))

        form = QFormLayout()
        form.addRow(self.checkbox_beep_hints)
        form.addRow(self.checkbox_voice_hints)

        group = QGroupBox(self)
        group.setTitle('Audio')
        group.setLayout(form)
        layout.addWidget(group)

        widget.setLayout(layout)

        return widget

    def on_cancel_click(self):
        self.close()

    def on_ok_click(self):
        self.on_submit()

    def on_submit(self):
        self.apply()
        self.close()

    def apply(self):
        settings = {
            'general': {
                'length_units': self.units_combobox.currentText(),
            },
            'default_corrections': {},
            'audio': {
                'beep_hints': self.checkbox_beep_hints.isChecked(),
                'voice_hints': self.checkbox_voice_hints.isChecked(),
            },
        }

        for p in const.BORE_PARTS:
            for dim in ('width', 'height'):
                # TODO: convert from units to mm
                settings['default_corrections'][p + '_groove_' + dim] = self.correction_spinboxes[p]['groove_' + dim].value()

        self.dw.app.settings.write(settings)
        # TODO: test
        self.dw.app.update_all_windows()

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()