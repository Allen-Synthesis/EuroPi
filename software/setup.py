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
    py_modules=["firmware.version"],
    namespace_packages=["contrib"],
)
