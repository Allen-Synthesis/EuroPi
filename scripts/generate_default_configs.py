#!/usr/bin/env python3
"""
This script can be used to generate default configuration files for all EuroPiScripts that use the 
configuration feature. Simply execute this script from the root of the project directory.

   $ python3 scripts/generate_default_configs.py

The config files will be generated in the a `config` directory. The files can be edited and then
loaded onto the pico in a `config` directory in the root of the pico's file system.
"""
import os
import sys
import importlib
from types import ModuleType


def find_europi_scripts():
    modules = sorted(
        set(
            f.partition(".")[0]
            for f in os.listdir(importlib.import_module("contrib").__path__[0])
            if f.endswith((".py", ".pyc", ".pyo")) and not f.startswith("__init__.py")
        )
    )

    pkg = __import__("contrib", fromlist=modules)
    visited = set()  # avoid processing scripts twice if they get imported twice (eg by the menu)

    # most of this code was taken from https://stackoverflow.com/a/3507271
    for m in modules:
        module = getattr(pkg, m)
        if type(module) == ModuleType:
            for c in dir(module):
                klass = getattr(module, c)
                if (
                    isinstance(klass, type)
                    and klass is not EuroPiScript
                    and issubclass(klass, EuroPiScript)
                ):
                    if klass not in visited:
                        visited.add(klass)
                        yield klass


def generate_default_config(europi_script):
    spec = ConfigSpec(europi_script.config_points())

    if spec:  # don't bother generating empty config files
        print(f"Generating: {ConfigFile.config_filename(europi_script)}")
        ConfigFile.save_config(europi_script, spec.default_config())


def mock_time_functions():
    # a file in the mock package doesn't work for the `time` package, so we will have to monkey
    # patch the missing functions to make the imports in contrib scripts succeed

    import time

    def noop():
        pass

    time.sleep_ms = noop
    time.ticks_ms = noop
    time.ticks_add = noop
    time.ticks_diff = noop


if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath("software/firmware"))
    sys.path.insert(0, os.path.abspath("software"))
    sys.path.insert(0, os.path.abspath("software/tests/mocks"))

    mock_time_functions()

    ConfigSpec = importlib.import_module("configuration").ConfigSpec
    ConfigFile = importlib.import_module("configuration").ConfigFile
    EuroPiScript = importlib.import_module("europi_script").EuroPiScript
    EuroPiConfig = importlib.import_module("europi_config").EuroPiConfig

    print(
        """
Generating default config files for any contrib scripts that have config points defined.
Edit and upload to /config on the pico to change a script's configuration.
"""
    )

    generate_default_config(EuroPiConfig)

    for script in find_europi_scripts():
        generate_default_config(script)
