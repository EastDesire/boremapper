import typing

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt, Signal
from PySide6.QtGui import QBrush, QPalette

from boremapper import const
from boremapper.enums import DataVariant
from boremapper.models.document_model import DocumentModel
from boremapper.utils import format_length


class BoreTableModel(QAbstractTableModel):
    """
    Note: This model references data from the main model, it doesn't hold any model state by itself.
    """

    data_set = Signal(QModelIndex, typing.Any)
    
    muted_text_alpha = 0.3

    def __init__(self, parent: 'DocumentModel'):
        super().__init__(parent)

        # TODO: call (if needed at all) layoutAboutToBeChanged() and layoutChanged() somehow only when changing order/number of items
        self.parent().bore.points.point_changed.connect(self.on_point_change)
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
                return format_length(point.position)
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
                val = self.value_for_cell(row, column, DataVariant.RESOLVED)
                return format_length(val)

            case Qt.ItemDataRole.EditRole:
                val = self.value_for_cell(row, column, DataVariant.RAW)
                return format_length(val)

            case Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

            case Qt.ItemDataRole.ForegroundRole:
                point = self.parent().bore.points[row]
                cd = self.column_detail(column)
                
                if any(w['part'] == cd['part'] for w in point.warnings):
                    return QBrush(Qt.GlobalColor.red)

                if cd['feature'] == 'cutter':
                    val = self.value_for_cell(row, column, DataVariant.RAW)
                    if val is None:
                        color = QPalette().color(QPalette.ColorRole.Text)
                        color.setAlphaF(self.muted_text_alpha)
                        return QBrush(color)
                        
                return QBrush(QPalette().color(QPalette.ColorRole.Text))
            
        return None

    def setData(self, index: 'QModelIndex|QPersistentModelIndex', value: typing.Any, /, role: int = ...):
        print('setData') # TODO
        if not index.isValid():
            return None
        match role:
            case Qt.ItemDataRole.EditRole:
                # QAbstractItemModel requires this signal to be explicitly emitted when data successfully changes
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                self.data_set.emit(index, value)
                return True # TODO needed? does anything?
                
                """ TODO rem
                self.parent().bore_points.set_value_for_cell(row, column, parsed_val)
                
                parsed_val = str_to_number(value, float, allow_empty=True)
                if parsed_val is not None:
                    # We round the value so that we store only decimals that are visible
                    parsed_val = round(parsed_val, const.LENGTH_DISPLAY_DECIMALS)
                self.parent().bore_points.set_value_for_cell(row, column, parsed_val)
                return True
                """
        return False # TODO needed? does anything?

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
            match cd['subcolumn']:
                case 0:
                    return getattr(point, p + '_' + ('resolved_' if variant == DataVariant.RESOLVED else '') + 'groove_width')
                case 1:
                    return getattr(point, p + '_' + ('resolved_' if variant == DataVariant.RESOLVED else '') + 'groove_height')
                case 2:
                    return getattr(point, p + '_' + ('resolved_' if variant == DataVariant.RESOLVED else '') + 'cutter_width')
                case 3:
                    return getattr(point, p + '_' + ('resolved_' if variant == DataVariant.RESOLVED else '') + 'cutter_height')
            
        elif cd['feature'] == 'equivalent_diameter':
            return point.equivalent_diameter
        
        elif cd['feature'] == 'override_diameter':
            return point.override_diameter

        return None

    def set_value_for_cell(self, row: int, column: int, value):
        cd = self.column_detail(column)
        point = self.parent().bore.points[row]

        if cd['part'] is not None:
            p = cd['part']
            match cd['subcolumn']:
                case 0:
                    setattr(point, p + '_groove_width', value)
                case 1:
                    setattr(point, p + '_groove_height', value)
                case 2:
                    setattr(point, p + '_cutter_width', value)
                case 3:
                    setattr(point, p + '_cutter_height', value)
                
        elif cd['feature'] == 'override_diameter':
            point.override_diameter = value

    @staticmethod
    def column_def(index: int):
        c = const.BORE_TABLE_COLUMNS[index]
        return {
            'label': c[0],
            'editable': c[1],
            'size_factor': c[2],
            'description': c[3],
        }

    @staticmethod
    def column_detail(index: int) -> dict|None:
        feature = None
        part = None
        subcolumn = None
        
        if 0 <= index <= 7:
            subcolumn = index % 4
            feature = 'groove' if subcolumn < 2 else 'cutter'
            part = 'bottom' if index < 4 else 'top'
            
        elif index == 8:
            feature = 'equivalent_diameter'
            
        elif index == 9:
            feature = 'override_diameter'

        return {
            'feature': feature,
            'part': part,
            'subcolumn': subcolumn,
        }

    def on_point_change(self, index: int):
        leftmost_index = self.index(index, 0)
        rightmost_index = self.index(index, self.columnCount() - 1)
        self.dataChanged.emit(leftmost_index, rightmost_index)

    def on_points_layout_change(self):
        self.layoutChanged.emit()