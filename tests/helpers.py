# -*- coding: utf-8 -*-

# See this for more info about GAE unit testing testbed:
# http://code.google.com/appengine/docs/python/tools/localunittesting.html
#
# Also, Python 2.7 unittesting:
# http://docs.python.org/library/unittest.html
import os

from google.appengine.ext import testbed
# from google.appengine.api import user_service_pb
# from google.appengine.tools import dev_appserver_index

# import webapp2
# import webtest

class BaseTestMixin(object):
  def setUp(self):
    super(BaseTestMixin, self).setUp()
    self.testbed = testbed.Testbed()
    self.testbed.activate()

    # setup datastore and its indexes
    # self.testbed.init_datastore_v3_stub(require_indexes=True)
    # dev_appserver_index.SetupIndexes(None, "%s/../" % os.path.dirname(__file__))
    self.testbed.init_datastore_v3_stub()
    
    self.testbed.init_memcache_stub()
    self.testbed.init_taskqueue_stub()
    self.testbed.init_urlfetch_stub()
    self.testbed.init_user_stub()
    self.testbed.init_xmpp_stub()
    self.testbed.init_mail_stub()
    self.testbed.init_blobstore_stub()
    
    
  def tearDown(self):
    super(BaseTestMixin, self).tearDown()
    self.testbed.deactivate()

# class  BaseTest(TestCase):
#   """
#   A base class for testing web requests. Provides a wrapper around
#   the webtest package that is compatable with gaetestbed's.
# 
#   To use, inherit from the WebTest class and define a class-level
#   variable called APPLICATION that is set to the WSGI application
#   under test.
#   
#   See these more more details:
#   
#   https://bitbucket.org/gumptioncom/agar/overview
#   http://webtest.pythonpaste.org/en/latest/index.html
#   http://lxml.de/parsing.html#parsing-html
# 
#   BeautifulSoup:
#   http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html#Parsing HTML
#   """
#   def setUp(self):
#     super(WebTest, self).setUp()
#     os.environ['HTTP_HOST'] = 'localhost'
#     
#   def tearDown(self):
#     super(WebTest, self).tearDown()
#     
#   @property
#   def app(self):
#     if not getattr(self, '_web_test_app', None):
#       self._web_test_app = webtest.TestApp(self.APPLICATION)
#     return self._web_test_app
#     
#   @property
#   def response(self):
#     """Returns response of the latest executed request"""
#     return self._last_response
#     
#   @property
#   def html(self):
#     """Returns BeautifulSoup body object"""
#     return self.response.html
#     
#   def first_by_xpath(self, xp, root_elem = None, response = None):
#     """
#     Searches for a specific element via XPath in the last response 
#     or provided element or response object
#     """
#     return (root_elem or (response or self.response).lxml).xpath(xp)[0]
# 
#   def assertTag(self, name, elem=None, **kwargs):
#     """Asserts that a tag with given name and other attributes exists.
#     This is a simple wrapper only to nicely format the message in case of a failure.
#     Examples:
#       self.assertTag('body', text='page body')
#       self.assertTag('h1', text=re.compile('list', re.I))
#     """
#     root = elem or self.html
#     kwargs.update({'name': name})
#     found = root.find(**kwargs)
#     if not found:
#       self.fail("Couldn't find <%s> %s in\n%s" % (name, kwargs, root.prettify()))
#     return found
#       
#   def assertReTagContent(self, pattern, tagname, **kwargs):
#     """Asserts that a tag with given tagname and kwargs matches a regexp pattern.
#     Examples:
#       self.assertReTagContent('pages', 'a', attrs={'href': self.pages_base_url})
#       self.assertReTagContent('sample page body', 'div', attrs={'role':"main", 'class':"container"})
#     """
#     kwargs.update({'name': tagname})
#     self.assertRegexpMatches(str(self.html.findAll(**kwargs)), pattern)
# 
#   def assertOK(self, response=None):
#     """Makes sure the HTTP response was 200 OK"""
#     self.assertEqual(200, (response or self.response).status_int)
# 
#   def assertRedirects(self, to=None, response=None):
#     """Asserts that a 302 redirect was received as a response"""
#     _resp = response or self.response
#     self.assertEqual(302, _resp.status_int)
#     if to:
#       if not to.startswith("http"):
#         to = 'http://localhost%s' % to
#       self.assertEqual(_resp.headers['Location'], to)
# 
#   def assertForbidden(self, response=None):
#     """Asserts that access to the requested path is forbidden"""
#     self.assertEqual(403, (response or self.response).status_int)
# 
#   def assertNotFound(self, response=None):
#     """Asserts 404 (not found) response is returned"""
#     self.assertEqual(404, (response or self.response).status_int)
#     
#   def get(self, url, params=None, headers=None, extra_environ=None):
#     """Sends a GET request (to self.APPLICATION) to the specified URL
#     and stores it this object. Can be accessed later on as self.response"""
#     self._last_response = self.app.get(url, params=params, headers=headers, status="*", expect_errors=True)
#     return self.response
# 
#   def post(self, url, params='', headers=None, extra_environ=None, upload_files=None):
#     """Same as self.get(...) but does a POST request."""
#     self._last_response = self.app.post(url, params, headers=headers, status="*", expect_errors=True, upload_files=upload_files)
#     return self.response
