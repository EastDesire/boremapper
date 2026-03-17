import os


APP_NAME = 'BoreMapper'
APP_HANDLE = 'BoreMapper'
APP_VERSION = '0.1.0'

ORGANIZATION_HANDLE = 'JanOdvarko'

# When comparing or storing floats, we round them to this number of decimals to avoid issues with floating point error
FLOAT_SAFE_DECIMALS = 10

LENGTH_UNITS = 'mm'
LENGTH_DISPLAY_DECIMALS = 2

BORE_PARTS = ('bottom', 'top')

BORE_TABLE_WIDTH = 700

# TODO: <size_factor> probably no longer needed, when using "stretch" resize mode on table header

# <label>, <editable>, <size_factor>, <description>
BORE_TABLE_COLUMNS = [
    ('b W', True, 1.0, 'Bottom: Groove Width'),
    ('b H', True, 1.0, 'Bottom: Groove Height'),
    ('b CW', True, 1.0, 'Bottom: Cutter Width'),
    ('b CH', True, 1.0, 'Bottom: Cutter Height'),
    ('t W', True, 1.0, 'Top: Groove Width'),
    ('t H', True, 1.0, 'Top: Groove Height'),
    ('t CW', True, 1.0, 'Top: Cutter Width'),
    ('t CH', True, 1.0, 'Top: Cutter Height'),
    ('D', True, 1.0, 'Diameter'),
]

BORE_TABLE_MIN_COLUMN_WIDTH = 70
BORE_TABLE_MAX_COLUMN_WIDTH = 150

DOCUMENT_WINDOW_WIDTH = BORE_TABLE_WIDTH + 100
DOCUMENT_WINDOW_HEIGHT = 600

INSERT_POSITIONS_RANGE_MIN = -10000
INSERT_POSITIONS_RANGE_MAX = 10000

APP_DIR = os.path.dirname(os.path.realpath(__file__))