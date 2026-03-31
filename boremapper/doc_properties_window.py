from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QTabWidget, \
    QGroupBox, QComboBox

from boremapper import const
from boremapper.length_units import LengthUnits


class DocPropertiesWindow(QWidget):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__(document_window)

        self.dw = document_window

        self.length_units = self.dw.app.current_length_units()
        
        self.bore_origin_spinbox = None
        self.length_type_combobox = None

        self.setWindowTitle('Document Properties')
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setFixedSize(400, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.export_tab = self.create_export_tab()

        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.export_tab, 'Export')
        self.layout.addWidget(self.tabs)

        buttons = QHBoxLayout()
        self.layout.addLayout(buttons)

        self.button_cancel = QPushButton('Cancel', self)
        self.button_cancel.clicked.connect(self.on_cancel_click)
        buttons.addWidget(self.button_cancel)

        self.button_ok = QPushButton('OK', self)
        self.button_ok.setDefault(True)
        self.button_ok.clicked.connect(self.on_ok_click)
        buttons.addWidget(self.button_ok)

    def create_export_tab(self):
        widget = QWidget(self)
        
        layout = QVBoxLayout()
        layout.setSpacing(const.LAYOUT_GROUPS_SPACING)
        widget.setLayout(layout)

        # Group

        range_max = float(self.dw.app.build_length_output(const.SPINBOX_MAX_RANGE_MM, self.length_units.symbol))

        self.bore_origin_spinbox = sb = QDoubleSpinBox(self)
        sb.setRange(-range_max, range_max)
        sb.setSingleStep(self.length_units.step)
        sb.setDecimals(self.length_units.display_decimals)
        sb.setValue(float(self.dw.app.build_length_output(self.dw.model.wid_export.bore_origin, self.length_units.symbol)))

        self.length_type_combobox = cb = QComboBox(self)
        for symbol in LengthUnits.symbols():
            cb.addItem(symbol)
        cb.setCurrentText(self.dw.model.wid_export.length_type)

        form = QFormLayout()
        form.addRow('Bore Origin (%s):' % self.length_units.symbol, self.bore_origin_spinbox)
        form.addRow('WIDesigner Length Type:', self.length_type_combobox)

        group = QGroupBox(self)
        group.setTitle('WIDesigner')
        group.setLayout(form)
        layout.addWidget(group)

        return widget

    def on_cancel_click(self):
        self.close()

    def on_ok_click(self):
        self.on_submit()

    def on_submit(self):
        self.apply()
        self.close()

    def apply(self):
        self.dw.model.wid_export.length_type = self.length_type_combobox.currentText()

        bore_origin = self.dw.app.parse_length_input(str(self.bore_origin_spinbox.value()), self.length_units.symbol)
        if bore_origin is not None:
            self.dw.model.wid_export.bore_origin = bore_origin

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()