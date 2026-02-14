"""Setup script for lattice_sdk package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lattice_sdk",
    version="0.1.0",
    author="Prisma Labs",
    description="Lattice SDK library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prisma-ml-labs/lattice_client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "httpx",
    ],
)
