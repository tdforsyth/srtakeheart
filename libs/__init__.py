# Here we define some universal things all classes / modules will need
import os
import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'template')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
