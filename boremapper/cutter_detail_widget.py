from boremapper.cutter_detail_diagram import CutterDetailDiagram
from boremapper.point_detail_widget import PointDetailWidget
from boremapper.utils import format_length


class CutterDetailWidget(PointDetailWidget):
    
    def __init__(self, parent: 'DocumentWindow', model: 'BoreModel'):
        super().__init__(parent, model)

        self.diagram = CutterDetailDiagram(self, parent.app)
        self.diagram.setMinimumHeight(PointDetailWidget.MIN_SIZE)

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
        return (self.target.part.capitalize() if self.target.part is not None else '') + ' Part \u2192 Cutter'

    def properties(self) -> list:
        point = self.target_point()
        if point is None or self.target.part is None:
            return []

        cutter_w = getattr(point, self.target.part + '_resolved_cutter_width')
        cutter_h = getattr(point, self.target.part + '_resolved_cutter_height')

        return [
            (
                'Cutter Width (CW)',
                format_length(cutter_w),
                'I.e. cutting diameter',
            ),
            (
                'Cutter Height (CH)',
                format_length(cutter_h),
                'Measured from ellipse center',
            ),
        ]
