import itertools

from PySide6.QtCore import QItemSelection, QItemSelectionRange, QModelIndex, QPersistentModelIndex, Qt, Signal, \
    QItemSelectionModel
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QStyleOptionViewItem, QTableView, QItemDelegate, QAbstractItemView, \
    QHeaderView, QLineEdit, QWidget

from boremapper import validators, const, commands
from boremapper.enums import DataVariant
from boremapper.models.bore_table_model import BoreTableModel
from boremapper.utils import str_to_number, format_length, has_same_values_in_columns


class BoreTableView(QTableView):

    selection_changed = Signal()

    def __init__(self, document_window: 'DocumentWindow', model: 'BoreTableModel'):
        super().__init__(document_window)

        self.dw = document_window
        
        self.setModel(model)
        self.model().data_set.connect(self.on_data_set)
        self.selectionModel().selectionChanged.connect(self.on_selection_change)

        self.setShowGrid(True)
        
        self.setHorizontalHeader(BoreTableHorizontalHeader(self))
        self.setVerticalHeader(BoreTableVerticalHeader(self))

        self.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

        item_delegate = BoreTableItemDelegate(self)
        item_delegate.data_committed.connect(self.on_data_committed, Qt.ConnectionType.QueuedConnection)
        self.setItemDelegate(item_delegate)

        self.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )

    def selected_ranges(self) -> list:
        sel_ranges = self.selectionModel().selection()
        return [sel_ranges.at(i) for i in range(0, sel_ranges.count())]

    def selected_rows(self) -> list:
        """
        Returns indexes of fully selected rows
        """
        return [index.row() for index in self.selectionModel().selectedRows(0)]
    
    def selected_cells_count(self) -> int:
        return len(self.selectionModel().selectedIndexes())

    def current_row(self) -> int|None:
        index = self.currentIndex()
        return index.row() if index else None

    def current_column(self) -> int|None:
        index = self.currentIndex()
        return index.column() if index else None

    def set_cell_selected(self, row: int, column: int, is_selected: bool):
        index = self.model().index(row, column)
        if index is not None:
            self.selectionModel().select(
                QItemSelection(index, index),
                QItemSelectionModel.SelectionFlag.Select if is_selected else \
                QItemSelectionModel.SelectionFlag.Deselect
            )

    def select_rows_by_indexes(self, indexes: list|tuple):
        self.clearSelection()
        
        last_column_index = self.model().columnCount() - 1
        for index in indexes:
            self.selectionModel().select(
                QItemSelection(
                    self.model().index(index, 0),
                    self.model().index(index, last_column_index),
                ),
                QItemSelectionModel.SelectionFlag.Select
            )

    def on_selection_change(self, selected: 'QItemSelection', deselected: 'QItemSelection'):
        self.selection_changed.emit()
        
    def on_data_set(self, index: 'QModelIndex|QPersistentModelIndex', value: str):
        parsed_val = str_to_number(value, float, allow_empty=True)

        if parsed_val is not None:
            # TODO: how to approchach rounding when converting from different units?
            # We round the value so that we store only decimals that are visible
            parsed_val = round(parsed_val, const.LENGTH_DISPLAY_DECIMALS)

        self.dw.do_command(
            commands.EditCells(self.dw, [{
                'row': index.row(),
                'column': index.column(),
                'value': parsed_val,
            }])
        )

    def on_data_committed(self, using_return: bool):
        if using_return:
            self.dw.app.try_beep()
            self.move_to_next_entry()

    def move_to_next_entry(self):
        index = self.currentIndex()
        row = index.row()
        column = index.column()
        if (
            row != -1 and
            column != -1
        ):
            if row + 1 < self.model().rowCount():
                next_index = self.model().index(row + 1, column)
                self.setCurrentIndex(next_index)
                self.edit(next_index)
                self.dw.try_say_current_position()
            else:
                self.dw.app.try_say('end')

    def delete_sel_range(self, sel_range: 'QItemSelectionRange'):
        data = []
        for row in range(sel_range.top(), sel_range.bottom() + 1):
            for column in range(sel_range.left(), sel_range.right() + 1):
                index = self.model().index(row, column)
                if (
                    (index.flags() & Qt.ItemFlag.ItemIsEditable) and
                    self.model().value_for_cell(row, column, DataVariant.RAW) is not None
                ):
                    data.append({
                        'row': row,
                        'column': column,
                        'value': None,
                    })
        if data:
            self.dw.do_command(commands.EditCells(self.dw, data))

    def copy_from_sel_range(self, sel_range: 'QItemSelectionRange'):
        lines = []
        for row in range(sel_range.top(), sel_range.bottom() + 1):
            line = []
            for column in range(sel_range.left(), sel_range.right() + 1):
                value = self.model().value_for_cell(row, column, DataVariant.DISPLAYED)
                line.append(format_length(value, decimals=10))
            lines.append(line)

        text = '\n'.join(['\t'.join(line) for line in lines])

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)

    def paste_into_sel_range(self, sel_range: 'QItemSelectionRange'):
        clipboard = QGuiApplication.clipboard()
        text = clipboard.text()

        origin_row = sel_range.top()
        origin_column = sel_range.left()

        lines = [line.split('\t') for line in text.split('\n')]

        # When pasting less rows than selected, and each of the pasted columns contains the same values,
        # stretch the values vertically across the entire selection.
        stretch_mode = \
            0 < len(lines) < sel_range.height() and \
            len(lines[0]) == sel_range.width() and \
            has_same_values_in_columns(lines)

        paste_lines = \
            lines if not stretch_mode else \
            itertools.repeat(lines[0], sel_range.height())

        data = []
        for line_index, line in enumerate(paste_lines):
            row = origin_row + line_index
            if row >= self.model().rowCount():
                break # Cell would be outside boundaries

            for value_index, value in enumerate(line):
                column = origin_column + value_index
                if column >= self.model().columnCount():
                    break # Cell would be outside boundaries

                index = self.model().index(row, column)
                if index.flags() & Qt.ItemFlag.ItemIsEditable:
                    data.append({
                        'row': row,
                        'column': column,
                        'value': str_to_number(value, float, allow_empty=True),
                    })
        if data:
            self.dw.do_command(commands.EditCells(self.dw, data))


