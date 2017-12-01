import opyscad
from setuptools import setup, find_packages
from os.path import join, dirname


setup(
	name = 'opyscad',
	version = opyscad.__version__,
	packages = find_packages(),
	long_description = open(join(dirname(__file__), 'README.txt')).read(),
)
