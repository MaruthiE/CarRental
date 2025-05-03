CREATE TABLE CUSTOMER (
    customer_id INT NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    payment_type VARCHAR(20)
);

CREATE TABLE EMPLOYEE (
    employee_id INT NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL
);

CREATE TABLE SUPERVISION (
    supervisor_id INT NOT NULL,
    supervisee_id INT NOT NULL,
    PRIMARY KEY (supervisor_id, supervisee_id),
    FOREIGN KEY (supervisor_id) REFERENCES EMPLOYEE(employee_id),
    FOREIGN KEY (supervisee_id) REFERENCES EMPLOYEE(employee_id)
);

CREATE TABLE VEHICLE (
    vehicle_id INT NOT NULL PRIMARY KEY,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT
);

CREATE TABLE MANAGES (
    employee_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    PRIMARY KEY (employee_id, vehicle_id),
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id),
    FOREIGN KEY (vehicle_id) REFERENCES VEHICLE(vehicle_id)
);

CREATE TABLE RENTAL (
    rental_id INT NOT NULL PRIMARY KEY,
    start_date DATETIME NOT NULL,
    return_date DATETIME NOT NULL,
    cost DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
    violations TEXT,
    vehicle_id INT NOT NULL,
    customer_id INT NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES VEHICLE(vehicle_id),
    FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    dob TEXT NOT NULL,
    password TEXT NOT NULL
);
