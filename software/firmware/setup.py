from setuptools import setup

__version__ = ""
exec(open("./version.py").read())


def build_firmware_module_list():
    import os

    dirs = {"experimental"}
    excluded = {"__init__.py", "setup.py"}

    return [f[:-3] for f in os.listdir(".") if f.endswith(".py") and f not in excluded] + [
        ".".join([d, f[:-3]])
        for d in dirs
        for f in os.listdir(d)
        if f.endswith(".py") and f not in excluded
    ]


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
