from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout, QScrollArea, QSizePolicy

from boremapper.bunch import Bunch
from boremapper.calculations import volume_based_diameter
from boremapper.const import DETAIL_WIDGET_SPACING
from boremapper.enums import DiagramAlign
from boremapper.models.bore_model import BorePointModel
from boremapper.profile_detail_diagram import ProfileDetailDiagram
from boremapper.property_table import PropertyTable


class ProfileDetailWidget(QWidget):
    
    MIN_HEIGHT = 500
    
    def __init__(self, document_window: 'DocumentWindow', model: 'BoreModel'):
        super().__init__(document_window)

        self.dw = document_window
        self.model = model
        
        self.target = Bunch(
            point_index_range = None,
            feature = None,
            part = None,
            property = None,
        )

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, DETAIL_WIDGET_SPACING, 0, 0)
        self.layout.setSpacing(DETAIL_WIDGET_SPACING)
        self.setLayout(self.layout)

        self.target_label = QLabel(self)
        self.target_label.setStyleSheet('font-weight: bold')

        self.position_label = QLabel(self)

        self.title_layout = QHBoxLayout()
        self.title_layout.setSpacing(20)
        self.title_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.title_layout.addWidget(self.target_label)
        self.title_layout.addWidget(self.position_label)
        self.title_layout.addStretch()
        self.layout.addLayout(self.title_layout, stretch=0)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(DETAIL_WIDGET_SPACING, DETAIL_WIDGET_SPACING, DETAIL_WIDGET_SPACING, DETAIL_WIDGET_SPACING)
        self.content_layout.setSpacing(DETAIL_WIDGET_SPACING)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_widget.setLayout(self.content_layout)

        self.content_scroll = QScrollArea()
        self.content_scroll.setWidget(self.content_widget)
        self.content_scroll.setWidgetResizable(True)
        self.layout.addWidget(self.content_scroll)

        self.property_table = PropertyTable()
        self.property_table.setMinimumHeight(100)
        self.property_table.setMaximumHeight(150)

        self.diagram = ProfileDetailDiagram(self, self.dw.app)
        self.diagram.setMinimumHeight(self.MIN_HEIGHT)

        self.content_layout.addWidget(self.property_table, stretch=0)
        self.content_layout.addWidget(self.diagram, stretch=100)

    def update_content(self):
        self.position_label.setText(self._position_text())
        self.target_label.setText(self.target_name())
        self.property_table.set_data(self.properties())
        self.diagram.update()

    def set_target(self, point_index_range: tuple|None, feature: str|None, part: str|None, prop: str|None):
        self.target.point_index_range = point_index_range
        self.target.feature = feature
        self.target.part = part
        self.target.property = prop
        
        self.diagram.set_data(
            profile=self.diagram_profile_data(),
            selection_range=self.diagram_selection_range(),
            align=self.diagram_align(),
        )
        
        self.update_content()
        
    def diagram_profile_data(self):
        match self.target.feature:
            case 'groove' | 'cutter':
                param = self.target.part + '_resolved_' + self.target.feature + '_' + self.target.property
            case 'diameter':
                param = 'diameter'
            case _:
                raise Exception('Cannot resolve target parameter')
            
        # We pass all positions, so that the diagram knows about them and offsets the shape correctly,
        # leaving empty space where the values are missing
        return [(p.position, getattr(p, param)) for p in self.model.points]

    def diagram_selection_points(self) -> list|None:
        if self.target.point_index_range is None:
            return None

        index_from, index_to = self.target.point_index_range
        if not self.model.points.has(index_from) or not self.model.points.has(index_to):
            return None
        
        return self.model.points[index_from:index_to+1]

    def diagram_selection_range(self) -> tuple|None:
        points = self.diagram_selection_points()
        if points is None:
            return None
        return points[0].position, points[-1].position

    def diagram_align(self):
        if self.target.property == 'height':
            return DiagramAlign.RIGHT
        return DiagramAlign.CENTER

    def target_name(self) -> str:
        loc = ''
        prop = ''
        
        match self.target.feature:
            case 'groove' | 'cutter':
                loc = self.target.part.capitalize() + ' Part'
                prop = self.target.feature.capitalize() + ' ' + self.target.property.capitalize()
            case 'diameter':
                loc = 'Joined Parts'
                prop = 'Bore Diameter'
            
        return loc + ' \u2192 ' + prop + ' Profile'

    def _position_text(self) -> str:
        sel_range = self.diagram_selection_range()
        if sel_range is None:
            return ''
        pos_from, pos_to = sel_range
        return 'Bore at: %s-%s' % (
            self.dw.app.build_length_output(pos_from),
            self.dw.app.build_length_output(pos_to),
        )

    def properties(self) -> list:
        info = self.selection_info()
        ratio = info['length'] / info['diameter'] if info['length'] is not None and info['diameter'] else None
        
        return [
            (
                'Selection Length',
                self.dw.app.build_length_output(info['length']) if info['length'] is not None else '',
                '',
            ),
            (
                'Volume-based Diameter (VD)',
                self.dw.app.build_length_output(info['diameter']) if info['diameter'] is not None else '',
                '',
            ),
            (
                'VD:Length Ratio',
                '1 : ' + ('{:.3f}'.format(ratio)) if ratio is not None else '',
                '',
            ),
        ]
    
    def selection_info(self) -> dict|None:
        points = self.diagram_selection_points()
        length = BorePointModel.distance(*points)
        diameter = None
        
        if points is not None and not any(point.diameter is None for point in points):
            diameter = volume_based_diameter(list((point.position, point.diameter) for point in points))
            
        return {
            'diameter': diameter,
            'length': length,
        }