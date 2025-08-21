
# System Imports
import os
import json

# Project Imports
from framework.BuildingBlock import BuildingBlock, exposed, autostart


@autostart
class Database(BuildingBlock):
    """Building Block for Storing Data Permanently"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._architecture = "CircuitGraph"
        self._version = "1"
        self._description = "Generates a Ramp Signal of adjustable length and Frequency"
        self._category = "Database"

        self._storage_path = self.setting("storage_path", "db.json")
        self._data = {}
        self._load_storage()


    @exposed
    def read(self, key: str):
        """Reads and Returns key Data"""

        if key in self._data:
            return self._data[key]

        else:
            self._info_msg(f" Couldn't find key {key}")

        return []


    @exposed
    def write(self, key: str, data: list):
        """Writes Data to Key Address"""

        self._data[key] = data
        self._save_storage()


    @exposed
    def add(self, key: str, date):
        """Appends date to existing entry"""

        existing = self.read(key)
        self.write(key, (existing if type(existing) is list else [existing]) + [date])


    def _load_storage(self):
        """Loads Data from File System to the Internal DB"""

        if os.path.isfile(self._storage_path):
            with open(self._storage_path) as storage:
                self._data = json.loads(storage.read())

        else:
            self._info_msg(" Warning: Data File does not exist")

        return {}


    def _save_storage(self):
        """Stores the Internal DB to the File System"""

        with open(self._storage_path, "w") as storage:
            storage.write(json.dumps(self._data))
