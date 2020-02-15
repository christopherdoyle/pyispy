#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

requirements = []

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest>=3"]

setup(
    author="Christopher Doyle",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description=" ",
    install_requires=requirements,
    extras_require={":python_version == '3.6'": ["dataclasses"]},
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords="pyspy",
    name="pyspy",
    packages=find_packages(include=["pyspy", "pyspy.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/christopherdoyle/pyspy",
    version="0.1.0",
    zip_safe=False,
)
