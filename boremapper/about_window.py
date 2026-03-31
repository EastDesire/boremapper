from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

from boremapper import const
from boremapper.pixmap_label import PixmapLabel


class AboutWindow(QWidget):

    def __init__(self, document_window: 'DocumentWindow'):
        super().__init__(document_window)

        self.dw = document_window

        self.setWindowTitle('About')
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setFixedSize(320, 560)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        pixmap = QPixmap(const.RESOURCES_DIR + '/app-icon.png')
        app_icon = PixmapLabel(pixmap, self)
        app_icon.setMaximumHeight(self.width())
        self.layout.addWidget(app_icon, stretch=100)
        
        app_name = QLabel(self)
        app_name.setText(const.APP_NAME)
        app_name.setStyleSheet('font-weight: bold')
        self.layout.addWidget(app_name, stretch=0)

        app_version = QLabel(self)
        app_version.setText('Version %s' % const.APP_VERSION)
        self.layout.addWidget(app_version, stretch=0)

        app_author = QLabel(self)
        app_author.setText('Author: %s <%s>' % (const.APP_AUTHOR, const.APP_AUTHOR_EMAIL))
        self.layout.addWidget(app_author, stretch=0)

        app_url = QLabel(self)
        app_url.setText('<a href="%s">%s</a>' % (const.APP_REPO_URL, const.APP_REPO_URL))
        app_url.setOpenExternalLinks(True)
        self.layout.addWidget(app_url, stretch=0)

        app_description = QLabel(self)
        app_description.setText(const.APP_DESCRIPTION)
        app_description.setWordWrap(True)
        self.layout.addWidget(app_description, stretch=0)

        self.layout.addStretch()

        buttons = QHBoxLayout()
        self.layout.addLayout(buttons, stretch=0)

        self.button_close = QPushButton('Close', self)
        self.button_close.clicked.connect(self.on_close_click)
        buttons.addWidget(self.button_close)

    def on_close_click(self):
        self.close()

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        match event.key():
            case Qt.Key.Key_Escape:
                self.close()