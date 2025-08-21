"""Clock.py: BB for Periodic Method Execution"""

# System Imports
import time
from threading import Thread

# Project Imports
from framework.BuildingBlock import BuildingBlock, exposed, autostart


@autostart
class Clock(BuildingBlock):
    """Periodic Method Execution"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._architecture = "CircuitGraph"
        self._version = "1.0"
        self._category = "Infrastructure"
        self._period = 10
        self._ticker = None
        self._status = False
        self._target_bb = None
        self._target_method = ""
        self._target_pars = {}

        if self.setting("start_immediate", False):
            self.start()

        if self.setting("period", False):
            self.set_period(self.setting("period", 10))

        if "name" in self.setting("target", {}):
            host, port = self._endpoint_by_name(self.setting("target")["name"])
            self._target_bb = BuildingBlock(host=host, port=port)
            self._target_method = self.setting("target")["method"] if "method" in self.setting("target") else "main"
            self._target_pars = {}  # TODO implement



    @exposed
    def get_period(self):
        """Returns the Invocation Time Interval (in Seconds)"""

        return self._period


    @exposed
    def set_period(self, newPeriod: int):
        """Returns the Invocation Time Interval (in Seconds, Between 1 and 1000)"""

        self._period = newPeriod


    @exposed
    def status(self):
        """Flag Indicating whether or not the Clock is Activated"""

        return self._status


    @exposed
    def start(self):
        """Starts the Clock with Immediate Invocation"""

        self._info_msg("Starting...")
        self._ticker = Thread(target=self._tick)
        self._status = True
        self._ticker.start()


    @exposed
    def stop(self):
        """Discontinues Method Invocation after the Next Iteration"""

        self._status = False


    def _tick(self):
        """Main Cycling Function"""

        while self._status:
            self._info_msg("Invoking Target...")
            self._target()
            self._info_msg(f"Sleeping {self._period} Seconds...")
            time.sleep(self._period)


    def _target(self):
        """The Periodically Executed Method"""

        if self._target_bb is not None:
            self._info_msg("Attempting to Execute Target")
            try:
                getattr(self._target_bb, self._target_method)(self._target_pars)
            except:
                self._info_msg("Error during Target Execution")

        else:
            self._info_msg("No Target to Execute")