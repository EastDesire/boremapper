from math import degrees

from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QWidget

from boremapper.bunch import Bunch
from boremapper.calculations import ellipse_angle_from_coordinates, ellipse_horizontal_chord
from boremapper.diagram import Diagram


class PointDetailDiagram(Diagram):

    margin_x = 8
    margin_y = 8
    min_wall = 40

    def __init__(self, parent: QWidget, app: 'App'):
        super().__init__(parent, app)
        self.data = Bunch()
    
    def get_content_geometry(self):
        return (
            self.margin_x,
            self.margin_y,
            self.width() - 2 * self.margin_x,
            self.height() - 2 * self.margin_y,
        )

    def set_data(self, **kwargs):
        self.data.__dict__.update(kwargs)

    def is_valid_for_groove_shape(
        self,
        groove_w: float,
        groove_h: float,
        cutter_w: float,
        cutter_h: float,
    ) -> bool:
        vals = (groove_w, groove_h, cutter_w, cutter_h)
        if None in vals or min(vals) <= 0:
            return False
        return True

    def create_groove_shape(
        self,
        flip: bool,
        left: float,
        top: float,
        s: float,
        groove_w: float,
        groove_h: float,
        cutter_w: float,
        cutter_h: float,
        joint_wall: float,
        closed_shape: bool,
    ) -> QPainterPath:
        
        k = -1 if flip else 1

        if cutter_h <= groove_h:
            # Deep cut
            arc_start = 0
            arc_offset = 0
        else:
            # Shallow cut
            chord = ellipse_horizontal_chord(cutter_w / 2, cutter_h, groove_h)
            arc_offset = cutter_w / 2 - chord / 2
            arc_start = degrees(ellipse_angle_from_coordinates(cutter_w / 2, cutter_h, chord / 2, cutter_h - groove_h))

        arc_len = 90 - arc_start

        path = QPainterPath()

        # Left joint
        path.moveTo(left, top)
        path.lineTo(left + joint_wall, top)
        
        arc_y = top - (0 if flip else cutter_h * 2 * s) + (groove_h * s) * k

        # Left arc
        path.arcTo(
            left + joint_wall - arc_offset * s,
            arc_y,
            cutter_w * s,
            cutter_h * 2 * s,
            90 - arc_len * k + (0 if flip else 180),
            arc_len * k
        )

        # Right arc
        path.arcTo(
            left + joint_wall + groove_w * s + arc_offset * s - cutter_w * s,
            arc_y,
            cutter_w * s,
            cutter_h * 2 * s,
            90 + (0 if flip else 180),
            arc_len * k
        )

        # Right joint
        path.lineTo(left + joint_wall + groove_w * s, top)
        path.lineTo(left + 2 * joint_wall + groove_w * s, top)

        if closed_shape:
            path.lineTo(
                left + 2 * joint_wall + groove_w * s,
                top + (groove_h * s + self.min_wall) * k,
            )
            path.lineTo(
                left,
                top + (groove_h * s + self.min_wall) * k,
            )
            path.closeSubpath()

        return path