import jinja2
import webapp2
import os
import sys

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(),'template')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Patientsearch(webapp2.RequestHandler):

    def get(self):

        template = JINJA_ENVIRONMENT.get_template('custsearchresult.html')
        self.response.write(template.render())
