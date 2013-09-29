#!/usr/bin/env python
# Copyright 2007 Robin Gottfried <google@kebet.cz>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @author Robin Gottfried <google@kebet.cz>
# part of gap project (https://github.com/czervenka/gap)
from restapi import VERSION

VERSION_STRING = '.'.join([str(v) for v in VERSION])

import os
from os.path import join, dirname
from setuptools import setup, findall
from collections import defaultdict


# hack to prevent Exceptions after running setup.py test
try:
    import multiprocessing
except ImportError:
    pass


def collect_files(path, prefix=''):
    ret = defaultdict(list)
    files = findall(path)
    for f in files:
        ret[os.path.join(prefix,os.path.dirname(f))].append(f)
    return ret.items()

long_description=open(join(dirname(__file__), 'README.rst')).read()

setup(
    name='gap-restapi',
    version= VERSION_STRING,
    description='Rest API for gap',
    long_description=long_description,
    author='Robin Gottfried',
    author_email='python@kebet.cz',
    url='https://github.com/czervenka/gap-restapi',
    packages=['restapi'],
    # scripts=[],
    zip_safe = True,
    license='Apache License 2.0',
    # requires=[],
    include_package_data=True,
    test_loader='tests.run_tests:TestLoader',
    test_suite='tests',
    tests_require=[
        'gap',
        'nose',
        'coverage',
    ],
)
