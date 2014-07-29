create database if not exists srtakeheart;

drop table if exists srtakeheart.leads;

drop table if exists srtakeheart.files;

drop table if exists srtakeheart.devices;

drop table if exists srtakeheart.patients;

drop table if exists srtakeheart.users;

drop table if exists srtakeheart.owners;

create table if not exists srtakeheart.owners (
  owner_id int not null auto_increment,
  owner_business_name varchar(255),
  owner_street_address varchar(255),
  owner_city varchar(255),
  owner_state varchar(2),
  owner_postal_code varchar(20),
  owner_country varchar(255),
  owner_email varchar(255),
  creation_timestamp timestamp not null default current_timestamp,
  creation_user varchar(255),
  update_timestamp timestamp not null default current_timestamp on update current_timestamp,
  update_user varchar(255),
  PRIMARY KEY(owner_id)
);

create table if not exists srtakeheart.users (
  user_id int not null auto_increment,
  owner_id int not null,
  user_name varchar(255) not null unique,
  pw_hash varchar(255),
  user_email varchar(255),
  user_first_name varchar(255),
  user_last_name varchar(255),
  user_role varchar(255),
  creation_timestamp timestamp not null default current_timestamp,
  creation_user varchar(255),
  update_timestamp timestamp not null default current_timestamp on update current_timestamp,
  update_user varchar(255),
  primary key (user_id),
  foreign key (owner_id) references srtakeheart.owners(owner_id)
);

create table if not exists srtakeheart.patients (
  patient_id int not null auto_increment,  
  owner_id int not null,
  first_name varchar(255),
  last_name varchar(255),
  salutation varchar(255),
  gender varchar(1),
  patient_street_address varchar(255),
  patient_city varchar(255),
  patient_state varchar(2),
  patient_postal_code varchar(20),
  patient_country varchar(255),
  patient_phone_number varchar(255),
  patient_email_address varchar(255),
  physician_name varchar(255),
  physician_street_address varchar(255),
  physician_city varchar(255),
  physician_state varchar(2),
  physician_postal_code varchar(20),
  physician_country varchar(255),
  physician_phone_number varchar(255),
  physician_email_address varchar(255),
  creation_timestamp timestamp not null default current_timestamp,
  creation_user varchar(255),
  update_timestamp timestamp not null default current_timestamp on update current_timestamp,
  update_user varchar(255),
  primary key (patient_id),
  foreign key (owner_id) references srtakeheart.owners(owner_id)
);

create table if not exists srtakeheart.devices (
  device_id int not null auto_increment,
  patient_id int not null,  
  owner_id int not null,
  service_start_date datetime,
  manufacturer_name varchar(255),
  model_name varchar(255),
  model_number varchar(255),
  serial_number varchar(255),
  creation_timestamp timestamp not null default current_timestamp,
  creation_user varchar(255),
  update_timestamp timestamp not null default current_timestamp on update current_timestamp,
  update_user varchar(255),
  primary key (device_id),
  foreign key (patient_id) references srtakeheart.patients(patient_id),
  foreign key (owner_id) references srtakeheart.owners(owner_id)
);

create table if not exists srtakeheart.files (
  file_id int not null auto_increment,
  device_id int not null,
  patient_id int not null,
  owner_id int not null,
  file_name varchar(255),
  file_blob_key varchar(2048),
  creation_timestamp timestamp not null default current_timestamp,
  creation_user varchar(255),
  update_timestamp timestamp not null default current_timestamp on update current_timestamp,
  update_user varchar(255),
  primary key (file_id),
  foreign key (device_id) references srtakeheart.devices(device_id),
  foreign key (owner_id) references srtakeheart.owners(owner_id),
  foreign key (patient_id) references srtakeheart.patients(patient_id)
);

create table if not exists srtakeheart.leads (
  lead_id int not null auto_increment,
  device_id int not null,
  patient_id int not null,  
  owner_id int not null,
  implant_date datetime,
  lead_type varchar(255),
  manufacturer_name varchar(255),
  model_name varchar(255),
  model_number varchar(255),
  serial_number varchar(255),
  creation_timestamp timestamp not null default current_timestamp,
  creation_user varchar(255),
  update_timestamp timestamp not null default current_timestamp on update current_timestamp,
  update_user varchar(255),
  primary key (lead_id),
  foreign key (device_id) references srtakeheart.devices(device_id),
  foreign key (patient_id) references srtakeheart.patients(patient_id),
  foreign key (owner_id) references srtakeheart.owners(owner_id)
);