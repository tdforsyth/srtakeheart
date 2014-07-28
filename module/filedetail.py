import fix_path

import os
import sys
import re
import jinja2
import webapp2

from google.appengine.ext import blobstore
from webapp2_extras import sessions

from basehandler import BaseHandler

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(),'template')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Filereader(BaseHandler):

    def get(self):

        # We check the session to see if the user is logged in
        user = self.session.get('user')
        if not user:
            self.redirect('/login')
        
        template_values = {
            'user': user,
            'session': self.session
            }

        # Get the Blobkey for the File to be displayed from the request
        blob_key = self.request.get('blob_key')
        file_name = self.request.get('file_name')
        
        # Instantiate a BlobReader for a given Blobstore value.
        blob_reader = blobstore.BlobReader(blob_key)

        #pattern1 = re.compile(r'(?P<lineindex>+)(?P<linevalue>.+)')
        pattern1 = re.compile(r'^(?P<lineindex>[^\x1C]+)\x1C(?P<linelabel>[^\x1C]+)\x1C(?P<linevalue>.+)')
        
        filecontents = {}

        for line in blob_reader:

            try:
                uline = unicode( line, 'utf-8')
            except Exception:
                uline = unicode( line, 'latin-1')

            # Check to see if this line matches the pattern we expect
            m = pattern1.match(uline)

            # If there's a match
            if m:

                # First, clean up the Value a bit
                line_value = m.group('linevalue')

                # Remove double File separators at the end of the line
                p = re.compile( '\x1c\x1c$')
                line_value = p.sub( '',line_value)

                # Remove single File separators at the end of the line
                p = re.compile( '\x1c$')
                line_value = p.sub( '',line_value)

                # If there are any file separators left, replace them
                # with spaces
                p = re.compile( '\x1c')
                line_value = p.sub( ' ',line_value)
                
                # Store the results in a dictionary of dictionaries
                filecontents[int(m.group('lineindex'))] = {'linelabel': m.group('linelabel'), 'linevalue': line_value}

        # OK, Done reading the file.  Get ready to show the output with a template
        template_values['file_name'] = file_name
        template_values['filecontents'] = filecontents

        template = JINJA_ENVIRONMENT.get_template('filedetail.html')
        self.response.write(template.render(template_values))
