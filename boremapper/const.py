import os


APP_NAME = 'BoreMapper'
APP_HANDLE = 'BoreMapper'
APP_ORG_HANDLE = 'EastDesire'
APP_VERSION = '0.1.0'
APP_AUTHOR = 'Jan Odvárko'
APP_AUTHOR_EMAIL = 'jan@odvarko.cz'
APP_DESCRIPTION = 'A tool for mapping the bore profile of woodwind instruments with a split bore.'
APP_REPO_URL = 'https://github.com/EastDesire/boremapper'

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

DETAIL_PANEL_MIN_WIDTH = 350
DETAIL_PANEL_MAX_WIDTH = 650

DETAIL_WIDGET_SPACING = 8
LAYOUT_GROUPS_SPACING = 30

APP_DIR = os.path.dirname(os.path.realpath(__file__))
RESOURCES_DIR = APP_DIR + '/resources'