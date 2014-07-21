import jinja2
import webapp2
import os
import sys
import MySQLdb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(),'template')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Handles the form that allows entry and update of user details
class Patientdetail(webapp2.RequestHandler):

    # This is the "Get" handler.  It is invoked when creating a new user,
    # or when loading an existing user record
    def get(self):

        # Try to get the Owner and Patient IDs from the Query String
        ownerid = self.request.get("oid")
        patientid = self.request.get("pid")
     
        # If there IS a Patient ID, connect to the DB and
        # look up the Patient Record
        if (patientid):

               patient = Loadpatientrecord(ownerid,patientid)

               template_values = {}
               template_values['oid'] = ownerid
               template_values['pid'] = patientid
               template_values['patient'] = patient

               # We're also going to see if this customer has any files
               # If they do, we're going to show a list of these
              
               files = Loadpatientfiles(ownerid,patientid)

               template_values['files'] = files                   

        # If there Isn't a Patient ID, then print up the basic verson
        # of the template with no values filled in
        else:
            
               template_values = {}
                    
        template = JINJA_ENVIRONMENT.get_template('patientdetail.html')
        self.response.write(template.render(template_values))

    # This is the "Post" handler.  It is invoked when the form
    # posts to itself with some user data filled in.  We will check whether
    # the data is good.  If not, we'll reload the same form with some errors
    # to be fixed.  If it is good, we'll save the changes
    def post(self):

        #Check values submitted

        #First set our error check variable to false; no errors have been found
        errvalidation = False
        errlastname = False
        
        if (
            not (self.request.get('firstname')) # Nothing in the firstname box
            ):
            errvalidation = True
            errfirstname = True
            errfirstnametext = 'First Name Field cannot be blank'
             

        #Something failed validation.  Reload the form with error messages
        if (errvalidation):
            
            template_values = {
                'firstname': self.request.get('firstname'),
                'lastname': self.request.get('lastname'),
                'address': self.request.get('address'),
                'phone': self.request.get('phone')
            }

            patientid = self.request.get('pid')
            ownerid = self.request.get('oid')
            if (patientid):
                template_values['pid'] = patientid
                template_values['oid'] = ownerid
                

            # Check to see if we found a problem with the Last Name
            # If so, get ready to send the associated text to the form
            if (errfirstname):
                template_values['errfirstnametext'] = errfirstnametext

            # OK, we have everything the form needs.  Reload it.
            template = JINJA_ENVIRONMENT.get_template('patientdetail.html')
            self.response.write(template.render(template_values))

        #Everything checked out OK - Write the record to the database
        else:

            # Open the DB Connection
            if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
                db = MySQLdb.connect(unix_socket='/cloudsql/your-project-id:your-instance-name', user='root', cursorclass=MySQLdb.cursors.DictCursor)
            else:
                db = MySQLdb.connect(host='localhost', user='root', passwd='Gl@cierHe@rt', db='srtakeheart', cursorclass=MySQLdb.cursors.DictCursor)

            # Create a cursor
            cursor = db.cursor()

            patientid = self.request.get('pid')
            ownerid = self.request.get('oid')

            # If there is a patient ID, this is an existing record; create
            # and update query
            if (patientid):

                query = ''' update  patients
                            set     first_name='{fname}',
                                    last_name='{lname}',
                                    address='{addr}',
                                    phone_number='{pnum}'
                            where   owner_id={oid}
                            and     patient_id={pid}
                        '''.format(fname=self.request.get('firstname'),
                                    lname=self.request.get('lastname'),
                                    addr=self.request.get('address'),
                                    pnum=self.request.get('phone'),
                                    oid=ownerid,
                                    pid=patientid)

            # This is a new customer - Create a query to insert the record
            else:

                # Placeholder - This is a dirty hack until the code takes
                # care of ownerid explicitly
                ownerid = 1
                
                query = ''' insert into patients
                            set     owner_id='{oid}',
                                    first_name='{fname}',
                                    last_name='{lname}',
                                    address='{addr}',
                                    phone_number='{pnum}'
                        '''.format( oid=ownerid,
                                    fname=self.request.get('firstname'),
                                    lname=self.request.get('lastname'),
                                    addr=self.request.get('address'),
                                    pnum=self.request.get('phone'))


            # Execute the Query
            cursor.execute(query)
    

            # Commit the changes and close the DB Connection
            db.commit()
            db.close()
    
            # We're done saving - Go back to the overview page
            self.redirect('/')

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

    # Connect to the MySQL Database.  If this is production, to production
    # otherwise to the Dev DB
    if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        db = MySQLdb.connect(unix_socket='/cloudsql/your-project-id:your-instance-name', user='root', cursorclass=MySQLdb.cursors.DictCursor)
    else:
        db = MySQLdb.connect(host='localhost', user='root', passwd='Gl@cierHe@rt', db='srtakeheart', cursorclass=MySQLdb.cursors.DictCursor)

    # Get the details for this customer
    cursor = db.cursor()
    query = ''' select  owner_id,
                        patient_id,
                        last_name,
                        first_name,
                        address,
                        phone_number
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
