from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QPushButton, QWidget


class ClipboardCopyButton(QPushButton):

    def __init__(self, text: str, parent: QWidget|None = None):
        super().__init__(parent=parent)
        
        self._text = text
        
        self.clicked.connect(self.on_click)
        
        self.confirmation_text = 'Copied'
        self.confirmation_timeout = 1500

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.on_timer)
        
        self.restore()
    
    def on_click(self):
        data = self.data_for_clipboard()
        
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(data)
        
        self.setText(self.confirmation_text)
        self.setEnabled(False)
        
        self.timer.start(self.confirmation_timeout)

    def on_timer(self):
        self.restore()
        
    def restore(self):
        self.setText(self._text)
        self.setEnabled(True)

    def data_for_clipboard(self) -> str:
        """
        To be overwritten
        """
        pass