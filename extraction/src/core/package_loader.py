"""package_loader.py: Utilities for Training/Inference"""

# System Imports
from inspect import getmembers
from importlib import import_module
from typing import Type

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"



def class_from_package(descriptor: str) -> Type:
    """Returns a Class given a Package/Class Descriptor String"""

    pack_name, cls_name = descriptor.split("/")
    cls_found = [value for key, value in getmembers(import_module(pack_name)) if key == cls_name]

    if not cls_found:
        print(f"ERROR: Can't find Class {cls_name} in Package {pack_name}\n")

    else:
        return cls_found[0]


def clsstr(cls: type) -> str:
    """"Returns a String Describing a Class"""

    return f"{cls.__module__}/{cls.__name__}"
