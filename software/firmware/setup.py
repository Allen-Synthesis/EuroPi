from setuptools import setup

__version__ = ""
exec(open("./version.py").read())

setup(
    name="micropython-europi",
    version=__version__,
    description="EuroPi module for MicroPython",
    long_description="""The EuroPi is a fully user reprogrammable EuroRack module based on the Raspberry Pi Pico, which allows users to process inputs and controls to produce outputs based on code written in Python.""",
    url="https://github.com/Allen-Synthesis/EuroPi",
    author="Allen Synthesis",
    author_email="contact@allensynthesis.co.uk",
    license="Apache 2.0",
    py_modules=[
        "bootloader",
        "calibrate",
        "europi_script",
        "europi",
        "ui",
        "version",
        "experimental.knobs",
    ],
    install_requires=[],
)
