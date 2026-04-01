from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QTabWidget, \
    QGroupBox, QCheckBox, QComboBox

from boremapper import const
from boremapper.bunch import Bunch
from boremapper.length_units import LengthUnits


class SettingsWindow(QWidget):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__()

        self.dw = document_window

        self.setWindowTitle('Settings')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setFixedSize(400, 250)

        self.tabs = Bunch(
            general = GeneralTab(self),
            audio = AudioTab(self),
        )
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(self.tabs.general, 'General')
        self.tab_widget.addTab(self.tabs.audio, 'Audio')
        self.layout.addWidget(self.tab_widget)

        buttons = QHBoxLayout()
        self.layout.addLayout(buttons)

        self.button_cancel = QPushButton('Cancel', self)
        self.button_cancel.clicked.connect(self.on_cancel_click)
        buttons.addWidget(self.button_cancel)

        self.button_ok = QPushButton('OK', self)
        self.button_ok.setDefault(True)
        self.button_ok.clicked.connect(self.on_ok_click)
        buttons.addWidget(self.button_ok)

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
                'length_units': self.tabs.general.length_units_combobox.currentText(),
            },
            'audio': {
                'beep_hints': self.tabs.audio.beep_hints_checkbox.isChecked(),
                'voice_hints': self.tabs.audio.voice_hints_checkbox.isChecked(),
            },
        }
        self.dw.app.settings.write(settings)

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()


class GeneralTab(QWidget):

    def __init__(self, parent: SettingsWindow):
        super().__init__(parent)
        
        self.parent_window = parent

        self.length_units_combobox = None

        layout = QVBoxLayout()
        layout.setSpacing(const.LAYOUT_GROUPS_SPACING)
        self.setLayout(layout)

        # Group

        self.length_units_combobox = cb = QComboBox(self)
        for symbol in LengthUnits.symbols():
            cb.addItem(symbol)
        cb.setCurrentText(self.parent_window.dw.app.current_length_units().symbol)

        form = QFormLayout()
        form.addRow('Length Units:', self.length_units_combobox)

        group = QGroupBox(self)
        group.setTitle('Units')
        group.setLayout(form)
        layout.addWidget(group)


class AudioTab(QWidget):

    def __init__(self, parent: SettingsWindow):
        super().__init__(parent)

        self.parent_window = parent

        self.beep_hints_checkbox = None
        self.voice_hints_checkbox = None

        layout = QVBoxLayout()
        layout.setSpacing(const.LAYOUT_GROUPS_SPACING)
        self.setLayout(layout)

        # Group

        self.beep_hints_checkbox = QCheckBox('Beeps', self)
        self.beep_hints_checkbox.setChecked(self.parent_window.dw.app.settings.load('audio', 'beep_hints'))
        self.voice_hints_checkbox = QCheckBox('Voice Hints', self)
        self.voice_hints_checkbox.setChecked(self.parent_window.dw.app.settings.load('audio', 'voice_hints'))

        form = QFormLayout()
        form.addRow(self.beep_hints_checkbox)
        form.addRow(self.voice_hints_checkbox)

        group = QGroupBox(self)
        group.setTitle('Hints')
        group.setLayout(form)
        layout.addWidget(group)