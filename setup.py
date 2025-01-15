import os
import re
from setuptools import setup, find_packages
from pathlib import Path

DISTNAME = 'rewet'
PACKAGES = find_packages()
DESCRIPTION = 'REstoration of Water after Event Tool (REWET)'
AUTHOR = 'Sina Naeimi'
MAINTAINER_EMAIL = 'snaeimi@udel.edu'
LICENSE = 'MIT'
URL = 'https://github.com/snaeimi/WNTR'
DEPENDENCIES = [
    'numpy>=1.21', 'scipy', 'networkx', 'pandas<=2.2.3', 'matplotlib',
    'setuptools', 'wntrfr==1.1.0.1.2', 'sphinx', 'openpyxl'
]

# Use README file as the long description
file_dir = Path(__file__).resolve().parent
with open(file_dir / 'README.md', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

# Get version from __init__.py
with open(file_dir / 'rewet' / '__init__.py') as f:
    version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        VERSION = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name=DISTNAME,
    version=VERSION,
    packages=PACKAGES,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    maintainer_email=MAINTAINER_EMAIL,
    license=LICENSE,
    url=URL,
    zip_safe=False,
    install_requires=DEPENDENCIES,
    scripts=[],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering',
    ],
    python_requires='>=3.6',
)