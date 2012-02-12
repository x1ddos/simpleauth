# -*- coding: utf-8 -*-
import logging
import secrets

import webapp2
from webapp2_extras import auth, sessions, jinja2
from jinja2.runtime import TemplateNotFound

from simpleauth import SimpleAuthHandler


class BaseRequestHandler(webapp2.RequestHandler):
  def dispatch(self):
    # Get a session store for this request.
    self.session_store = sessions.get_store(request=self.request)
    
    try:
      # Dispatch the request.
      webapp2.RequestHandler.dispatch(self)
    finally:
      # Save all sessions.
      self.session_store.save_sessions(self.response)
  
  @webapp2.cached_property    
  def jinja2(self):
    """Returns a Jinja2 renderer cached in the app registry"""
    return jinja2.get_jinja2(app=self.app)
    
  @webapp2.cached_property
  def session(self):
    """Returns a session using the default cookie key"""
    return self.session_store.get_session()
    
  # @webapp2.cached_property
  # def auth(self):
  #     return auth.get_auth()
  
  @webapp2.cached_property
  def user(self):
    """Returns currently logged in user"""
    return auth.get_auth().get_user_by_session()
      
  @webapp2.cached_property
  def logged_in(self):
    """Returns true if a user is currently logged in, false otherwise"""
    return self.user is not None
  
      
  def render(self, template_name, template_vars={}):
    # Preset values for the template
    values = {
      'url_for'    : self.uri_for,
      'logged_in'  : self.logged_in
    }
    
    # Add manually supplied template values
    values.update(template_vars)
    
    # read the template or 404.html
    try:
      self.response.write(self.jinja2.render_template(template_name, **values))
    except TemplateNotFound:
      self.abort(404)

  def head(self, *args):
    """Head is used by Twitter. If not there the tweet button shows 0"""
    pass
    
    
class RootHandler(BaseRequestHandler):
  def get(self):
    """Handles default langing page"""
    self.render('home.html')
    
class ProfileHandler(BaseRequestHandler):
  def get(self):
    """Handles GET /profile"""    
    if self.logged_in:
      self.render('profile.html', {'user': self.user, 'session': self.session})
    else:
      self.redirect('/')


class AuthHandler(BaseRequestHandler, SimpleAuthHandler):
  """Authentication handler for all kinds of auth."""
  
  def _on_signin(self, data, auth_info):
    """Return value is ignored. Raise an exception if needed."""
    auth_id = auth_info['id']
    self.redirect('/')

  def logout(self):
    self.auth.unset_session()
    self.redirect('/')
    
  def _callback_uri_for(self, provider):
    return self.uri_for('auth_callback', provider=provider, _full=True)
    
  def _get_consumer_info_for(self, provider):
    """Returns a tuple (key, secret) for auth init requests."""
    return secrets.AUTH_CONFIG[provider]
