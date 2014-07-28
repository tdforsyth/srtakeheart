create database if not exists srtakeheart;

drop table if exists srtakeheart.files;

drop table if exists srtakeheart.patients;

drop table if exists srtakeheart.users;

drop table if exists srtakeheart.owners;

create table if not exists srtakeheart.owners (
  owner_id int not null auto_increment,
  owner_name VARCHAR(255),
  PRIMARY KEY(owner_id)
);

create table if not exists srtakeheart.users (
  user_id int not null auto_increment,
  owner_id int not null,
  user_name varchar(255) not null,
  pw_hash varchar(255),
  user_email varchar(255),
  user_first_name varchar(255),
  user_last_name varchar(255),
  user_role varchar(255)
  primary key (user_id),
  foreign key (owner_id) references srtakeheart.owners(owner_id)
);

create table if not exists srtakeheart.patients (
  patient_id int not null auto_increment,  
  owner_id int not null,
  first_name varchar(255),
  last_name varchar(255),
  address varchar(255),
  phone_number varchar(255),
  primary key (patient_id),
  foreign key (owner_id) references srtakeheart.owners(owner_id)
);

create table if not exists srtakeheart.files (
  file_id int not null auto_increment,
  owner_id int not null,
  patient_id int not null,
  file_name varchar(255),
  file_blob_key varchar(2048),
  primary key (file_id),
  foreign key (owner_id) references srtakeheart.owners(owner_id),
  foreign key (patient_id) references srtakeheart.patients(patient_id)
);