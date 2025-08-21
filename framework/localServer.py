#!/usr/bin/env python3


# System Imports
import sys
import json
import subprocess
import os
from os.path import exists, join
import requests
import time
from datetime import datetime



FOLDER_LOG = "debug"


def load_settings(settings_file: str = 'settings.json') -> dict:
    """Loads the Settings from the Settings File"""

    if exists(settings_file):
        print(f"Using Settings file: {settings_file}")
        with open(settings_file) as sf:
            return json.load(sf)
    else:
        print(f"Can't find Settings file: {settings_file}")
        return {}


def check_bb(setting: dict) -> bool:
    """Checks the Function of a BB by Querying its Info Page"""

    try:
        time.sleep(1)
        return requests.get(f"http://{setting['host']}:{setting['port']}/info").status_code == 200

    except requests.exceptions.ConnectionError:
        return False


def execute_cmd(settings: dict):
    """Performs the specified CLI Command on Building Blocks Specified as Local Servers"""

    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"

    if not os.path.exists(FOLDER_LOG):
        os.mkdir(FOLDER_LOG)

    if cmd not in ["start", "stop"]:
        print(f"Invalid Command: {cmd}")
        return None

    for bb_name, bb_settings in settings.items():
        if 'host' in bb_settings and bb_settings['host'] == 'localhost':

            if cmd == "start":
                print(f"Starting Module: {bb_name}... ", end="")
                subprocess.run(["screen", "-d", "-m", "-S", f"BuildingBlock.{bb_name}",
                                "-L", "-Logfile", join(FOLDER_LOG, f"{bb_name}.{datetime.now()}.log"),
                                "python3", "-m", f"{bb_settings['module']}", bb_name])
                print("OK" if check_bb(bb_settings) else "FAIL")

            elif cmd == "stop":
                print(f"Stopping Module: {bb_name}")
                subprocess.run(["screen", "-X", "-S", f"BuildingBlock.{bb_name}", "quit"])


settings_current = load_settings()
execute_cmd(settings_current)
