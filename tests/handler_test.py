# -*- coding: utf-8 -*-
import unittest
from tests import TestMixin

import time
import base64

try:
  import json
except ImportError:
  import simplejson as json

from webapp2 import WSGIApplication, Route, RequestHandler
from httplib2 import Response

import simpleauth as sa
from simpleauth import SimpleAuthHandler

#
# test subjects
#

class OAuth1ClientMock(object):
  def __init__(self, **kwargs):
    super(OAuth1ClientMock, self).__init__()
    self._response_content = kwargs.pop('content', '')
    self._response_dict = kwargs
    
  def request(self, url, method):
    return (Response(self._response_dict), self._response_content)
  
class DummyAuthHandler(RequestHandler, SimpleAuthHandler):
  SESSION_MOCK = {}

  def __init__(self, *args, **kwargs):
    super(DummyAuthHandler, self).__init__(*args, **kwargs)
    self.PROVIDERS.update({
      'dummy_oauth1': ('oauth1', {
        'request': 'https://dummy/oauth1_rtoken',
        'auth'  : 'https://dummy/oauth1_auth?{0}'
      }, 'https://dummy/oauth1_atoken'),
      'dummy_oauth2': ('oauth2', 'https://dummy/oauth2?{0}', 
                                 'https://dummy/oauth2_token'),
    })
    
    self.TOKEN_RESPONSE_PARSERS.update({
      'dummy_oauth1': '_json_parser',
      'dummy_oauth2': '_json_parser'
    })

    self.session = self.SESSION_MOCK.copy()
    
  def dispatch(self):
    RequestHandler.dispatch(self)
    self.response.headers['SessionMock'] = json.dumps(self.session)

  def _on_signin(self, user_data, auth_info, provider):
    self.redirect('/logged_in?provider=%s' % provider)
    
  def _callback_uri_for(self, provider):
    return '/auth/%s/callback' % provider
    
  def _get_consumer_info_for(self, provider):
    return {
      'dummy_oauth1': ('cons_key', 'cons_secret'),
      'dummy_oauth2': ('cl_id', 'cl_secret', 'a_scope'),
    }.get(provider, (None, None))

  # Mocks

  def _oauth1_client(self, token=None, 
                           consumer_key=None, consumer_secret=None):
    """OAuth1 client mock"""
    return OAuth1ClientMock(
      content='{"oauth_token": "some oauth1 request token"}')
    
  def _get_dummy_oauth1_user_info(self, auth_info, key=None, secret=None):
    return 'an oauth1 user info'

  def _get_dummy_oauth2_user_info(self, auth_info, key=None, secret=None):
    return 'oauth2 mock user info'

  # Mocked token so we can test the value
  def _generate_csrf_token(self, _time=None):
    return 'valid-csrf-token'


#
# test suite
#

