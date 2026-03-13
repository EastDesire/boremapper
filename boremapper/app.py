import sys
from xml.etree import ElementTree as ET

import pyttsx3
from PySide6.QtCore import QByteArray, QUrl, QLocale
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

import const
from boremapper import exceptions
from boremapper.document_window import DocumentWindow
from boremapper.models.document_model import DocumentModel
from boremapper.models.settings_model import SettingsModel
from boremapper.utils import format_length


class App(QApplication):

    def __init__(self):
        super().__init__(sys.argv)

        self.settings = None
        self.sounds = None
        self.document_windows = []

        # This is to set floating point symbol to '.' in QLineEdit validators etc.
        QLocale.setDefault(QLocale.c())

        self.setApplicationName(const.APP_NAME)
        self.setApplicationVersion(const.APP_VERSION)
        self.setQuitOnLastWindowClosed(True)

        self.init_settings()
        self.init_sounds()
        self.init_speech()

        #self.new_document()
        self.open_document(const.APP_DIR + '/sample-flute.xml')

    def init_settings(self):
        self.settings = SettingsModel(self, {
            'document_window': {
                'geometry': (QByteArray, None),
            },
            'default_corrections': {
                'bottom_groove_width': (float, 0),
                'bottom_groove_height': (float, 0),
                'top_groove_width': (float, 0),
                'top_groove_height': (float, 0),
            },
            'audio': {
                'beep_hints': (bool, False),
                'voice_hints': (bool, False),
            },
        })

    def create_document_window(self, model: 'DocumentModel') -> 'DocumentWindow':
        dw = DocumentWindow(self, model)

        self.document_windows.append(dw)
        dw.destroyed.connect(lambda: self.on_document_window_destroyed(dw))

        dw.show()
        return dw

    def on_document_window_destroyed(self, window: 'DocumentWindow'):
        self.document_windows.remove(window)

    def new_document(self, show_init: bool = False):
        model = DocumentModel.from_defaults(self)
        dw = self.create_document_window(model)
        if show_init:
            dw.show_insert_positions_range_window()

    def open_document(self, file: str):
        if self.bring_document_into_view(file):
            return # Document was already open and we brought it into view

        try:
            model = DocumentModel.from_file(self, file)

            if len(self.document_windows) == 1 and self.document_windows[0].is_blank():
                self.document_windows[0].close() # There's no need to keep the document window if it's blank

            self.create_document_window(model)

        except OSError:
            self.error_reading_file(file)
            return
        except (ET.ParseError, exceptions.XmlException):
            self.error_invalid_file_data()
            return

    def open_document_with_dialog(self):
        dialog = self.create_open_document_dialog()
        dialog.exec()

    def create_open_document_dialog(self):
        dialog = QFileDialog(None)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setNameFilter('XML files (*.xml)')
        dialog.fileSelected.connect(self.on_document_open_dialog_file_selected)
        return dialog

    def bring_document_into_view(self, file):
        """
        # If the document is opened in any window, bring it into view.
        """
        for dw in self.document_windows:
            if dw.file == file:
                dw.bring_into_view()
                return True
        return False

    def on_document_open_dialog_file_selected(self, file):
        if file:
            self.open_document(file)

    def init_sounds(self):
        self.sounds = {
            'entry_beep': QSoundEffect(source=QUrl.fromLocalFile(const.APP_DIR + '/resources/beep3.wav')),
        }

    def init_speech(self):
        # Initialize the speech engine, so that the speech starts promptly when first used
        pyttsx3.init()

    def play_sound(self, name):
        self.sounds[name].play()

    def try_beep(self):
        if self.settings.load('audio', 'beep_hints'):
            self.play_sound('entry_beep')

    def say(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def try_say(self, text):
        if self.settings.load('audio', 'voice_hints'):
            self.say(text)

    def show_error(self, text):
        msg = QMessageBox(None)
        msg.setWindowTitle('Error')
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.exec()

    def error_reading_file(self, file):
        self.show_error('Could not read file: %s' % file)

    def error_writing_file(self, file):
        self.show_error('Could not write file: %s' % file)

    def error_invalid_file_data(self):
        self.show_error('Invalid file data')

    def msg_incomplete_data_for_export(self, incomplete_positions: list):
        max_items = 3
        show_positions = [format_length(p) for p in incomplete_positions[:max_items]]
        if len(incomplete_positions) > max_items:
            show_positions.append('etc.')

        text = (
            'Will omit position ' + (', '.join(show_positions)) + ' because of missing diameter.\n\n' +
            'Export anyway?'
        )

        msg = QMessageBox(None)
        msg.setWindowTitle('Incomplete Data')
        msg.setText(text)
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        msg.setIcon(QMessageBox.Icon.Critical)
        reply = msg.exec()
        
        return reply == QMessageBox.StandardButton.Yes