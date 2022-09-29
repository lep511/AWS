CREATE DATABASE IF NOT EXISTS employees;
use employees

CREATE TABLE IF NOT EXISTS employee (
  id int not null auto_increment primary key,
  object_key nvarchar(80),
  full_name nvarchar(200) not null,
  location nvarchar(200) not null,
  job_title nvarchar(200) not null,
  badges nvarchar(200) not null,
  created_datetime DATETIME DEFAULT now()
);
