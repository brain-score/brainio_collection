#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    "numpy>=1.16",
    "brainio_base @ git+https://github.com/brain-score/brainio_base",
    "six",
    "requests",
    "boto3",
    "tqdm",
    "netcdf4",
    "pandas",
    # test_requirements
    "pytest",
    "Pillow",
    "imageio",
    "opencv-python",
]

setup(
    name='brainio_collection',
    version='0.1.0',
    description="BrainIO Collection of brain data.",
    long_description=readme,
    author="Jon Prescott-Roy, Martin Schrimpf",
    author_email='jjpr@mit.edu, mschrimpf@mit.edu',
    url='https://github.com/brain-score/brainio_collection',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='BrainIO',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
)
