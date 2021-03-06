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
from patientdetail import Patientdetail
from fileupload import Fileupload
from fileupload import Fileuploadhandler
from fileupload import Filedownloadhandler
from filedetail import Filereader
from login import Login

from dbutils import OpenCursor
from basehandler import BaseHandler

# Set up our Config Dictionary
config = {}

# Set the Secret Key for Webapp2 Sessions
my_secret_key_text = 'simplyright takeheart secret session key'
my_secret_key = hashlib.sha1(my_secret_key_text).hexdigest()
config['webapp2_extras.sessions'] = {
    'secret_key': my_secret_key,
    'backends': {'datastore': 'webapp2_extras.appengine.sessions_ndb.DatastoreSessionFactory',
                 'memcache': 'webapp2_extras.appengine.sessions_memcache.MemcacheSessionFactory',
                 'securecookie': 'webapp2_extras.sessions.SecureCookieSessionFactory'}
    }
    

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
            'user': user,
            'session': self.session
            }

        # Let's get some information about the Application Owner

        # Get db Connection, Cursor
        (db,cursor) = OpenCursor()

        # db Query to get information for this user
        query = ''' select  owner_business_name,
                            owner_street_address,
                            owner_city,
                            owner_state
                    from    owners
                    where   owner_id='{ownid}'
                '''.format(ownid=self.session.get('owner_id'))
             
        cursor.execute(query)
        ownerinfo = cursor.fetchone()

        # Make Owner Information available to the Template
        template_values['ownerinfo'] = ownerinfo

        # db Query to get the count of patients for this owner
        query = ''' select  count(*)
                    from    patients
                    where   owner_id='{ownid}'
                '''.format(ownid=self.session.get('owner_id'))
             
        cursor.execute(query)
        patientcount = cursor.fetchone()
        template_values['patientcount'] = patientcount['count(*)']

        # db Query to get the count of devices for this owner
        query = ''' select  count(*)
                    from    devices
                    where   owner_id='{ownid}'
                '''.format(ownid=self.session.get('owner_id'))
             
        cursor.execute(query)
        devicecount = cursor.fetchone()
        template_values['devicecount'] = devicecount['count(*)']

        # db Query to get the count of files for this owner
        query = ''' select  count(*)
                    from    devices
                    where   owner_id='{ownid}'
                '''.format(ownid=self.session.get('owner_id'))
             
        cursor.execute(query)
        filecount = cursor.fetchone()
        template_values['filecount'] = filecount['count(*)']

        # Close the DB Connection
        db.close()

        # Make Owner Information available to the Template
        template_values['ownerinfo'] = ownerinfo
        
        # Set up the template and render the page
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

        template_values = {
            'user': user,
            'session': self.session
            }

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
                            patient_street_address,
                            patient_phone_number
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
        template_values['patients'] = patients

        template = JINJA_ENVIRONMENT.get_template('patientsearchresult.html')
        self.response.write(template.render(template_values))
            
app = webapp2.WSGIApplication([
    ('/', Overview),
    ('/patientdetail', Patientdetail),
    ('/fileupload', Fileupload),
    ('/fileuploadhandler',Fileuploadhandler),
    ('/filedownloadhandler/([^/]+)?',Filedownloadhandler),
    ('/filedetails', Filereader),
    ('/login', Login)
], debug=True, config=config)
