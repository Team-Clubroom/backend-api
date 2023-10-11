-- Create the database
CREATE DATABASE IF NOT EXISTS backend_test;
USE backend_test;

-- Create the employees table
CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_first_name VARCHAR(255),
    employee_middle_name VARCHAR(255),
    employee_last_name VARCHAR(255)
);

-- Create the employer_relations table
CREATE TABLE employer_relations (
    employer_relation_id INT AUTO_INCREMENT PRIMARY KEY,
    parent_employer_id INT,
    child_employer_id INT,
    employer_relation_type VARCHAR(255),
    employer_relation_start_date VARCHAR(10),
    employer_relation_end_date VARCHAR(10)
);

-- Create the employers table
CREATE TABLE employers (
    employer_id INT AUTO_INCREMENT PRIMARY KEY,
    employer_name VARCHAR(255),
    employer_previous_name VARCHAR(255),
    employer_founded_date VARCHAR(10),
    employer_dissolved_date VARCHAR(10),
    employer_bankruptcy_date VARCHAR(10),
    employer_status VARCHAR(255),
    employer_legal_status VARCHAR(255),
    employer_name_change_reason VARCHAR(255)
);

-- Create the employments table
CREATE TABLE employments (
    employment_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    employer_id INT,
    job_title VARCHAR(255),
    start_date VARCHAR(10),
    end_date VARCHAR(10)
);

-- Create the users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_first_name VARCHAR(255),
    user_last_name VARCHAR(255),
    email_address VARCHAR(255),
    password VARCHAR(255),
    pending_registr_expiry_datetime DATETIME,
    access_permissions VARCHAR(1)
);

-- Insert the sample data
INSERT INTO employers (employer_name, employer_founded_date, employer_dissolved_date, employer_status, employer_legal_status)
VALUES ("Pine and Dandy", "2001-02-19", NULL, "Active", "Co."),
       ("Really Arboreal", "2005-08-06", "2009-04-10", "Dissolved", "Co.");

INSERT INTO employer_relations (parent_employer_id, child_employer_id, employer_relation_type, employer_relation_start_date, employer_relation_end_date)
VALUES (1, 2, "Subsidiary", "2005-08-06", "2009-04-10");

INSERT INTO users (user_first_name, user_last_name, email_address, password, pending_registr_expiry_datetime, access_permissions)
VALUES ("Brandon", "Huckaby", "bkhuckaby@ualr.edu", "brandonspassword", NULL, NULL),
       ("Luka", "Woodson", "llwoodson@ualr.edu", "lukaspassword", "2023-10-09 20:06:32", NULL),
       ("Dako", "Albeik", "mfalbeik@ualr.edu", "dakospassword", "2023-10-13 20:05:12", NULL),
       ("Cory", "Eheart", "cleheart@ualr.edu", "coryspassword", "2023-10-13 20:12:12", "2");

-- USE clause should not be necessary, but trials in local environment suggest otherise
USE backend_test;

-- Create the trigger
DELIMITER //
CREATE TRIGGER before_user_insert 
BEFORE INSERT ON users 
FOR EACH ROW 
BEGIN
    SET NEW.pending_registr_expiry_datetime = NOW() + INTERVAL 72 HOUR;
END;
//
DELIMITER ;

