from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout, QScrollArea, QSizePolicy

from boremapper.bunch import Bunch
from boremapper.const import DETAIL_WIDGET_SPACING
from boremapper.enums import DiagramAlign
from boremapper.profile_detail_diagram import ProfileDetailDiagram


class ProfileDetailWidget(QWidget):
    
    MIN_WIDTH = 350
    MAX_WIDTH = 650
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

        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMaximumWidth(self.MAX_WIDTH)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, DETAIL_WIDGET_SPACING, 0, 0)
        self.layout.setSpacing(DETAIL_WIDGET_SPACING)
        self.setLayout(self.layout)

        self.target_label = QLabel(self)
        self.target_label.setStyleSheet('font-weight: bold')

        self.title_layout = QHBoxLayout()
        self.title_layout.setSpacing(20)
        self.title_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.title_layout.addWidget(self.target_label)
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

        self.diagram = ProfileDetailDiagram(self, self.dw.app)
        # TODO: put somewhere better? Here as well as in other classes
        self.diagram.setMinimumHeight(self.MIN_HEIGHT)
        self.content_layout.addWidget(self.diagram, stretch=100)

    def update_content(self):
        self.target_label.setText(self.target_name())
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
    
    def diagram_selection_range(self) -> tuple|None:
        if self.target.point_index_range is None:
            return None
        
        index_from, index_to = self.target.point_index_range
        if not self.model.points.has(index_from) or not self.model.points.has(index_to):
            return None
        
        return (
            self.model.points[index_from].position,
            self.model.points[index_to].position,
        )

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