import os
import sys

from setuptools import setup, find_packages

__version__ = "0.1"
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = ['nose',
            'coverage',
            'repoze.bfg',
            'ming',
            'supervisor',
            ]

if sys.version_info < (2,6):
    requires.apend('simplejson')

tests_require = requires + [ 'Sphinx',
                             ]



setup(name='tattoo',
      version=__version__,
      description='tattoo - another url shortener',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: BFG",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires+tests_require,
      test_suite="nose.collector",
      entry_points = """\
      [paste.app_factory]
      app = tattoo.run:app
      """
      )

