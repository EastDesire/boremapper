import math

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QTransform, QPainterPath, QBrush, QPalette, QFont, QTextOption, QPen
from PySide6.QtWidgets import QWidget

from boremapper import const
from boremapper.bunch import Bunch
from boremapper.diagram import Diagram
from boremapper.enums import DiagramAlign


class ProfileDetailDiagram(Diagram):

    margin_x = 30
    margin_y = 30

    pos_label_font_size = 16
    pos_label_height = 20
    pos_label_width = 30
    pos_label_box_width = 200
    
    labels_margin = 10
    profile_margin = 15
    mark_width = 25

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
        
    def draw(self):
        left, top, width, height = self.get_content_geometry()

        if not hasattr(self.data, 'profile') or len(self.data.profile) < 2:
            return # Insufficient data to draw the diagram

        profile_start = min([d[0] for d in self.data.profile])
        profile_length = max([d[0] for d in self.data.profile]) - profile_start
        
        profile_widths = [d[1] for d in self.data.profile if d[1] is not None]
        profile_width = 0 if not profile_widths else max(profile_widths)

        if profile_width == 0 or any(val < 0 for val in profile_widths):
            return # Cannot draw the diagram

        # Maximum dimensions the profile diagram can take
        profile_max_w = width - (self.pos_label_width + self.labels_margin + self.mark_width + self.profile_margin)
        profile_max_h = height
        
        scale = min(
            profile_max_w / profile_width,
            profile_max_h / profile_length,
        )
        
        profile_sw = scale * profile_width
        profile_sh = scale * profile_length
        content_w = profile_sw + self.pos_label_width + self.labels_margin + self.mark_width + self.profile_margin

        transform = QTransform()
        transform.translate(left + width / 2 + content_w / 2 - profile_sw / 2, top + height / 2 - profile_sh / 2)
        self.painter.setTransform(transform)

        # cx0 is x origin factor
        match self.data.align:
            case DiagramAlign.CENTER:
                cx0, l_cx, r_cx = 0, -0.5, 0.5
            case DiagramAlign.LEFT:
                cx0, l_cx, r_cx = -0.5, 0, 1
            case DiagramAlign.RIGHT:
                cx0, l_cx, r_cx = 0.5, -1, 0
            case _:
                raise Exception('Cannot resolve diagram align')

        x0 = cx0 * profile_sw

        # Position marks

        font = QFont()
        font.setFamilies(const.FONTS_SANS_SERIF)
        font.setPointSize(self.pos_label_font_size)
        self.painter.setFont(font)

        label_opt = QTextOption()
        label_opt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        label_opt.setWrapMode(QTextOption.WrapMode.NoWrap)

        marks_x = -profile_sw / 2 - self.profile_margin
        last_label_bottom = -math.inf

        for pos, w in self.data.profile:
            y = (pos - profile_start) * scale
            label_y = y - self.pos_label_height / 2
            label_show = label_y >= last_label_bottom
            has_value = w is not None
            alpha = self.muted_alpha if has_value else self.extra_muted_alpha
            
            # Mark line
            self.painter.setPen(self.thin_line_pen(alpha))
            self.painter.drawLine(marks_x, y, marks_x - self.mark_width, y)
            
            # Position label
            if label_show:
                last_label_bottom = label_y + self.pos_label_height
            
                pen = QPen()
                pen.setColor(self.foreground_color(alpha))
                self.painter.setPen(pen)
                
                self.painter.drawText(
                    QRectF(
                        marks_x - self.mark_width - self.pos_label_box_width - self.labels_margin,
                        label_y,
                        self.pos_label_box_width,
                        self.pos_label_height
                    ),
                    self.app.build_length_output(pos),
                    label_opt
                )
        
        # Profile shape

        l_edge_path = QPainterPath()
        r_edge_path = QPainterPath()
        face_path = QPainterPath()
        
        shape_started = False
        
        for pos, w in self.data.profile:
            if w is not None:
                sw = w * scale
                y = (pos - profile_start) * scale
                if not shape_started:
                    shape_started = True
                    face_path.moveTo(x0 + l_cx * sw, y)
                    l_edge_path.moveTo(x0 + l_cx * sw, y)
                    r_edge_path.moveTo(x0 + r_cx * sw, y)
                else:
                    face_path.lineTo(x0 + l_cx * sw, y)
                    l_edge_path.lineTo(x0 + l_cx * sw, y)
                    r_edge_path.lineTo(x0 + r_cx * sw, y)

        for pos, w in reversed(self.data.profile):
            if w is not None:
                sw = w * scale
                y = (pos - profile_start) * scale
                face_path.lineTo(x0 + r_cx * sw, y)
        
        face_path.closeSubpath()
        self.painter.fillPath(face_path, self.face_brush())

        # Selection

        self.painter.save()

        if self.data.selection_range is not None:
            self.painter.setClipRect(
                -profile_sw / 2,
                (self.data.selection_range[0] - profile_start) * scale,
                profile_sw,
                (self.data.selection_range[1] - self.data.selection_range[0]) * scale,
            )
            self.painter.fillPath(face_path, QBrush(QPalette().color(QPalette.ColorRole.Highlight)))

        self.painter.restore()
        
        # Edge outlines

        pen = self.thin_line_pen()
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        self.painter.setPen(pen)

        self.painter.drawPath(l_edge_path)
        self.painter.drawPath(r_edge_path)
