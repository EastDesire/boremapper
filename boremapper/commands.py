from PySide6.QtGui import QUndoCommand

from boremapper.enums import DataVariant
from boremapper.models.bore_model import BorePointModel


class EditCells(QUndoCommand):

    def __init__(self, document_window, data):
        super().__init__()
        self.dw = document_window
        self.redo_data = data
        self.undo_data = None
        self.undone = False
        self.setText('Edit ' + ('Cell' if len(self.redo_data) == 1 else 'Cells'))

    def redo(self):
        self.undo_data = self.cells_data(self.redo_data)
        self.set_cells_data(self.redo_data)

        if self.undone:
            self.select_cells_by_data(self.redo_data)

    def undo(self):
        self.set_cells_data(reversed(self.undo_data))

        self.select_cells_by_data(self.undo_data)
        self.undone = True

    def cells_data(self, data):
        out = []
        for d in data:
            model_value = self.dw.table_model.value_for_cell(d['row'], d['column'], DataVariant.RAW)
            out.append({
                'row': d['row'],
                'column': d['column'],
                'value': model_value,
            })
        return out

    def set_cells_data(self, data):
        for d in data:
            self.dw.table_model.set_value_for_cell(d['row'], d['column'], d['value'])

    def select_cells_by_data(self, data):
        self.dw.table_view.clearSelection()
        for d in data:
            self.dw.table_view.set_cell_selected(d['row'], d['column'], True)


class InsertPositions(QUndoCommand):

    def __init__(self, document_window, data):
        super().__init__()
        self.dw = document_window
        self.redo_data = data
        self.undo_data = None
        self.undone = False
        self.setText('Insert ' + ('Position' if len(self.redo_data) == 1 else 'Positions'))

    def redo(self):
        inserted_indexes = self.dw.model.bore.points.add([
            BorePointModel(self.dw.model.bore.points, p) for p in self.redo_data
        ])
        self.undo_data = inserted_indexes

        if self.undone:
            self.dw.table_view.select_rows_by_indexes(inserted_indexes)
        else:
            self.dw.table_view.select_rows_by_indexes([])

    def undo(self):
        self.dw.model.bore.points.delete(self.undo_data)
        self.dw.table_view.select_rows_by_indexes([])
        self.undone = True


class DeletePositions(QUndoCommand):

    def __init__(self, document_window, data):
        super().__init__()
        self.dw = document_window
        self.redo_data = data
        self.undo_data = None
        self.undone = False
        self.setText('Delete ' + ('Position' if len(self.redo_data) == 1 else 'Positions'))

    def redo(self):
        deleted_points = [self.dw.model.bore.points[index] for index in self.redo_data]
        self.dw.model.bore.points.delete(self.redo_data)
        self.undo_data = deleted_points
        self.dw.table_view.select_rows_by_indexes([])

    def undo(self):
        inserted_indexes = self.dw.model.bore.points.add(self.undo_data)
        self.dw.table_view.select_rows_by_indexes(inserted_indexes)
        self.undone = True