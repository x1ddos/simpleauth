# -*- coding: utf-8 -*-
import re
import unicodedata

def decode(var):
  """Safely decode form input"""
  if not var: return var
  return unicode(var, 'utf-8') if isinstance(var, str) else unicode(var)


def slugify(value):
  """
  Normalizes string, converts to lowercase, removes non-alpha characters,
  and converts spaces to hyphens.

  From Django's "django/template/defaultfilters.py".
  """
  value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
  value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
  return re.sub('[-\s]+', '-', value)
