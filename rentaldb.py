import sqlite3
import csv

conn = sqlite3.connect("rental.db")
cursor = conn.cursor()

# Step 1: Run the schema
with open("Create.sql", "r") as f:
    cursor.executescript(f.read())

# Step 2: EMPLOYEE
with open("static/employee.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute("INSERT INTO EMPLOYEE VALUES (?, ?, ?)", (
            row['employee_id'], row['name'], row['email']
        ))

# Step 3: SUPERVISION
with open("static/supervision.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute("INSERT INTO SUPERVISION VALUES (?, ?)", (
            row['supervisor_id'], row['supervisee_id']
        ))

# Step 4: MANAGES
with open("static/manages.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute("INSERT INTO MANAGES VALUES (?, ?)", (
            row['employee_id'], row['vehicle_id']
        ))

# Step 5: VEHICLE, CUSTOMER, RENTAL from combined CSV
vehicles = set()
customers = set()

with open("static/Car_rental_combined_data.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # VEHICLE table (insert unique vehicles)
        if row['car_id'] not in vehicles:
            cursor.execute("INSERT INTO VEHICLE VALUES (?, ?, ?, ?)", (
                row['car_id'], row['car_make'], row['car_model'], row['car_year']
            ))
            vehicles.add(row['car_id'])

        # CUSTOMER table (insert unique customers)
        if row['company_id'] not in customers:
            cursor.execute("INSERT INTO CUSTOMER VALUES (?, ?, ?, ?)", (
                row['company_id'], row['company_name'], f"{row['company_name'].lower()}@email.com", row['payment_method']
            ))
            customers.add(row['company_id'])

        # RENTAL table
        cursor.execute("""
            INSERT INTO RENTAL (rental_id, start_date, return_date, cost, violations, vehicle_id, customer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row['rental_id'], row['rental_start_date'], row['rental_end_date'],
            row['total_cost_usd'], None, row['car_id'], row['company_id']
        ))

conn.commit()
conn.close()
print("Database rental.db created and all tables populated.")
