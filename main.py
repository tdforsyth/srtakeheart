import fix_path

import cgi
import cgitb
import os
import sys
import urllib
import jinja2
import webapp2
import re
import MySQLdb
import hashlib

from webapp2_extras import sessions

# Here we are importing 3rd Party Libraries
import libs.py_bcrypt.bcrypt as bcrypt

# Here we are importing the classes we have defined
from patientsearchresult import Patientsearch
from patientdetail import Patientdetail
from fileupload import Fileupload
from fileupload import Fileuploadhandler
from fileupload import Filedownloadhandler
from filedetail import Filereader
from login import Login
from basehandler import BaseHandler

# Set up our Config Dictionary
config = {}

# Set the Secret Key for Webapp2 Sessions
my_secret_key_text = 'simplyright takeheart secret session key'
my_secret_key = hashlib.sha1(my_secret_key_text).hexdigest()
config['webapp2_extras.sessions'] = {'secret_key': my_secret_key}

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(),'template')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Overview(BaseHandler):

    def get(self):
    # This is the "Get" method - It shows the summary of current
    # application state, and allows users to search for existing
    # patients, or create new ones

        # We check the session to see if the user is logged in
        user = self.session.get('user')
        if not user:
            self.redirect('/login')
        
        template_values = {
            'user': user
            }

        template = JINJA_ENVIRONMENT.get_template('overview.html')
        self.response.out.write(template.render(template_values))

    def post(self):
    # This is the "Post" method - If the user searches for an
    # existing patient, it either gets the patient and transfers
    # control to the Search Results pages, 
    # or returns to the Overview page with a "No Patient Found" message

        # We check the session to see if the user is logged in
        user = self.session.get('user')
        if not user:
            self.redirect('/login')

        # Connect to the MySQL Database.  If this is production, to production
        # otherwise to the Dev DB
        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/your-project-id:your-instance-name', user='root', cursorclass=MySQLdb.cursors.DictCursor)
        else:
            db = MySQLdb.connect(host='localhost', user='root', passwd='Gl@cierHe@rt', db='srtakeheart', cursorclass=MySQLdb.cursors.DictCursor)

        search_text = self.request.get('searchtext')

        # Open a cursor to show contects of srtakeheart.patients
        cursor = db.cursor()
        query = ''' select  owner_id,
                            patient_id,
                            last_name,
                            first_name,
                            address,
                            phone_number
                    from    patients
                    where   lower(patients.last_name) like lower('%{srch_txt}%')
                    or      lower(patients.first_name) like lower('%{srch_txt}%')
                    order by 3,4
        '''.format(srch_txt=search_text)
        cursor.execute(query)

        # Write the results of all the rows in the cursor to a list of
        # patient dictionaries
        patients = cursor.fetchall()

        # Close the Database connection
        db.close()
    
        # Prepare values to call the template
        template_values = {'patients': patients}

        template = JINJA_ENVIRONMENT.get_template('patientsearchresult.html')
        self.response.write(template.render(template_values))
            
app = webapp2.WSGIApplication([
    ('/', Overview),
    ('/patientsearch', Patientsearch),
    ('/patientdetail', Patientdetail),
    ('/fileupload', Fileupload),
    ('/fileuploadhandler',Fileuploadhandler),
    ('/filedownloadhandler/([^/]+)?',Filedownloadhandler),
    ('/filedetails', Filereader),
    ('/login', Login)
], debug=True, config=config)
