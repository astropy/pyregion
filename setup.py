#!/usr/bin/env python

# NOTE: most of the configuration is defined in setup.cfg

import sys

import setuptools
from setuptools import setup

from extension_helpers import get_extensions


setup(use_scm_version=True,
      setup_requires=['setuptools_scm'],
      ext_modules=get_extensions()
      )
