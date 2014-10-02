# -*- coding: utf-8 -*-
import ez_setup
ez_setup.use_setuptools()

import os
import re
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


_init = read('simpleauth/__init__.py')
version = re.search(r"__version__ = '([^']+)'", _init).group(1)
author = re.search(r"__author__ = '([^']+)'", _init).group(1)
license = re.search(r"__license__ = '([^']+)'", _init).group(1)


setup(name='simpleauth',
      version=version,
      author=author,
      url='https://github.com/crhym3/simpleauth',
      download_url='https://github.com/crhym3/simpleauth/archive/master.zip',
      description='A simple auth handler for Google App Engine supporting '
                  'OAuth 1.0a, 2.0 and OpenID',
      keywords='oauth oauth2 openid appengine google',
      platforms=['any'],
      license=license,
      install_requires=['oauth2', 'httplib2'],
      extras_require={
        'LinkedIn': ['lxml']
      },
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries',    
      ],
      packages=['simpleauth'],
      long_description=read('README.md')
)
