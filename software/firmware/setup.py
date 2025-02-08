# Copyright 2024 Allen Synthesis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from setuptools import setup

__version__ = ""
exec(open("./version.py").read())


def build_firmware_module_list():
    import os

    dirs = {"experimental", "tools"}
    excluded = {"__init__.py", "setup.py"}

    # grab files from the local directory first
    modules = [f[:-3] for f in os.listdir(".") if f.endswith(".py") and not f in excluded]

    # add any modules in additional directories
    for d in dirs:
        for root_dir, subdirs, files in os.walk(d):
            for f in files:
                if f.endswith(".py") and not f in excluded:
                    modules.append(root_dir.replace("/", ".") + "." + f[:-3])

    return modules


setup(
    name="micropython-europi",
    version=__version__,
    description="EuroPi module for MicroPython",
    long_description="""The EuroPi is a fully user reprogrammable EuroRack module based on the Raspberry Pi Pico, which allows users to process inputs and controls to produce outputs based on code written in Python.""",
    url="https://github.com/Allen-Synthesis/EuroPi",
    author="Allen Synthesis",
    author_email="contact@allensynthesis.co.uk",
    license="Apache 2.0",
    py_modules=build_firmware_module_list(),
    install_requires=[],
)
