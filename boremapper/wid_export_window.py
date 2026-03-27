from xml.etree import ElementTree as ET

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeyEvent, QGuiApplication
from PySide6.QtWidgets import QLabel, QMainWindow, QPlainTextEdit, QToolBar, QComboBox, QDoubleSpinBox, QPushButton

from boremapper import const
from boremapper.length_units import LengthUnits


class WidExportWindow(QMainWindow):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__(document_window)

        self.dw = document_window
        
        self.xml_snippet = None

        self.setWindowTitle('WIDesigner Export')
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowType.Window)
        self.resize(800, 600)

        font = QFont()
        font.setFamilies(['Courier New', 'Courier', 'Monospace'])
        font.setPointSize(14)

        self.xml_textbox = QPlainTextEdit(self)
        self.xml_textbox.setReadOnly(True)
        self.xml_textbox.setFont(font)

        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addSeparator()

        label = QLabel(self)
        label.setText('Bore Origin:')
        toolbar.addWidget(label)

        range_max = float(self.dw.app.build_length_output(const.SPINBOX_MAX_RANGE_MM))
        
        self.origin_spinbox = sb = QDoubleSpinBox(self)
        sb.setRange(-range_max, range_max)
        sb.setSingleStep(self.dw.app.current_length_units().step)
        sb.setDecimals(self.dw.app.current_length_units().display_decimals)
        toolbar.addWidget(sb)

        self.origin_units_label = label = QLabel(self)
        toolbar.addWidget(label)

        toolbar.addSeparator()
        
        label = QLabel(self)
        label.setText('WIDesigner Length Type:')
        toolbar.addWidget(label)
        
        self.length_type_combobox = cb = QComboBox(self)
        for symbol in LengthUnits.symbols():
            cb.addItem(symbol)
        toolbar.addWidget(cb)

        toolbar.addSeparator()

        self.copy_button = b = QPushButton('Copy to Clipboard', self)
        b.setMinimumWidth(150)
        toolbar.addWidget(b)

        self.setCentralWidget(self.xml_textbox)
        self.update_all()
        
        # Note: We connect the change signals after setting values to the controls, otherwise they would be emitted too early
        self.origin_spinbox.valueChanged.connect(self.on_param_change)
        self.length_type_combobox.currentIndexChanged.connect(self.on_param_change)
        self.copy_button.clicked.connect(self.on_copy_click)

    def update_all(self):
        self.origin_spinbox.setValue(float(self.dw.app.build_length_output(self.dw.model.wid_export.bore_origin)))
        self.origin_units_label.setText(self.dw.app.current_length_units().symbol)
        self.length_type_combobox.setCurrentText(self.dw.model.wid_export.length_type)
        self.update_xml_snippet()

    def update_xml_snippet(self):
        self.xml_snippet = self.build_xml_snippet()
        self.xml_textbox.setPlainText(self.xml_snippet)

    def build_xml_snippet(self):
        length_type = self.dw.model.wid_export.length_type
        bore_origin = self.dw.model.wid_export.bore_origin
        
        xml_blocks = []
        for element in self.dw.model.to_wid_bore_points(length_type, bore_origin):
            tree = ET.ElementTree(element)
            ET.indent(tree, space='    ')
            xml_blocks.append(ET.tostring(tree.getroot(), encoding='unicode'))
        return '\n'.join(xml_blocks)

    def on_param_change(self):
        self.dw.model.wid_export.length_type = self.length_type_combobox.currentText()
        
        bore_origin = self.dw.app.parse_length_input(str(self.origin_spinbox.value()))
        if bore_origin is not None:
            self.dw.model.wid_export.bore_origin = bore_origin
            
        self.update_xml_snippet()

    def on_copy_click(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.xml_snippet)
        self.copy_button.setText('Copied')
        self.copy_button.setEnabled(False)
        
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.on_copy_timer)
        timer.start(1500)

    def on_copy_timer(self):
        self.copy_button.setText('Copy to Clipboard') # TODO
        self.copy_button.setEnabled(True)

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()