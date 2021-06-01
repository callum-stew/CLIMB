-- -----------------------------------------------------
-- Schema CLIMB
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Table person
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS person (
    person_id INTEGER NOT NULL,
    user_type TEXT NOT NULL,
    first_name TEXT,
    middle_name TEXT,
    last_name TEXT,
    address_line_1 TEXT,
    address_line_2 TEXT,
    address_line_3 TEXT,
    county TEXT NOT NULL,
    postcode TEXT NOT NULL,
    email TEXT,
    home_phone TEXT,
    mobile_phone TEXT,
    date_of_birth DATE,
    emergency_name TEXT,
    emergency_phone TEXT,
    deleted INTEGER NOT NULL DEFAULT 0,
    registration_date TEXT NOT NULL,
    PRIMARY KEY (person_id)
);
create unique index person_email_uindex
    on person (email);


-- -----------------------------------------------------
-- Table login
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS login (
    person_id INTEGER NOT NULL,
    password_hash TEXT NOT NULL,
    temp INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (person_id),
    FOREIGN KEY (person_id)
        REFERENCES person (person_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- -----------------------------------------------------
-- Table product
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS product (
    product_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    price TEXT NOT NULL,
    shop_position INTEGER,
    deleted INT NOT NULL DEFAULT 0,
    PRIMARY KEY (product_id)
);


-- -----------------------------------------------------
-- Table sale
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS sale (
    sale_id INTEGER NOT NULL,
    staff_person_id INTEGER NOT NULL,
    member_person_id INTEGER,
    date TEXT NOT NULL,
    PRIMARY KEY (sale_id),
    FOREIGN KEY (staff_person_id)
        REFERENCES person (person_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE,
    FOREIGN KEY (member_person_id)
        REFERENCES person (person_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE
);


-- -----------------------------------------------------
-- Table sale_has_product
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS sale_has_product (
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    number_of_products INTEGER NOT NULL,
    PRIMARY KEY (sale_id, product_id),
    FOREIGN KEY (sale_id)
        REFERENCES sale (sale_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,
    FOREIGN KEY (product_id)
        REFERENCES product (product_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);


-- -----------------------------------------------------
-- Table permission
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS permission (
    permission_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (permission_id)
);
create unique index permission_name_uindex
    on permission (name);


-- -----------------------------------------------------
-- Table person_has_permission
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS person_has_permission (
    person_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    PRIMARY KEY (person_id, permission_id),
    FOREIGN KEY (person_id)
        REFERENCES person (person_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (permission_id)
        REFERENCES permission (permission_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- -----------------------------------------------------
-- Table setting
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS setting (
    setting_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    value TEXT,
    PRIMARY KEY (setting_id)
);
create unique index setting_name_uindex
    on setting (name);


-- -----------------------------------------------------
-- Table weekly_opening_days
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS weekly_opening_days (
    day_id INTEGER NOT NULL,
    day TEXT NOT NULL,
    open INTEGER NOT NULL,
    opening_time TEXT,
    closing_time TEXT,
    PRIMARY KEY (day_id)
);
create unique index weekly_opening_days_day_uindex
    on weekly_opening_days (day);


-- -----------------------------------------------------
-- Table custom_opening_days
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS custom_opening_days (
    date_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    open INTEGER NOT NULL,
    opening_time TEXT,
    closing_time TEXT,
    PRIMARY KEY (date_id)
);


-- -----------------------------------------------------
-- Table booking
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS booking (
    booking_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    start_timestamp INTEGER NOT NULL,
    end_timestamp INTEGER NOT NULL,
    adults INTEGER NOT NULL,
    children INTEGER NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (booking_id),
    FOREIGN KEY (person_id)
        REFERENCES person (person_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE
);