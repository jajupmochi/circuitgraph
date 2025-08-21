# Framework

This repository contains a generic framework for python based, distributed computing via REST APIs. Its main idea is to encapsulate code fragments into classes which are referred to as **Building Blocks**.

These Building Blocks can be called seamlessly, i.e. the programmer does not need to be concerned with whether or nor a Building Block runs locally or on a remote location. Rather, the location of Building Blocks is configured via a **configuration** JSON file.

## Requirements
Apart from `python3.6`, this module assumes:

 - `requests`
 - `flask`
 - `matplotlib`

Furthermore to run start servers:

 - `screen`

## Usage
Utilizing the framework is illustrated by the mean of example modules.

### General
As Building Blocks are regular Python classes, method calls work as usual in a local setup. 

#### Running a single Building Block
Assuming that the Building Block is decorated with the `@autostart` decorator (should always be done), it can be run as a server directly via calling its containing script, e.g.:

```
python3 -m framework.example.signal.rampGenerator

```

#### Accessing a  Building Block via HTTP and CLI
Once a building block is running as a server, its `main()` method as well as all its methods decorated as `@exposed` can by accessed by `HTTP POST` queries. The following command asks the ramp generator sample building block to return a sequence of five ramps of length five:

```
curl -i -X POST -H 'Content-Type: application/json' -d '{"parameters":{"length": 25, "period": 5},"input":{}}' http://127.0.0.1:7000/main
```

#### Accessing a Remote Building Block in Python

Instances of `BuildingBlock` Subclasses can be used like other Python classes. Hence, they are typically composed in python code directly by invoking the subclass's constructor. However, for the sake of generality and for usage inside `Pipeline`s (where the specific `BuldingBlock` subclasses are unknown a priory), remote `BuildingBlock` instances can also be accessed by just specifying the remote endpoint. This way, the local BB becomes a clone of the remote BB (including access to the remote BB's `@exposed` methods):

```
>>> from framework.BuildingBlock import BuildingBlock
>>> b = BuildingBlock(host="localhost", port="8000")
>>> b.garlic()
[2022-09-14 03:53:56.114772] [BuildingBlock].garlic() -> REMOTE
[2022-09-14 03:53:56.130395] [BuildingBlock].garlic() -> FINISHED
{'amount': 3, 'good': False, 'type': 'garlic', 'unit': 'cloves', 'weight': 34.523, 'weights': [11.232, 10.23423, 14.879]}
```

#### Remarks

 - Don't Overwrite `BuildingBlock`'s essential methods like `main()`, `serve()`, `descriptor()` or `setting()` unless you really know what you do
 - Only have one BB in per Python File 
 - Always decorate BB classes with `@autostart`
 - Don't Clone/Instantiate the `BuildingBlock` Base Class unless you really have to



### Example Building Blocks
This repository comes with a set of sample building blocks as well as setting files and scripts for invoking them.
Please note that in order to perform these tests (and ideally for the whole project in general), the parent directory of the `framework` folder is **always** assumed as starting point.

#### Local Setup
As all calls are local by default, the entire scenario can be run locally by simply using:
```
$ python3 -m framework.example.signal.signalView
```

Note that there are two flavors of doing this:

 - If no `settings.json` is present in the working directory, then all calls are done as regular python calls
 - If the `settings.json` is present, but all BB entries lack the `host` field, calls are also done as regular python calls. This can be used to supply `settings` to individual BBs.

#### Remote Setup
As the remote calling of building blocks both requires the presence of a settings file and the availability of respective BB servers, both need to be generated first:

```
$ cp framework/example/signal/settings.json .
$ python3 -m framework.localServer
$ python3 -m framework.example.signal.signalView
```

Please note that the `localServer` script spawns the Building Block servers in detached [screen]("https://de.wikipedia.org/wiki/GNU_Screen") sessions. Therefore, stopping them is recommended after their utilization:

```
$ python3 -m framework.localServer stop
```

Likewise, every building block server exposes an info JSON file, which can be retrieved via an `HTTP GET` query. This can be even done using a web browser (e.g. Firefox) or CLI (in the case of the `SignalGenerator` sample):

```
curl http://127.0.0.1:7200/info
```

