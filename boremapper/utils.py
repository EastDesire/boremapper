import re
from xml.etree import ElementTree as ET

from PySide6.QtGui import QColor

import const
from boremapper import exceptions


def is_float_str(string: str) -> bool:
    try:
        float(string)
        return True
    except ValueError:
        return False

def str_to_number(
    string: str,
    num_type: type,
    allow_empty: bool = False,
    value_if_empty = None,
    value_if_invalid = None,
    raise_if_invalid: bool = False
):
    if allow_empty and string.strip() == '':
        return value_if_empty
    try:
        out = num_type(string)
    except ValueError as e:
        if raise_if_invalid:
            raise e
        else:
            out = value_if_invalid
    return out

# TODO: remove? or just remove the default value from 'decimals' parameter
def format_length(value: float, decimals=const.LENGTH_DISPLAY_DECIMALS) -> str:
    if value is None:
        return ''
    return ('{0:.%df}' % decimals).format(value).rstrip('0').rstrip('.')

def units_def(symbol):
    u = const.UNITS[symbol]
    return {
        'mm_factor': u[0],
        'display_decimals': u[1],
    }

def length_from_mm(value, units_symbol) -> float:
    return value / units_def(units_symbol)['mm_factor']

def length_to_mm(value, units_symbol) -> float:
    return value * units_def(units_symbol)['mm_factor']

# TODO rem
#def convert_length(value, value_units, to_units):
#    ud_val = units_def(value_units)
#    ud_to = units_def(to_units)
#    return (value * ud_val['mm']) / ud_to['mm']

""" TODO: use?
def from_mm(value, to_units):
    return convert_length(value, 'mm', to_units)

def to_mm(value, from_units):
    return convert_length(value, from_units, 'mm')
"""

def has_same_values_in_columns(data: list) -> bool:
    """
    Takes two-dimensional data in format [row][column] and returns True if each column contains identical values in it,
    and each row has the same number of columns.
    """
    rows_count = len(data)

    if rows_count == 0:
        return True

    if [len(row) for row in data].count(len(data[0])) != rows_count:
        return False # Rows don't have the same number of columns

    for i, value in enumerate(data[0]):
        if [row[i] for row in data].count(value) != rows_count:
            return False # Column doesn't contain identical values

    return True

def format_position_for_speech(number: str, shorten_hundreds = True) -> str:
    out = str(number)
    if shorten_hundreds:
        # Convert e.g. '250' (two hundred and fifty) to '2 50' (two fifty)
        out = re.sub(
            r'^(-?\d)(\d\d)\b',
            lambda m: m[0] if m[2] == '00' else m[1] + ' ' + m[2],
            out
        )
    out = re.sub(r'^-', 'minus ', out)
    return out

def xml_build_float(val: float, decimals=const.FLOAT_SAFE_DECIMALS) -> str:
    if val is None:
        return ''
    return ('{0:.%df}' % decimals).format(val).rstrip('0').rstrip('.')

def xml_parse_float(val: str) -> float|None:
    if val.strip() == '':
        return None
    return float(val)

def xml_find_mandatory(e: ET.Element, path: str) -> ET.Element:
    found = e.find(path)
    if found is None:
        raise exceptions.XmlException('Element not found: %s' % path)
    return found

def lengths_range(range_start: float, range_end: float, step: float) -> list:
    values = []
    scale = pow(10, const.LENGTH_DISPLAY_DECIMALS)

    for pos_scaled in range(
        round(scale * range_start),
        round(scale * range_end) + 1,
        round(scale * step),
    ):
        values.append(round(pos_scaled / scale, const.LENGTH_DISPLAY_DECIMALS))
    return values

def text_color_to_red(color):
    return QColor.fromRgb(224, 0, 0) if color.lightnessF() < 0.5 else QColor.fromRgb(255, 96, 96)
    
def base_color_to_alternate(color):
    return color.lighter(124) if color.lightnessF() < 0.5 else color.darker(108)