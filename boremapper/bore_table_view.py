from PySide6.QtCore import QItemSelection, QItemSelectionRange, QModelIndex, QPersistentModelIndex, Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QAbstractItemDelegate, QStyleOptionViewItem, QTableView, QItemDelegate, QAbstractItemView, \
    QHeaderView, QLineEdit, QWidget

from boremapper import validators, const, commands
from boremapper.models.bore_table_model import BoreTableModel
from boremapper.utils import str_to_number


class BoreTableView(QTableView):

    # TODO use?
    data_entered = Signal()
    selection_changed = Signal()

    def __init__(self, document_window: 'DocumentWindow', model: 'BoreTableModel'):
        super().__init__(document_window)

        self.dw = document_window
        
        self.setModel(model)
        self.model().data_set.connect(self.on_data_set)

        self.setHorizontalHeader(BoreTableHorizontalHeader(self))
        self.setVerticalHeader(BoreTableVerticalHeader(self))

        self.setShowGrid(True)
        # TODO: grid keeps its color after color scheme

        self.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

        self.setItemDelegate(BoreTableItemDelegate(self))

        self.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )

        self.selectionModel().selectionChanged.connect(self.on_selection_change)

        # TODO: use?
        #self.selectionModel().currentRowChanged.connect(self.on_current_row_change())

        #self.itemSelectionChanged.connect(self.on_item_selection_change)
        ## Note that QueuedConnection is needed here, since DirectConnection sometimes causes runtime error
        ## 'Internal C++ object already deleted', or in combination message box it causes segmentation fault.
        #self.itemChanged.connect(self.on_item_change, Qt.ConnectionType.QueuedConnection)

        # TODO: still use?
        #self.data_entered.connect(self.on_data_entered, Qt.ConnectionType.QueuedConnection)

        column_sizes_sum = sum(map(
            lambda e: self.model().column_def(e[0])['size_factor'],
            enumerate(const.BORE_TABLE_COLUMNS)
        ))
        for index, _ in enumerate(const.BORE_TABLE_COLUMNS):
            col = self.model().column_def(index)
            self.setColumnWidth(index, const.BORE_TABLE_WIDTH * (col['size_factor'] / column_sizes_sum))

    def selected_rows(self):
        rows = []
        for sel_range in self.selected_ranges():
            if sel_range.columnCount() == self.model().columnCount(): # Only if entire row selected
                for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
                    rows.append(row)
        return rows

    def selected_ranges(self):
        # TODO
        #self.selectionModel().selection() ??????
        return []
    
    def selected_cells_count(self) -> int:
        return len(self.selectionModel().selectedIndexes())

    def current_row(self) -> int|None:
        index = self.currentIndex()
        return index.row() if index else None

    def current_column(self) -> int|None:
        index = self.currentIndex()
        return index.column() if index else None

    def set_cell_selected(self, row: int, column: int, is_selected: bool):
        # TODO
        #self.setRangeSelected(QTableWidgetSelectionRange(row, column, row, column), is_selected)
        pass

    def select_rows_by_indexes(self, indexes: list|tuple):
        pass
        """
        # TODO: do this in document window upon emitting a signal here
        self.clearSelection()
        for index in indexes:
            self.setRangeSelected(QTableWidgetSelectionRange(index, 0, index, self.columnCount() - 1), True)
        """

    def on_selection_change(self, selected: 'QItemSelection', deselected: 'QItemSelection'):
        self.selection_changed.emit()
        
    # TODO
    def on_data_set(self, index: 'QModelIndex|QPersistentModelIndex', value: str):
        print('on_data_set') # TODO
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

    def on_data_entered(self):
        print('Data entered') # TODO
        # TODO: do this in document window upon emitting a signal here
        #self.dw.app.try_beep()
        #self.move_to_next_entry()

    def move_to_next_entry(self):
        index = self.currentIndex()
        row = index.row()
        column = index.column()
        if (
            row != -1 and
            column != -1
        ):
            pass
            # TODO: do this in document window upon emitting a signal here
            #if row + 1 < self.model().rowCount(): # TODO: get row count directly like this?
            #    next_index = self.model().index(row + 1, column)
            #    self.setCurrentIndex(next_index)
            #    self.edit(next_index)
            #    self.dw.try_say_current_position()
            #else:
            #    self.dw.app.try_say('end')

    def delete_sel_range(self, sel_range: 'QItemSelectionRange'):
        pass
        """
        data = []
        # TODO: do this in document window upon emitting a signal here
        for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
            for column in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                item = self.item(row, column)
                if (
                    (item.flags() & Qt.ItemFlag.ItemIsEditable) and
                    self.model_value_for_cell(row, column) is not None
                ):
                    data.append({
                        'row': row,
                        'column': column,
                        'value': None,
                    })
        if data:
            # TODO put back (and maybe emit as a signal and do the command in document window)
            self.dw.do_command(commands.EditCells(self.dw, data))
        """

    def copy_from_sel_range(self, sel_range: 'QItemSelectionRange'):
        pass
        """
        # TODO: do this in document window upon emitting a signal here
        lines = []
        for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
            line = []
            for column in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                #value = self.item(row, column).text()
                value = self.model_value_for_cell(row, column)
                line.append(format_length(value, decimals=10))
            lines.append(line)

        text = '\n'.join(['\t'.join(line) for line in lines])

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        """

    def paste_into_sel_range(self, sel_range: 'QItemSelectionRange'):
        pass
        """
        clipboard = QGuiApplication.clipboard()
        text = clipboard.text()

        # TODO: do this in document window upon emitting a signal here
        
        origin_row = sel_range.topRow()
        origin_column = sel_range.leftColumn()

        lines = [line.split('\t') for line in text.split('\n')]

        # When pasting less rows than selected, and each of the pasted columns contains the same values,
        # stretch the values vertically across the entire selection.
        stretch_mode = \
            0 < len(lines) < sel_range.rowCount() and \
            len(lines[0]) == sel_range.columnCount() and \
            has_same_values_in_columns(lines)

        paste_lines = \
            lines if not stretch_mode else \
            itertools.repeat(lines[0], sel_range.rowCount())

        data = []
        for line_index, line in enumerate(paste_lines):
            row = origin_row + line_index
            if row >= self.rowCount():
                break # Cell would be outside boundaries

            for value_index, value in enumerate(line):
                column = origin_column + value_index
                if column >= self.columnCount():
                    break # Cell would be outside boundaries

                item = self.item(row, column)
                if item.flags() & Qt.ItemFlag.ItemIsEditable:
                    data.append({
                        'row': row,
                        'column': column,
                        'value': str_to_number(value, float, allow_empty=True),
                    })
        if data:
            # TODO put back (and maybe emit as a signal and do the command in document window)
            self.dw.do_command(commands.EditCells(self.dw, data))
        """

    # TODO: rem?
    def closeEditor(self, editor: 'QWidget', hint: 'QAbstractItemDelegate.EndEditHint', /):
        super().closeEditor(editor, hint)

    def keyPressEvent(self, event: 'QKeyEvent'):
        # This is important to check before calling super() method in order to get the original state before the key was pressed
        is_editing = self.state() == QAbstractItemView.State.EditingState

        super().keyPressEvent(event)

        if (
            is_editing and
            event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and
            not event.isAutoRepeat()
        ):
            index = self.currentIndex()
            if index and index.isValid():
                # TODO: do it like this, by calling flags directly?
                if self.model().flags(index) & Qt.ItemFlag.ItemIsEditable:
                    self.data_entered.emit()


