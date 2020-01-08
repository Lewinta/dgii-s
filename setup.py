# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
        install_requires = f.read().strip().split('\n')

# get version from __version__ variable in dgii/__init__.py
from dgii import __version__ as version

setup(
        name='dgii',
        version=version,
        description='Una aplicacion para la generacion de los reportes que son enviados a la Direccion General de Impuestos Internos en la Republica Dominicana',
        author='TZCODE SRL',
        author_email='info@tzcode.tech',
        packages=find_packages(),
        zip_safe=False,
        include_package_data=True,
        install_requires=install_requires
)
