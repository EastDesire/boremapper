from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout, QScrollArea, QSizePolicy

from boremapper.bunch import Bunch
from boremapper.const import DETAIL_WIDGET_SPACING
from boremapper.models.bore_model import BorePointModel
from boremapper.point_message_list import PointMessageList
from boremapper.point_property_table import PointPropertyTable


class PointDetailWidget(QWidget):
    
    MIN_HEIGHT = 350
    
    def __init__(self, document_window: 'DocumentWindow', model: 'BoreModel'):
        super().__init__(document_window)

        self.dw = document_window
        self.model = model
        
        self.target = Bunch(
            point_index = None,
            feature = None,
            part = None,
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

        self.property_table = PointPropertyTable()
        self.property_table.setMinimumHeight(100)
        self.property_table.setMaximumHeight(150)
        
        self.message_list = PointMessageList()
        self.message_list.setMinimumHeight(50)

        
    def update_content(self):
        self.position_label.setText(self._position_text())
        self.target_label.setText(self.target_name())
        self.property_table.set_data(self.properties())
        
        messages = self.messages()
        self.message_list.set_data(messages)
        self.message_list.setVisible(len(messages) != 0)

    def set_target(self, point_index: int|None, feature: str|None, part: str|None):
        self.target.point_index = point_index
        self.target.feature = feature
        self.target.part = part
        self.update_content()

    def target_point(self) -> 'BorePointModel|None':
        return None if self.target.point_index is None else self.model.points[self.target.point_index]

    def target_name(self) -> str:
        # To be implemented in a child class
        return ''

    def _position_text(self) -> str:
        point = self.target_point()
        return '' if point is None else 'Bore at: %s' % self.dw.app.build_length_output(point.position)

    def properties(self) -> list:
        # To be implemented in a child class
        return []

    def messages(self) -> list:
        point = self.target_point()
        if point is None:
            return []
        
        if self.target.part is not None:
            # Only messages related to given part
            return [w['text'] for w in point.warnings if 'part' in w and w['part'] == self.target.part]
        else:
            # All messages, with part-related messages prefixed with part name
            return [BorePointModel.format_warning(w) for w in point.warnings]