
# Project Imports
from framework.BuildingBlock import BuildingBlock, exposed, autostart


@autostart
class Actuator(BuildingBlock):
    """Building Block for Controlling Physical Devices"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._architecture = "CircuitGraph"
        self._version = "0.0.1"
        self._description = "Generates a Ramp Signal of adjustable length and Frequency"
        self._category = "Consumer"


    @exposed
    def set_state(self, state: str):
        """Controls the Actuator"""

        pass
