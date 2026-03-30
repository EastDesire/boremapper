import threading
from pathlib import Path
from xml.etree import ElementTree as ET

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence, QUndoCommand, QUndoStack
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QMainWindow, QMenu, QMenuBar, QMessageBox, \
    QStatusBar, QVBoxLayout, QWidget

from boremapper import commands, const
from boremapper.bore_table_view import BoreTableView
from boremapper.cutter_detail_widget import CutterDetailWidget
from boremapper.doc_properties_window import DocPropertiesWindow
from boremapper.groove_detail_widget import GrooveDetailWidget
from boremapper.insert_position_window import InsertPositionWindow
from boremapper.insert_positions_range_window import InsertPositionsRangeWindow
from boremapper.joined_detail_widget import JoinedDetailWidget
from boremapper.models.bore_model import BorePointModel
from boremapper.models.bore_table_model import BoreTableModel
from boremapper.models.document_model import DocumentModel
from boremapper.offset_positions_window import OffsetPositionsWindow
from boremapper.profile_detail_widget import ProfileDetailWidget
from boremapper.settings_window import SettingsWindow
from boremapper.utils import format_position_for_speech, center_window
from boremapper.wid_export_window import WidExportWindow


class DocumentWindow(QMainWindow):

    def __init__(self, app: 'App', model: 'DocumentModel'):
        super().__init__()

        self.app = app
        self.model = model
        self.model.setParent(self)
        self.table_model = None
        
        self.is_touched = False

        self.layout = None
        self.content_widget = None
        self.table_view = None
        self.detail_panel = None
        self.detail_widgets = {}
        
        self.undo_stack = None

        self.settings_window = None
        self.doc_properties_window = None
        self.insert_position_window = None
        self.insert_positions_range_window = None
        self.offset_positions_window = None
        self.wid_export_window = None

        self.actions = {}
        self.status_bar_units = None

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self.init_models()
        self.init_undo_stack()
        self.init_menu()
        self.init_content()
        self.init_status_bar()
        
        self.restore_gui()
        self.update_all()
        
    def init_models(self):
        self.model.file_changed.connect(self.on_file_change)
        self.model.bore.points.point_changed.connect(self.on_point_data_change)
        self.model.bore.points.layout_changed.connect(self.on_points_layout_change)
        self.model.wid_export.changed.connect(self.on_wid_export_change)
        
        self.table_model = BoreTableModel(self.model, self.app)

    def init_undo_stack(self):
        # Note that the parent should be specified, or the undo_stack might be deleted too soon during exit
        self.undo_stack = QUndoStack(self)
        self.undo_stack.cleanChanged.connect(self.on_clean_state_change)

    def init_menu(self):
        menu_bar = QMenuBar(self)

        menu = QMenu('&File', self)
        menu_bar.addMenu(menu)

        a = self.actions['file_new'] = QAction('New', self)
        a.setShortcut(QKeySequence.StandardKey.New)
        a.triggered.connect(self.on_action_file_new_trigger)
        menu.addAction(a)

        a = self.actions['file_open'] = QAction('Open...', self)
        a.setShortcut(QKeySequence.StandardKey.Open)
        a.triggered.connect(self.on_action_file_open_trigger)
        menu.addAction(a)

        a = self.actions['file_save'] = QAction('Save', self)
        a.setShortcut(QKeySequence.StandardKey.Save)
        a.triggered.connect(self.on_action_file_save_trigger)
        menu.addAction(a)

        a = self.actions['file_save_as'] = QAction('Save as...', self)
        a.setShortcut(QKeySequence.StandardKey.SaveAs)
        a.triggered.connect(self.on_action_file_save_as_trigger)
        menu.addAction(a)

        a = self.actions['file_close'] = QAction('Close', self)
        a.setShortcut(QKeySequence.StandardKey.Close)
        a.triggered.connect(self.on_action_file_close_trigger)
        menu.addAction(a)

        menu.addSeparator()

        a = self.actions['doc_properties'] = QAction('Document Properties...', self)
        a.triggered.connect(self.on_action_doc_properties_trigger)
        menu.addAction(a)

        menu.addSeparator()

        a = self.actions['settings'] = QAction('Settings...', self)
        a.triggered.connect(self.on_action_settings_trigger)
        menu.addAction(a)

        menu = QMenu('&Edit', self)
        menu_bar.addMenu(menu)

        a = self.actions['undo'] = self.undo_stack.createUndoAction(self, prefix='Undo')
        a.setShortcut(QKeySequence.StandardKey.Undo)
        menu.addAction(a)

        a = self.actions['redo'] = self.undo_stack.createRedoAction(self, prefix='Redo')
        a.setShortcut(QKeySequence.StandardKey.Redo)
        menu.addAction(a)

        menu.addSeparator()

        a = self.actions['cut'] = QAction('Cut', self)
        a.setShortcut(QKeySequence.StandardKey.Cut)
        a.triggered.connect(self.on_action_cut_trigger)
        menu.addAction(a)

        a = self.actions['copy'] = QAction('Copy', self)
        a.setShortcut(QKeySequence.StandardKey.Copy)
        a.triggered.connect(self.on_action_copy_trigger)
        menu.addAction(a)

        a = self.actions['paste'] = QAction('Paste', self)
        a.setShortcut(QKeySequence.StandardKey.Paste)
        a.triggered.connect(self.on_action_paste_trigger)
        menu.addAction(a)

        a = self.actions['delete'] = QAction('Delete', self)
        a.setShortcut(QKeySequence.StandardKey.Delete)
        a.triggered.connect(self.on_action_delete_trigger)
        menu.addAction(a)

        a = self.actions['select_all'] = QAction('Select All', self)
        a.setShortcut(QKeySequence.StandardKey.SelectAll)
        a.triggered.connect(self.on_action_select_all_trigger)
        menu.addAction(a)

        menu.addSeparator()

        a = self.actions['delete_positions'] = QAction('-', self)
        a.triggered.connect(self.on_action_delete_positions_trigger)
        menu.addAction(a)

        a = self.actions['insert_position'] = QAction('Insert Position...', self)
        a.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_I))
        a.triggered.connect(self.on_action_insert_position_trigger)
        menu.addAction(a)

        a = self.actions['insert_positions_range'] = QAction('Insert Positions Range...', self)
        a.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_I))
        a.triggered.connect(self.on_action_insert_positions_range_trigger)
        menu.addAction(a)

        a = self.actions['offset_positions'] = QAction('Offset Positions...', self)
        a.triggered.connect(self.on_action_offset_positions_trigger)
        menu.addAction(a)

        menu = QMenu('&Options', self)
        menu_bar.addMenu(menu)

        a = self.actions['beep_hints'] = QAction('Beep', self)
        a.setCheckable(True)
        a.triggered.connect(self.on_action_beep_hints_trigger)
        menu.addAction(a)

        a = self.actions['voice_hints'] = QAction('Voice Hints', self)
        a.setCheckable(True)
        a.triggered.connect(self.on_action_voice_hints_trigger)
        menu.addAction(a)

        menu = QMenu('E&xport', self)
        menu_bar.addMenu(menu)

        a = self.actions['wid_export'] = QAction('WIDesigner...', self)
        a.triggered.connect(self.on_action_wid_export_trigger)
        menu.addAction(a)

        self.setMenuBar(menu_bar)

    def init_content(self):
        self.layout = QHBoxLayout()

        self.content_widget = QWidget(self)
        self.content_widget.setLayout(self.layout)

        self.table_view = BoreTableView(self, self.table_model)
        self.table_view.selection_changed.connect(self.on_table_selection_change)
        
        self.detail_panel = QVBoxLayout()
        self.detail_widgets = {
            'groove': GrooveDetailWidget(self, self.model.bore),
            'cutter': CutterDetailWidget(self, self.model.bore),
            'joined': JoinedDetailWidget(self, self.model.bore),
            'profile': ProfileDetailWidget(self, self.model.bore),
        }
        for widget in self.detail_widgets.values():
            self.detail_panel.addWidget(widget)

        self.layout.addWidget(self.table_view, stretch=60)
        self.layout.addLayout(self.detail_panel, stretch=40)

        self.setCentralWidget(self.content_widget)

    def init_status_bar(self):
        status_bar = QStatusBar()

        self.status_bar_units = QLabel(self)

        status_bar.addPermanentWidget(StatusBarSeparator())
        status_bar.addPermanentWidget(self.status_bar_units)

        self.setStatusBar(status_bar)

    def create_save_document_dialog(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setDefaultSuffix('xml')
        dialog.fileSelected.connect(self.on_document_save_dialog_file_selected)
        return dialog

    def update_all(self):
        self.update_menu()
        self.update_title()
        self.update_status_bar()
        self.update_table()
        self.update_detail()

    def update_menu(self):
        selected_rows = len(self.table_view.fully_selected_rows())
        selected_anything = len(self.table_view.selectedIndexes()) > 0
        selected_one_range = len(self.table_view.selected_ranges()) == 1

        self.actions['file_save'].setDisabled(self.is_saved())

        self.actions['cut'].setEnabled(selected_one_range)
        self.actions['copy'].setEnabled(selected_one_range)
        self.actions['paste'].setEnabled(selected_one_range)
        self.actions['delete'].setEnabled(selected_anything)

        self.actions['delete_positions'].setText('Delete Rows (%d)' % selected_rows)
        self.actions['delete_positions'].setVisible(selected_rows != 0)

        self.actions['beep_hints'].setChecked(self.app.settings.load('audio', 'beep_hints'))
        self.actions['voice_hints'].setChecked(self.app.settings.load('audio', 'voice_hints'))

    def update_title(self):
        title = self.document_name()
        if not self.is_clean():
            title = '*' + title
        self.setWindowTitle(title)

    def update_status_bar(self):
        self.status_bar_units.setText(
            'Units: %s' % self.app.current_length_units().symbol
        )
        
    def update_table(self):
        # Note: This is for example to update vertical header geometry in case the units change and labels change their width
        self.table_model.layoutChanged.emit()

    def update_detail(self):
        cd = self.current_column_detail()
        sel_ranges = self.table_view.selected_ranges()
        widget_name = None
        widget_target = None

        if self.table_view.selected_cells_count() == 1:
            match cd['feature']:
                case 'groove':
                    widget_name = 'groove'
                case 'cutter':
                    widget_name = 'cutter'
                case _:
                    widget_name = 'joined'
            widget_target = (self.current_point_index(), cd['feature'], cd['part'])
                
        elif len(sel_ranges) == 1 and sel_ranges[0].width() == 1 and sel_ranges[0].height() > 1:
            # Single-column continuous range of multiple rows
            range = (sel_ranges[0].top(), sel_ranges[0].bottom())
            widget_name = 'profile'
            widget_target = (range, cd['feature'], cd['part'], cd['property'])

        for k, widget in self.detail_widgets.items():
            if k == widget_name:
                widget.setVisible(True)
                widget.set_target(*widget_target)
                widget.update_content()
            else:
                widget.setVisible(False)

    def current_point_index(self) -> int|None:
        row = self.table_view.current_row()
        if 0 <= row < len(self.model.bore.points):
            return row
        return None

    def current_point(self) -> 'BorePointModel|None':
        index = self.current_point_index()
        if index is None:
            return None
        return self.model.bore.points[index]

    def current_column_detail(self) -> dict|None:
        return BoreTableModel.column_detail(self.table_view.current_column())

    def try_say_current_position(self):
        point = self.current_point()
        if point is not None:
            say_text = format_position_for_speech(
                self.app.build_length_output(point.position)
            )
            threading.Thread(
                target=self.app.try_say,
                args=[say_text],
            ).start()

    def is_clean(self):
        return self.undo_stack.isClean()

    def is_blank(self):
        return (
            self.is_clean() and
            self.model.file is None and
            not self.is_touched
        )

    def is_saved(self):
        return (
            self.is_clean() and
            self.model.file is not None
        )

    def document_name(self):
        if self.model.file is None:
            return 'Untitled'
        else:
            path = Path(self.model.file)
            return path.name

    def on_point_data_change(self, index: int):
        # FIXME: When changing many points at once, this is unnecessarily called multiple times too
        self.update_detail()

    def on_points_layout_change(self):
        # FIXME: When doing many layout changes at once, this is unnecessarily called multiple times too
        self.update_detail()

    def on_wid_export_change(self):
        self.on_nonstacked_change()

    def on_table_selection_change(self):
        self.update_menu()
        self.update_detail()
        
    def on_file_change(self):
        self.update_title()
        self.update_menu()

    def on_clean_state_change(self):
        self.is_touched = True
        self.update_title()
        self.update_menu()

    def on_action_file_new_trigger(self):
        self.app.new_document(show_init=True)

    def on_action_file_open_trigger(self):
        self.app.open_document_with_dialog()

    def on_action_file_save_trigger(self):
        self.save_document()

    def on_action_file_save_as_trigger(self):
        self.save_document_with_dialog()

    def on_action_file_close_trigger(self):
        self.close()

    def on_action_doc_properties_trigger(self):
        self.doc_properties_window = DocPropertiesWindow(self)
        self.doc_properties_window.show()

    def on_action_settings_trigger(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()

    def on_document_save_dialog_file_selected(self, file: str):
        if file:
            self.save_document_as(file)

    def on_action_cut_trigger(self):
        if len(self.table_view.selected_ranges()) != 1:
            return
        sel_range = self.table_view.selected_ranges()[0]
        self.table_view.copy_from_sel_range(sel_range)
        self.table_view.delete_sel_range(sel_range)

    def on_action_copy_trigger(self):
        if len(self.table_view.selected_ranges()) != 1:
            return
        sel_range = self.table_view.selected_ranges()[0]
        self.table_view.copy_from_sel_range(sel_range)

    def on_action_paste_trigger(self):
        if len(self.table_view.selected_ranges()) != 1:
            return
        sel_range = self.table_view.selected_ranges()[0]
        self.table_view.paste_into_sel_range(sel_range)

    def on_action_delete_trigger(self):
        for sel_range in self.table_view.selected_ranges():
            self.table_view.delete_sel_range(sel_range)

    def on_action_select_all_trigger(self):
        self.table_view.selectAll()

    def on_action_delete_positions_trigger(self):
        selected_rows = self.table_view.fully_selected_rows()
        if not selected_rows:
            return
        self.do_command(commands.DeletePositions(self, selected_rows))

    def on_action_insert_position_trigger(self):
        self.show_insert_position_window()

    def on_action_insert_positions_range_trigger(self):
        self.show_insert_positions_range_window()

    def on_action_offset_positions_trigger(self):
        self.show_offset_positions_window()

    def on_action_beep_hints_trigger(self):
        self.app.settings.toggle('audio', 'beep_hints')

    def on_action_voice_hints_trigger(self):
        self.app.settings.toggle('audio', 'voice_hints')

    def on_action_wid_export_trigger(self):
        incomplete_positions = self.model.wid_incomplete_positions()
        if incomplete_positions:
            reply = self.app.msg_incomplete_data_for_export(incomplete_positions)
            if not reply:
                return
        self.wid_export_window = WidExportWindow(self)
        self.wid_export_window.show()

    def show_insert_position_window(self):
        self.insert_position_window = InsertPositionWindow(self)
        self.insert_position_window.show()

    def show_insert_positions_range_window(self):
        self.insert_positions_range_window = InsertPositionsRangeWindow(self)
        self.insert_positions_range_window.show()

    def show_offset_positions_window(self):
        self.offset_positions_window = OffsetPositionsWindow(self)
        self.offset_positions_window.show()

    def try_insert_positions_command(self, position_inputs: list):
        insert_positions = []
        
        # Pick only positions that do not yet exist in the model
        for pos_input in position_inputs:
            pos = self.app.parse_length_input(str(pos_input))
            if self.model.bore.points.find_position(pos) is None:
                insert_positions.append(pos)

        if insert_positions:
            self.do_command(commands.InsertPositions(self, insert_positions))

    def try_ask_save_before_proceed(self):
        """
        If the document is unsaved, ask whether to save it, and do save it if user wants to.
        Returns True if can proceed, otherwise False.
        """
        if self.is_clean():
            # Already clean state, can proceed. Note that it's enough that the state is clean, document doesn't have to be saved.
            # This happens e.g. when we have a new blank document that wasn't saved.
            return True

        msg = QMessageBox(self)
        msg.setWindowTitle('Unsaved Changes')
        msg.setText('Save changes to "%s"?' % self.document_name())
        msg.setStandardButtons(
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Save)
        msg.setIcon(QMessageBox.Icon.Warning)
        reply = msg.exec()

        match reply:
            case QMessageBox.StandardButton.Discard:
                return True
            case QMessageBox.StandardButton.Save:
                self.save_document()
                return self.is_saved()

        return False

    def do_command(self, command: QUndoCommand):
        self.undo_stack.push(command)

    def on_nonstacked_change(self):
        # Reset the clean state, because the change doesn't come from a command, so it's not included in undo stack
        self.undo_stack.resetClean()

    def save_document_as(self, file: str):
        # Cannot overwrite a file that is already open in another window
        dw = self.app.find_document_window_by_file(file)
        if dw is not None and dw != self:
            self.app.error_file_already_open_in_another_window()
            return
        
        try:
            e_root = self.model.to_xml()
            tree = ET.ElementTree(e_root)
            ET.indent(tree, space='  ')

            with open(file, 'w') as f:
                tree.write(f, encoding='unicode')

            self.undo_stack.setClean()
            self.model.file = file
            
        except OSError:
            self.app.error_writing_file(file)
            return

    def save_document_with_dialog(self):
        dialog = self.create_save_document_dialog()
        dialog.exec()

    def save_document(self):
        if self.model.file:
            self.save_document_as(self.model.file)
        else:
            self.save_document_with_dialog()

    def bring_into_view(self):
        self.setWindowState((self.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive)
        self.activateWindow()  # for Windows
        self.raise_()  # for MacOS

    def restore_gui(self):
        geometry = self.app.settings.load('document_window', 'geometry')
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(const.DOCUMENT_WINDOW_WIDTH, const.DOCUMENT_WINDOW_HEIGHT)
            center_window(self)

    def save_gui(self):
        """
        This intentionally overrides the settings, so that the next window opened gets geometry of the last window closed.
        """
        self.app.settings.write({ 'document_window': { 'geometry': self.saveGeometry() } })

    def on_before_close(self):
        """
        When returns False, the close event will be aborted.
        """
        proceed = True
        if not self.try_ask_save_before_proceed():
            proceed = False
        return proceed

    def on_close(self):
        self.save_gui()

    def closeEvent(self, event: QCloseEvent):
        super().closeEvent(event)

        proceed = self.on_before_close()
        if not proceed:
            event.ignore()
        else:
            event.accept()
            self.on_close()


class StatusBarSeparator(QFrame):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)