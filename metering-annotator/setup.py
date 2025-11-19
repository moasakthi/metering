"""Setup script for Metering Annotator."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="metering-annotator",
    version="1.0.0",
    author="Metering Framework",
    description="Python integration library for Metering Service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "tenacity>=8.2.0",
    ],
    extras_require={
        "async": ["aiohttp>=3.9.0"],
        "fastapi": ["fastapi>=0.104.0"],
    },
)

