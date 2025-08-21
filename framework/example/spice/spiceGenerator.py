"""spiceGenerator.py: BB for Illustrating the exposed Decorator"""

# Project Imports
from framework.BuildingBlock import BuildingBlock, exposed, autostart


@autostart
class SpiceGenerator(BuildingBlock):
    """Generates various Kinds of Delicious Spices"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._architecture = "CircuitGraph"
        self._version = "0.0.2"
        self._category = "Generator"


    @exposed
    def pepper(self, amount: int = 5, quality: str = "good") -> str:
        """Gives You Pepper, a Very Good Replacement of Salt."""

        print(f"I am a sample message displayed at the EXECUTION side. I am so {quality}")
        return f"Here you got {amount} pieces of {quality} quality peppercorns."


    @exposed
    def garlic(self) -> dict:
        """Gives You Garlic, a Tasty, Hot and Very Healthy Spice."""

        return {"type": "garlic", "unit": "cloves", "amount": 3, "good": False,
                "weight": 34.523, "weights": [11.232, 10.23423, 14.879]}


    def salt(self, amount: int = 10) -> str:
        """Gives You Salt"""

        return f"Here you got {amount} grams of salt."
