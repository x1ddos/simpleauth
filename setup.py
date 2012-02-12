# -*- coding: utf-8 -*-
import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='simpleauth',
      version='0.1.1',
      author='Alex Vagin (http://alex.cloudware.it)',
      author_email='alex at cloudware.it',
      url='http://simpleauth.appspot.com',
      download_url='https://github.com/crhym3/simpleauth/zipball/master',
      description='A simple auth handler for Google App Engine supporting OAuth 1.0a, 2.0 and OpenID',
      keywords='oauth oauth2 openid appengine google',
      platforms = ["any"],
      license='MIT',
      requires=['lxml', 'oauth2'],
      provides=['simpleauth'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries',    
      ],
      packages=['simpleauth', 'tests', 'example'],
      long_description=read('README')
)
