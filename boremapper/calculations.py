import math

from boremapper import const


def coordinates_from_angle(angle: float, radius: float, x0: float = 0, y0: float = 0) -> tuple:
    """
    :param angle: Angle in radians
    :param radius: Radius
    :param x0: X origin
    :param y0: Y origin
    :return: Tuple representing X,Y coordinates
    """
    return (
        x0 + math.cos(angle) * radius,
        y0 + math.sin(angle) * radius,
    )


def angle_from_coordinates(x: float, y: float) -> float:
    """
    Calculates the angle from given coordinates.
    :param x: X coordinate
    :param y: Y coordinate
    :return: Angle in radians
    """
    return math.atan2(y, x)


def distance_between_points(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt(
        math.pow(x2 - x1, 2) +
        math.pow(y2 - y1, 2)
    )


def ellipse_angle_from_coordinates(a: float, b: float, x: float, y: float) -> float:
    """
    Calculates the angle from given coordinates lying on circumference of the ellipse.
    See: https://stackoverflow.com/a/26422533
    :param a: Length of the semi-major axis
    :param b: Length of the semi-minor axis
    :param x: X coordinate relative to ellipse center
    :param y: Y coordinate relative to ellipse center
    :return: Angle in radians
    """
    return math.atan2(y * (a / b), x)


def circle_radius_from_area(area: float) -> float:
    """
    Calculates the radius of a circle of given area.
    See https://www.sensorsone.com/circle-area-to-radius-calculator/
    :param area: Area of the circle
    :return: Radius
    """
    return math.sqrt(area / math.pi)


def ellipse_area(a: float, b: float) -> float:
    """
    Calculates the area of an ellipse.
    See https://www.vcalc.com/wiki/vCalc/Ellipse+-+area
    :param a: Length of the semi-major axis
    :param b: Length of the semi-minor axis
    :return: Area
    """
    return math.pi * a * b


def ellipse_horizontal_segment_area(a: float, b: float, h: float) -> float:
    """
    Calculates the area of an ellipse segment on its minor axis.
    See https://www.had2know.org/academics/ellipse-segment-tank-volume-calculator.html
    :param a: Length of the semi-major axis
    :param b: Length of the semi-minor axis
    :param h: Segment height (on the minor axis)
    :return: Area of the segment
    """
    if a == 0 or b == 0:
        return 0
    c = 2 * a
    d = 2 * b
    return (d*c/4) * (math.acos(1 - 2*h/d) - (1 - 2*h/d) * math.sqrt(4*h/d - 4*pow(h,2) / pow(d,2)))


def ellipse_horizontal_chord(a: float, b: float, h: float) -> float:
    """
    Calculates the horizontal chord of an ellipse at given distance from its edge.
    See https://www.vcalc.com/wiki/ellipse-horizontal-chord-from-edge
    :param a: Length of the semi-major axis
    :param b: Length of the semi-minor axis
    :param h: Vertical distance from the edge (on the minor axis)
    :return: Horizontal chord
    """
    return 2 * (a / b) * math.sqrt((2 * b * h) - (h * h))


def cutter_used_dimensions(groove_w: float, groove_h: float, cutter_w: float, cutter_h: float) -> tuple:
    """
    Calculates how much of the cutter width and height is used in the groove.
    :param groove_w: Groove width
    :param groove_h: Groove height
    :param cutter_w: Width (diameter) of the cutter used
    :param cutter_h: Length of the cutter ellipse's semiaxis
    """

    if groove_w <= 0:
        raise ValueError('Invalid groove width')
    if groove_h <= 0:
        raise ValueError('Invalid groove height')
    if cutter_w <= 0:
        raise ValueError('Invalid cutter width')
    if cutter_h <= 0:
        raise ValueError('Invalid cutter height')

    if cutter_h <= groove_h:
        # Case deep cut
        if cutter_w > groove_w:
            raise ValueError('Cutter does not fit into groove')
        used_w = cutter_w
        used_h = cutter_h
    else:
        # Case shallow cut
        chord = ellipse_horizontal_chord(cutter_w / 2, cutter_h, groove_h)
        if round(chord, const.FLOAT_SAFE_DECIMALS) > round(groove_w, const.FLOAT_SAFE_DECIMALS):
            raise ValueError('Cutter does not fit into groove')
        used_w = chord
        used_h = groove_h

    return used_w, used_h


def groove_crosssectional_area(groove_w: float, groove_h: float, cutter_w: float, cutter_h: float) -> float:
    """
    Calculates cross-sectional area of the groove in flute's half part.

    :param groove_w: Groove width
    :param groove_h: Groove height
    :param cutter_w: Width (diameter) of the cutter used
    :param cutter_h: Length of the cutter ellipse's semiaxis. Distance between cutter ellipse's center and the tip.
    :return: Calculated cross-sectional area of the groove
    """

    cutter_used_w, cutter_used_h = cutter_used_dimensions(groove_w, groove_h, cutter_w, cutter_h)

    return (
        ellipse_horizontal_segment_area(cutter_w / 2, cutter_h, cutter_used_h) + # Round corners area
        ((groove_w - cutter_used_w) * cutter_used_h) + # Rectangular area between round corners
        (groove_w * (groove_h - cutter_used_h)) # Remaining rectangular area
    )