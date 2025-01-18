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
