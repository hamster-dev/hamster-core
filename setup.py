#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from pip.req import parse_requirements

install_reqs = parse_requirements(
    'requirements.txt',
    session=False
)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='hamster',
    version='0.4',
    description="Small furry animal.",
    author="Mike Waters",
    author_email='robert.waters@gmail.com',
    install_requires=reqs  # open("requirements.txt").readlines(),
)
