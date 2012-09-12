"""
SimpleAuth testing
"""
import os
import sys
import logging

from dev_appserver import fix_sys_path

saved_path = [p for p in sys.path]
fix_sys_path() # wipes out sys.path
sys.path.extend(saved_path) # put back our original paths

from google.appengine.ext import testbed

class TestMixin(object):
  def setUp(self): 
    super(TestMixin, self).setUp()
    self.testbed = testbed.Testbed()
    self.testbed.activate()

    self.testbed.init_datastore_v3_stub()    
    self.testbed.init_memcache_stub()
    self.testbed.init_urlfetch_stub()
    self.testbed.init_user_stub()

    self._logger = logging.getLogger()
    self._old_log_level = self._logger.getEffectiveLevel()
    
  def tearDown(self):
    super(TestMixin, self).tearDown()
    self._logger.setLevel(self._old_log_level)
    self.testbed.deactivate()

  def login_user(self, email, user_id, admin=False, **kwargs):
    """Fake user login.

    Additional params in kwargs:
      - federated_identity (OpenID)
      - federated_provider (OpenID)
    """
    user = {
      'user_email': email or '',
      'user_id': str(user_id or ''),
      'user_is_admin': str(int(bool(admin)))
    }
    user.update(kwargs)
    self.testbed.setup_env(overwrite=True, **user)

  def logout_user(self):
    self.login_user(None, None)

  def expectErrors(self):
    if self.isDefaultLogging():
      self._logger.setLevel(logging.CRITICAL)

  def expectWarnings(self):
    if self.isDefaultLogging():
      self._logger.setLevel(logging.ERROR)

  def isDefaultLogging(self):
    return self._old_log_level == logging.WARNING
