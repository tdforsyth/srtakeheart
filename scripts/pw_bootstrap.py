import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..\libs'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..\module'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import MySQLdb, MySQLdb.cursors

import py_bcrypt.bcrypt as bcrypt

from dbutils import OpenCursor

def main():
    # Make a little password hash
    username = 'tdforsyth'
    password = '1Cluster'
    salt = bcrypt.gensalt(6)
    hashed = bcrypt.hashpw(password, salt)

    # Get db Connection, Cursor
    (db,cursor) = OpenCursor()

    # db Query to set the pw for a particular user
    query = ''' update users
                set    pw_hash='{pw_hash}'
                where  user_name='{uname}'
            '''.format(pw_hash=hashed,uname=username)
             
    cursor.execute(query)
           
    # Commit and close the DB Connection
    db.commit()
    db.close()       

if __name__ == "__main__":
    # if you call this script from the command line (the shell) it will
    # run the 'main' function
    main()
