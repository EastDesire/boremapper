import os


APP_NAME = 'BoreMapper'
APP_HANDLE = 'BoreMapper'
APP_VERSION = '0.1.0'

ORGANIZATION_HANDLE = 'JanOdvarko'

# When comparing or storing floats, we round them to this number of decimals to avoid issues with floating point error
FLOAT_SAFE_DECIMALS = 10

LENGTH_UNITS = 'mm' # TODO: remove after UNITS are implemented
LENGTH_DISPLAY_DECIMALS = 2 # TODO: remove after UNITS are implemented

# TODO: use
# (<mm_conversion_factor>, <display_decimals>)
UNITS = {
    'mm': (1, 2),
    'in': (25.4, 3),
}

BORE_PARTS = ('bottom', 'top')

BORE_TABLE_WIDTH = 700 # TODO: smaller?

# (<label>, <editable>, <description>)
BORE_TABLE_COLUMNS = [
    ('b W', True, 'Bottom: Groove Width'),
    ('b H', True, 'Bottom: Groove Height'),
    ('b CW', True, 'Bottom: Cutter Width'),
    ('b CH', True, 'Bottom: Cutter Height'),
    ('t W', True, 'Top: Groove Width'),
    ('t H', True, 'Top: Groove Height'),
    ('t CW', True, 'Top: Cutter Width'),
    ('t CH', True, 'Top: Cutter Height'),
    ('D', True, 'Diameter'),
]

BORE_TABLE_MIN_COLUMN_WIDTH = 70
BORE_TABLE_MAX_COLUMN_WIDTH = 150

DOCUMENT_WINDOW_WIDTH = BORE_TABLE_WIDTH + 100
DOCUMENT_WINDOW_HEIGHT = 600

INSERT_POSITIONS_RANGE_MIN = -10000
INSERT_POSITIONS_RANGE_MAX = 10000

APP_DIR = os.path.dirname(os.path.realpath(__file__))