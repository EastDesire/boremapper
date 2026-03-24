#!/usr/bin/env python3

import sys
import csv
from xml.etree import ElementTree as ET


MINOR_AXIS_FACTOR = 0.925 # 1.0 = circle


def parse_csv(file):
    out = []
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
        for row in reader:
            out.append({
                'position': row[0],
                'top_groove_width': row[1],
                'top_groove_height': row[2],
                'top_cutter_width': row[3],
                'bottom_groove_width': row[7],
                'bottom_groove_height': row[8],
                'bottom_cutter_width': row[9],
            })
    return out

def main():
    PARTS = ('top', 'bottom')

    records = parse_csv(sys.argv[1])
    e_root = ET.Element('boremapper-document')

    e_bore = ET.SubElement(e_root, 'bore')

    e_corrections = ET.SubElement(e_bore, 'corrections')
    for p in PARTS:
        e_corrections.set(p + '-groove-width', str(0))
        e_corrections.set(p + '-groove-height', str(0))

    e_points = ET.SubElement(e_bore, 'points')
    for record in records:
        e_point = ET.SubElement(e_points, 'point')
        e_point.set('position', record['position'])
        for p in PARTS:
            cutter_height_str = \
                str((float(record[p + '_cutter_width']) / 2) * MINOR_AXIS_FACTOR) if record[p + '_cutter_width'] else ''
            e_point.set(p + '-groove-width', record[p + '_groove_width'])
            e_point.set(p + '-groove-height', record[p + '_groove_height'])
            e_point.set(p + '-cutter-width', record[p + '_cutter_width'])
            e_point.set(p + '-cutter-height', cutter_height_str)

    e_wid_export = ET.SubElement(e_root, 'wid-export')
    e_wid_export.set('length-type', 'mm')
    e_wid_export.set('bore-origin', str(0))

    tree = ET.ElementTree(e_root)
    ET.indent(tree, space='  ')
    tree.write(sys.stdout, encoding='unicode')

if __name__ == '__main__':
  main()
