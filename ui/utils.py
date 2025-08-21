"""utils.py: Helper Functions for Circuitgraph"""

# System Imports
from typing import Tuple, Union

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2022, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"


Number = Union[int, float]


def bbox_to_pos(x_min: Number, x_max: Number, y_min: Number, y_max: Number, rot: Number = 0) -> dict:
    """Converts a Bounding Box to a Position as Used in EngGraph"""

    return {"x": (x_min + x_max) / 2.0, "y": (y_min + y_max) / 2.0,
            "width": abs(x_max - x_min), "height": abs(y_max - y_min), "rotation": rot}


def pos_to_bbox(pos: dict) -> Tuple[int, int, int, int, int]:
    """Converts a Position as Used in EngGraph to a Bounding Box"""

    return round(pos['x'] - abs(pos['width'] / 2.0)),  \
           round(pos['x'] + abs(pos['width'] / 2.0)),  \
           round(pos['y'] - abs(pos['height'] / 2.0)), \
           round(pos['y'] + abs(pos['height'] / 2.0)), \
           pos['rotation']


def encode_color(color):
    """Encodes a Color to Hex"""

    if not color:
        return ""

    return f"#{'0' if color[2] < 16 else ''}{hex(color[2])[2:]}" \
           f"{'0' if color[1] < 16 else ''}{hex(color[1])[2:]}" \
           f"{'0' if color[0] < 16 else ''}{hex(color[0])[2:]}"
