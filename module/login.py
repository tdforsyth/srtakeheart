import fix_path

import os
import sys
import jinja2
import webapp2
import MySQLdb

from webapp2_extras import sessions

import py_bcrypt.bcrypt as bcrypt

from wtforms import Form, TextField, PasswordField, SubmitField, validators
from wtforms.validators import ValidationError
from wtforms.validators import StopValidation


from dbutils import OpenCursor
from basehandler import BaseHandler

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

        # We will use a blank Login Form (defined below) for this page
        form = LoginForm()

        # If it hasn't been done already, log the user out
        self.session = {}
        self.session['isloggedin'] = False

        # Initialize the Template Values
        template_values = {}
        template_values['form'] = form

        # Display the Template
        self.response.write(template.render(template_values))

    def post(self):

        #This is the "Post" Handler - Process
        #the user's login information and decide if he's eligible to access
        #the application

        # Define the Template we will be using
        template = JINJA_ENVIRONMENT.get_template('login.html')

        # We will use a populated Login Form (defined below) for this page
        form = LoginForm(self.request.POST)

        # Check the user's login
        if self.request.method == 'POST' and form.validate():
            # Everything checks out - Log the user in

            # Set up the basics of the user's session
            self.session['isloggedin'] = True
            self.session['user'] = form.username.data

            # Lookup the rest of the user's information
            
            # Get db Connection, Cursor
            (db,cursor) = OpenCursor()

            # db Query to get information for this user
            query = ''' select  user_id,
                                owner_id,
                                user_first_name,
                                user_role
                        from    users
                        where   user_name='{uname}'
                    '''.format(uname=self.session['user'])
             
            cursor.execute(query)
            userinfo = cursor.fetchone()

            # Set up the rest of the user's session
            self.session['user_id'] = userinfo['user_id']
            self.session['owner_id'] = userinfo['owner_id']
            self.session['user_first_name'] = userinfo['user_first_name']
            self.session['user_role'] = userinfo['user_role']
   
            # Close the DB Connection
            db.close()

            # Send the user to the main application page - We are done
            # logging the user in
            self.redirect('/')
            
        else:
            # Things didn't validate, so go back to the login form
            
            # Initialize the Template Values
            template_values = {}
            template_values['form'] = form

            # Display the Template
            self.response.write(template.render(template_values))

# Custom Validators for our Forms (those requiring DB access)
class ValidatePassword(object):
    
    def __init__(self, message=None):
        if not message:
            message = u'Invalid Username or Password.  Please check your records.'
        self.message = message

    def __call__(self, form, field):
        # We run this validator last.  If there are already errors, we don't want
        # to run this validator; everything else needs to be checked first, THEN
        # we run the expensive DB calls
        if form.errors:
            raise StopValidation()
        
        # Get db Connection, Cursor
        (db,cursor) = OpenCursor()

        # db Query to get pw_hash for this user, if the user exists
        query = ''' select  pw_hash
                    from    users
                    where   user_name='{uname}'
                '''.format(uname=form.username.data)
             
        cursor.execute(query)
        pw_hash_dict = cursor.fetchone()
   
        # Close the DB Connection
        db.close()

        #IF we found a user, get the pw_hash.  If not, validation has failed
        if pw_hash_dict:
            pw_hash = pw_hash_dict['pw_hash']
        else:
            raise ValidationError(self.message)

        # Compare the DB password hash to the one the user submitted.  If
        # they don't match, validation has failed.
        # This also catches the case where the DB password is blank
        if pw_hash and not pw_hash=='':
            if not bcrypt.hashpw(field.data, pw_hash) == pw_hash:
                raise ValidationError(self.message)
        else:
            raise ValidationError(self.message)
 
#Here we define the Forms the Login Page will use
class LoginForm(Form):
    username  = TextField('Username', [
                        validators.Required(message=(u'A Username is required to Log In.')),
                        validators.Length(min=6, max=40, message=(u'Username must be between 6 and 40 charaters in length.')),
    ])
    password  = PasswordField('Password', [
                        validators.Required(message=(u'A Password is required to Log In.')),
                        validators.Length(min=8, max=40, message=(u'Password must be between 8 and 40 charaters in length.')),
                        validators.Regexp(regex='.*[A-Z].*', message=(u'Password must contain at least one capital letter.')),
                        validators.Regexp(regex='.*[0-9].*', message=(u'Password must contain at least one number.')),
                        ValidatePassword(message=(u'Invalid Username or Password.  Please check your records.'))
    ])
    submit    = SubmitField('Log In')
