-- If the database "backend_test" does not exist, create it.
CREATE DATABASE IF NOT EXISTS backend_test;

-- All commands hereafter act upon the database "backend_test".
USE backend_test;

-- To ensure the most up-to-date tables are created, this script will drop all
-- tables within backend_test.
DELIMITER //

CREATE PROCEDURE DropAllTablesInDatabase()
BEGIN
    DECLARE _done INT DEFAULT FALSE;
    DECLARE _tableName VARCHAR(255);
    DECLARE _cursor CURSOR FOR 
        SELECT table_name 
        FROM information_schema.tables
        WHERE table_schema = "backend_test";

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET _done = TRUE;

    OPEN _cursor;

    DROP_TABLES_LOOP: LOOP

        FETCH _cursor INTO _tableName;

        IF _done THEN
            LEAVE DROP_TABLES_LOOP;
        END IF;

        SET @dropStatement = CONCAT('DROP TABLE IF EXISTS backend_test.`', _tableName, '`;');
        PREPARE dynamicStatement FROM @dropStatement;
        EXECUTE dynamicStatement;
        DEALLOCATE PREPARE dynamicStatement;

    END LOOP;

    CLOSE _cursor;
END //

DELIMITER ;

-- Now call the procedure
CALL DropAllTablesInDatabase();

-- Don't forget to drop the procedure after using it
DROP PROCEDURE IF EXISTS DropAllTablesInDatabase;

-- With backend_test wiped clean, this script will now build the tables.
-- Create table containing employees and their demographic data.
CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_first_name VARCHAR(255),
    employee_middle_name VARCHAR(255) DEFAULT NULL,
    employee_last_name VARCHAR(255)
);

-- Create table containing relational data between two or more employers.
CREATE TABLE employer_relations (
    employer_relation_id INT AUTO_INCREMENT PRIMARY KEY,
    parent_employer_id INT,
    child_employer_id INT,
    employer_relation_type VARCHAR(255),
    employer_relation_start_date VARCHAR(10),
    employer_relation_end_date VARCHAR(10)
);

-- Create table containing employers and employer data.
CREATE TABLE employers (
    employer_id INT AUTO_INCREMENT PRIMARY KEY,
    employer_name VARCHAR(255),
    employer_previous_name VARCHAR(255) DEFAULT NULL,
    employer_founded_date VARCHAR(10),
    employer_dissolved_date VARCHAR(10) DEFAULT NULL,
    employer_bankruptcy_date VARCHAR(10) DEFAULT NULL,
    employer_status VARCHAR(255),
    employer_legal_status VARCHAR(255),
    employer_name_change_reason VARCHAR(255) DEFAULT NULL
);

-- Create table of employment relations between employee and employer.
CREATE TABLE employments (
    employment_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    employer_id INT,
    job_title VARCHAR(255),
    start_date VARCHAR(10),
    end_date VARCHAR(10) DEFAULT NULL
);

-- Create table of application users, their demographic information, and
-- access permissions data.
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_first_name VARCHAR(255),
    user_last_name VARCHAR(255),
    email_address VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    pending_registr_expiry_datetime DATETIME,
    access_permissions VARCHAR(1)
);

-- With all tables in backend_test now created, this script will insert dummy
-- data for each of the tables.
-- Create and insert employee records.
INSERT INTO backend_test.employees (employee_first_name, employee_middle_name, employee_last_name)
VALUES
    ("Niall", "Shoal", "Billingsly"),
    ("John", "Edward", "Smith"),
    ("Jane", "Marie", "Doe"),
    ("Ella", "Rose", "Johnson"),
    ("Mark", "Allen", "Bennett"),
    ("Oliver", "James", "Lee"),
    ("Sophia", "Lynn", "Garcia"),
    ("Mason", "Robert", "Harris"),
    ("Liam", "Patrick", "Clark"),
    ("Isabella", "Claire", "Young"),
    ("Ava", "Grace", "Turner"),
    ("Lucas", "Daniel", "Wright"),
    ("Anna", "Elizabeth", "Thomas"),
    ("Brad", "William", "Hayes"),
    ("Charlie", "Joseph", "Ross"),
    ("Zoe", "Amelia", "Adams"),
    ("Amelia", "Louise", "Carter"),
    ("James", "Benjamin", "Mitchell"),
    ("Emily", "Victoria", "Anderson"),
    ("Aiden", "Michael", "Phillips"),
    ("Rachel", "Christine", "Gray"),
    ("David", "Henry", "Price"),
    ("Oscar", "Leonard", "Nelson"),
    ("Grace", "Katherine", "Parker"),
    ("Lisa", "Michelle", "White"),
    ("Henry", "Andrew", "Kelly"),
    ("Samuel", "Richard", "Murphy"),
    ("Michael", "Scott", "King"),
    ("Lily", "Nicole", "Collins"),
    ("Dido", "Marcopolis", "Marcel"),
    ("Howard", "Benjamin", "Forrester"),
    ("José", "Aníbal", "Guererra"),
    ("Sarah", "Alicia", "Hansen");

