from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QTabWidget, \
    QGroupBox, QComboBox

from boremapper import const
from boremapper.bunch import Bunch
from boremapper.length_units import LengthUnits


class DocPropertiesWindow(QWidget):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__(document_window)

        self.dw = document_window

        self.length_units = self.dw.app.current_length_units()
        
        self.setWindowTitle('Document Properties')
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setFixedSize(400, 300)

        self.tabs = Bunch(
            export = ExportTab(self),
        )

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(self.tabs.export, 'Export')
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
        self.dw.model.wid_export.length_type = self.tabs.export.length_type_combobox.currentText()

        bore_origin = self.dw.app.parse_length_input(
            str(self.tabs.export.bore_origin_spinbox.value()),
            self.length_units.symbol
        )
        if bore_origin is not None:
            self.dw.model.wid_export.bore_origin = bore_origin

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()


class ExportTab(QWidget):

    def __init__(self, parent: DocPropertiesWindow):
        super().__init__(parent)

        self.parent_window = parent

        self.bore_origin_spinbox = None
        self.length_type_combobox = None

        layout = QVBoxLayout()
        layout.setSpacing(const.LAYOUT_GROUPS_SPACING)
        self.setLayout(layout)

        # Group

        range_max = float(self.parent_window.dw.app.build_length_output(const.SPINBOX_MAX_RANGE_MM, self.parent_window.length_units.symbol))

        val = float(self.parent_window.dw.app.build_length_output(
            self.parent_window.dw.model.wid_export.bore_origin,
            self.parent_window.length_units.symbol
        ))
        self.bore_origin_spinbox = sb = QDoubleSpinBox(self)
        sb.setRange(-range_max, range_max)
        sb.setSingleStep(self.parent_window.length_units.step)
        sb.setDecimals(self.parent_window.length_units.display_decimals)
        sb.setValue(val)

        self.length_type_combobox = cb = QComboBox(self)
        for symbol in LengthUnits.symbols():
            cb.addItem(symbol)
        cb.setCurrentText(self.parent_window.dw.model.wid_export.length_type)

        form = QFormLayout()
        form.addRow('Bore Origin (%s):' % self.parent_window.length_units.symbol, self.bore_origin_spinbox)
        form.addRow('WIDesigner Length Type:', self.length_type_combobox)

        group = QGroupBox(self)
        group.setTitle('WIDesigner')
        group.setLayout(form)
        layout.addWidget(group)