import re
from xml.etree import ElementTree as ET

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

def format_length(val: float, decimals=const.LENGTH_DISPLAY_DECIMALS) -> str:
    if val is None:
        return ''
    return ('{0:.%df}' % decimals).format(val).rstrip('0').rstrip('.')

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