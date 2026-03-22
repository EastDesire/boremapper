from PySide6.QtCore import Qt
from PySide6.QtGui import QTransform, QPainterPath, QBrush, QPalette
from PySide6.QtWidgets import QWidget

from boremapper.bunch import Bunch
from boremapper.diagram import Diagram
from boremapper.enums import DiagramAlign


class ProfileDetailDiagram(Diagram):

    margin_x = 20
    margin_y = 20

    def __init__(self, parent: QWidget, app: 'App'):
        super().__init__(parent, app)
        # TODO: use?
        self.data = Bunch()
    
    def get_content_geometry(self):
        return (
            self.margin_x,
            self.margin_y,
            self.width() - 2 * self.margin_x,
            self.height() - 2 * self.margin_y,
        )

    # TODO: use?
    def set_data(self, **kwargs):
        self.data.__dict__.update(kwargs)
        
    def draw(self):
        left, top, width, height = self.get_content_geometry()

        if not hasattr(self.data, 'profile') or len(self.data.profile) < 2:
            return # Insufficient data to draw the diagram

        # TODO: test profiles that don't start from 0
        profile_start = min([d[0] for d in self.data.profile])
        profile_length = max([d[0] for d in self.data.profile]) - profile_start
        
        profile_widths = [d[1] for d in self.data.profile if d[1] is not None]
        profile_width = 0 if not profile_widths else max(profile_widths)

        if profile_width == 0 or any(val < 0 for val in profile_widths):
            return # Cannot draw the diagram

        scale = min(
            width / profile_width,
            height / profile_length,
        )

        transform = QTransform()
        transform.translate(left + width / 2, top + height / 2)
        self.painter.setTransform(transform)

        match self.data.align:
            case DiagramAlign.CENTER:
                cx0, l_cx, r_cx = 0, -0.5, 0.5
            case DiagramAlign.LEFT:
                cx0, l_cx, r_cx = -0.5, 0, 1
            case DiagramAlign.RIGHT:
                cx0, l_cx, r_cx = 0.5, -1, 0
            case _:
                raise Exception('Cannot resolve diagram align')

        x0 = cx0 * profile_width * scale
        y0 = -(profile_length / 2) * scale
        
        # Profile shape

        l_edge_path = QPainterPath()
        r_edge_path = QPainterPath()
        face_path = QPainterPath()
        
        shape_started = False
        
        for pos, w in self.data.profile:
            if w is not None:
                sw = w * scale
                y = y0 + (pos - profile_start) * scale
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
                y = y0 + (pos - profile_start) * scale
                face_path.lineTo(x0 + r_cx * sw, y)
        
        face_path.closeSubpath()
        self.painter.fillPath(face_path, self.face_brush())

        # Selection

        self.painter.save()

        if self.data.selection_range is not None:
            self.painter.setClipRect(
                -(profile_width / 2) * scale,
                y0 + (self.data.selection_range[0] - profile_start) * scale,
                profile_width * scale,
                (self.data.selection_range[1] - self.data.selection_range[0]) * scale,
            )
            self.painter.fillPath(face_path, QBrush(QPalette().color(QPalette.ColorRole.Highlight)))

        self.painter.restore()
        
        # Edge outlines

        pen = self.solid_line_pen()
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        self.painter.setPen(pen)

        self.painter.drawPath(l_edge_path)
        self.painter.drawPath(r_edge_path)
