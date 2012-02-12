# -*- coding: utf-8 -*-
import unittest
from tests.helpers import BaseTestMixin

from simpleauth import SimpleAuthHandler

class NotSupportedException(Exception):
  pass
  
class DummyAuthError(Exception):
  pass

class DummyAuthHandler(SimpleAuthHandler):
  def __init__(self):
    super(DummyAuthHandler, self).__init__()
    self.PROVIDERS.update({
      'dummy_oauth2': ('oauth2', 'https://dummy/oauth2', 'https://dummy/oauth2_token')
    })
    
  def _provider_not_supported(self, provider):
    raise NotSupportedException()

class SimpleAuthHandlerTestCase(BaseTestMixin, unittest.TestCase):
  def setUp(self):
    super(SimpleAuthHandlerTestCase, self).setUp()
    self.handler = DummyAuthHandler()
    
  def test_providers_dict(self):
    for p in ('google', 'windows_live', 'facebook', 'linkedin', 'twitter', 'openid'):
      self.assertIn(self.handler.PROVIDERS[p][0], ['oauth2', 'oauth1', 'openid'])
    
  def test_token_parsers_dict(self):
    for p in ('google', 'windows_live', 'facebook', 'linkedin', 'twitter'):
      parser = self.handler.TOKEN_RESPONSE_PARSERS['google']
      self.assertIsNotNone(parser)
      self.assertTrue(hasattr(self.handler, parser))

  def test_not_supported_provider(self):
    with self.assertRaises(NotSupportedException):
      self.handler.auth()
      
    with self.assertRaises(NotSupportedException):
      self.handler.auth('whatever')
