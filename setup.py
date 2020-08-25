from setuptools import setup, find_packages

setup(
    name='pdfstructure',
    description="PDF Natural Structure Parser",
    version='0.0.1',
    author="Christian Hofer",
    author_email="christianhofer91@gmail.com",
    packages=find_packages(exclude=("tests"))
)
