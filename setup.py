from setuptools import setup, find_packages
setup(
    name = "regender",
    version = "0.0.1",
    packages=find_packages(),
    install_requires=[
        "inflect",
        "pattern",
    ]
    )
