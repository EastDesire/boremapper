import typing

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt, Signal
from PySide6.QtGui import QBrush, QPalette

from boremapper import const
from boremapper.enums import DataVariant
from boremapper.models.document_model import DocumentModel
from boremapper.utils import text_color_to_red, base_color_to_alternate


class BoreTableModel(QAbstractTableModel):
    """
    Note: This model references data from the main model, it doesn't hold any model state by itself.
    """

    data_set = Signal(QModelIndex, typing.Any)
    
    muted_text_alpha = 0.3

    def __init__(self, parent: 'DocumentModel', app: 'App'):
        super().__init__(parent)
        
        self.app = app

        self.parent().bore.points.point_changed.connect(self.on_point_data_change)
        self.parent().bore.points.layout_changed.connect(self.on_points_layout_change)

    def rowCount(self, /, parent: 'QModelIndex|QPersistentModelIndex' = ...) -> int:
        return len(self.parent().bore.points)

    def columnCount(self, /, parent: 'QModelIndex|QPersistentModelIndex' = ...) -> int:
        return len(const.BORE_TABLE_COLUMNS)

    def headerData(self, section: int, orientation: 'Qt.Orientation', /, role = ...):
        match orientation:
            case Qt.Orientation.Horizontal:
                return self.horizontal_header_data(section, role)
            case Qt.Orientation.Vertical:
                return self.vertical_header_data(section, role)
        return None

    def horizontal_header_data(self, section: int, role):
        match role:
            case Qt.ItemDataRole.DisplayRole:
                return self.column_def(section)['label']
            case Qt.ItemDataRole.ToolTipRole:
                return self.column_def(section)['description']
            case Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        return None

    def vertical_header_data(self, section: int, role):
        match role:
            case Qt.ItemDataRole.DisplayRole:
                point = self.parent().bore.points[section]
                return self.app.build_length_output(point.position)
            case Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return None

    def data(self, index: 'QModelIndex|QPersistentModelIndex', /, role: int = ...):
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()

        match role:
            case Qt.ItemDataRole.DisplayRole:
                val = self.value_for_cell(row, column, DataVariant.DISPLAYED)
                return self.app.build_length_output(val)

            case Qt.ItemDataRole.EditRole:
                val = self.value_for_cell(row, column, DataVariant.RAW)
                return self.app.build_length_output(val)

            case Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

            case Qt.ItemDataRole.ForegroundRole:
                point = self.parent().bore.points[row]
                cd = self.column_detail(column)
                
                if any((
                    ('feature' in w and w['feature'] == cd['feature']) or
                    ('part' in w and w['part'] == cd['part'])
                ) for w in point.warnings):
                    return QBrush(text_color_to_red(QPalette().color(QPalette.ColorRole.Text)))

                if cd['feature'] in ('cutter', 'diameter'):
                    val = self.value_for_cell(row, column, DataVariant.RAW)
                    if val is None:
                        color = QPalette().color(QPalette.ColorRole.Text)
                        color.setAlphaF(self.muted_text_alpha)
                        return QBrush(color)
                        
                return QBrush(QPalette().color(QPalette.ColorRole.Text))

            case Qt.ItemDataRole.BackgroundRole:
                cd = self.column_detail(column)
                if cd['feature'] in ('cutter'):
                    return QBrush(base_color_to_alternate(QPalette().color(QPalette.ColorRole.Base)))
            
        return None

    def setData(self, index: 'QModelIndex|QPersistentModelIndex', value: typing.Any, /, role: int = ...):
        if not index.isValid():
            return False
        
        match role:
            case Qt.ItemDataRole.EditRole:
                orig_data = self.data(index, role)
                if value == orig_data:
                    return False # Cell data not changed
                
                # Note: QAbstractItemModel requires this signal to be explicitly emitted when data successfully changes
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                self.data_set.emit(index, value)
                return True
        
        return False

    def flags(self, index: 'QModelIndex|QPersistentModelIndex', /) -> Qt.ItemFlag:
        c = self.column_def(index.column())
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if c['editable']:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def value_for_cell(self, row: int, column: int, variant: 'DataVariant' = None):
        cd = self.column_detail(column)
        point = self.parent().bore.points[row]

        if cd['part'] is not None:
            p = cd['part']
            match cd['feature']:
                case 'groove':
                    return getattr(point, p + '_groove_' + cd['property'])
                case 'cutter':
                    return getattr(point, p + '_' + ('resolved_' if variant == DataVariant.DISPLAYED else '') + 'cutter_' + cd['property'])
            
        elif cd['feature'] == 'diameter':
            return getattr(point, 'diameter' if variant == DataVariant.DISPLAYED else 'custom_diameter')

        return None

    def set_value_for_cell(self, row: int, column: int, value):
        cd = self.column_detail(column)
        point = self.parent().bore.points[row]

        if cd['part'] is not None:
            p = cd['part']
            match cd['feature']:
                case 'groove':
                    setattr(point, p + '_groove_' + cd['property'], value)
                case 'cutter':
                    setattr(point, p + '_cutter_' + cd['property'], value)
                
        elif cd['feature'] == 'diameter':
            point.custom_diameter = value

    @staticmethod
    def column_def(index: int):
        c = const.BORE_TABLE_COLUMNS[index]
        return {
            'label': c[0],
            'editable': c[1],
            'description': c[2],
        }

    @staticmethod
    def column_detail(index: int) -> dict|None:
        feature = None
        part = None
        prop = None
        
        if 0 <= index <= 7:
            subcolumn = index % 4
            feature = 'groove' if subcolumn < 2 else 'cutter'
            part = 'bottom' if index < 4 else 'top'
            prop = 'width' if subcolumn % 2 == 0 else 'height'
            
        elif index == 8:
            feature = 'diameter'

        return {
            'feature': feature,
            'part': part,
            'property': prop,
        }

    def on_point_data_change(self, index: int):
        leftmost_index = self.index(index, 0)
        rightmost_index = self.index(index, self.columnCount() - 1)
        self.dataChanged.emit(leftmost_index, rightmost_index)
        
        # Note: Because dataChanged signal alone doesn't seem to update vertical header,
        # we also emit this to accommodate for situations when position is being changed too.
        self.layoutChanged.emit()

    def on_points_layout_change(self):
        self.layoutChanged.emit()