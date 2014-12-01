#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='Ojota',
    version='2.1.0',
    author='Felipe Lerena, Juan Pedro Fisanoti, Ezequiel Chan, Nicolas Sarubbi, Hernan Lozano, Nicolas Bases, Franco Mariluis, Ezequiel Alvarez',
    author_email='flerena@msa.com.ar, fisadev@gmail.com, echan@msa.com.ar, nicosarubi@gmail.com, hernantz@gmail.com, nmbases@gmail.com, fmariluis@gmail.com, welcometothechango@gmail.com',
    packages=['ojota'],
    scripts=[],
    url='http://pypi.python.org/pypi/Ojota/',
    license='LICENSE.txt',
    description='Flat File Database with ORM',
    long_description=open('README.rst').read(),
    install_requires=[],
)
