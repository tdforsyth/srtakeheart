delete from srtakeheart.patients;

delete from srtakeheart.users;

delete from srtakeheart.owners;

load data local infile 'c:/simplyright/srtakeheart/sql/sample data - owner' ignore into table srtakeheart.owners
fields terminated by ',' enclosed by '"'
lines terminated by '\r\n'
set creation_timestamp = CURRENT_TIMESTAMP, update_timestamp = CURRENT_TIMESTAMP;

load data local infile 'c:/simplyright/srtakeheart/sql/sample data - user' ignore into table srtakeheart.users
fields terminated by ',' enclosed by '"'
lines terminated by '\r\n'
set creation_timestamp = CURRENT_TIMESTAMP, update_timestamp = CURRENT_TIMESTAMP;

load data local infile 'c:/simplyright/srtakeheart/sql/sample data - patient' ignore into table srtakeheart.patients
fields terminated by ',' enclosed by '"'
lines terminated by '\r\n'
set creation_timestamp = CURRENT_TIMESTAMP, update_timestamp = CURRENT_TIMESTAMP;