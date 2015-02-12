from distutils.core import setup
from setuptools import find_packages

setup(
  name = 'ems',
  packages = find_packages(),
  version = '0.2.1',
  description = 'Small collection of classes to build model centric applications with python and Qt',
  author = 'Michael Tils',
  author_email = 'mtils@web-utils.de',
  url = 'https://github.com/mtils/ems',
  download_url = 'https://github.com/mtils/ems/tarball/0.2.1',
  keywords = ['qt', 'gui', 'rad','scaffolding'],
  install_requires = [
    # 'dbfpy', not installable via pip
    'xlrd',
    'xlwt'
  ],
  classifiers = [
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
  ]
)