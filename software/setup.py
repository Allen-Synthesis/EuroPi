from email.policy import default
import sys

from setuptools import setup

DEFAULTS = dict(
    version="0.0.2.dev3",
    url="https://github.com/Allen-Synthesis/EuroPi",
    author="Allen Synthesis",
    author_email="contact@allensynthesis.co.uk",
    license="Apache 2.0",
)

setup(
    name="micropython-europi",
    description="EuroPi module for MicroPython",
    long_description="EuroPi module for MicroPython",
    package_dir={'': "firmware"},
    packages=[""],
    **DEFAULTS,
)

setup(
    name="micropython-europi-contrib",
    description="Community Contributions to EuroPi module for MicroPython",
    long_description="Community Contributions to EuroPi module for MicroPython",
    packages=["contrib"],
    namespace_packages=["contrib"],
    **DEFAULTS,
)