-- Create and insert employer records.
INSERT INTO backend_test.employers (employer_name, employer_founded_date, employer_dissolved_date, employer_status, employer_legal_status)
VALUES
    ("Pine and Dandy", "2001-02-19", NULL, "Active", "Co."),
    ("Really Arboreal", "2005-08-06", "2009-04-10", "Dissolved", "Co.");

-- Create and insert employer-relation record.
INSERT INTO backend_test.employer_relations (parent_employer_id, child_employer_id, employer_relation_type, employer_relation_start_date, employer_relation_end_date)
VALUES (1, 2, "Subsidiary", "2005-08-06", "2009-04-10");

-- Create and insert employment records.
INSERT INTO backend_test.employments (employee_id, employer_id, job_title, start_date, end_date)
VALUES
    (1, 1, "Chief Executive Officer", "2001-02-19", NULL),
    (2, 1, "Logging Crew Chief", "2001-02-19", "2013-05-19"),
    (3, 1, "Logger", "2001-02-19", "2013-08-02"),
    (3, 1, "Logging Crew Chief", "2013-08-03", NULL),
    (4, 1, "Logger", "2001-02-19", "2016-11-02"),
    (5, 1, "Logger", "2002-04-23", NULL),
    (6, 1, "Logger", "2002-04-23", "2004-01-19"),
    (7, 1, "Logger", "2002-09-29", "2013-12-19"),
    (8, 1, "Logger", "2005-12-10", NULL),
    (9, 1, "Logger", "2006-03-11", "2012-07-06"),
    (9, 1, "Logger", "2014-02-18", NULL),
    (10, 1, "Logger", "2006-04-09", "2017-02-15"),
    (11, 1, "Logger", "2007-09-21", "2021-02-09"),
    (12, 1, "Logger", "2011-05-25", NULL),
    (13, 1, "Milling Operator Chief", "2001-02-19", NULL),
    (14, 1, "Milling Operator", "2001-02-19", "2006-08-06"),
    (15, 1, "Milling Operator", "2001-02-19", "2020-10-29"),
    (16, 1, "Milling Operator", "2001-02-19", NULL),
    (17, 1, "Milling Operator", "2002-11-02", "2019-01-31"),
    (18, 1, "Milling Operator", "2006-10-09", NULL),
    (19, 1, "Milling Operator", "2008-02-28", "2011-09-12"),
    (20, 1, "Milling Operator", "2013-12-04", NULL),
    (21, 1, "Sales Executive", "2001-02-19", "2011-08-29"),
    (22, 1, "Marketing Specialist", "2001-02-28", "2019-01-19"),
    (23, 1, "Sales Executive", "2012-01-10", NULL),
    (24, 1, "Marketing Associate", "2001-03-02", "2012-01-06"),
    (25, 1, "Transport Driver", "2001-02-19", "2003-05-21"),
    (26, 1, "Transport Driver", "2001-02-23", "2021-02-15"),
    (27, 1, "Transport Driver", "2003-04-12", NULL),
    (28, 1, "Maintenance Technician", "2001-02-19", NULL),
    (29, 1, "Support Technician", "2001-02-20", "2014-06-30"),
    (30, 2, "President", "2005-08-06", "2009-04-10"),
    (31, 2, "Office Manager", "2005-08-06", "2009-04-10"),
    (32, 2, "Landscaper", "2005-08-06", "2008-11-13"),
    (33, 2, "Landscaper", "2005-09-19", "2009-04-10");

-- Create and insert user records; in particular, insert administrative records.
INSERT INTO backend_test.users (user_first_name, user_last_name, email_address, password, pending_registr_expiry_datetime, access_permissions)
VALUES
    ("Mohamed", "Albeik", "mfalbeik@ualr.edu", "dakospassword", "2023-10-01 17:32:12", '2'),
    ("Cory", "Eheart", "cleheart@ualr.edu", "coryspassword", "2023-10-01 17:33:13", '2'),
    ("Brandon", "Huckaby", "bkhuckaby@ualr.edu", "brandonspassword", "2023-10-01 17:34:14", '2'),
    ("Luka", "Woodson", "llwoodson@ualr.edu", "lukaspassword", "2023-10-01 17:35:15", '2');

-- Create trigger for backend_test.users so that user records are assigned a
-- pending_registr_expiry_datetime equal to 72 hours from the current datetime.
USE backend_test;

DELIMITER //
CREATE TRIGGER before_user_insert
BEFORE INSERT ON backend_test.users
FOR EACH ROW
BEGIN
	SET NEW.pending_registr_expiry_datetime = NOW() + INTERVAL 72 HOUR;
END;
//
DELIMITER ;
