from xml.etree import ElementTree as ET

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeyEvent, QGuiApplication
from PySide6.QtWidgets import QLabel, QMainWindow, QPlainTextEdit, QToolBar, QComboBox, QDoubleSpinBox, QPushButton, \
    QTabWidget, QWidget, QVBoxLayout, QHBoxLayout

from boremapper import const
from boremapper.bunch import Bunch
from boremapper.length_units import LengthUnits


class WidExportWindow(QMainWindow):
    
    CONTENT_MARGINS = 15

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__(document_window)

        self.dw = document_window
        
        # As long as the window is open, we work with the settings that was in place when the window has loaded
        self.length_units = self.dw.app.current_length_units()

        self.setWindowTitle('WIDesigner Export')
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowType.Window)
        self.resize(800, 600)

        self.tabs = Bunch(
            table = TableTab(self),
            xml = XmlTab(self),
        )

        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addSeparator()

        label = QLabel(self)
        label.setText('Bore Origin:')
        toolbar.addWidget(label)

        range_max = float(self.dw.app.build_length_output(const.SPINBOX_MAX_RANGE_MM, self.length_units.symbol))
        
        self.bore_origin_spinbox = sb = QDoubleSpinBox(self)
        sb.setRange(-range_max, range_max)
        sb.setSingleStep(self.length_units.step)
        sb.setDecimals(self.length_units.display_decimals)
        sb.setValue(float(self.dw.app.build_length_output(self.dw.model.wid_export.bore_origin, self.length_units.symbol)))
        toolbar.addWidget(sb)

        self.origin_units_label = lbl = QLabel(self)
        lbl.setText(self.length_units.symbol)
        toolbar.addWidget(lbl)

        toolbar.addSeparator()
        
        label = QLabel(self)
        label.setText('WIDesigner Length Type:')
        toolbar.addWidget(label)
        
        self.length_type_combobox = cb = QComboBox(self)
        for symbol in LengthUnits.symbols():
            cb.addItem(symbol)
        cb.setCurrentText(self.dw.model.wid_export.length_type)
        toolbar.addWidget(cb)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(self.tabs.table, 'Table')
        self.tab_widget.addTab(self.tabs.xml, 'XML')

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)

        main_content = QWidget(self)
        main_content.setContentsMargins(self.CONTENT_MARGINS, self.CONTENT_MARGINS, self.CONTENT_MARGINS, self.CONTENT_MARGINS)
        main_content.setLayout(layout)
        self.setCentralWidget(main_content)

        # Note: We connect the change signals after setting values to the controls, otherwise they would be emitted too early
        self.bore_origin_spinbox.valueChanged.connect(self.on_param_change)
        self.length_type_combobox.currentIndexChanged.connect(self.on_param_change)

        self.update_tabs()

    def update_tabs(self):
        self.tabs.xml.update_from_model(self.dw.model)\

    def on_param_change(self):
        self.dw.model.wid_export.length_type = self.length_type_combobox.currentText()
        
        bore_origin = self.dw.app.parse_length_input(str(self.bore_origin_spinbox.value()), self.length_units.symbol)
        if bore_origin is not None:
            self.dw.model.wid_export.bore_origin = bore_origin
            
        self.update_tabs()

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()
                
                
class TableTab(QWidget):

    def __init__(self, parent: WidExportWindow):
        super().__init__(parent)


class XmlTab(QWidget):

    def __init__(self, parent: WidExportWindow):
        super().__init__(parent)

        self._xml_snippet = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        toolbar = QWidget(self)
        layout.addWidget(toolbar, stretch=0)
        
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toolbar.setLayout(toolbar_layout)

        self.copy_button_text = 'Copy to Clipboard'
        self.copy_button = b = QPushButton(self.copy_button_text, self)
        self.copy_button.clicked.connect(self.on_copy_click)
        b.setMinimumWidth(150)
        toolbar_layout.addWidget(b)

        font = QFont()
        font.setFamilies(['Courier New', 'Courier', 'Monospace'])
        font.setPointSize(14)

        self.xml_textbox = QPlainTextEdit(self)
        self.xml_textbox.setReadOnly(True)
        self.xml_textbox.setFont(font)
        layout.addWidget(self.xml_textbox, stretch=100)

    def update_from_model(self, model: 'DocumentModel'):
        self.xml_snippet = self._build_xml_snippet(model)

    def _build_xml_snippet(self, model: 'DocumentModel') -> str:
        length_type = model.wid_export.length_type
        bore_origin = model.wid_export.bore_origin
        
        xml_blocks = []
        for element in model.to_wid_bore_points(length_type, bore_origin):
            tree = ET.ElementTree(element)
            ET.indent(tree, space='    ')
            xml_blocks.append(ET.tostring(tree.getroot(), encoding='unicode'))
        return '\n'.join(xml_blocks)
        
    @property
    def xml_snippet(self) -> str:
        return self._xml_snippet

    @xml_snippet.setter
    def xml_snippet(self, value: str):
        self._xml_snippet = value
        self.xml_textbox.setPlainText(self._xml_snippet)
        
    def on_copy_click(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self._xml_snippet)
        self.copy_button.setText('Copied')
        self.copy_button.setEnabled(False)
        
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.on_copy_timer)
        timer.start(2000)

    def on_copy_timer(self):
        self.copy_button.setText(self.copy_button_text)
        self.copy_button.setEnabled(True)