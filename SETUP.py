
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
    packages=["QuantFin"],
    version="0.0.2",
    license="MIT",
    description="Library for Academic Research on Asset Pricing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Stephen Zhang",
    author_email="stephen_se@outlook.com",
    url="https://github.com/yuz0101/QuantFin",
    download_url='https://github.com/yuz0101/QuantFin/archive/refs/tags/Test.tar.gz',
    keywords=['ACADEMIC', 'EMPIRICAL', 'FIANCE', 'RESEARCH', 'QUANT', 'PORTFOLIO'],
    install_requires=["numpy", "pandas", "linearmodels", "statsmodels", "requests"],
    
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

)