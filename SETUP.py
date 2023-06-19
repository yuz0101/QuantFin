
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="QuantFin",
    version="0.0.1",
    description="Library for Academic Research on Asset Pricing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yuz0101/QuantFin",
    author="Stephen Zhang",
    author_email="stephen_se@outlook.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent"
    ],
    packages=["QuantFin"],
    include_package_data=True,
    install_requires=["numpy", "pandas", "linearmodels", "statemodels", "requests"]
)