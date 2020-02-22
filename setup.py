#!/usr/bin/env python
from setuptools import find_packages, setup

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

with open("README.rst") as f:
    LONG_DESCRIPTION = f.read()

config = configparser.ConfigParser()
config.read("setup.cfg")

setup(
    name="warhammer",  # wh40k
    version=config.get("src", "version"),
    license="MIT",
    description="Models statistics of units attacking each other",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    author="Peilonrayz",
    author_email="peilonrayz@gmail.com",
    url="https://peilonrayz.github.io/warhammer",
    project_urls={
        "Bug Tracker": "https://github.com/Peilonrayz/warhammer/issues",
        "Documentation": "https://peilonrayz.github.io/warhammer",
        "Source Code": "https://github.com/Peilonrayz/warhammer",
    },
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=["mm_json", "dice_stats", "dataclasses_json"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="",
    entry_points={"console_scripts": ["warhammer=warhammer.__main__:main"]},
)
