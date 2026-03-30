from boremapper.joined_detail_diagram import JoinedDetailDiagram
from boremapper.point_detail_widget import PointDetailWidget


class JoinedDetailWidget(PointDetailWidget):
    
    def __init__(self, document_window: 'DocumentWindow', model: 'BoreModel'):
        super().__init__(document_window, model)

        self.diagram = JoinedDetailDiagram(self, document_window.app)
        self.diagram.setMinimumHeight(PointDetailWidget.MIN_HEIGHT)

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
                self.dw.app.build_length_output(point.area),
                '',
            ),
            (
                'Equivalent Diameter',
                self.dw.app.build_length_output(point.equivalent_diameter),
                '',
            ),
        ]
        
        if point.custom_diameter is not None:
            props.append((
                'Custom Diameter',
                self.dw.app.build_length_output(point.custom_diameter),
                '',
            ))

        return props