class BoreTableHorizontalHeader(QHeaderView):

    def __init__(self, table_view: 'BoreTableView'):
        super().__init__(Qt.Orientation.Horizontal, parent=table_view)
        self.table_view = table_view
        self.setModel(table_view.model())
        self.setSelectionModel(self.table_view.selectionModel())
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        self.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setMinimumSectionSize(const.BORE_TABLE_MIN_COLUMN_WIDTH)
        self.setMaximumSectionSize(const.BORE_TABLE_MAX_COLUMN_WIDTH)


class BoreTableVerticalHeader(QHeaderView):

    def __init__(self, table_view: 'BoreTableView'):
        super().__init__(Qt.Orientation.Vertical, parent=table_view)
        self.table_view = table_view
        self.setModel(table_view.model())
        self.setSelectionModel(self.table_view.selectionModel())
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        self.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)


class BoreTableItemDelegate(QItemDelegate):
    
    data_committed = Signal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        self.commitData.connect(self.on_commit_data)
        self._return_pressed_for_commit = None

    def createEditor(self, parent: 'QWidget', option: 'QStyleOptionViewItem', index: 'QModelIndex|QPersistentModelIndex', /):
        self._return_pressed_for_commit = False
        
        editor = QLineEdit(parent)
        editor.setValidator(validators.OptionalDoubleValidator())
        editor.returnPressed.connect(self.on_return_pressed)
        
        return editor

    def destroyEditor(self, editor: 'QWidget', index: 'QModelIndex|QPersistentModelIndex', /):
        editor.destroy()

    def on_return_pressed(self):
        self._return_pressed_for_commit = True

    def on_commit_data(self):
        self.data_committed.emit(self._return_pressed_for_commit)