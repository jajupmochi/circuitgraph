# System Imports
from random import random

# Project Imports
from framework.BuildingBlock import BuildingBlock, autostart


@autostart
class NoiseApplicator(BuildingBlock):
    """Building Block for Generating a Ramp Signal"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._architecture = "CircuitGraph"
        self._version = "1"
        self._description = "Applies Random Noise to an Input Signal"
        self._category = "Transformer"
        self._inputData = [int]
        self._outputData = [float]
        self._parameter = {}


    def _main(self, inputData):

        outputData = [i+self.setting("mean", 1)+(random()-0.5)*self.setting("std", 1) for i in inputData]

        return outputData
