# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='StockTool',
    version='0.1.0',
    description='Stock Tool by Alvin Lai',
    long_description=readme,
    author='Alvin Lai',
    author_email='toy112221@gmail.com',
    url='https://github.com/kennethreitz/samplemod',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

