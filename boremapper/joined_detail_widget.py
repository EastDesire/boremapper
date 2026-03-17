from boremapper.joined_detail_diagram import JoinedDetailDiagram
from boremapper.point_detail_widget import PointDetailWidget
from boremapper.utils import format_length


class JoinedDetailWidget(PointDetailWidget):
    
    def __init__(self, parent: 'DocumentWindow', model: 'BoreModel'):
        super().__init__(parent, model)

        self.diagram = JoinedDetailDiagram(self, parent.app)
        self.diagram.setMinimumHeight(PointDetailWidget.MIN_SIZE)
        self.diagram.setMaximumHeight(PointDetailWidget.MAX_SIZE)

        self.content_layout.addWidget(self.property_table, stretch=0)
        self.content_layout.addWidget(self.message_list, stretch=0)
        self.content_layout.addWidget(self.diagram, stretch=100)

    def update_content(self):
        super().update_content()
        self.diagram.update()

    def set_target(self, point_index: int|None, feature: str|None, part: str|None):
        super().set_target(point_index, feature, part)
        self.diagram.set_data(point=self.target_point())

    def target_name(self) -> str:
        return 'Joined Parts'

    def properties(self) -> list:
        point = self.target_point()
        if point is None:
            return []
        
        props = [
            (
                'Area',
                format_length(point.area),
                '',
            ),
            (
                'Equivalent Diameter',
                format_length(point.equivalent_diameter),
                '',
            ),
        ]
        
        if point.override_diameter is not None:
            props.append((
                'Custom Diameter',
                format_length(point.override_diameter),
                '',
            ))

        return props