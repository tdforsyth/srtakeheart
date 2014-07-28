# Allows us to find all our Modules and 3rd Party Tools
import fix_path

import os
import sys
import MySQLdb

#Returns a cursor connected to the database
def OpenCursor():

         # Open the DB Connection
        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/your-project-id:your-instance-name', user='root', cursorclass=MySQLdb.cursors.DictCursor)
        else:
            db = MySQLdb.connect(host='localhost', user='root', passwd='Gl@cierHe@rt', db='srtakeheart', cursorclass=MySQLdb.cursors.DictCursor)

        # Create a cursor
        cursor = db.cursor()

        # return the cursor
        return (db,cursor)
