"""spiceGeneratorAdvanced.py: BB for Illustrating Inheritance"""

# Project Imports
from framework.BuildingBlock import exposed, autostart
from framework.example.spice.spiceGenerator import SpiceGenerator

@autostart
class SpiceGeneratorAdvanced(SpiceGenerator):
    """Generates all Kinds of Delicious Spices, even more than a normal Generator!"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._version = "0.0.2"


    @exposed
    def cinnamon(self) -> dict:
        """Gives You Cinnamon, hot yet sweet."""

        return {"type": "cinnamon", "unit": "stick", "amount": 3, "good": False,
                "weight": 34.523, "weights": [11.232, 10.23423, 14.879]}


    @exposed
    def sugar(self) -> dict:
        """Sugar is not only a spice, it is essential to all form of life!"""

        return {"type": "sugar", "unit": "crystal", "amount": 3, "good": False,
                "weight": 34.523, "weights": [11.232, 10.23423, 14.879]}
