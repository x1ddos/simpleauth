# -*- coding: utf-8 -*-
import unittest
import helpers

from webapp2 import WSGIApplication, Route, RequestHandler
from webob import Request

from simpleauth import SimpleAuthHandler

#
# test subjects
#

class NotSupportedException(Exception): pass
class DummyAuthError(Exception): pass

class DummyAuthHandler(RequestHandler, SimpleAuthHandler):
  def __init__(self, *args, **kwargs):
    super(DummyAuthHandler, self).__init__(*args, **kwargs)
    self.PROVIDERS.update({
      'dummy_oauth2': ('oauth2', 'https://dummy/oauth2', 'https://dummy/oauth2_token')
    })
    
  def _on_signin(self, user_data, auth_info, provider):
    self.redirect('/logged_in?provider=%s' % provider)
    
  def _callback_uri_for(self, provider):
    return '/auth/openid/callback'
    
  def _provider_not_supported(self, provider):
    raise NotSupportedException()

  def _auth_error(self, provider, msg=None):
    raise DummyAuthError("Couldn't authenticate against %s: %s" % (provider, msg))
   
# dummy app to test requests against 
app = WSGIApplication([
  Route('/auth/<provider>', handler=DummyAuthHandler, handler_method='_simple_auth'),
  Route('/auth/<provider>/callback', handler=DummyAuthHandler, handler_method='_auth_callback')  
], debug=True)

#
# test suite
#

class SimpleAuthHandlerTestCase(helpers.BaseTestMixin, unittest.TestCase):
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
      self.handler._simple_auth()
      
    with self.assertRaises(NotSupportedException):
      self.handler._simple_auth('whatever')

  def test_openid_init(self):
    resp = app.get_response('/auth/openid?identity_url=some.oid.provider.com')
    self.assertEqual(resp.status_int, 302)
    self.assertEqual(resp.headers['Location'], 
                    'https://www.google.com/accounts/Login?continue=http%3A//testbed.example.com/auth/openid/callback')
                    
  def test_openid_callback_success(self):
    self.login_user('dude@example.org', 123, federated_id='http://dude.example.org', provider='example.org')
    resp = app.get_response('/auth/openid/callback')
    
    self.assertEqual(resp.status_int, 302)
    self.assertEqual(resp.headers['Location'], 'http://localhost/logged_in?provider=openid')
    
    uinfo, auth = self.handler._openid_callback()
    self.assertEqual(auth, {'provider': 'example.org'})
    self.assertEqual(uinfo, {
      'id': 'http://dude.example.org', 
      'nickname': 'http://dude.example.org',
      'email': 'dude@example.org'
    })
  
  def test_openid_callback_failure(self):
    with self.assertRaisesRegexp(DummyAuthError, 'OpenID Authentication failed'):
      app.get_response('/auth/openid/callback')
