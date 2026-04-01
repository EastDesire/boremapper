#!/usr/bin/env python3

import math

import drawsvg as draw

strip_spacing = 10
margin_l = 60
margin_r = 31
margin_t = 22
margin_b = 22

variant_defaults = {
    'strip_width': 7,
    'marks': True,
    'mark_width': 0.1,
    'mark_color': '#808080',
    'mark_bleed': 2,
    'font_size': 4,
    'text_vertical_offset': 0.3,
}

variants = (
    {},
    {
        'strip_width': 7,
        'font_size': 5,
    },
    {
        'strip_width': 7,
        'font_size': 4,
    },
    {
        'strip_width': 6,
        'font_size': 4,
    },
    {
        'strip_width': 5,
        'font_size': 4,
    },
    {
        'strip_width': 5,
        'font_size': 3,
    },
    {
        'strip_width': 6,
        'font_size': 4,
    },
    {
        'strip_width': 6,
        'font_size': 3,
    },
    {
        'strip_width': 5,
        'font_size': 3,
    },
    {
        'strip_width': 4,
        'font_size': 3,
    },
    {
        'strip_width': 4,
        'font_size': 2.5,
    },
    {
        'strip_width': 6,
        'font_size': 4,
        'marks': False,
    },
    {
        'strip_width': 6,
        'font_size': 3,
        'marks': False,
    },
    {
        'strip_width': 5,
        'font_size': 3,
        'marks': False,
    },
    {
        'strip_width': 4,
        'font_size': 3,
        'marks': False,
    },
    {
        'strip_width': 4,
        'font_size': 2.5,
        'marks': False,
    },
)

def generate_measure(length: int, width: int, out_file: str):
    """
    :param length: Length of the measure in mm
    :param width: Width of the measure in mm
    :param out_file: Output SVG file to create
    """
    canvas_width = length + margin_l + margin_r
    canvas_height = width + margin_t + margin_b
    d = draw.Drawing(canvas_width, canvas_height, origin=(0, 0))
    i_last = math.ceil(length / 10)

    print('Canvas size: %d x %d' % (canvas_width, canvas_height))

    for row in range(0, math.ceil(width / strip_spacing)):
        y = margin_t + (row * strip_spacing)
        v = variant_defaults | variants[row % len(variants)]
        h = v['strip_width'] / 2
        mark_len = (v['strip_width'] - v['font_size']) / 2

        for i in range(0, i_last + 1):
            x = margin_l + (i * 10)
            tens = math.floor(i / 10)
            units = i % 10
            is_major = i % 10 == 0

            if i in (0, i_last):
                d.append(draw.Line(
                    x, y - v['mark_bleed'],
                    x, y + v['strip_width'] + v['mark_bleed'],
                    stroke='#000000',
                    stroke_width=v['mark_width'],
                ))
            else:
                if v['marks']:
                    # d.append(draw.Line(x, y, x, y + v['strip_width'], stroke=v['mark_color'], stroke_width=v['mark_width']))
                    d.append(draw.Line(
                        x, y - v['mark_bleed'],
                        x, y + mark_len,
                        stroke=v['mark_color'],
                        stroke_width=v['mark_width'],
                    ))
                    d.append(draw.Line(
                        x, y + v['strip_width'] + v['mark_bleed'],
                        x, y + v['strip_width'] - mark_len,
                        stroke=v['mark_color'],
                        stroke_width=v['mark_width'],
                    ))

                if is_major:
                    p = draw.Path(fill='#000000')
                    p.M(x, y)
                    p.L(x + h, y + h)
                    p.L(x, y + v['strip_width'])
                    p.L(x - h, y + h)
                    d.append(p)

                text = str(tens if is_major else units)
                text_color = '#FFFFFF' if is_major else '#000000'
                d.append(draw.Text(text, v['font_size'], x, y + h + v['text_vertical_offset'], fill=text_color, text_anchor='middle', center=True))

    d.save_svg(out_file)

def main():
    generate_measure(750, 550, 'measure.svg')

if __name__ == '__main__':
    main()
