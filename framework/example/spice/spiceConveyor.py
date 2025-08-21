"""Conveyor.py: BB for Illustrating Threads and State Machines"""

# Project Imports
from framework.BuildingBlock import BuildingBlock, exposed, autostart


@autostart
class SpiceConveyor(BuildingBlock):
    """A Conveyor Belt"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._architecture = "CircuitGraph"
        self._version = "1"
        self._description = "Generates all Kinds of Delicious Spices"
        self._category = "Transformer"


    @exposed
    def turn_on(self, amount: int = 5, quality: str = "good") -> str:

        return f"Here you got {amount} pieces of {quality} quality peppercorns."


    @exposed
    def turn_off(self, amount: int) -> str:

        return f"Here you got {amount} pieces of  quality peppercorns."
