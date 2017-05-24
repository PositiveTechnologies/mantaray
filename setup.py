import sys
from setuptools import setup, find_packages
from codecs import open
from os import path

from mantaray.__metadata__ import __version__, __author__, __author_email__, __description__, __title__

if sys.version_info < (3, 5):
    sys.exit('Python < 3.5 is not supported')


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name=str.lower(__title__),
    version=__version__,
    description=__description__,
    long_description=long_description,
    url='https://github.com/kochetkov/mantaray',
    download_url='https://github.com/kochetkov/mantaray/tarball/' + __version__,
    license='GPL v3',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
    ],
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author=__author__,
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email=__author_email__
)
