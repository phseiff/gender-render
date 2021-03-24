#!/usr/bin/env python

from setuptools import setup

import src as gr  # <- read author and version.
from src import gender_nouns  # <- build the gendered nouns.

setup(
    name='gender_render',
    version=gr.__version__,
    description="Template-system and proof-of-concept for rendering gender-neutral text- and email-templates with \
the correct pronouns of all people involved.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords="template-engine template-language specification gender-equality gender pronouns grammatical-gender",
    author=gr.__author__,
    author_email="phseiff@phseiff.com",
    url='https://github.com/phseiff/gender-render/',
    packages=['gender_render'],
    package_dir={'gender_render': 'src'},
    package_data={'gender_render': ['*']},
    include_package_data=True,
    install_requires=open("requirements.txt", "r").read().splitlines(),
    license="MIT\n(limited to python-files that are actually part of the package installation,\
    which excludes data sets and documentation/specifications that come with the software;\
    refer to the `LICENSE-implementation.txt`-file that comes with this version of the software on PyPi for the full\
    definition of what is covered by this license and what is not.)",
    extras_require={
        'more_warnings': ["nltk"],
        'testing': ["typing_extensions"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
