# -*- coding: utf-8 -*-
import unittest
from tests import TestMixin

from webapp2 import WSGIApplication, Route, RequestHandler
from webob import Request
import httplib2

from simpleauth import SimpleAuthHandler

#
# test subjects
#

class NotSupportedException(Exception):
  """Provider not supported"""
  pass

class DummyAuthError(Exception):
  """Generic auth error for Dummy handler"""
  pass

class OAuth1ClientMock(object):
  def __init__(self, **kwargs):
    super(OAuth1ClientMock, self).__init__()
    self._response_content = kwargs.pop('content', '')
    self._response_dict = kwargs
    
  def request(self, url, method):
    return (httplib2.Response(self._response_dict), self._response_content)
  
class DummyAuthHandler(RequestHandler, SimpleAuthHandler):
  def __init__(self, *args, **kwargs):
    super(DummyAuthHandler, self).__init__(*args, **kwargs)
    self.PROVIDERS.update({
      'dummy_oauth1': ('oauth1', {
        'request': 'https://dummy/oauth1_rtoken',
        'auth'  : 'https://dummy/oauth1_auth?{0}'
      }, 'https://dummy/oauth1_atoken'),
      'dummy_oauth2': ('oauth2', 'https://dummy/oauth2{0}', 
                                 'https://dummy/oauth2_token'),
    })
    
    self.TOKEN_RESPONSE_PARSERS.update({
      'dummy_oauth1': '_json_parser',
      'dummy_oauth2': '_json_parser'
    })
    
    self.session = {'req_token': {
      'oauth_token':'oauth1 token', 
      'oauth_token_secret':'a secret'
    }}

  def _on_signin(self, user_data, auth_info, provider):
    self.redirect('/logged_in?provider=%s' % provider)
    
  def _callback_uri_for(self, provider):
    return '/auth/%s/callback' % provider
    
  def _get_consumer_info_for(self, provider):
    return {
      'dummy_oauth1': ('cons_key', 'cons_secret'),
      'dummy_oauth2': ('cl_id', 'cl_secret', 'a_scope'),
    }.get(provider, (None, None))
    
  def _provider_not_supported(self, provider):
    raise NotSupportedException(provider)

  def _auth_error(self, provider, msg=None):
    raise DummyAuthError(
      "Couldn't authenticate against %s: %s" % (provider, msg))

  # mocks

  def _oauth1_client(self, token=None, 
                           consumer_key=None, consumer_secret=None):
    """OAuth1 client mock"""
    return OAuth1ClientMock(
      content='{"oauth_token": "some oauth1 request token"}')
    
  def _get_dummy_oauth1_user_info(self, auth_info, key=None, secret=None):
    return 'an oauth1 user info'

# Dummy app to run the tests against
app = WSGIApplication([
  Route('/auth/<provider>', handler=DummyAuthHandler, 
                            handler_method='_simple_auth'),
  Route('/auth/<provider>/callback', handler=DummyAuthHandler, 
                                     handler_method='_auth_callback')  
], debug=True)


#
# test suite
#

class SimpleAuthHandlerTestCase(TestMixin, unittest.TestCase):
  def setUp(self):
    super(SimpleAuthHandlerTestCase, self).setUp()
    self.handler = DummyAuthHandler()
    
  def test_providers_dict(self):
    for p in ('google', 'twitter', 'linkedin', 'openid', 
              'facebook', 'windows_live'):
      self.assertIn(self.handler.PROVIDERS[p][0], 
                   ['oauth2', 'oauth1', 'openid'])
    
  def test_token_parsers_dict(self):
    for p in ('google', 'windows_live', 'facebook', 'linkedin', 'twitter'):
      parser = self.handler.TOKEN_RESPONSE_PARSERS['google']
      self.assertIsNotNone(parser)
      self.assertTrue(hasattr(self.handler, parser))

  def test_not_supported_provider(self):
    self.expectErrors()
    with self.assertRaises(NotSupportedException):
      self.handler._simple_auth()
      
    with self.assertRaises(NotSupportedException):
      self.handler._simple_auth('whatever')

    resp = app.get_response('/auth/xxx')
    self.assertEqual(resp.status_int, 500)
    self.assertRegexpMatches(resp.body, 'NotSupportedException: xxx')

  def test_openid_init(self):
    resp = app.get_response('/auth/openid?identity_url=some.oid.provider.com')
    self.assertEqual(resp.status_int, 302)
    self.assertEqual(resp.headers['Location'], 
      'https://www.google.com/accounts/Login?'
      'continue=http%3A//testbed.example.com/auth/openid/callback')
        
  def test_openid_callback_success(self):
    self.login_user('dude@example.org', 123, 
      federated_identity='http://dude.example.org', 
      federated_provider='example.org')

    resp = app.get_response('/auth/openid/callback')
    self.assertEqual(resp.status_int, 302)
    self.assertEqual(resp.headers['Location'], 
      'http://localhost/logged_in?provider=openid')
    
    uinfo, auth = self.handler._openid_callback()
    self.assertEqual(auth, {'provider': 'example.org'})
    self.assertEqual(uinfo, {
      'id': 'http://dude.example.org', 
      'nickname': 'http://dude.example.org',
      'email': 'dude@example.org'
    })
  
  def test_openid_callback_failure(self):
    self.expectErrors()
    resp = app.get_response('/auth/openid/callback')
    self.assertEqual(resp.status_int, 500)
    self.assertRegexpMatches(resp.body, 'DummyAuthError')

  def test_oauth1_init(self):
    resp = app.get_response('/auth/dummy_oauth1')
    
    self.assertEqual(resp.status_int, 302)
    self.assertEqual(resp.headers['Location'], 
      'https://dummy/oauth1_auth?'
      'oauth_token=some+oauth1+request+token&'
      'oauth_callback=%2Fauth%2Fdummy_oauth1%2Fcallback')

  def test_oauth1_callback_success(self):
    url = '/auth/dummy_oauth1/callback?oauth_verifier=a-verifier-token'
    resp = app.get_response(url)
    self.assertEqual(resp.status_int, 302)
    self.assertEqual(resp.headers['Location'], 
      'http://localhost/logged_in?provider=dummy_oauth1')
        
  def test_oauth1_callback_failure(self):
    self.expectErrors()
    resp = app.get_response('/auth/dummy_oauth1/callback')
    self.assertEqual(resp.status_int, 500)
    self.assertRegexpMatches(resp.body, 'No OAuth verifier was provided')
      
  def test_query_string_parser(self):
    parsed = self.handler._query_string_parser('param1=val1&param2=val2')
    self.assertEqual(parsed, {'param1':'val1', 'param2':'val2'})

if __name__ == '__main__':
  unittest.main()
