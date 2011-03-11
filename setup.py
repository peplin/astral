import astral
import os
from distutils.core import setup
from setuptools import find_packages

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
long_description = open(os.path.join(ROOT_PATH, 'README.rst')).read()

setup(name='astral',
      version=astral.__version__,
      description='Astral Streaming P2P Client',
      long_description=long_description,
      author='Astral Project Group',
      author_email='astral@bueda.com',
      url='http://github.com/peplin/astral',
      test_suite='nose.collector',
      setup_requires=['nose>=0.11', 'unittest>=0.5.1'],
      install_requires=[
          'tornado>=1.2.1',
      ],
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'astralnode = astral.bin.astralnode:main',],
      },
)
