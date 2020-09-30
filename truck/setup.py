""" This file helps installing all dependencies for trucklib. """

import setuptools

with open("README.md", "r") as fh:
    README = fh.read()

with open("LICENSE.md", "r") as fh:
    LICENSE = fh.read()

setuptools.setup(
    name="trucklib-mauricebauer",
    version="0.0.1",
    author="Maurice Bauer",
    description="A library to control an autonomous truck-robot "
    "using Raspberry Pi, BrickPi 3 and the Raspberry Pi Camera.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/mauricebauer/trucklib",
    packages=setuptools.find_packages(),
    install_requires=['zmq', 'opencv-contrib-python', 'paho-mqtt',
                      'simple-pid'],
    license=LICENSE,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
