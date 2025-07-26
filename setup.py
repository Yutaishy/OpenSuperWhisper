#!/usr/bin/env python3
"""
Setup script for OpenSuperWhisper
For PyInstaller builds and installation support
"""

from setuptools import setup, find_packages

setup(
    name="opensuperwhisper",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'opensuperwhisper=run_app:main',
        ],
    },
)