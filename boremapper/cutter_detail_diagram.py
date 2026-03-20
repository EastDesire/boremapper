from PySide6.QtCore import Qt
from PySide6.QtGui import QTransform, QPainterPath
from PySide6.QtWidgets import QWidget

from boremapper.bunch import Bunch
from boremapper.diagram import ShortDimensionLineStyle
from boremapper.point_detail_diagram import PointDetailDiagram
from boremapper.utils import format_length


class CutterDetailDiagram(PointDetailDiagram):
    
    margin_y = 25
    bottom_dim_offset = 15

    def __init__(self, parent: QWidget, app: 'App'):
        super().__init__(parent, app)

    def is_valid_for_cutter_shape(
        self,
        cutter_w: float,
        cutter_h: float,
    ) -> bool:
        vals = (cutter_w, cutter_h)
        if None in vals or min(vals) <= 0:
            return False
        return True
        
    def draw(self):
        left, top, width, height = self.get_content_geometry()
        point = self.data.point
        p = self.data.part

        if point is None or p is None:
            return

        if not self.is_valid_for_cutter_shape(
            getattr(point, p + '_resolved_cutter_width'),
            getattr(point, p + '_resolved_cutter_height'),
        ):
            return # Missing values necessary to draw the diagram

        diagram_max_cutter_w = width - 2 * self.dim_space

        # Pre-scaling factor
        scale = diagram_max_cutter_w / getattr(point, p + '_resolved_cutter_width')

        sp = Bunch()

        # Point's scaled parameters
        try:
            cutter_w = getattr(point, p + '_resolved_cutter_width')
            cutter_h = getattr(point, p + '_resolved_cutter_height')
            setattr(sp, 'cutter_w', scale * cutter_w)
            setattr(sp, 'cutter_h', scale * cutter_h)
                
        except ValueError:
            return

        needed_height = 2 * (sp.cutter_h + self.bottom_dim_offset + self.dim_space)
        post_scale = min(1, height / needed_height)
        
        transform = QTransform()
        transform.translate(left + width / 2, top + height / 2)
        transform.scale(post_scale, post_scale)
        self.painter.setTransform(transform)
        
        # Axes
        x_len = sp.cutter_w / 2 + self.dim_line_pos + self.ext_line_overrun
        y_len = sp.cutter_h + self.bottom_dim_offset + self.dim_space

        self.painter.setPen(self.dash_dot_line_pen())
        self.painter.drawLine(0, 0, 0, -y_len)
        self.painter.drawLine(0, 0, 0, y_len)
        self.painter.drawLine(0, 0, -x_len, 0)
        self.painter.drawLine(0, 0, x_len, 0)

        self.painter.setPen(self.dash_line_pen())
        self.painter.drawEllipse(-sp.cutter_w / 2, -sp.cutter_h, sp.cutter_w, sp.cutter_h * 2)

        # Shank
        
        shank_min_w = sp.cutter_w * (1 / 12)
        shank_max_w = sp.cutter_w * (2 / 3)
        shank_abs_w = 7 # mm
        shank_w = (sp.cutter_w / getattr(point, p + '_resolved_cutter_width')) * shank_abs_w
        shank_w = min(shank_max_w, max(shank_w, shank_min_w))
        shank_d = shank_w / 2
        shank_h = min(shank_w * 4, sp.cutter_h / 2 + self.bottom_dim_offset + self.dim_space)

        y0 = -sp.cutter_h / 2
        path = QPainterPath()
        path.moveTo(-shank_d, y0)
        path.lineTo(-shank_d, y0 - shank_h)
        path.lineTo(-shank_d + shank_d * (1 / 3), y0 - shank_h)
        path.lineTo(-shank_d + shank_d * (2 / 3), y0 - shank_h + shank_d / 3)
        path.lineTo(shank_d - shank_d * (2 / 3), y0 - shank_h - shank_d / 3)
        path.lineTo(shank_d - shank_d * (1 / 3), y0 - shank_h)
        path.lineTo(shank_d, y0 - shank_h)
        path.lineTo(shank_d, y0)
        path.closeSubpath()
        self.painter.fillPath(path, self.face_brush())

        pen = self.bold_line_pen()
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        self.painter.setPen(pen)

        self.painter.drawLine(
            -shank_d, y0,
            -shank_d, y0 - shank_h,
        )
        self.painter.drawLine(
            shank_d, y0,
            shank_d, y0 - shank_h,
        )

        # Cutter body

        path = QPainterPath()
        path.moveTo(-sp.cutter_w / 2, -sp.cutter_h / 2)
        path.lineTo(-sp.cutter_w / 2, 0)
        path.arcTo(-sp.cutter_w / 2, -sp.cutter_h, sp.cutter_w, sp.cutter_h * 2, 180, 180)
        path.lineTo(sp.cutter_w / 2, -sp.cutter_h / 2)
        path.closeSubpath()

        pen = self.bold_line_pen()
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.painter.setPen(pen)

        self.painter.fillPath(path, self.face_brush())
        self.painter.drawPath(path)

        # Cutter width dimension

        x0 = -sp.cutter_w / 2
        y0 = sp.cutter_h + self.bottom_dim_offset + self.dim_space - self.dim_line_pos

        text = 'CW = ' + format_length(getattr(point, p + '_resolved_cutter_width'))
        self.draw_dimension(x0, y0, x0 + sp.cutter_w, y0, text)
        self.draw_extension_line(x0, 0, x0, y0 + self.ext_line_overrun)
        self.draw_extension_line(x0 + sp.cutter_w, 0, x0 + sp.cutter_w, y0 + self.ext_line_overrun)

        # Cutter height dimension

        x0 = -sp.cutter_w / 2 - self.dim_line_pos
        
        text = 'CH = ' + format_length(getattr(point, p + '_resolved_cutter_height'))
        self.draw_dimension(x0, sp.cutter_h, x0, 0, text, ShortDimensionLineStyle.EXTEND_START)
        self.draw_extension_line(x0 - self.ext_line_overrun, sp.cutter_h, 0, sp.cutter_h)