import sys

# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
# sys.path.pop(0)
from setuptools import setup

# import sdist_upip

setup(
    name="micropython-europi",
    version="0.0.2.dev2",
    description="EuroPi module for MicroPython",
    long_description="",
    url="https://github.com/Allen-Synthesis/EuroPi",
    author="Allen Synthesis",
    author_email="contact@allensynthesis.co.uk",
    license="Apache 2.0",
    # cmdclass={'sdist': sdist_upip.sdist},
    py_modules=["europi", "calibrate"],
    install_requires=[],
)
