# Project Imports
from framework.BuildingBlock import BuildingBlock, autostart
from framework.example.signal.rampGenerator import RampGenerator
from framework.example.signal.noiseApplicator import NoiseApplicator


@autostart
class SignalGenerator(BuildingBlock):
    """Building Block for Generating a Ramp Signal"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._architecture = "CircuitGraph"
        self._version = "1"
        self._description = "Generates a Noised Ramp Signal"
        self._category = "Generator"
        self._inputData = [int]
        self._outputData = [float]
        self._parameter = {"length": int, "period": int, "noise": str}

        self.rampGenerator = RampGenerator(name="RampGen")
        self.littleNoise = NoiseApplicator(name="LittleNoise")
        self.muchNoise = NoiseApplicator(name="MuchNoise")


    def _main(self, inputData, length=100, period=10, noise=None):

        signal = self.rampGenerator(None, length=length, period=period)

        if noise == "little":
            signal = self.littleNoise(signal)

        if noise == "much":
            signal = self.muchNoise(signal)

        return signal
