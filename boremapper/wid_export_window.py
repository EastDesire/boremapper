from xml.etree import ElementTree as ET

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtWidgets import QLabel, QMainWindow, QPlainTextEdit, QToolBar

from boremapper.utils import format_length


class WidExportWindow(QMainWindow):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__(document_window)

        self.dw = document_window

        self.setWindowTitle('WIDesigner Export')
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowType.Window)
        self.resize(800, 600)

        font = QFont()
        font.setFamilies(['Courier New', 'Courier', 'Monospace'])
        font.setPointSize(14)

        self.xmlTextbox = QPlainTextEdit(self)
        self.xmlTextbox.setReadOnly(True)
        self.xmlTextbox.setFont(font)
        self.xmlTextbox.setPlainText(self.build_xml_snippet())

        toolbar = QToolBar(self)
        self.addToolBar(toolbar)

        label = QLabel(self)
        label.setText('Bore Origin: %s' % format_length(self.dw.model.wid_export.bore_origin))
        toolbar.addWidget(label)

        self.setCentralWidget(self.xmlTextbox)

    def build_xml_snippet(self):
        xml_blocks = []
        for element in self.dw.model.to_wid_bore_points():
            tree = ET.ElementTree(element)
            ET.indent(tree, space='    ')
            xml_blocks.append(ET.tostring(tree.getroot(), encoding='unicode'))
        return '\n'.join(xml_blocks)

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()