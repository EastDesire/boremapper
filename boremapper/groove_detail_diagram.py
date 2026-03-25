from PySide6.QtCore import Qt
from PySide6.QtGui import QTransform
from PySide6.QtWidgets import QWidget

from boremapper.bunch import Bunch
from boremapper.calculations import cutter_used_dimensions
from boremapper.diagram import ShortDimensionLineStyle
from boremapper.point_detail_diagram import PointDetailDiagram


class GrooveDetailDiagram(PointDetailDiagram):

    def __init__(self, parent: QWidget, app: 'App'):
        super().__init__(parent, app)
        
    def draw(self):
        left, top, width, height = self.get_content_geometry()
        point = self.data.point
        p = self.data.part

        if point is None or p is None:
            return

        if not self.is_valid_for_groove_shape(
            getattr(point, p + '_resolved_groove_width'),
            getattr(point, p + '_resolved_groove_height'),
            getattr(point, p + '_resolved_cutter_width'),
            getattr(point, p + '_resolved_cutter_height'),
        ):
            return # Insufficient data to draw the diagram

        diagram_max_groove_w = width - 2 * self.min_wall - 2 * self.dim_space

        # Pre-scaling factor
        scale = diagram_max_groove_w / getattr(point, p + '_resolved_groove_width')

        sp = Bunch()

        # Point's scaled parameters
        try:
            groove_w = getattr(point, p + '_resolved_groove_width')
            groove_h = getattr(point, p + '_resolved_groove_height')
            cutter_w = getattr(point, p + '_resolved_cutter_width')
            cutter_h = getattr(point, p + '_resolved_cutter_height')
            
            # Can raise ValueError with invalid combination of values
            cutter_used_w, cutter_used_h = cutter_used_dimensions(groove_w, groove_h, cutter_w, cutter_h)
            
            setattr(sp, 'groove_w', scale * groove_w)
            setattr(sp, 'groove_h', scale * groove_h)
            setattr(sp, 'cutter_w', scale * cutter_w)
            setattr(sp, 'cutter_h', scale * cutter_h)
            setattr(sp, 'cutter_used_w', scale * cutter_used_w)
            setattr(sp, 'cutter_used_h', scale * cutter_used_h)
                
        except ValueError:
            return

        joint_wall = self.min_wall
        needed_height = sp.groove_h + self.min_wall + self.dim_space
        post_scale = min(1, height / needed_height)
        
        transform = QTransform()
        transform.translate(left + width / 2, top + height / 2)
        transform.scale(post_scale, post_scale)
        transform.translate(
            -width / 2 + self.dim_space,
            -(sp.groove_h + self.min_wall) / 2
        )
        self.painter.setTransform(transform)

        # Wood cross-section

        path = self.create_groove_shape(
            False,
            0,
            0,
            scale,
            getattr(point, p + '_resolved_groove_width'),
            getattr(point, p + '_resolved_groove_height'),
            getattr(point, p + '_resolved_cutter_width'),
            getattr(point, p + '_resolved_cutter_height'),
            joint_wall,
            True
        )
        self.painter.fillPath(path, self.face_brush())

        # Groove outline

        pen = self.thick_line_pen()
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.painter.setPen(pen)

        path = self.create_groove_shape(
            False,
            0,
            0,
            scale,
            getattr(point, p + '_resolved_groove_width'),
            getattr(point, p + '_resolved_groove_height'),
            getattr(point, p + '_resolved_cutter_width'),
            getattr(point, p + '_resolved_cutter_height'),
            joint_wall,
            False
        )
        self.painter.drawPath(path)

        # Groove width dimension

        x0 = joint_wall
        y0 = sp.groove_h + self.min_wall + self.dim_space - self.dim_line_pos

        text = 'W = ' + self.app.build_length_output(getattr(point, p + '_resolved_groove_width'))
        self.draw_dimension(x0, y0, x0 + sp.groove_w, y0, text)
        self.draw_extension_line(x0, 0, x0, y0 + self.ext_line_overrun)
        self.draw_extension_line(x0 + sp.groove_w, 0, x0 + sp.groove_w, y0 + self.ext_line_overrun)

        # Groove height dimension

        x0 = -self.dim_line_pos
        x1 = joint_wall + sp.cutter_used_w / 2
        
        text = 'H = ' + self.app.build_length_output(getattr(point, p + '_resolved_groove_height'))
        self.draw_dimension(x0, sp.groove_h, x0, 0, text, ShortDimensionLineStyle.EXTEND_START)
        self.draw_extension_line(x0 - self.ext_line_overrun, 0, 0, 0)
        self.draw_extension_line(x0 - self.ext_line_overrun, sp.groove_h, x1, sp.groove_h)

        # Cutter ellipse X center marks
        
        y0 = sp.groove_h
        x0 = joint_wall + sp.cutter_used_w / 2
        self.draw_extension_line(
            x0, y0 - self.mark_size / 2,
            x0, y0 + self.mark_size / 2,
        )
        x0 = joint_wall - sp.cutter_used_w / 2 + sp.groove_w
        self.draw_extension_line(
            x0, y0 - self.mark_size / 2,
            x0, y0 + self.mark_size / 2,
        )

        # Cutter ellipse Y center marks

        y0 = sp.groove_h - sp.cutter_used_h
        x0 = joint_wall 
        self.draw_extension_line(
            x0 - self.mark_size / 2, y0,
            x0 + self.mark_size / 2, y0,
        )
        x0 = joint_wall + sp.groove_w
        self.draw_extension_line(
            x0 + self.mark_size / 2, y0,
            x0 - self.mark_size / 2, y0,
        )