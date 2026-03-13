import math
import unittest

from boremapper.calculations import (
    circle_radius_from_area, ellipse_area, ellipse_horizontal_chord, ellipse_horizontal_segment_area,
    groove_crosssectional_area
)


class CalculationsTestCase(unittest.TestCase):

    def test_circle_radius_from_area(self):
        self.assertAlmostEqual(circle_radius_from_area(0), 0)
        self.assertAlmostEqual(circle_radius_from_area(math.pi), 1)

    def test_ellipse_area(self):
        self.assertAlmostEqual(ellipse_area(0, 0), 0)
        self.assertAlmostEqual(ellipse_area(1, 0), 0)
        self.assertAlmostEqual(ellipse_area(0, 1), 0)
        self.assertAlmostEqual(ellipse_area(1, 1), math.pi)
        self.assertAlmostEqual(ellipse_area(5, 10), 157.07963267948966)
        self.assertAlmostEqual(ellipse_area(10, 5), 157.07963267948966)

    def test_ellipse_horizontal_segment_area(self):
        self.assertAlmostEqual(ellipse_horizontal_segment_area(0, 0, 0), 0)
        self.assertAlmostEqual(ellipse_horizontal_segment_area(5, 0, 0), 0)
        self.assertAlmostEqual(ellipse_horizontal_segment_area(0, 5, 0), 0)
        self.assertAlmostEqual(ellipse_horizontal_segment_area(5, 5, 0), 0)
        self.assertAlmostEqual(ellipse_horizontal_segment_area(0, 0, 5), 0)
        self.assertAlmostEqual(ellipse_horizontal_segment_area(5, 0, 5), 0)
        self.assertAlmostEqual(ellipse_horizontal_segment_area(0, 5, 5), 0)
        self.assertAlmostEqual(ellipse_horizontal_segment_area(10, 5, 2.5), 30.709242465218917)
        self.assertAlmostEqual(ellipse_horizontal_segment_area(5, 10, 2.5), 11.332793849440245)
        self.assertAlmostEqual(ellipse_horizontal_segment_area(10, 10, 10), (math.pi * pow(10, 2)) / 2)

    def test_ellipse_horizontal_chord(self):
        self.assertAlmostEqual(ellipse_horizontal_chord(0, 5, 0), 0)
        self.assertAlmostEqual(ellipse_horizontal_chord(5, 5, 0), 0)
        self.assertAlmostEqual(ellipse_horizontal_chord(10, 5, 5), 20)
        self.assertAlmostEqual(ellipse_horizontal_chord(10, 5, 2.5), 17.320508075688775)
        self.assertAlmostEqual(ellipse_horizontal_chord(5, 10, 2.5), 6.614378277661476)

    def test_groove_crosssectional_area_zero_cutter(self):
        self.assertAlmostEqual(
            groove_crosssectional_area(10, 5, 0.000001, 0.000001),
            50
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(10, 2.5, 0.000001, 0.000001),
            25
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(0.000001, 0.000001, 0.000001, 0.000001),
            0
        )

    def test_groove_crosssectional_area_circular_cutter_deep_cut(self):
        self.assertAlmostEqual(
            groove_crosssectional_area(10, 5, 10, 5),
            39.26990817
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(10, 5, 0.1, 0.05),
            49.99892699081698 # Pre-generated
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(10, 5, 1, 0.5),
            49.89269908169872 # Pre-generated
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(10, 5, 2, 1),
            49.5707963267949 # Pre-generated
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(10, 5, 5, 2.5),
            47.317477042468106 # Pre-generated
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(10, 10, 10, 5),
            89.26990817
        )

        with self.assertRaises(ValueError):
            groove_crosssectional_area(10, 10, -0.1, -0.05)

    def test_groove_crosssectional_area_circular_cutter_shallow_cut(self):
        self.assertAlmostEqual(
            groove_crosssectional_area(10, 4, 10, 5),
            30.145144780016935 # Pre-generated
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(10, 1, 3, 1.5),
            9.234124783084006 # Pre-generated
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(10, 1, 10, 5),
            8.087527719832106 # Pre-generated
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(10, 1, 20, 10),
            7.154792800678825 # Pre-generated
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(0.000001, 0.000001, 0.000001, 0.000001),
            0
        )

        for invalid in (0, -0.000001):
            with self.assertRaises(ValueError):
                groove_crosssectional_area(invalid, 1, 1, 1)

            with self.assertRaises(ValueError):
                groove_crosssectional_area(1, invalid, 1, 1)

            with self.assertRaises(ValueError):
                groove_crosssectional_area(1, 1, invalid, 1)

            with self.assertRaises(ValueError):
                groove_crosssectional_area(1, 1, 1, invalid)

    def test_groove_crosssectional_area_elliptical_cutter_deep_cut(self):
        self.assertAlmostEqual(
            groove_crosssectional_area(12, 2.5, 10, 2.5),
            (2 * 2.5) + (39.269908169872416 / 2)
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(7, 5, 5, 5),
            (2 * 5) + (39.269908169872416 / 2)
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(12, 4, 10, 2.5),
            (12 * 1.5) + (2 * 2.5) + (39.269908169872416 / 2)
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(7, 7, 5, 5),
            (7 * 2) + (2 * 5) + (39.269908169872416 / 2)
        )

        with self.assertRaises(ValueError):
            groove_crosssectional_area(3, 2, 3.01, 2)

    def test_groove_crosssectional_area_elliptical_cutter_shallow_cut(self):
        self.assertAlmostEqual(
            groove_crosssectional_area(10, 0.5, 8, 2),
            4.167495704845848
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(10, 0.5, 12, 3),
            3.9341530159848164
        )

        self.assertAlmostEqual(
            groove_crosssectional_area(9.682458365518542, 3, 10, 4),
            21.521092250297087
        )

        with self.assertRaises(ValueError):
            groove_crosssectional_area(9.6824583654, 3, 10, 4)

    def test_groove_crosssectional_area_input_range(self):
        height = 2
        for i in range(1, 100000):
            width = i / 10000
            groove_crosssectional_area(width, height, width, height),

    def test_groove_crosssectional_area_circle(self):
        """
        A circle of radius 'x' should have the same area as two half parts of groove_width=2*x, groove_height=x, cutter_width=2*x, cutter_height=x
        """
        x = 10
        self.assertAlmostEqual(
            2 * groove_crosssectional_area(2 * x, x, 2 * x, x),
            math.pi * pow(x, 2),
        )

    def test_groove_crosssectional_area_square(self):
        """
        A square of side length 'x' should have the same area as two half parts of groove_width=x, groove_height=x/2, cutter_width=0, cutter_height=0
        """
        x = 10
        self.assertAlmostEqual(
            2 * groove_crosssectional_area(x, x / 2, 0.000001, 0.000001),
            x * x,
        )