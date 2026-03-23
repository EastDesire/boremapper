import math
from enum import IntEnum, auto
from math import degrees, radians

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QFont, QPaintEvent, QPainter, QPainterPath, QPalette, QPen, \
    QPixmap, \
    QTextOption
from PySide6.QtWidgets import QWidget

from boremapper.calculations import angle_from_coordinates, coordinates_from_angle, distance_between_points


class ShortDimensionLineStyle(IntEnum):
    EXTEND_START = auto()
    EXTEND_END = auto()


class Diagram(QWidget):

    font_families = ['Arial', 'Helvetica', 'sans-serif']
    muted_alpha = 0.55
    extra_muted_alpha = 0.2

    # Dimension line and text
    dim_space = 64 # Space reserved for a dimension line with text
    dim_line_pos = dim_space / 2 # Position of the dimension line within its reserved space
    dim_line_arrow_size = 15
    dim_line_arrow_angle = 30
    dim_line_extend = 50
    dim_text_box_height = 24 # Height of the dimension text (including space)
    dim_font_size = 14

    # Extension line, mark
    ext_line_overrun = 7
    mark_size = 18

    def __init__(self, parent: QWidget, app: 'App'):
        super().__init__(parent)

        self.app = app
        self.pr = app.primaryScreen().devicePixelRatio()

        self.pixmap = None
        self.painter = QPainter()
        self.update_pixmap()

    def paintEvent(self, event: QPaintEvent):
        with QPainter(self) as painter:
            self.draw_on_pixmap()
            painter.drawPixmap(0, 0, self.pixmap)
            
    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        self.update_pixmap()

    def update_pixmap(self):
        self.pixmap = QPixmap(
            self.width() * self.pr,
            self.height() * self.pr,
        )
        self.pixmap.setDevicePixelRatio(self.pr)

    def draw_on_pixmap(self):
        self.pixmap.fill(self.background_color())
        
        self.painter.begin(self.pixmap)
        try:
            # This is to make lines sharper, because painter's origin is "between" the pixels
            self.painter.translate(0.5, 0.5)
            self.painter.setRenderHints(QPainter.RenderHint.Antialiasing, True)
            self.draw()
        finally:
            # This does a proper cleanup even if an error occurs during painting.
            # Otherwise, the app might crash with 'Painter already active' error.
            self.painter.end()

    def draw(self):
        # To be implemented in a child class
        pass

    def background_color(self, alpha: float = 1.0):
        """
        Note that the reason for methods like this one is to always get the fresh system color,
        in case the system color scheme changes in runtime.
        """
        color = QPalette().color(QPalette.ColorRole.Base)
        color.setAlphaF(alpha)
        return color

    def foreground_color(self, alpha: float = 1.0):
        color = QPalette().color(QPalette.ColorRole.Text)
        color.setAlphaF(alpha)
        return color

    def thick_line_pen(self, alpha=1.0):
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(self.foreground_color(alpha))
        return pen

    def thin_line_pen(self, alpha=1.0):
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(self.foreground_color(alpha))
        return pen

    def dash_line_pen(self, alpha=1.0):
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(self.foreground_color(alpha))
        pen.setStyle(Qt.PenStyle.CustomDashLine)
        pen.setDashPattern([4, 6])
        return pen

    def dash_dot_line_pen(self, alpha=1.0):
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(self.foreground_color(alpha))
        pen.setStyle(Qt.PenStyle.CustomDashLine)
        pen.setDashPattern([15, 6, 0.5, 6])
        return pen

    def face_brush(self):
        return QBrush(self.foreground_color(0.09))

    def draw_dimension(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        text: str,
        style_when_short: ShortDimensionLineStyle = ShortDimensionLineStyle.EXTEND_START,
        extend_when_short: int = None,
    ):
        if extend_when_short is None:
            extend_when_short = self.dim_line_extend
            
        is_short = distance_between_points(x1, y1, x2, y2) < self.dim_line_arrow_size * 3

        self.draw_dimension_line(
            x1, y1, x2, y2,
            is_short,
            extend_when_short if is_short and style_when_short == ShortDimensionLineStyle.EXTEND_START else 0,
            extend_when_short if is_short and style_when_short == ShortDimensionLineStyle.EXTEND_END else 0,
            self.dim_line_arrow_size,
            self.dim_line_arrow_angle,
        )

        a = degrees(angle_from_coordinates(x2 - x1, y2 - y1))
        
        # Default text position is the center of the dimension line
        text_x = (x1 + x2) / 2
        text_y = (y1 + y2) / 2
        
        if is_short:
            match style_when_short:
                case ShortDimensionLineStyle.EXTEND_START:
                    text_x, text_y = coordinates_from_angle(radians(a + 180), self.dim_line_arrow_size + extend_when_short / 2, x1, y1)
                case ShortDimensionLineStyle.EXTEND_END:
                    text_x, text_y = coordinates_from_angle(radians(a), self.dim_line_arrow_size + extend_when_short / 2, x2, y2)
            
        # We assume the text won't be longer than the diagonal of the drawing
        text_area_w = distance_between_points(0, 0, self.width(), self.height())

        self.painter.save()
        self.painter.translate(text_x, text_y)
        self.painter.rotate(a)
        self.draw_dimension_text(
            -text_area_w / 2,
            -self.dim_text_box_height,
            text_area_w,
            self.dim_text_box_height,
            text,
        )
        self.painter.restore()

    def draw_dimension_text(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
    ):
        font = QFont()
        font.setFamilies(self.font_families)
        font.setPointSize(self.dim_font_size)
        self.painter.setFont(font)

        pen = QPen()
        pen.setColor(self.foreground_color(self.muted_alpha))
        self.painter.setPen(pen)

        opt = QTextOption()
        opt.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        opt.setWrapMode(QTextOption.WrapMode.NoWrap)

        self.painter.drawText(QRectF(x, y, width, height), text, opt)

    def draw_dimension_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        converging_arrows: bool = False,
        extend_start: int = 0,
        extend_end: int = 0,
        arrow_size: float = 15,
        arrow_angle: float = 30,
    ):
        color = self.foreground_color(self.muted_alpha)

        a = math.degrees(angle_from_coordinates(x2 - x1, y2 - y1))
        shorten_ends = arrow_size

        if converging_arrows:
            a += 180
            shorten_ends = 0

        a1 = a + arrow_angle / 2
        a2 = a - arrow_angle / 2

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(color)
        self.painter.setPen(pen)
        
        # Dimension line extension at start
        if converging_arrows and extend_start:
            self.painter.drawLine(
                QPointF(*coordinates_from_angle(math.radians(a), arrow_size, x1, y1)),
                QPointF(*coordinates_from_angle(math.radians(a), arrow_size + extend_start, x1, y1)),
            )
            
        # Dimension line
        self.painter.drawLine(
            QPointF(*coordinates_from_angle(math.radians(a), shorten_ends, x1, y1)),
            QPointF(*coordinates_from_angle(math.radians(a + 180), shorten_ends, x2, y2)),
        )

        # Dimension line extension at end
        if converging_arrows and extend_end:
            self.painter.drawLine(
                QPointF(*coordinates_from_angle(math.radians(a + 180), arrow_size, x2, y2)),
                QPointF(*coordinates_from_angle(math.radians(a + 180), arrow_size + extend_end, x2, y2)),
            )

        # Start arrow
        path = QPainterPath()
        path.moveTo(x1, y1)
        path.lineTo(*coordinates_from_angle(math.radians(a1), arrow_size, x1, y1))
        path.lineTo(*coordinates_from_angle(math.radians(a2), arrow_size, x1, y1))
        path.closeSubpath()
        self.painter.fillPath(path, QBrush(color))

        # End arrow
        path = QPainterPath()
        path.moveTo(x2, y2)
        path.lineTo(*coordinates_from_angle(math.radians(a1 + 180), arrow_size, x2, y2))
        path.lineTo(*coordinates_from_angle(math.radians(a2 + 180), arrow_size, x2, y2))
        path.closeSubpath()
        self.painter.fillPath(path, QBrush(color))

    def draw_extension_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
    ):
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(self.foreground_color(self.muted_alpha))
        self.painter.setPen(pen)
        self.painter.drawLine(x1, y1, x2, y2)