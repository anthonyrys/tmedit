TITLE = 'Tmedit'
FRAME_RATE = 60

SCREEN_DIMENSIONS = (1400, 800)
SCREEN_COLOR = (0, 0, 0)

import os
IMAGE_PATH = os.path.join('resources', 'images')
del os

from scripts.components import Button, Alert, Tile
from scripts.navbar import Navbar
from scripts.sidebar import Sidebar
from scripts.tools import TOOLS
from scripts.tmedit import Tmedit
