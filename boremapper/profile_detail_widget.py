from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout, QScrollArea, QSizePolicy

from boremapper.bunch import Bunch
from boremapper.utils import format_length


class ProfileDetailWidget(QWidget):
    
    MIN_SIZE = 350
    MAX_SIZE = 650
    SPACING = 8 # TODO: somewhere global?
    
    def __init__(self, parent: 'DocumentWindow', model: 'BoreModel'):
        super().__init__(parent)

        self.model = model
        
        self.target = Bunch(
            point_indexes = [], # TODO
            feature = None,
            part = None,
            property = None,
        )

        self.setMinimumWidth(self.MIN_SIZE)
        self.setMaximumWidth(self.MAX_SIZE)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, self.SPACING, 0, 0)
        self.layout.setSpacing(self.SPACING)
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
        self.content_layout.setContentsMargins(self.SPACING, self.SPACING, self.SPACING, self.SPACING)
        self.content_layout.setSpacing(self.SPACING)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_widget.setLayout(self.content_layout)

        self.content_scroll = QScrollArea()
        self.content_scroll.setWidget(self.content_widget)
        self.content_scroll.setWidgetResizable(True)
        self.layout.addWidget(self.content_scroll)

    def update_content(self):
        self.target_label.setText(self.target_name())
        # TODO: redraw the diagram?

    def set_target(self, point_indexes: list, feature: str|None, part: str|None, prop: str|None):
        self.target.point_indexes = point_indexes
        self.target.feature = feature
        self.target.part = part
        self.target.property = prop
        self.update_content()

    def target_points(self) -> list:
        return [self.model.points[index] for index in self.target.point_indexes]

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