# setup.py
from setuptools import setup, find_packages

setup(
    name="my_app",                # choose your package name
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # your dependencies, e.g. "streamlit", "pandas", ...
    ],
)
