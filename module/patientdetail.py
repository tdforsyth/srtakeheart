import fix_path

import os
import sys
import jinja2
import webapp2
import MySQLdb

from webapp2_extras import sessions

from wtforms import Form, TextField, SelectField, PasswordField, SubmitField, validators
from wtforms.validators import ValidationError
from wtforms.validators import StopValidation

from dbutils import OpenCursor
from basehandler import BaseHandler

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(),'template')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Handles the form that allows entry and update of user details
class Patientdetail(BaseHandler):

    # This is the "Get" handler.  It is invoked when creating a new user,
    # or when loading an existing user record
    def get(self):

        # We check the session to see if the user is logged in
        user = self.session.get('user')
        if not user:
            self.redirect('/login')
        
        template_values = {
            'user': user,
            'session': self.session
            }

        # We will use a blank Login Form (defined below) for this page
        form = PatientForm()

        # Try to get the Owner and Patient IDs from the Query String
        ownerid = self.session.get('owner_id')
        patientid = self.request.get('pid')
        self.session['patient_id'] = patientid
     
        # If there IS a Patient ID, connect to the DB and
        # look up the Patient Record
        if (patientid):

               # Look up the patient in the DB
               patient = Loadpatientrecord(ownerid,patientid)

               #Load the values into the form to be rendered
               form.firstname.data = patient['first_name']
               form.lastname.data = patient['last_name']
               form.salutation.data = patient['salutation']
               form.gender.data = patient['gender']
               form.address.data = patient['patient_street_address']
               form.city.data = patient['patient_city']
               form.state.data = patient['patient_state']
               form.postcode.data = patient['patient_postal_code']
               form.country.data = patient['patient_country']
               form.phone_number.data = patient['patient_phone_number']
               form.email.data = patient['patient_email_address']

               template_values['form'] = form

               # We're also going to see if this customer has any files
               # If they do, we're going to show a list of these
              
               files = Loadpatientfiles(ownerid,patientid)

               template_values['files'] = files                   

        # Render the Template (blank if we didn't find values above)                          
        template = JINJA_ENVIRONMENT.get_template('patientdetail.html')
        self.response.write(template.render(template_values))

    # This is the "Post" handler.  It is invoked when the form
    # posts to itself with some user data filled in.  We will check whether
    # the data is good.  If not, we'll reload the same form with some errors
    # to be fixed.  If it is good, we'll save the changes
    def post(self):

        # We check the session to see if the user is logged in
        user = self.session.get('user')
        if not user:
            self.redirect('/login')
        
        template_values = {
            'user': user,
            'session': self.session
            }

        # We will use a populated Login Form (defined below) for this page
        form = PatientForm(self.request.POST)

        # Check the user's submitted patient data
        if self.request.method == 'POST' and form.validate():
            # Everything checks out - Save the data

            # Get db Connection, Cursor
            (db,cursor) = OpenCursor()

            # Get the Owner and Patient IDs from the Session (Patient ID may not exist)
            ownerid = self.session.get('owner_id')
            patientid = self.session.get('patient_id')

            if (patientid):

                # If there is a patient ID, this is an existing record; create
                # an update query

                query= u''' update  patients'
                            set     first_name='{fname}',
                                    last_name='{lname}',
                                    salutation='{salut}',
                                    gender='[gender}',
                                    patient_street_address='{addr}',
                                    patient_city='{city}',
                                    patient_state='[state]'
                                    patient_postal_code='{postcode}',
                                    patient_country='{country}',
                                    patient_phone_number='{pnum}',
                                    patient_email_address = '{email}'
                            where   owner_id={oid}
                            and     patient_id={pid}
                        '''.format(oid=ownerid,
                                   pid=patientid,
                                   fname=form.firstname.data,
                                   lname=form.lastname.data,
                                   salut=form.salutation.data,
                                   gender=form.gender.data,
                                   addr=form.address.data,
                                   city=form.city.data,
                                   state=form.state.data,
                                   postcode=form.postalcode.data,
                                   country=form.country.data,
                                   pnum=form.phonenumber.data,
                                   email=form.email.data)

            
            else:
                # This is a new customer - Create a query to insert the record
                
                query = u''' insert into patients'
                             set         owner_id={oid},
                                         first_name='{fname}',
                                         last_name='{lname}',
                                         salutation='{salut}',
                                         gender='[gender}',
                                         patient_street_address='{addr}',
                                         patient_city='{city}',
                                         patient_state='[state]'
                                         patient_postal_code='{postcode}',
                                         patient_country='{country}',
                                         patient_phone_number='{pnum}',
                                         patient_email_address = '{email}'
                        '''.format(oid=ownerid,
                                   pid=patientid,
                                   fname=form.firstname.data,
                                   lname=form.lastname.data,
                                   salut=form.salutation.data,
                                   gender=form.gender.data,
                                   addr=form.address.data,
                                   city=form.city.data,
                                   state=form.state.data,
                                   postcode=form.postalcode.data,
                                   country=form.country.data,
                                   pnum=form.phonenumber.data,
                                   email=form.email.data)

            # Execute the Query
            cursor.execute(query)
    
            # Commit the changes and close the DB Connection
            db.commit()
            db.close()
    
            # We're done saving - Go back to the overview page
            self.redirect('/')
            
        else:
            # Send the user back to the form for more work
            
            # Initialize the Template Values                     
            template = JINJA_ENVIRONMENT.get_template('patientdetail.html')
            template_values['form'] = form

            # Display the Template
            self.response.write(template.render(template_values))

