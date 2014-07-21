import jinja2
import webapp2
import os
import sys
import urllib
import MySQLdb

#from google.appengine.ext import webapp
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(),'template')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Fileupload(webapp2.RequestHandler):

    # This is the GET handler - It loads the File Upload Form
    # and makes sure the submitted file is uploaded to the blobstore
    def get(self):
       
        # Read the Patient and Owner IDs from the URL String
        patientid = self.request.get('pid')
        ownerid = self.request.get('oid')

        #Here we create a URL to upload the file to
        upload_url = blobstore.create_upload_url('/fileuploadhandler')

        #Load all the values that the webpage will need
        template_values = {
            'upload_url': upload_url,
            'oid': ownerid,
            'pid': patientid
        }

        #Serve the webpage
        template = JINJA_ENVIRONMENT.get_template('fileupload.html')
        self.response.write(template.render(template_values))

class Fileuploadhandler(blobstore_handlers.BlobstoreUploadHandler):
    # This is the POST handler - It handles the file once it has been
    # uploaded 
    def post(self):

        # Read the Patient and Owner IDs from the prior form
        patientid = self.request.get('pid')
        ownerid = self.request.get('oid')
        
        # Deal with the files uploaded.  Loop in case there
        # is more than one file

        for upload in self.get_uploads():

               # Insert an entry for this file into the files table
               self.response.write(str(upload.key()))
               self.response.write('<br>')
               self.response.write(upload.filename)
               #current_file.blob_key = upload.key()



               # Open the DB Connection
               if (os.getenv('SERVER_SOFTWARE') and
                   os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
                   db = MySQLdb.connect(unix_socket='/cloudsql/your-project-id:your-instance-name', user='root', cursorclass=MySQLdb.cursors.DictCursor)
               else:
                   db = MySQLdb.connect(host='localhost', user='root', passwd='Gl@cierHe@rt', db='srtakeheart', cursorclass=MySQLdb.cursors.DictCursor)

               # Create a cursor
               cursor = db.cursor()
            
               query = ''' insert into files
                           set     owner_id='{oid}',
                                   patient_id='{pid}',
                                   file_name='{fname}',
                                   file_blob_key='{fbkey}'
                       '''.format( oid=ownerid,
                                   pid=patientid,
                                   fname=upload.filename,
                                   fbkey=str(upload.key()))

               # Execute the Query
               cursor.execute(query)

        # Commit the changes and close the DB Connection
        db.commit()
        db.close()
    
        # We're done saving files - Go back to the Patient Details page
        self.redirect('/patientdetail?oid=%s&pid=%s' % (ownerid,patientid))

        # Placeholder - Shows what was committed, and allows the uploaded
        # file to be downloaded
        #self.response.write('<a href="/filedownloadhandler/%s">Download File</a>' % str(upload.key()))
        
class Filedownloadhandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource)) 
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)
