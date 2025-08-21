"""symbol.py Symbol Management"""

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2022-2024, DFKI & RPTU & Others"
__status__ = "Development"

# System Imports
import json
from os import listdir
from os.path import join
from pathlib import Path
from typing import NamedTuple, Dict, List, Optional

# Project Imports
from converter.core.geometry import Point, Line, Circle, Polygon

CUR_ABS_DIR = Path(__file__).parent.resolve()


class Port(NamedTuple):
    name: str
    position: Point


class Property(NamedTuple):
    name: str
    value: Optional[any]
    position: Optional[Point]


class Symbol(NamedTuple):
    name: str
    geometry: list
    ports: List[Port] = []
    properties: List[Property] = []


def load_symbols() -> Dict[str, Symbol]:
    """Loads all JSON Files from the Symbols Folder"""

    file_names = [file_name for file_name in listdir(CUR_ABS_DIR / "../symbols") if file_name.endswith(".json")]
    symbols = {}

    for file_name in file_names:
        with open(CUR_ABS_DIR / f"../symbols/{file_name}") as symbol_file:
            file_content = json.load(symbol_file)

            if type(file_content) is dict:
                symbol_name = ".".join(file_name.split(".")[:-1])
                symbol_geo = []

                for item in file_content.get("geometry", []):

                    if item.get("type", "") == "Line":
                        symbol_geo.append(Line(Point(item['a']['x'], item['a']['y']),
                                               Point(item['b']['x'], item['b']['y']),
                                               None, None, None))

                    if item.get("type", "") == "Circle":
                        symbol_geo.append(Circle(item['center']['x'], item['center']['y'], item['radius'],
                                                 None, None, item.get("fill", False), None))

                    if item.get("type", "") == "Polygon":
                        symbol_geo.append(Polygon([[point['x'], point['y']] for point in item['points']],
                                                  None, None, item.get("fill", False), None))

                symbol_ports = [Port(port['name'],
                                     Point(float(port['position']['x']),
                                           float(port['position']['y'])))
                                for port in file_content.get("ports", [])]

                symbols[symbol_name] = Symbol(symbol_name, symbol_geo, symbol_ports)

    return symbols


def store_symbols(symbols: dict) -> None:
    """Stores all Entries of the Provided Dict as Separate JSON Files in the Symbols Folder"""

    for name, geo in symbols.items():
        with open(join("converter", "symbols", f"{name}.json"), "w") as symbol_file:
            json.dump({"geometry": [{'type': 'Line',
                                     'a': {'x': line.a.x, 'y': line.a.y},
                                     'b': {'x': line.b.x, 'y': line.b.y}} for line in geo]}, symbol_file, indent=4)
