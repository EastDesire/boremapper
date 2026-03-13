from PySide6.QtCore import Qt
from PySide6.QtGui import QTransform
from PySide6.QtWidgets import QWidget

from boremapper import const
from boremapper.bunch import Bunch
from boremapper.calculations import cutter_used_dimensions
from boremapper.diagram import ShortDimensionLineStyle
from boremapper.point_detail_diagram import PointDetailDiagram
from boremapper.utils import format_length


class JoinedDetailDiagram(PointDetailDiagram):

    def __init__(self, parent: QWidget, app: 'App'):
        super().__init__(parent, app)

    def draw(self):
        left, top, width, height = self.get_content_geometry()
        point = self.data.point

        if point is None:
            return

        for p in const.BORE_PARTS:
            if not self.is_valid_for_groove_shape(
                getattr(point, p + '_resolved_groove_width'),
                getattr(point, p + '_resolved_groove_height'),
                getattr(point, p + '_resolved_cutter_width'),
                getattr(point, p + '_resolved_cutter_height'),
            ):
                return # Missing values necessary to draw the diagram

        bore_height = point.bottom_resolved_groove_height + point.top_resolved_groove_height
        diagram_max_groove_w = width - 2 * self.min_wall - 2 * self.dim_space

        # Pre-scaling factor
        scale = min(
            diagram_max_groove_w / point.bottom_resolved_groove_width,
            diagram_max_groove_w / point.top_resolved_groove_width,
        )

        # Point's scaled parameters
        try:
            scaled = Bunch()
            scaled.bore_height = scale * bore_height
            for p in const.BORE_PARTS:
                sp = Bunch()
                
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
                
                setattr(scaled, p, sp)
                
        except ValueError:
            return

        needed_height = scaled.bore_height + 2 * self.min_wall + 2 * self.dim_space
        post_scale = min(1, height / needed_height)
        
        # Post-scaling
        transform = QTransform()
        transform.translate(left + width / 2, top + height / 2)
        transform.scale(post_scale, post_scale)
        transform.translate(
            -width / 2 + self.dim_space,
            -scaled.bore_height / 2 + scaled.top.groove_h
        )
        self.painter.setTransform(transform)

        for p in const.BORE_PARTS:
            sp = getattr(scaled, p)
            
            flip = p == 'top'
            joint_wall = (width - 2 * self.dim_space - sp.groove_w) / 2

            # Wood cross-section

            path = self.create_groove_shape(
                flip,
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

            pen = self.bold_line_pen()
            pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            self.painter.setPen(pen)

            path = self.create_groove_shape(
                flip,
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

        # Common extension lines

        x0 = -self.dim_line_pos - self.ext_line_overrun
        x1 = width - 2 * self.dim_space + self.dim_line_pos + self.ext_line_overrun
        self.draw_extension_line(x0, 0, 0, 0)
        self.draw_extension_line(x0, scaled.bottom.groove_h, x1, scaled.bottom.groove_h)
        self.draw_extension_line(x0, -scaled.top.groove_h, x1, -scaled.top.groove_h)

        # Bottom part
        
        sp = scaled.bottom
        joint_wall = (width - 2 * self.dim_space - sp.groove_w) / 2

        # Bottom part - Groove width dimension

        x0 = joint_wall
        y0 = sp.groove_h + self.min_wall + self.dim_space - self.dim_line_pos

        text = format_length(point.bottom_resolved_groove_width)
        self.draw_dimension(x0, y0, x0 + sp.groove_w, y0, text)
        self.draw_extension_line(x0, 0, x0, y0 + self.ext_line_overrun)
        self.draw_extension_line(x0 + sp.groove_w, 0, x0 + sp.groove_w, y0 + self.ext_line_overrun)

        # Bottom part - Groove height dimension

        x0 = -self.dim_line_pos
        text = format_length(point.bottom_resolved_groove_height)
        self.draw_dimension(x0, sp.groove_h, x0, 0, text, ShortDimensionLineStyle.EXTEND_START)

        # Bottom part - Cutter ellipse X center marks
        
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

        # Bottom part - Cutter ellipse Y center marks

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

        # Top part

        sp = scaled.top
        joint_wall = (width - 2 * self.dim_space - sp.groove_w) / 2

        # Top part - Groove width dimension

        x0 = joint_wall
        y0 = -sp.groove_h - self.min_wall - self.dim_line_pos

        text = format_length(point.top_resolved_groove_width)
        self.draw_dimension(x0, y0, x0 + sp.groove_w, y0, text)
        self.draw_extension_line(
            x0, 0,
            x0, y0 - self.ext_line_overrun,
        )
        self.draw_extension_line(
            x0 + sp.groove_w, 0,
            x0 + sp.groove_w, y0 - self.ext_line_overrun,
        )

        # Top part - Groove height dimension

        x0 = -self.dim_line_pos
        text = format_length(point.top_resolved_groove_height)
        self.draw_dimension(x0, 0, x0, -sp.groove_h, text, ShortDimensionLineStyle.EXTEND_END)

        # Top part - Cutter ellipse X center marks

        y0 = -sp.groove_h
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

        # Top part - Cutter ellipse Y center marks

        y0 = -(sp.groove_h - sp.cutter_used_h)
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

        # Bore height dimension

        x0 = width - 2 * self.dim_space + self.dim_line_pos
        text = format_length(bore_height)
        self.draw_dimension(
            x0, scaled.bottom.groove_h,
            x0, -scaled.top.groove_h,
            text,
            ShortDimensionLineStyle.EXTEND_END
        )