class BoreTableHorizontalHeader(QHeaderView):

    def __init__(self, table_view: 'BoreTableView'):
        super().__init__(Qt.Orientation.Horizontal, parent=table_view) # TODO: really set parent?
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
        super().__init__(Qt.Orientation.Vertical, parent=table_view) # TODO: really set parent?
        self.table_view = table_view
        self.setModel(table_view.model())
        self.setSelectionModel(self.table_view.selectionModel())
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        self.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)


class BoreTableItemDelegate(QItemDelegate):

    def __init__(self, parent):
        super().__init__(parent)
        self.commitData.connect(self.on_commit_data)
        self.closeEditor.connect(self.on_close_editor)

    def createEditor(self, parent: 'QWidget', option: 'QStyleOptionViewItem', index: 'QModelIndex|QPersistentModelIndex', /):
        print('Creating editor') # TODO
        editor = QLineEdit(parent)
        editor.setValidator(validators.OptionalDoubleValidator())
        editor.returnPressed.connect(self.on_return_pressed)
        return editor

    def destroyEditor(self, editor: 'QWidget', index: 'QModelIndex|QPersistentModelIndex', /):
        editor.destroy()

    # TODO needed?
    #def setEditorData(self, editor: 'QWidget', index: 'QModelIndex|QPersistentModelIndex', /):
    #    super().setEditorData(editor, index)
    #    # TODO
    #    print('setEditorData')
    #    # TODO
    #    if isinstance(editor, QLineEdit):
    #        editor.selectAll()
        
    def on_commit_data(self):
        # TODO
        print('Data committed')

    def on_close_editor(self):
        # TODO
        print('Editor closed')

    def on_return_pressed(self):
        # TODO
        print('Return pressed')