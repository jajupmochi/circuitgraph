"""spiceRefinerBB.py: BB for Illustrating Data Transforming"""

# System Imports
import time

# Project Imports
from framework.BuildingBlock import BuildingBlock, exposed, autostart


@autostart
class SpiceRefiner(BuildingBlock):
    """Refines Selected Tasty Spices"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._architecture = "CircuitGraph"
        self._version = "0.0.2"
        self._category = "Transformer"


    @exposed
    def selectGarlic(self, garlicForRefinement: dict) -> dict:
        """Hand-Picks the best Garlic for your Enjoyment."""

        refinementTime = self.setting("refinementTime", 1)
        print(f"I will wait for such a long time: {refinementTime}")
        time.sleep(refinementTime)
        garlicForRefinement["good"] = True

        return garlicForRefinement
