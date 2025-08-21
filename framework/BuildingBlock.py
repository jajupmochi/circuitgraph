
# System Imports
import requests
import json
import os
import sys
import __main__
import inspect
from typing import Tuple
from datetime import datetime

# Third-Party Imports
from flask import Flask
import flask



def exposed(method: callable, method_name: str = None, bb=None) -> callable:
    """Decorator for exposing arbitrary methods as Web Service"""

    BuildingBlock._register_method(method, method_name, bb)
    return BuildingBlock.proxy_factory(method, method_name, bb)


def autostart(bb_cls):
    """Decorator for Automatically Running a BB Server for Direct Script Invocations"""

    if inspect.getfile(bb_cls) == inspect.getfile(__main__):
        bb_cls._info_msg(" Autostarting")
        bb = bb_cls(name=sys.argv[1] if len(sys.argv) > 1 else "", prevent_proxy=True)
        bb.serve()

    else:
        return bb_cls


class BuildingBlock:
    """Module Framework Base Class"""

    debug = False #also allow to set server host
    # TODO Wording setting vs. config
    __global_settings = {}
    _method_registry = {}  # Rename -> __exposed_class_method

    def __init__(self, name="", host=None, port=None, prevent_proxy=False):
        self._architecture = None
        self._name = name
        self._class = type(self).__name__
        self._version = "0.0.1"
        self._description = type(self).__doc__
        self._category = None
        self._inputData = None
        self._outputData = None
        self._parameter = None
        self.__is_proxy = False
        self.__is_server = False
        self.__remote_host = None
        self.__remote_port = None
        self.__exposed_own_methods = None
        self.__settings = {}
        self.__apply_settings(host, port, prevent_proxy)


    @property
    def proxy(self):
        """Returns whether or not this BB works by querying another Remote BB Server"""

        return self.__is_proxy


    @property
    def server(self):
        """Return whether or not this BB serves its Methods via a Web Server"""

        return self.__is_server


    @property
    def name(self):
        """BB Name Property"""

        return self._name


    @property
    def descriptor(self) -> dict:
        """Generates a BB Descriptor Object"""

        meth_descriptors = [(meth_name, meth.__doc__, inspect.signature(meth))
                            for meth_name, meth in self._exposed_methods.items()]

        return {"architecture": self._architecture,
                "class": self._class,
                "name": self._name,
                "version": self._version,
                "description": self._description,
                "category": self._category,
                "methods": {meth_name: {"description": meth_doc,
                                        "parameters": [{"name": meth_sig.parameters[p].name,
                                                        "type": meth_sig.parameters[p].annotation.__name__
                                                        if meth_sig.parameters[p].annotation else None}
                                                       for p in meth_sig.parameters
                                                       if meth_sig.parameters[p].name != "self"],
                                        "return": meth_sig.return_annotation.__name__
                                        if meth_sig.return_annotation else None}
                            for meth_name, meth_doc, meth_sig in meth_descriptors},
                "input": str(self._inputData),
                "output": str(self._outputData),
                "parameter": {pName: str(pType)
                              for pName, pType in
                              (self._parameter.items() if self._parameter else [])}}


    @classmethod
    def _info_msg(cls, text: str) -> None:

        print(f"[{datetime.now()}] [{cls.__name__}]{text}")


    def _expose_method(self, method: callable, method_name: str, server: Flask) -> None:
        """Adds a Method to the BB Server under a given Name"""

        def serv_handle(method, method_name):
            """Factory for Server Handler Functions"""

            def serv_method():
                """Server Handler"""

                self._info_msg(f".{method_name}() Remote Call Received")
                data_query = flask.request.get_json()
                data_input = data_query["parameters"]
                data_output = method(self, **data_input)
                self._info_msg(f".{method_name}() Remote Call Finished")

                response = flask.jsonify({"result": data_output})

                return response

            serv_method.__name__ = f"{method_name}_handler"
            return serv_method

        self._info_msg(f".{method_name}() Exposing Method...")
        server.add_url_rule(f"/{method_name}",
                            view_func=serv_handle(method, method_name),
                            methods=['GET', 'POST'])


    def serve(self) -> None:
        """Starts an HTTP Server that serves the main() Method"""

        if self.server:
            self._info_msg("Error: Server already running")
            return None

        self.__is_server = True
        server = Flask(self._name)

        @server.route("/info")
        def bb_server_info():
            """Returns a BB Descriptor Object"""

            return self.descriptor

        @server.route("/main", methods=['GET', 'POST'])
        def bb_server_main():
            """Serves the BB Main Function"""

            # add somewhere here: add_url_rule

            self._info_msg(f" Call FROM REMOTE")
            data_query = flask.request.get_json()
            inputData = data_query["input"]
            parameters = data_query["parameters"]
            outputData = self._main(inputData, **parameters)
            self._info_msg(f" Call Finished")

            response = flask.jsonify({"output": outputData})

            return response

        # Expose Decorated Methods
        for method_name, method in self._exposed_methods.items():
            self._expose_method(method, method_name, server)

        server.run(port=self.__remote_port)


    def __integrity(self):
        """Performs an Integrity Check"""

        return True


    @classmethod
    def read_settings(cls, settingsFile="settings.json") -> None:
        """Reads a Global Settings File to configure Remote Calls and User-Defined Settings"""

        if os.path.exists(settingsFile):
            with open(settingsFile) as sf:
                cls.__global_settings = json.load(sf)
            cls._info_msg(f" Applied Remote Configuration File: {settingsFile}")

        else:
            cls._info_msg(f" Can't find Remote Configuration File: {settingsFile}")


    def __apply_settings(self, host: str, port: str, prevent_proxy: bool = False) -> None:
        """Applies the Global Settings to Itself"""
        if host and port:
            if type(self).__name__ == "BuildingBlock":
                self.__set_endpoint(host, port, proxy=True)
                self.__copycat()

            else:
                print("Error: Remote Parameters should be given directly only to Bare BuildingBlock Instances!")
                print("Info: For regular remote communication use configuration via settings.json")

        else:
            if self._name in self.__global_settings:
                self.__settings = self.__global_settings[self._name].get("settings", {})
                if "host" in self.__global_settings[self._name] and \
                   "port" in self.__global_settings[self._name]:
                    self.__set_endpoint(self.__global_settings[self._name]["host"],
                                        self.__global_settings[self._name]["port"],
                                        not prevent_proxy)


    def __set_endpoint(self, host: str, port: str, proxy=False):
        """Sets the Endpoint for this BB"""

        self.__is_proxy = proxy
        self.__remote_host = host
        self.__remote_port = port


    def __copycat(self):
        """Replicates Exposed Methods and Descriptors of the remote BB to Itself"""

        remote_info = requests.get(f"http://{self.__remote_host}:{self.__remote_port}/info").json()

        self._architecture = remote_info["architecture"]
        self._name = remote_info["name"]
        self._class = remote_info["class"]
        self._version = remote_info["version"]
        self._description = remote_info["description"]
        self._category = remote_info["category"]
        self._inputData = remote_info["input"]
        self._outputData = remote_info["output"]
        self._parameter = remote_info["parameter"]

        for meth_name, meth_descriptor in remote_info["methods"].items():
            setattr(self, meth_name, exposed(lambda x: None, meth_name, self))


    def setting(self, name: str, fallback=None):
        """Returns an Object's User-Definable Setting"""

        return self.__settings.get(name, fallback)


    def __call__(self, inputData, **parameters):
        """Remote/Local Wrapper for the main() Method"""

        if self.__is_proxy:
            self._info_msg(f" Call REMOTE")
            result = requests.post(f"http://{self.__remote_host}:{self.__remote_port}/main",
                                   json={"input": inputData, "parameters": parameters})
            outputData = result.json()["output"]

        else:
            self._info_msg(f" Call LOCAL")
            outputData = self._main(inputData, **parameters)

        self._info_msg(f" Call Finished")

        return outputData


    def _main(self, inputData, parameters):
        """Main Method, to be overwritten in Subclass"""

        print("ERROR: main() Method not defined")


    @classmethod
    def _register_method(cls, method: callable, method_name: str = None, bb=None) -> None:
        """Registers a BB Method in the Global Method Registry for Optional Web Exposure

        By default, the method is registered the class level (for exposed decorator usage
        in regular BB method definitions). Optionally, a BB instance can be supplied for
        registering a method for this specific instance (used for proxying arbitrary BBs)."""

        bb_cls = f"BuildingBlock@{id(bb)}"
        bb_meth = method_name

        if not method_name:
            bb_cls, bb_meth = method.__qualname__.split(".")

        if bb_cls in cls._method_registry:
            cls._method_registry[bb_cls][bb_meth] = method

        else:
            cls._method_registry[bb_cls] = {bb_meth: method}

        cls._info_msg(f" {bb_cls}.{bb_meth}() Registered for Possible Exposure")


    @staticmethod
    def proxy_factory(method: callable, method_name: str = None, bb=None) -> callable:
        """Returns a Wrapped Version of the given Method

        See BuildingBlock._register_method() for Optional Parameter Usage"""

        def proxy(*args, **kwargs):
            """Wrapped Version of the given Method for local/remote Calls"""

            obj = bb if bb else args[0]
            cls = obj.__class__
            cls_name = obj.__class__.__name__
            meth_name = method_name if method_name else method.__name__

            if obj.__is_proxy:
                cls._info_msg(f".{meth_name}() -> REMOTE")
                result_remote = requests.post(f"http://{obj.__remote_host}:{obj.__remote_port}/{meth_name}",
                                       json={"parameters": {**kwargs}})
                result = result_remote.json()["result"]

            else:
                cls._info_msg(f".{meth_name}() -> LOCAL")
                result = method(*args, **kwargs)

            cls._info_msg(f".{meth_name}() -> FINISHED")

            return result

        return proxy


    @property
    def _exposed_methods(self) -> dict:
        """Return a Description of all Exposed Methods of the BB's Class"""

        methods = {}
        ancestors = [cls.__name__ for cls in self.__class__.__mro__ if cls.__name__ != "object"]
        
        for ancestor in ancestors:
            if ancestor in self._method_registry:
                methods = {**methods, **self._method_registry[ancestor]}

        return methods


    def _endpoint_by_name(self, bb_name: str) -> Tuple[str, int]:
        """Determines the Remote Endpoint of an Arbitrary BB given its name in the Settings File"""

        host = ""
        port = 0

        if bb_name in self.__global_settings:
            if "host" not in self.__global_settings[bb_name] or "port" not in self.__global_settings[bb_name]:
                print(f"Error: Endpoint of BB {bb_name} not properly defined")

            else:
                host = str(self.__global_settings[bb_name]["host"])
                port = int(self.__global_settings[bb_name]["port"])

        else:
            print(f"Error: Undefined BB Name: {bb_name}")

        return host, port


# Read Default Settings
BuildingBlock.read_settings()
