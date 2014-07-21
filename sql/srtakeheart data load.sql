delete from srtakeheart.files;

delete from srtakeheart.patients;

delete from srtakeheart.owners;

load data local infile 'c:/simplyright/srtakeheart/sql/sample data - owner' ignore into table srtakeheart.owners
fields terminated by ',' enclosed by '"'
lines terminated by '\r\n';

load data local infile 'c:/simplyright/srtakeheart/sql/sample data - patient' ignore into table srtakeheart.patients
fields terminated by ',' enclosed by '"'
lines terminated by '\r\n';

load data local infile 'c:/simplyright/srtakeheart/sql/sample data - files' ignore into table srtakeheart.files
fields terminated by ',' enclosed by '"'
lines terminated by '\r\n';