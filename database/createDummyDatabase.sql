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
    employer_relation_start_date VARCHAR(10)
);

-- Create table containing employers and employer data.
CREATE TABLE employers (
    employer_id INT AUTO_INCREMENT PRIMARY KEY,
    employer_name VARCHAR(255),
    employer_addr_line_1 VARCHAR(255),
    employer_addr_line_2 VARCHAR(255),
    employer_addr_city VARCHAR(255),
    employer_addr_state VARCHAR(2),
    employer_addr_zip_code VARCHAR(10),
    employer_founded_date VARCHAR(10),
    employer_dissolved_date VARCHAR(10) DEFAULT NULL,
    employer_bankruptcy_date VARCHAR(10) DEFAULT NULL,
    employer_industry_sector_code INT,
    employer_status VARCHAR(255),
    employer_legal_status VARCHAR(255)
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

-- Create table of NAICS codes.
CREATE TABLE naics_codes (
    naics_code_id INT AUTO_INCREMENT PRIMARY KEY,
    naics_sector_code INT,
    naics_sector_definition VARCHAR(255),
    naics_release_year VARCHAR(4)
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
INSERT INTO backend_test.employees (
    employee_first_name,
    employee_middle_name,
    employee_last_name
)
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
INSERT INTO backend_test.employers (
    employer_name,
    employer_addr_line_1,
    employer_addr_line_2,
    employer_addr_city,
    employer_addr_state,
    employer_addr_zip_code,
    employer_founded_date,
    employer_dissolved_date,
    employer_industry_sector_code,
    employer_status,
    employer_legal_status
)
VALUES
    ("Pine and Dandy", "123 Fantasy Rd", NULL, "Anytown", "AR", "99999", "2001-02-19", NULL, 32, "Active", "Co."),
    ("Really Arboreal", "357 Dreamy Cir", "Lot E", "Anytown", "AR", "99999", "2005-08-06", "2009-04-10", 44, "Dissolved", "Co."),
    ("Patty's Cakes", "2023 Rightnow Blvd", NULL, "Somecity", "AR", "88888", "2012-04-16", "2019-04-30", 31, "Merged", "LLC."),
    ("Smooth Eddie\'s Smoothie Eatery", "888 Eighty Ln", NULL, "Thatcity", "AR", "77777", "2008-11-04", "2019-04-30", 31, "Merged", "Co."),
    ("Just Desserts", "4545 Cupcake Way", "Suite B", "Thatcity", "AR", "77777", "2019-05-01", NULL, 31, "Active", "Co."),
    ("Twiddler", "1010 Example Rd", NULL, "Anytown", "AR", "99999", "2007-03-21", NULL, 51, "Active", "Inc."),
    ("Hex", "1010 Example Rd", NULL, "Anytown", "AR", "99999", "2023-07-22", NULL, 51, "Active", "Inc."),
    ("Scantine", "1234 Imaginary Ave", NULL, "Thatcity", "AR", "77777", "2002-12-03", NULL, 52, "Active", "Co."),
    ("HelpQuest", "123 Beowulf Dr", NULL, "Somecity", "AR", "88888", "1999-03-09", "2014-07-09", 52, "Acquired", "Inc."),
    ("Talcum State Healthcare", "123 Gilgamesh Ave", NULL, "Anytown", "AR", "99999", "2005-10-29", "2011-09-02", 52, "Acquired", "Co."),
    ("Five-O Pensions", "123 Bluebell Rd", NULL, "Anytown", "AR", "99999", "2004-03-17", "2021-01-04", 52, "Acquired", "Co."),
    ("Synagogues Fish & Chips", "123 Everywhere Cir", NULL, "Thatcity", "AR", "77777", "1972-06-12", NULL, 72, "Active", "Co."),
    ("Ultra-Mart", "123 Tinker Ave", NULL, "Everycity", "AR", "66666", "1988-09-21", NULL, 45, "Active", "Co."),
    ("Ultra-Rx", "456 Builder Ln", NULL, "Everycity", "AR", "66666", "1993-11-11", NULL, 44, "Active", "Co."),
    ("Mega-Mart", "9876 Inventor Rd", NULL, "Somecity", "AR", "88888", "1999-03-16", NULL, 45, "Active", "Co."),
    ("Okay-Mart", "369 Patent Blvd", NULL, "Thatcity", "AR", "77777", "2000-02-21", NULL, 45, "Active", "Co."),
    ("Mega-Mart Neighborhoods", "123 Millionaire Cir", NULL, "Thatcity", "AR", "77777", "2000-07-01", NULL, 44, "Active", "Co."),
    ("Not-Great-Mart", "2468 Radio Rd", NULL, "Everycity", "AR", "66666", "2006-08-16", NULL, 45, "Active", "Co."),
    ("We Own Everything", "987 Corporate Blvd", NULL, "Anytown", "AR", "99999", "2001-09-19", "2012-07-27", 32, "Spun-off", "Co."),
    ("We Only Own Half the Stuff", "147 Colony Cir", NULL, "Anytown", "AR", "99999", "2012-07-28", NULL, 32, "Active", "Co."),
    ("We Own the Rest", "456 Split Dr", NULL, "Somecity", "AR", "88888", "2012-07-28", NULL, 32, "Active", "Co."),
    ("The Tooth Hurts", "123 Dumb Ln", "Ste C", "Somecity", "AR", "88888", "2014-03-01", NULL, 62, "Active", "LLP"),
    ("Lizzie Borden's Flowers & Boutique", "456 Seriously Dr", NULL, "Anytown", "AR", "99999", "2000-10-14", NULL, 45, "Active", "Co.");

-- Create and insert employer-relation record.
INSERT INTO backend_test.employer_relations (
    parent_employer_id,
    child_employer_id,
    employer_relation_type,
    employer_relation_start_date
)
VALUES
    (1, 2, "Subsidiary", "2005-08-06"),
    (3, 5, "Merger", "2019-05-01"),
    (4, 5, "Merger", "2019-05-01"),
    (6, 7, "Rebrand", "2023-07-22"),
    (8, 9, "Acquisition", "2014-07-10"),
    (8, 10, "Acquisition", "2011-09-03"),
    (8, 11, "Acquisition", "2021-01-05"),
    (13, 14, "Subsidiary", "1993-11-11"),
    (13, 15, "Subsidiary", "1999-03-16"),
    (15, 16, "Subsidiary", "2000-02-21"),
    (15, 17, "Subsidiary", "2000-07-01"),
    (16, 18, "Subsidiary", "2006-08-16"),
    (19, 20, "Spin-off", "2012-07-28"),
    (19, 21, "Spin-off", "2012-07-28");

-- Create and insert employment records.
INSERT INTO backend_test.employments (
    employee_id,
    employer_id,
    job_title,
    start_date,
    end_date
)
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

-- Create and insert NAICS sector codes.
INSERT INTO backend_test.naics_codes (
    naics_sector_code,
    naics_sector_definition,
    naics_release_year
)
VALUES
    (11, "Agriculture, Forestry, Fishing and Hunting", 2022),
    (21, "Mining, Quarrying, and Oil and Gas Extraction", 2022),
    (22, "Utilities", 2022),
    (23, "Construction", 2022),
    (31, "Manufacturing", 2022),
    (32, "Manufacturing", 2022),
    (33, "Manufacturing", 2022),
    (42, "Wholesale Trade", 2022),
    (44, "Retail Trade", 2022),
    (45, "Retail Trade", 2022),
    (48, "Transportation and Warehousing", 2022),
    (49, "Transportation and Warehousing", 2022),
    (51, "Information", 2022),
    (52, "Finance and Insurance", 2022),
    (53, "Real Estate and Rental and Leasing", 2022),
    (54, "Professional, Scientific, and Technical Services", 2022),
    (55, "Management of Companies and Enterprises", 2022),
    (56, "Administrative and Support and Waste Management and Remediation Services", 2022),
    (61, "Educational Services", 2022),
    (62, "Health Care and Social Assistance", 2022),
    (71, "Arts, Entertainment, and Recreation", 2022),
    (72, "Accommodation and Food Services", 2022),
    (81, "Other Services (except Public Administration)", 2022),
    (92, "Public Administration", 2022);

-- Create and insert user records; in particular, insert administrative records.
INSERT INTO backend_test.users (
    user_first_name,
    user_last_name,
    email_address,
    password,
    pending_registr_expiry_datetime,
    access_permissions
)
VALUES
    ("Mohamed", "Albeik", "mfalbeik@ualr.edu", "dakospassword", "2023-10-01 17:32:12", '2'),
    ("Cory", "Eheart", "cleheart@ualr.edu", "coryspassword", "2023-10-01 17:33:13", '2'),
    ("Brandon", "Huckaby", "bkhuckaby@ualr.edu", "brandonspassword", "2023-10-01 17:34:14", '2'),
    ("Luka", "Woodson", "llwoodson@ualr.edu", "lukaspassword", "2023-10-01 17:35:15", '2');