class SimpleAuthHandlerTestCase(TestMixin, unittest.TestCase):
  def setUp(self):
    super(SimpleAuthHandlerTestCase, self).setUp()
    # set back to default value
    DummyAuthHandler.OAUTH2_CSRF_STATE = SimpleAuthHandler.OAUTH2_CSRF_STATE
    DummyAuthHandler.SESSION_MOCK = {
      'req_token': {
        'oauth_token':'oauth1 token', 
        'oauth_token_secret':'a secret' 
      }
    }

    # handler instance for some of the tests
    self.handler = DummyAuthHandler()

    # Dummy app to run the tests against
    routes = [
      Route('/auth/<provider>', handler=DummyAuthHandler, 
        handler_method='_simple_auth'),
      Route('/auth/<provider>/callback', handler=DummyAuthHandler, 
        handler_method='_auth_callback') ]
    self.app = WSGIApplication(routes, debug=True)
    
  def test_providers_dict(self):
    for p in ('google', 'twitter', 'linkedin', 'linkedin2', 'openid', 
              'facebook', 'windows_live'):
      self.assertIn(self.handler.PROVIDERS[p][0], 
                   ['oauth2', 'oauth1', 'openid'])
    
  def test_token_parsers_dict(self):
    for p in ('google', 'windows_live', 'facebook', 'linkedin', 'linkedin2',
              'twitter'):
      parser = self.handler.TOKEN_RESPONSE_PARSERS[p]
      self.assertIsNotNone(parser)
      self.assertTrue(hasattr(self.handler, parser))

  def test_not_supported_provider(self):
    self.expectErrors()
    with self.assertRaises(sa.UnknownAuthMethodError):
      self.handler._simple_auth()
      
    with self.assertRaises(sa.UnknownAuthMethodError):
      self.handler._simple_auth('whatever')

    resp = self.app.get_response('/auth/xxx')
    self.assertEqual(resp.status_int, 500)
    self.assertRegexpMatches(resp.body, 'UnknownAuthMethodError')

  def test_openid_init(self):
    resp = self.app.get_response('/auth/openid?identity_url=some.oid.provider.com')
    self.assertEqual(resp.status_int, 302)
    self.assertEqual(resp.headers['Location'], 
      'https://www.google.com/accounts/Login?'
      'continue=http%3A//testbed.example.com/auth/openid/callback')
        
  def test_openid_callback_success(self):
    self.login_user('dude@example.org', 123, 
      federated_identity='http://dude.example.org', 
      federated_provider='example.org')

    resp = self.app.get_response('/auth/openid/callback')
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
    resp = self.app.get_response('/auth/openid/callback')
    self.assertEqual(resp.status_int, 500)
    self.assertRegexpMatches(resp.body, 'InvalidOpenIDUserError')

  def test_oauth1_init(self):
    resp = self.app.get_response('/auth/dummy_oauth1')
    
    self.assertEqual(resp.status_int, 302)
    self.assertEqual(resp.headers['Location'], 
      'https://dummy/oauth1_auth?'
      'oauth_token=some+oauth1+request+token&'
      'oauth_callback=%2Fauth%2Fdummy_oauth1%2Fcallback')

  def test_oauth1_callback_success(self):
    url = '/auth/dummy_oauth1/callback?oauth_verifier=a-verifier-token'
    resp = self.app.get_response(url)
    self.assertEqual(resp.status_int, 302)
    self.assertEqual(resp.headers['Location'], 
      'http://localhost/logged_in?provider=dummy_oauth1')
        
  def test_oauth1_callback_failure(self):
    self.expectErrors()
    resp = self.app.get_response('/auth/dummy_oauth1/callback')
    self.assertEqual(resp.status_int, 500)
    self.assertRegexpMatches(resp.body, 'No OAuth verifier was provided')
      
  def test_query_string_parser(self):
    parsed = self.handler._query_string_parser('param1=val1&param2=val2')
    self.assertEqual(parsed, {'param1':'val1', 'param2':'val2'})

  #
  # CSRF tests
  # 
  
  def test_csrf_default(self):
    # Backward compatibility with older versions
    self.assertFalse(SimpleAuthHandler.OAUTH2_CSRF_STATE)

  def test_csrf_oauth2_init(self):
    DummyAuthHandler.OAUTH2_CSRF_STATE = True
    resp = self.app.get_response('/auth/dummy_oauth2')

    self.assertEqual(resp.status_int, 302)
    self.assertEqual(resp.headers['Location'], 'https://dummy/oauth2?'
      'scope=a_scope&'
      'state=valid-csrf-token&'
      'redirect_uri=%2Fauth%2Fdummy_oauth2%2Fcallback&'
      'response_type=code&'
      'client_id=cl_id')

    session = json.loads(resp.headers['SessionMock'])
    session_token = session.get(DummyAuthHandler.OAUTH2_CSRF_SESSION_PARAM, '')
    self.assertEqual(session_token, 'valid-csrf-token')

  def test_csrf_oauth2_callback_success(self):
    # need a real token here to have a valid timestamp
    csrf_token = SimpleAuthHandler()._generate_csrf_token()
    DummyAuthHandler.OAUTH2_CSRF_STATE = True
    DummyAuthHandler.SESSION_MOCK = {
      DummyAuthHandler.OAUTH2_CSRF_SESSION_PARAM: csrf_token
    }

    fetch_resp = json.dumps({
      "access_token":"1/fFAGRNJru1FTz70BzhT3Zg",
      "expires_in": 3600,
      "token_type":"Bearer"
      })
    self.set_urlfetch_response('https://dummy/oauth2_token', 
      content=fetch_resp)

    resp = self.app.get_response('/auth/dummy_oauth2/callback?'
      'code=auth-code&state=%s' % csrf_token)

    self.assertEqual(resp.status_int, 302)
    self.assertEqual(resp.headers['Location'], 
      'http://localhost/logged_in?provider=dummy_oauth2')

    # token should be removed after during the authorization step
    session = json.loads(resp.headers['SessionMock'])
    self.assertFalse(DummyAuthHandler.OAUTH2_CSRF_SESSION_PARAM in session)

  def test_csrf_oauth2_failure(self):
    self.expectErrors()
    DummyAuthHandler.OAUTH2_CSRF_STATE = True
    DummyAuthHandler.SESSION_MOCK = {}

    token = SimpleAuthHandler()._generate_csrf_token()
    resp = self.app.get_response('/auth/dummy_oauth2/callback?'
      'code=auth-code&state=%s' % token)

    self.assertEqual(resp.status_int, 500)
    self.assertRegexpMatches(resp.body, 'InvalidCSRFTokenError')

  def test_csrf_oauth2_tokens_dont_match(self):
    self.expectErrors()

    token1 = SimpleAuthHandler()._generate_csrf_token()
    token2 = SimpleAuthHandler()._generate_csrf_token()
    
    DummyAuthHandler.OAUTH2_CSRF_STATE = True
    DummyAuthHandler.SESSION_MOCK = {
      DummyAuthHandler.OAUTH2_CSRF_SESSION_PARAM: token1
    }

    resp = self.app.get_response('/auth/dummy_oauth2/callback?'
      'code=auth-code&state=%s' % token2)

    self.assertEqual(resp.status_int, 500)
    self.assertRegexpMatches(resp.body, 'InvalidCSRFTokenError')

  def test_csrf_token_generation(self):
    h = SimpleAuthHandler()
    token = h._generate_csrf_token()
    token2 = h._generate_csrf_token()
    self.assertNotEqual(token, token2)

    decoded = base64.urlsafe_b64decode(token)
    tok, ts = decoded.rsplit(h.OAUTH2_CSRF_DELIMITER, 1)
    # > 10 so that I won't have to modify this test if the length changes
    # in the future
    self.assertTrue(len(tok) > 10)
    # token generation can't really take more than 1 sec here
    self.assertFalse(long(time.time()) - long(ts) > 1)

  def test_csrf_validation(self):
    self.expectErrors()
    h = SimpleAuthHandler()

    token = h._generate_csrf_token()
    token2 = h._generate_csrf_token()
    self.assertTrue(h._validate_csrf_token(token, token))
    self.assertFalse(h._validate_csrf_token(token, token2))
    self.assertFalse(h._validate_csrf_token('', token))
    self.assertFalse(h._validate_csrf_token(token, ''))
    self.assertFalse(h._validate_csrf_token('', ''))
    self.assertFalse(h._validate_csrf_token('invalid b64', 'invalid b64'))

    # no timestamp
    token = base64.urlsafe_b64encode('random')
    self.assertFalse(h._validate_csrf_token(token, token))
    token = base64.urlsafe_b64encode('random%s' % h.OAUTH2_CSRF_DELIMITER)
    self.assertFalse(h._validate_csrf_token(token, token))

    # no token key
    token = '%s%d' % (h.OAUTH2_CSRF_DELIMITER, long(time.time()))
    encoded = base64.urlsafe_b64encode(token)
    self.assertFalse(h._validate_csrf_token(encoded, encoded))

    # token timeout
    timeout = long(time.time()) - h.OAUTH2_CSRF_TOKEN_TIMEOUT - 1
    token = h._generate_csrf_token(_time=timeout)
    self.assertFalse(h._validate_csrf_token(token, token))


if __name__ == '__main__':
  unittest.main()
