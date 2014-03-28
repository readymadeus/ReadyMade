#schema.sql
drop table if exists users;
create table users (
  userid integer primary key autoincrement,
  username text not null,
  password text,
  create_date date,
  update_date date
);

drop table if exists projects;
create table users (
  projid integer primary key autoincrement,
  userid integer not null,
  orgname text,
  mission text,
  primary_user text,
  secondary_user text,
  other_users text,
  input_vars text,
  control_vars text,
  performance_vars text,
  create_date date,
  update_date date
);

drop table if exists users;
create table users (
  userid integer primary key autoincrement,
  username text not null,
  password text,
  create_date date,
  update_date date
);