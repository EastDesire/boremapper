from boremapper.groove_detail_diagram import GrooveDetailDiagram
from boremapper.point_detail_widget import PointDetailWidget


class GrooveDetailWidget(PointDetailWidget):
    
    def __init__(self, document_window: 'DocumentWindow', model: 'BoreModel'):
        super().__init__(document_window, model)

        self.dw = document_window

        self.diagram = GrooveDetailDiagram(self, document_window.app)
        self.diagram.setMinimumHeight(PointDetailWidget.MIN_HEIGHT)

        self.content_layout.addWidget(self.property_table, stretch=0)
        self.content_layout.addWidget(self.message_list, stretch=0)
        self.content_layout.addWidget(self.diagram, stretch=100)

    def update_content(self):
        super().update_content()
        self.diagram.update()

    def set_target(self, point_index: int|None, feature: str|None, part: str|None):
        super().set_target(point_index, feature, part)
        self.diagram.set_data(point=self.target_point(), part=part)

    def target_name(self) -> str:
        return (self.target.part.capitalize() if self.target.part is not None else '') + ' Part \u2192 Groove'
        
    def properties(self) -> list:
        point = self.target_point()
        if point is None or self.target.part is None:
            return []

        groove_w = getattr(point, self.target.part + '_resolved_groove_width')
        groove_h = getattr(point, self.target.part + '_resolved_groove_height')
        area = getattr(point, self.target.part + '_area')
        
        return [
            (
                'Width (W)',
                self.dw.app.build_length_output(groove_w),
                '',
            ),
            (
                'Height (H)',
                self.dw.app.build_length_output(groove_h),
                '',
            ),
            (
                'Area',
                self.dw.app.build_length_output(area),
                '',
            ),
        ]