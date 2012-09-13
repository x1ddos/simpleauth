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

from google.appengine.api import apiproxy_stub
from google.appengine.api import urlfetch_service_pb
from google.appengine.api.urlfetch import DownloadError

class MockURLFetchServiceStub(apiproxy_stub.APIProxyStub):
  """URL Fetch AppEngine service mock that does not do actual requests.

  This mock doesn't follow redirects though.
  See https://bitbucket.org/gumptioncom/agar/overview for more details.
  """
  _responses = {}
  _method_map = {
    urlfetch_service_pb.URLFetchRequest.GET: 'GET',
    urlfetch_service_pb.URLFetchRequest.POST: 'POST',
    urlfetch_service_pb.URLFetchRequest.HEAD: 'HEAD',
    urlfetch_service_pb.URLFetchRequest.PUT: 'PUT',
    urlfetch_service_pb.URLFetchRequest.DELETE: 'DELETE' }
  
  def __init__(self, service_name='urlfetch'):
      super(MockURLFetchServiceStub, self).__init__(service_name)

  @classmethod
  def set_response(cls, url, method=None, **kwargs):
    """Registers fake response to a urlfetch of the given url.

    Additional kwargs may contain: 'content', 'status_code' and 'headers'.
    """
    MockURLFetchServiceStub._responses[(url, method)] = kwargs

  @classmethod
  def clear_responses(cls):
      MockURLFetchServiceStub._responses.clear()

  def _decode_http_method(self, pb_method):
    """Decode the method from the protocol buffer; stolen from urlfetch_stub.py
    """
    method = self._method_map.get(pb_method)

    if not method:
      raise apiproxy_errors.ApplicationError(
        urlfetch_service_pb.URLFetchServiceError.UNSPECIFIED_ERROR)

    return method
          
  def _Dynamic_Fetch(self, request, response):
    url = request.url()
    method = self._decode_http_method(request.method())
    http_response = MockURLFetchServiceStub._responses.get((url, method)) \
      or MockURLFetchServiceStub._responses.get((url, None))

    if http_response is None:
      raise Exception(
        "No HTTP response was found for the URL '%s' %s" %
        (url, repr(MockURLFetchServiceStub._responses)) )

    if isinstance(http_response['content'], DownloadError):
      raise http_response['content']

    response.set_statuscode(http_response.get('status_code') or 200)
    response.set_content(http_response.get('content'))

    if http_response.get('headers'):
      for header_key, header_value in http_response['headers'].items():
          header_proto = response.add_header()
          header_proto.set_key(header_key)
          header_proto.set_value(header_value)


class TestMixin(object):
  def setUp(self): 
    super(TestMixin, self).setUp()
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()    
    self.testbed.init_memcache_stub()
    self.testbed.init_user_stub()
    urlfetch_stub = MockURLFetchServiceStub()
    self.testbed._register_stub(testbed.URLFETCH_SERVICE_NAME, urlfetch_stub)

    self._logger = logging.getLogger()
    self._old_log_level = self._logger.getEffectiveLevel()
    
  def tearDown(self):
    super(TestMixin, self).tearDown()
    self._logger.setLevel(self._old_log_level)
    MockURLFetchServiceStub.clear_responses()
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

  def set_urlfetch_response(self, url, content=None, status_code=None, 
                            headers=None, method=None):
    """
    Register an HTTP response for ``url`` with body containing ``content``.

    Examples::

      # Will cause a 200 OK response with no body for all HTTP methods:
      self.set_response("http://example.com")

      # Will cause a 404 Not Found for GET requests with 'gone fishing' 
      # as the body:
      self.set_response("http://example.com/404ed", 
        content='gone fishing', status_code=404)

      # Will cause a 303 See Other for POST requests with a Location header 
      # and no body:
      self.set_response("http://example.com/posts", 
        status_code=303, headers={'Location': 'http://example.com/posts/123'})

      # Will cause a DownloadError to be raised when the URL is requested:
      from google.appengine.api import urlfetch
      self.set_response("http://example.com/boom", 
        content=urlfetch.DownloadError("Something Failed"))

    :param url: the URL for the HTTP request.
    :param content: the HTTP response's body, or an instance of DownloadError 
                    to simulate a failure.
    :param status_code: the expected status code. Defaults to 200 if not set.
    :param headers: a ``dict`` of headers for the HTTP response.
    :param method: the HTTP method that the response must match. If not set, 
                   all requests with the same URL will return the same thing.
    """
    MockURLFetchServiceStub.set_response(url, 
      content=content, status_code=status_code, headers=headers, method=method)

  def expectErrors(self):
    if self.isDefaultLogging():
      self._logger.setLevel(logging.CRITICAL)

  def expectWarnings(self):
    if self.isDefaultLogging():
      self._logger.setLevel(logging.ERROR)

  def isDefaultLogging(self):
    return self._old_log_level == logging.WARNING
