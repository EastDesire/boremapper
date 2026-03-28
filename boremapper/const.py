import os


APP_NAME = 'BoreMapper'
APP_HANDLE = 'BoreMapper'
APP_VERSION = '0.1.0'

ORGANIZATION_HANDLE = 'JanOdvarko'

DOCUMENT_XML_VERSION = '0.1'

# When comparing or storing floats, we round them to this number of decimals to avoid issues with floating point error
FLOAT_SAFE_DECIMALS = 10

# Maximum float value accepted as input (after converting it to internal representation in mm)
MAX_INTERNAL_FLOAT = pow(2, 24)

SPINBOX_MAX_RANGE_MM = 10000

MAX_POSITIONS_TO_INSERT = 1000

BORE_PARTS = ('bottom', 'top')

# (<label>, <editable>, <description>)
BORE_TABLE_COLUMNS = [
    ('W b', True, 'Width of the Groove (bottom)'),
    ('H b', True, 'Height of the Groove (bottom)'),
    ('CW b', True, 'Cutter Width (bottom)'),
    ('CH b', True, 'Cutter Height (bottom)'),
    ('W t', True, 'Width of the Groove (top)'),
    ('H t', True, 'Height of the Groove (top)'),
    ('CW t', True, 'Cutter Width (top)'),
    ('CH t', True, 'Cutter Height (top)'),
    ('D', True, 'Diameter'),
]

DOCUMENT_WINDOW_WIDTH = 1280
DOCUMENT_WINDOW_HEIGHT = 720

BORE_TABLE_MIN_COLUMN_WIDTH = 70
BORE_TABLE_MAX_COLUMN_WIDTH = 150

GROUPS_SPACING = 30

APP_DIR = os.path.dirname(os.path.realpath(__file__))