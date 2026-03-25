import os


APP_NAME = 'BoreMapper'
APP_HANDLE = 'BoreMapper'
APP_VERSION = '0.1.0'

ORGANIZATION_HANDLE = 'JanOdvarko'

DOCUMENT_XML_VERSION = '0.1'

# When comparing or storing floats, we round them to this number of decimals to avoid issues with floating point error
FLOAT_SAFE_DECIMALS = 10

MAX_INPUT_VALUE = pow(2, 24)

SPINBOX_MAX_RANGE_MM = 10000

BORE_PARTS = ('bottom', 'top')

# (<mm_conversion_factor>, <display_decimals>, <step>)
UNITS = {
    'mm': (1, 2, 1),
    'cm': (10, 3, 0.1),
    'm': (1000, 5, 0.001),
    'in': (25.4, 3, 0.05),
    'ft': (304.8, 4, 0.005),
}

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

DOCUMENT_WINDOW_WIDTH = 1280
DOCUMENT_WINDOW_HEIGHT = 720

BORE_TABLE_MIN_COLUMN_WIDTH = 70
BORE_TABLE_MAX_COLUMN_WIDTH = 150

GROUPS_SPACING = 30

APP_DIR = os.path.dirname(os.path.realpath(__file__))