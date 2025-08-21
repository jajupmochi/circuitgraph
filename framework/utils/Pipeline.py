
# System Imports
from datetime import datetime
from threading import Thread

# Project Imports
from framework.BuildingBlock import BuildingBlock, exposed, autostart


@autostart
class Pipeline(BuildingBlock):
    """Dynamically Configurable Pipeline BB"""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._architecture = "CircuitGraph"
        self._version = "1.1"
        self._category = "Infrastructure"
        self._nodes = []
        self._node_counter = 0
        self._jobs = []
        self._job_counter = 0

        if "name" in kwargs:
            for node in self.setting("nodes", fallback=[]):
                host, port = self._endpoint_by_name(node["name"])
                self.add(BuildingBlock(host=host, port=port),
                         node["method"] if "method" in node else "",
                         node["transform"] if "transform" in node else None)


    @exposed
    def add(self, bb: BuildingBlock, method: str = "", transform: dict = None) -> int:
        """Appends a Building Block the Pipeline"""

        self._info_msg(f" Adding BB {bb._name}")

        if transform:
            for para_name, para_source in transform.items():
                if "source" in para_source:
                    if para_source["source"] not in [node["id"] for node in self._nodes]:
                        para_source["source"] = [node["id"] for node in self._nodes
                                                 if node["block"].name == para_source["source"]][0]

        node = {"block": bb, "method": method, "transform": transform, "id": self._new_node_id()}
        self._nodes.append(node)
        return node["id"]


    @exposed
    def clear(self) -> None:
        """Removes all Building Blocks from the Pipeline"""

        self._nodes = []


    @exposed
    def structure(self) -> list:
        """Returns the Current Pipeline Structure and BB Connection Status"""

        return [{"number": 1, "alive": True, "method": "main", }]


    def _new_job_id(self):
        """Creates and Returns a New Job ID"""

        self._job_counter += 1
        return self._job_counter - 1


    def _new_node_id(self):
        """Creates and Returns a New Node ID"""

        self._node_counter += 1
        return self._node_counter - 1


    def _compile_paras(self, node: dict, job: dict):
        """Prepares the Parameters for the Method of a Given Node"""

        if node["transform"]:
            return {para_name: para_dev["value"] if "value" in para_dev else
                    (job["data"][para_dev["source"]] if para_dev["slice"] is None else
                     job["data"][para_dev["source"]][para_dev["slice"]])
                    for para_name, para_dev in node["transform"].items()}

        return {}


    def _jobworker(self, job: dict):
        """Handles the Execution Graph of one Job"""

        self._info_msg(f" [Jobworker {job['id']}] started.")
        for node in self._nodes:
            self._info_msg(f" [Jobworker {job['id']}] State {node['id']}")
            job["state"] = node["id"]
            job["data"][job["state"]] = getattr(node["block"], node["method"])(**self._compile_paras(node, job))

        job["state"] = "Done"


    @exposed
    def execute(self, **kwargs) -> int:
        """Triggers a new Process and returns the Job ID"""

        job = {"started": datetime.now(), "id": self._new_job_id(), "process": None,
               "state": 0, "data": {"initial": kwargs}}
        job["process"] = Thread(target=self._jobworker, args=[job])
        self._info_msg(f" Received New Job: {job['id']}")
        self._jobs.append(job)
        job["process"].start()

        return job["id"]


    @exposed
    def status(self, jobId: int) -> dict:
        """Returns the Status of a Job"""

        job = [job for job in self._jobs if job["id"] == jobId]

        if job:
            return job[0]["state"]

        return None


    @exposed
    def wait(self, jobId: int) -> None:
        """Blocks until the Job has finished"""

        job = [job for job in self._jobs if job["id"] == jobId]

        if job:
            job[0]["process"].join()

        return None


    @exposed
    def result(self, jobId: int, nodeId: int) -> dict:
        """Returns the Results of at a given Node for a Given Job"""

        job = [job for job in self._jobs if job["id"] == jobId]

        if job:
            return job[0]["data"][nodeId]

        return None
