[![Build Status](https://drone.io/github.com/crhym3/simpleauth/status.png)](https://drone.io/github.com/crhym3/simpleauth/latest)

This python module provides a simple authentication wrapper for a
[Google App Engine][13] app.

Supported specs:

  - OAuth 2.0
  - OAuth 1.0(a)
  - OpenID

Supported providers out of the box:

  - Google (OAuth 2.0)
  - Facebook (OAuth 2.0)
  - Windows Live (OAuth 2.0)
  - foursquare (OAuth 2.0)
  - Twitter (OAuth 1.0a)
  - LinkedIn (OAuth 1.0a, deprecated)
  - LinkedIn (OAuth 2.0)
  - OpenID, using App Engine users module API

Dependencies:

  - [python-oauth2][1]. This is actually a library implementing OAuth 1.0 specs.
  - [httplib2][2] (as a dependency of python-oauth2)

Links:

  - Demo (example app): https://simpleauth.appspot.com
  - Source code: https://github.com/crhym3/simpleauth
  - Mirror on Google Code: http://code.google.com/p/gae-simpleauth/
  - Discussions: https://groups.google.com/d/forum/gae-simpleauth


## Install
  
1. Clone the source repo and place `simpleauth` module into your
   app root or a sub dir. If you do the latter don't forget to add
   it to your `sys.path`.

2. Get oauth2 lib (e.g. `pip install oauth2` or [clone the repo][1]) and copy it
   over to your app root or a sub dir.
  
3. Get [httplib2][2] and again, copy it to your app root.

## Usage

1. Create a request handler by subclassing SimpleAuthHandler, e.g.

    ```python
    class AuthHandler(SomeBaseRequestHandler, SimpleAuthHandler):
      """Authentication handler for all kinds of auth."""

      def _on_signin(self, data, auth_info, provider):
      """Callback whenever a new or existing user is logging in.
      data is a user info dictionary.
      auth_info contains access token or oauth token and secret.

      See what's in it with logging.info(data, auth_info)
      """

      auth_id = '%s:%s' % (provider, data['id'])

      # Possible flow:
      # 
      # 1. check whether user exist, e.g.
      #    User.get_by_auth_id(auth_id)
      #
      # 2. create a new user if it doesn't
      #    User(**data).put()
      #
      # 3. sign in the user
      #    self.session['_user_id'] = auth_id
      #
      # 4. redirect somewhere, e.g. self.redirect('/profile')
      #
      # See more on how to work the above steps here:
      # http://webapp-improved.appspot.com/api/webapp2_extras/auth.html
      # http://code.google.com/p/webapp-improved/issues/detail?id=20
     
      def logout(self):
        self.auth.unset_session()
        self.redirect('/')

      def _callback_uri_for(self, provider):
        return self.uri_for('auth_callback', provider=provider, _full=True)

      def _get_consumer_info_for(self, provider):
        """Should return a tuple (key, secret) for auth init requests.
        For OAuth 2.0 you should also return a scope, e.g.
        ('my app id', 'my app secret', 'email,user_about_me')

        The scope depends solely on the provider.
        See example/secrets.py.template
        """
        return secrets.AUTH_CONFIG[provider]
    ```

   Note that SimpleAuthHandler isn't a real request handler. It's up to you.
   For instance, SomeBaseRequestHandler could be [webapp2.RequestHandler][6].

2. Add routing so that `/auth/<PROVIDER>`, `/auth/<PROVIDER>/callback`
   and `/logout` requests go to your `AuthHandler`.
   
   For instance, in webapp2 you could do:
   
   ```python
   # Map URLs to handlers
   routes = [
     Route('/auth/<provider>',
       handler='handlers.AuthHandler:_simple_auth', name='auth_login'),
     Route('/auth/<provider>/callback', 
       handler='handlers.AuthHandler:_auth_callback', name='auth_callback'),
     Route('/logout',
       handler='handlers.AuthHandler:logout', name='logout')
   ]
   ```

3. That's it. See a sample app in the [example dir][3].
   To run the example app, copy `example/secrets.py.template` into
   `example/secrets.py`, modify accordingly and start the app locally
   by executing `dev_appserver.py example/`


## OAuth scopes, keys and secrets

This section is just a bunch of links to the docs on authentication with
various providers.

### Google

  - Docs: https://developers.google.com/accounts/docs/OAuth2WebServer
  - Get client/secret: http://code.google.com/apis/console

Multiple scopes should be space-separated, e.g.
`https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email`

Multiple callback URLs on different domains are awesomely supported.
If you're running two versions of the app, say one on `localhost` and another
on `example.org`, simply add all of the callbacks including host, port and 
protocol to `Redirect URIs` list on API Access tab.

### Facebook

  - Docs: https://developers.facebook.com/docs/authentication/server-side/
  - Get client/secret: https://developers.facebook.com/apps

Multiple Scopes should be comma-separated, e.g. `user_about_me,email`.

Full list of scopes:
http://developers.facebook.com/docs/authentication/permissions/

Multiple callback URLs on different domains are not supported by a single app
registration. If you need to test your app on say, `localhost` and
`example.org`, you should probably register two different applications and use
the appropriate set of key/secret: one for localhost, and the other
for example.org.

Also, there's a `Sandbox Mode` checkbox on Facebook's app settings page. Make
sure it's disabled for a public/live website. Otherwise, almost nobody
except you will be able to authenticate.

### LinkedIn OAuth 2.0

  - Docs: https://developer.linkedin.com/documents/authentication
  - Get client/secret: https://www.linkedin.com/secure/developer

Scopes are space-separated, e.g. `r_fullprofile r_emailaddress r_network`.

See Member Permissions section for more details:
https://developer.linkedin.com/documents/authentication#granting

### Windows Live

  - Docs: http://msdn.microsoft.com/en-us/library/live/hh243649.aspx
  - Get client/secret: https://manage.dev.live.com

Scopes are space-separated, e.g. `wl.signin wl.basic`.

Full list of scopes:
http://msdn.microsoft.com/en-us/library/live/hh243646.aspx

Multiple callback URLs on different domains are not supported by a single app
registration. If you need to test your app on say, `localhost` and
`example.org`, you should probably register two different applications and use
the appropriate set of key/secret: one for localhost, and the other
for example.org.

### LinkedIn OAuth 1.0a (deprecated)

  - Docs: https://developer.linkedin.com/documents/authentication
  - Get client/secret: https://www.linkedin.com/secure/developer

Scopes are not supported. This is OAuth 1.0a.

Even though LinkedIn will not give you any error about improper callback URI,
it'll always use the value set in app's settings page. So, if you have two
versions, say one on `localhost` and another on `example.org`, you'll probably
want to register two applications (e.g. `dev` and `production`) and use 
appropriate set of key/secret accordingly.

### Twitter

  - Docs: https://dev.twitter.com/docs/auth/implementing-sign-twitter
  - Get client/secret: https://dev.twitter.com/apps

Scopes are not supported. This is OAuth 1.0a.

When registering a new app, you have to specify a callback URL. Otherwise,
it is considered as an `off-band` app and users will be given a PIN code
instead of being redirected back to your site.

Even though Twitter will not give you any error about improper callback URI,
it'll always use the value set in app's settings page. So, if you have two
versions, say one on `localhost` and another on `example.org`, you'll probably
want to register two applications (e.g. `dev` and `production`) and use 
appropriate set of key/secret accordingly.

### OpenID

For OpenID to work you'll need to set `AuthenticationType` to `FederatedLogin`
in [App Engines application settings][4]. Beware of [this issue][12] if you enable FederatedLogin.


## CSRF protection

You can optionally enable cross-site-request-forgery protection for OAuth 2.0:

```python
class AuthHandler(webapp2.RequestHandler, SimpleAuthHandler):

  # enabled CSRF state token for OAuth 2.0
  OAUTH2_CSRF_STATE = True

  # ...
  # rest of the stuff from step 4 of the above.
```

This will use the optional OAuth 2.0 `state` param to guard against CSRFs by
setting a user session token during Authorization step and comparing it 
against the `state` parameter on callback.

For this to work your handler has to have a session dict-like object on the 
instance. Here's an example using [webapp2_extras session][5]:

```python
import webapp2
from webapp2_extras import sessions

class AuthHandler(webapp2.RequestHandler, SimpleAuthHandler):
  # enabled CSRF state token for OAuth 2.0
  OAUTH2_CSRF_STATE = True

  @webapp2.cached_property
  def session(self):
    """Returns a session using the default cookie key"""
    return self.session_store.get_session()

  def dispatch(self):
    # Get a session store for this request.
    self.session_store = sessions.get_store(request=self.request)
    try:
      # Dispatch the request.
      webapp2.RequestHandler.dispatch(self)
    finally:
      # Save all sessions.
      self.session_store.save_sessions(self.response)

  # ...
  # the rest of the stuff from step 1 of Usage example.
```

This simple implementation assumes it is safe to use user sessions.
If, however, user's session can be hijacked, the authentication flow could
probably be bypassed anyway and this CSRF protection becomes the least 
of the problems.

Alternative implementation could involve `HMAC` digest. If anything serious 
pops up (e.g. [see this SO question][7]) please submit a bug on the issue
tracker.


## Catching errors

There are a couple ways to catch authentication errors if you don't want your
app to display a `Server Error` message when something goes wrong during
an auth flow.

You can use [webapp2's built-in functionality][8] and define
`handle_exception(self, exception, debug)` instance method on the handler
that processes authentication requests or on a base handler if you have one.
Here's a simple example:

```python
class AuthHandler(webapp2.RequestHandler, SimpleAuthHandler):
  # _on_signin() and other stuff
  # ...

  def handle_exception(self, exception, debug):
    # Log the error
    logging.error(exception)
 
    # Do something based on the exception: notify users, etc.
    self.response.write(exception)
    self.response.set_status(500)
```

You can also define global (app-wise) error handlers using `app.error_handlers`
dict (where app is a `webapp2.WSGIApplication instance`).


Another solution is, if you're using webapp2's `dispatch` method like in the
CSRF snippet above, you could do something like this:

```python
  from simpleauth import Error as AuthError

  def dispatch(self):
    try:
      # Dispatch the request.
      webapp2.RequestHandler.dispatch(self)
    except AuthError as e:
      # Do something based on the error: notify users, etc.
      logging.error(e)
      self.redirect('/')
```

Alternatively, you can also use App Engine built-in functionality and define
error handlers in `app.yaml` as described in [Custom Error Responses][9].

Lastly, if nothing from the above works for you, override `_simple_auth()`
and/or `_auth_callback()` methods. For instance:

```python
from simpleauth import SimpleAuthHandler
from simpleauth import Error as AuthError

class AuthHandler(webapp2.RequestHandler, SimpleAuthHandler):
  def _simple_auth(self, provider=None):
    try:
      super(AuthHandler, self)._simple_auth(provider)
    except AuthError as e:
      # Do something based on the error: notify users, etc.
      logging.error(e)
      self.redirect('/')
```

## CONTRIBUTORS

Submit a pull request or better yet, use Rietveld at
[codereview.appspot.com][10].

There are so many people contributed to this project (which is awesome!)
but I seemed to have lost track of some of them to put a complete and up-to-date list.
Though I try keeping all [commits][11] with their authors intact, or just 
mention people in commit messages.

If you want to be mentioned here please do send me an email!


## CHANGELOG

  - v0.1.4 - 2013-01-09
    * lxml lib requirement is now optional
      http://code.google.com/p/gae-simpleauth/issues/detail?id=3
    * Updated Windows Live OAuth 2.0 endpoints
    * A little more doc in this readme and code comments

  - v0.1.3 - 2012-09-19
    * CSRF protection for OAuth 2.0
      http://code.google.com/p/gae-simpleauth/issues/detail?id=1
    * Custom exceptions
      http://code.google.com/p/gae-simpleauth/issues/detail?id=2
    * Example app improvements, including:
      - CSRF guard
      - show exception messages for demo purposes
      - prettier output of session, profile data and auth_info dictionaries
      - https://github.com/crhym3/simpleauth/issues/4
      - https://github.com/crhym3/simpleauth/issues/5
    * More useful info in README


[1]: https://github.com/simplegeo/python-oauth2
[2]: http://code.google.com/p/httplib2/
[3]: https://github.com/crhym3/simpleauth/tree/master/example
[4]: https://developers.google.com/appengine/docs/adminconsole/applicationsettings
[5]: http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html
[6]: http://webapp-improved.appspot.com/api/webapp2.html#webapp2.RequestHandler
[7]: http://security.stackexchange.com/questions/20187/oauth2-cross-site-request-forgery-and-state-parameter
[8]: http://webapp-improved.appspot.com/guide/exceptions.html
[9]: https://developers.google.com/appengine/docs/python/config/appconfig#Custom_Error_Responses
[10]: https://codereview.appspot.com/
[11]: https://github.com/crhym3/simpleauth/commits/master
[12]: https://code.google.com/p/googleappengine/issues/detail?id=3258
[13]: https://cloud.google.com/products/
