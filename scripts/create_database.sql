-- Run this in MySQL Workbench or: mysql -u root -p < scripts/create_database.sql

CREATE DATABASE IF NOT EXISTS rbac_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE rbac_db;

-- Django will create all tables via: python manage.py migrate
