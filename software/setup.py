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
exec(open("./firmware/version.py").read())

setup(
    name="micropython-europi-contrib",
    version=__version__,
    description="Community Contributions to EuroPi module for MicroPython",
    long_description="Community Contributions to EuroPi module for MicroPython",
    url="https://github.com/Allen-Synthesis/EuroPi",
    author="Allen Synthesis",
    author_email="contact@allensynthesis.co.uk",
    license="Apache 2.0",
    packages=["contrib"],
    data_files=[("/", ["main.py"])],
    py_modules=["firmware.version"],
    namespace_packages=["contrib"],
)
