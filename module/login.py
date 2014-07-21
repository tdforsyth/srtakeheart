import fix_path

import jinja2
import webapp2
import os
import sys
import MySQLdb

from webapp2_extras import sessions

from wtforms import Form, BooleanField, TextField, validators

from module.basehandler import BaseHandler

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(),'template')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Login(BaseHandler):

    def get(self):

        # This is the "Get" version of the page
        # Display this to get the user's name and password

        # Define the Template we will be using
        template = JINJA_ENVIRONMENT.get_template('login.html')

        # If it hasn't been done already, log the user out
        self.session['isloggedin'] = False
        self.session['resetpassword'] = False

        # Initialize the Template Values
        template_values = {}
        template_values['message'] = 'Please enter your username and password<br> to log into the application'

        # Display the Template
        self.response.write(template.render(template_values))

    def post(self):

        #This is the "Post" Handler - Process
        #the user's login information and decide if he's eligible to access
        #the application

        # Set the template and reset our output dictionary
        # so we'll be ready to output at any time
        template = JINJA_ENVIRONMENT.get_template('login.html')
        template_values = {}

        # Get the user_name from the input form
        user_name = self.request.get('user_name')

        # Get the user's information from the database
        
        # Open the DB Connection
        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/your-project-id:your-instance-name', user='root', cursorclass=MySQLdb.cursors.DictCursor)
        else:
            db = MySQLdb.connect(host='localhost', user='root', passwd='Gl@cierHe@rt', db='srtakeheart', cursorclass=MySQLdb.cursors.DictCursor)

        # Create a cursor
        cursor = db.cursor()

        query = ''' select  user_id,
                            owner_id,
                            pw_salt,
                            pw_hash,
                            user_email,
                            user_first_name,
                            user_last_name,
                            user_role
                    from    users
                    where   user_name='{uname}'
                '''.format(uname=user_name)
             
        cursor.execute(query)

        user = cursor.fetchone()
   
        # Close the DB Connection
        db.close()

        # If we found the user, do some stuff
        if user:

            # We check to see if the user is resetting their password.
            # If so, we'll set the values in the pw_salt and pw_hash
            # columns
            if self.session.get('resetpassword'):

                # Validate the Passwords Fields
                if   self.request.get('password_text') and \
                     self.request.get('confirm_password_text') and \
                      len(self.request.get('password_text'))>=8 and \
                     len(self.request.get('confirm_password_text'))>=8 and \
                     self.request.get('password_text')==self.request.get('confirm_password_text'):

                    # We Reset the Password
                    self.response.write('We\'re resetting the PW')
                    return

                else:

                    # We go back to the form with an error message
                    template_values['resetpassword'] = True
                    template_values['message'] = '''
                    Your password needs to be reset.<br>
                    Please enter a new password below.'

                    Both Passwords must match
                    and must be at least 8 characters in length
                    '''
                    template_values['user_name'] = user_name
                    
                    self.response.write(template.render(template_values))
                    return

            # First, we'll see if the password salt and hash fields
            # are populated.

             

            if user['pw_salt'] and user['pw_hash']:
                # If so, we'll check their password
                 self.response.write('<br>Checking PW...')

            else:
                # If the password and password salt are NOT populated,
                # We'll ask them to reset their password

                self.session['resetpassword'] = True

                template_values['resetpassword'] = True
                template_values['message'] = 'Your password needs to be reset.<br>  Please enter a new password below.'
                template_values['user_name'] = user_name
                
                self.response.write(template.render(template_values))            
        else:
            # If we didn't find the user, do some other stuff
            self.response.write('Nope - No User Like That')
    
        # We're done loggin in - Redirect to the main page
        # self.redirect('/')
