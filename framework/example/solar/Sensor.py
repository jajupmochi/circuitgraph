
# System Imports
from datetime import datetime

# Project Imports
from framework.BuildingBlock import BuildingBlock, exposed, autostart



@autostart
class Sensor(BuildingBlock):
    """Building Block for Reading Physical Sensors"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._architecture = "CircuitGraph"
        self._version = "0.0.1"
        self._description = "Adapter to Physical Sensors"
        self._category = "Generator"

        self._type = "Temperature"
        self._unit = "Degree Centigrade"
        self._location = ""


    @exposed
    def data(self):
        """Returns Timestamped Sensor Data Readings"""

        return {"time": str(datetime.now()), "value": self._read_sensor()}


    @exposed
    def metadata(self):
        """Returns the Sensor's Standard Information"""

        return {"type": self._type, "unit": self._unit, "location": self._location}


    def _read_sensor(self):
        """Physical Sensor Reading Implementation"""

        from random import random
        return 42.0+random() * 3
