#!/usr/bin/env python

from setuptools import setup

setup(
    name='gender_render',
    version='1.0.0',
    description='Easy to use template engine to correctly gender persons of gender in automatically generated emails.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='phseiff',
    author_email='contact@phseiff.com',
    url='https://github.com/phseiff/gender-render/',
    packages=['gender_render'],
    package_dir={'gender_render': 'src'},
    package_data={'gender_render': ['*']},
    include_package_data=True,
    install_requires=open("requirements.txt", "r").read().splitlines(),
    license="LICENSE.txt",
    extras_require={
        'more_warnings': ["nltk"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