def Loadpatientfiles(ownerid,patientid):

    # Connect to the MySQL Database.  If this is production, to production
    # otherwise to the Dev DB
    if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        db = MySQLdb.connect(unix_socket='/cloudsql/your-project-id:your-instance-name', user='root', cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host='localhost', user='root', passwd='Gl@cierHe@rt', db='srtakeheart', cursorclass=MySQLdb.cursors.DictCursor)

    # Create a cursor
    cursor = db.cursor()

    # Create a query to find the Files for Patient
    query = ''' select  file_name,
                        file_blob_key
                from    files
                where   owner_id = {ownid}
                and      patient_id = {patid}
            '''.format(ownid=ownerid,patid=patientid)

    # Execute the Query and load the results to a dictionary
    cursor.execute(query)
    files = cursor.fetchall()

    # Close the DB Connection
    db.close()

    # Return the details of the customer to whoever called
    return files

def Loadpatientrecord(ownerid,patientid):

    # Get db Connection, Cursor
    (db,cursor) = OpenCursor()

    # Get the details for this customer
    query = ''' select  first_name,
                        last_name,
                        salutation,
                        gender,
                        patient_street_address,
                        patient_city,
                        patient_state,
                        patient_postal_code,
                        patient_country,
                        patient_phone_number,
                        patient_email_address
                from    patients
                where   owner_id = {ownid}
                and     patient_id = {patid}
                      '''.format(ownid=ownerid,patid=patientid)
    cursor.execute(query)

    patient = cursor.fetchone()

    # Close the DB Connection
    db.close()

    # Return the details of the customer to whoever called
    return patient

#Here we define the Forms the Patient Detail Page will use
class PatientForm(Form):
    firstname = TextField('First Name', [
                        validators.Required(message=(u'Patient First Name is a required field.')),
    ])
    lastname = TextField('Last Name', [
                        validators.Required(message=(u'Patient Last Name is a required field.')),
    ])
    salutation = SelectField('Salutation', choices=[
                                             ('Dr.','Dr.'),
                                             ('Mr.','Mr.'),
                                             ('Mrs.','Mrs.'),
                                             ('Ms.','Ms.')
    ])
    gender = SelectField('Gender', choices=[
                                             ('F','Female'),
                                             ('M','Male')
    ])
    address = TextField('Address', [
                        validators.Optional(),
    ])
    city = TextField('City', [
                        validators.Optional(),
    ])
    state = SelectField('State', choices=[
                                             ('AL','Alabama'),
                                             ('AK','Alaska'),
                                             ('AZ','Arizona'),
                                             ('AR','Arkansas'),
                                             ('CA','California'),
                                             ('CO','Colorado'),
                                             ('CT','Connecticut'),
                                             ('DE','Delaware'),
                                             ('GA','Georgia'),
                                             ('HI','Hawaii'),
                                             ('ID','Idaho'),
                                             ('IL','Illinois'),
                                             ('IN','Indiana'),
                                             ('IA','Iowa'),
                                             ('KS','Kansas'),
                                             ('KY','Kentucky'),
                                             ('LA','Louisiana'),
                                             ('ME','Maine'),
                                             ('MD','Maryland'),
                                             ('MA','Massachusetts'),
                                             ('MI','Michigan'),
                                             ('MN','Minnesota'),
                                             ('MS','Mississippi'),
                                             ('MO','Missouri'),
                                             ('MT','Montana'),
                                             ('NE','Nebraska'),
                                             ('NV','Nevada'),
                                             ('NH','New Hampshire'),
                                             ('NJ','New Jersey'),
                                             ('NM','New Mexico'),
                                             ('NY','New York'),
                                             ('NC','North Carolina'),
                                             ('ND','North Dakota'),
                                             ('OH','Ohio'),
                                             ('OK','Oklahoma'),
                                             ('OR','Oregon'),
                                             ('PA','Pennsylvania'),
                                             ('RI','Rhode Island'),
                                             ('SC','South Carolina'),
                                             ('SD','South Dakota'),
                                             ('TN','Tennessee'),
                                             ('TX','Texas'),
                                             ('UT','Utah'),
                                             ('VT','Vermont'),
                                             ('VA','Virginia'),
                                             ('WA','Washington'),
                                             ('WV','West Virginia'),
                                             ('WI','Wisconsin'),
                                             ('WY','Wyoming')
    ])
    postcode = TextField('Postal Code', [
                        validators.Length(min=5, max=10, message=u'Enter 5 Character Zip Code (99999) or 10 Character Zip+4 (99999-9999)'),
                        validators.Regexp(u'^\d{5}(?:[-\s]\d{4})?$', flags=0, message=u'Enter 5 Character Zip Code (99999) or 10 Character Zip+4 (99999-9999)'),
                        validators.Optional(),
    ])
    country = SelectField('Country', choices=[
                                             ('USA','United States of America')
    ])
    phone_number = TextField('Phone Number', [
                        validators.Length(min=7, max=25, message=u'Enter Phone Numbers in this format:  999-999-9999 or 999-9999'),
                        validators.Regexp(u'^(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$', flags=0, message=u'Enter Phone Numbers in this format:  999-999-9999 or 999-9999'),
                        validators.Optional(),
    ])
    email = TextField('Email Address', [
                        validators.Email(message=u'Invalid email address.'),
                        validators.Optional(),
    ])
    submit    = SubmitField('Save Patient Information')
