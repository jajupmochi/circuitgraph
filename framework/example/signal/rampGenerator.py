
# Project Imports
from framework.BuildingBlock import BuildingBlock, autostart


@autostart
class RampGenerator(BuildingBlock):
    """Building Block for Generating a Ramp Signal"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._architecture = "CircuitGraph"
        self._version = "1"
        self._description = "Generates a Ramp Signal of adjustable length and Frequency"
        self._category = "Generator"
        self._inputData = None
        self._outputData = [int]
        self._parameter = {"length": int, "period": int}


    def _main(self, inputData, length=20, period=4):

        outputData = [i % period for i in range(length)]

        return outputData
