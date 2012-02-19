# -*- coding: utf-8 -*-

# See this for more info about GAE unit testing testbed:
# http://code.google.com/appengine/docs/python/tools/localunittesting.html
#
# Also, Python 2.7 unittesting:
# http://docs.python.org/library/unittest.html
import os
import sys

gae_path = '/usr/local/google_appengine'

current_path = os.path.abspath(os.path.dirname(__file__))
sys.path[0:0] = [
    current_path,
    gae_path,
    os.path.join(current_path, '..', 'simpleauth'),
]

# save current sys paths
saved_path = [p for p in sys.path]

from dev_appserver import fix_sys_path
fix_sys_path() # wipes out sys.path
sys.path.extend(saved_path) # put back our previous path



class BaseTestMixin(object):
  def setUp(self):
    from google.appengine.ext import testbed
    super(BaseTestMixin, self).setUp()
    self.testbed = testbed.Testbed()
    self.testbed.activate()

    self.testbed.init_datastore_v3_stub()    
    self.testbed.init_memcache_stub()
    self.testbed.init_urlfetch_stub()
    self.testbed.init_user_stub()
    
  def tearDown(self):
    super(BaseTestMixin, self).tearDown()
    self.testbed.deactivate()

  def login_user(self, email, user_id, federated_id=None, provider=None, is_admin=False):
    self.testbed.setup_env(user_email=email or '', overwrite=True)
    self.testbed.setup_env(user_id=str(user_id) or '', overwrite=True)
    self.testbed.setup_env(user_is_admin='1' if is_admin else '0', overwrite=True)
    self.testbed.setup_env(federated_identity=federated_id or '', overwrite=True)
    self.testbed.setup_env(federated_provider=provider or '', overwrite=True)

  def logout_user(self):
    self.login_user(None, None)
