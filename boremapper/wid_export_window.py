from xml.etree import ElementTree as ET

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeyEvent, QGuiApplication
from PySide6.QtWidgets import QLabel, QMainWindow, QPlainTextEdit, QToolBar, QComboBox, QDoubleSpinBox, QPushButton, \
    QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QAbstractItemView, QHeaderView, QTableWidgetItem

from boremapper import const
from boremapper.bunch import Bunch
from boremapper.length_units import LengthUnits
from boremapper.utils import length_units, format_length


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
        self.tabs.table.update_from_model(self.dw.model)
        self.tabs.xml.update_from_model(self.dw.model)

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

    COLUMN_WIDTH = 200
    DISPLAY_EXTRA_DECIMALS = 10

    def __init__(self, parent: WidExportWindow):
        super().__init__(parent)
        
        self.parent_window = parent # TODO: use everywhere instead of self.parent()?

        layout = QVBoxLayout()
        self.setLayout(layout)

        toolbar = QWidget(self)
        layout.addWidget(toolbar, stretch=0)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        toolbar.setLayout(toolbar_layout)
        
        # TODO
        self.copy_positions_button = btn = QPushButton('Copy Positions to Clipboard', self)
        btn.setFixedWidth(self.COLUMN_WIDTH)
        toolbar_layout.addWidget(btn)
        
        self.table = WIDesignerBorePointsTable(self)
        self.table.set_column_width(self.COLUMN_WIDTH)
        
        layout.addWidget(self.table, stretch=100)

    def update_from_model(self, model: 'DocumentModel'):
        units = length_units(model.wid_export.length_type)
        display_decimals = units.display_decimals + self.DISPLAY_EXTRA_DECIMALS
        
        points = model.to_wid_bore_points(
            model.wid_export.length_type,
            model.wid_export.bore_origin
        )
        
        data = []
        for position, diameter in points:
            data.append((
                format_length(position, display_decimals),
                format_length(diameter, display_decimals),
            ))
            
        self.table.set_data(data)


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
        self.copy_button = btn = QPushButton(self.copy_button_text, self)
        self.copy_button.clicked.connect(self.on_copy_click)
        btn.setMinimumWidth(150)
        toolbar_layout.addWidget(btn)

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
        elements = model.to_wid_xml_bore_points(
            model.wid_export.length_type,
            model.wid_export.bore_origin
        )
        xml_blocks = []
        for element in elements:
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
        timer.start(1500)

    def on_copy_timer(self):
        self.copy_button.setText(self.copy_button_text)
        self.copy_button.setEnabled(True)
        

class WIDesignerBorePointsTable(QTableWidget):

    COLUMNS = (
        'Position',
        'Diameter',
    )

    def __init__(self, parent: QWidget|None = None):
        super().__init__(parent)
        
        self._column_width = None
        
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        header = QHeaderView(Qt.Orientation.Horizontal)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.setHorizontalHeader(header)
        
        self.verticalHeader().setVisible(False)
        
    def set_data(self, data: list):
        self.setColumnCount(len(self.COLUMNS))
        self.setRowCount(len(data))
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self._update_column_widths()

        for r, row in enumerate(data):
            for c, col_text in enumerate(self.COLUMNS):
                item = QTableWidgetItem(str(row[c]))
                item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled |
                    Qt.ItemFlag.ItemIsSelectable
                )
                self.setItem(r, c, item)

    def set_column_width(self, value: int):
        self._column_width = value
        self._update_column_widths()

    def _update_column_widths(self):
        if self._column_width is not None:
            for c, column in enumerate(self.COLUMNS):
                self.setColumnWidth(c, self._column_width)