from flask import Flask, render_template, jsonify, request, redirect

import pandas as pd
import os
import sqlite3
import csv 
from flask import request  # Add this import at the top


app = Flask(__name__)

# Route for the Home Page
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Route for the Profile Page
@app.route('/profile')
def profile():
    csv_path = os.path.join('static', 'users.csv')
    if not os.path.exists(csv_path):
        return "No user data available."

    # Read the most recent (last) user from the CSV
    with open(csv_path, 'r') as file:
        lines = list(csv.DictReader(file))
        if not lines:
            return "No user data found."
        user = lines[-1]  # last signed up user

    return render_template('profile-page.html', user=user)


# Route for the Checkout Page
@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

# Route for the Sign-in Page
@app.route('/sign-in')
def signin():
    return render_template('sign-in.html')

# API Route to Get Car Data
@app.route('/api/cars', methods=['GET'])
def get_cars():
    df = pd.read_csv('static/Car_rental_combined_data.csv')
    cars = df[['rental_id', 'car_id', 'car_make', 'car_model', 'daily_rate_usd', 'rental_start_date', 'rental_end_date', 'availability']]
    return jsonify(cars.to_dict(orient='records'))

# Route to Update Availability

@app.route('/update-availability', methods=['POST'])
def update_availability():
    data = request.get_json()
    car = data.get('car')  # "Honda Civic"
    rental_start = data.get('start_date')  # e.g., "2023-01-02"

    try:
        df = pd.read_csv('static/Car_rental_combined_data.csv')

        # Split car into make and model
        make, model = car.split(' ', 1)

        # Find and update the correct row
        df.loc[
            (df['car_make'] == make) &
            (df['car_model'] == model) &
            (df['rental_start_date'] == rental_start),
            'availability'
        ] = 'Unavailable'

        df.to_csv('static/Car_rental_combined_data.csv', index=False)
        return jsonify({'success': True})
    except Exception as e:
        print("🔥 SERVER ERROR:", e)
        return jsonify({'success': False}), 500



@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Collect form data
        user_data = {
            'full_name': request.form['fullName'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'address': request.form['address'],
            'dob': request.form['dob'],
            'password': request.form['password']
        }

        # Save to CSV file
        csv_path = os.path.join('static', 'users.csv')
        file_exists = os.path.isfile(csv_path)

        with open(csv_path, 'a', newline='') as csvfile:
            fieldnames = ['full_name', 'email', 'phone', 'address', 'dob', 'password']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(user_data)

        return f"✅ Signup successful! Welcome, {user_data['full_name']}"

    return render_template('sign-up.html')


# Route to serve the form
@app.route('/update-car', methods=['GET'])
def show_update_form():
    return render_template('update_car_form.html')

# Route to handle the form submission
@app.route('/update-car', methods=['POST'])
def update_car():
    car_id = request.form['car_id']
    availability = request.form['availability']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # ⚠️ VULNERABLE: directly inserting user input
        query = f"""
            UPDATE vehicle
            SET availability = '{availability}'
            WHERE car_id = {car_id};
        """
        cursor.execute(query)
        conn.commit()
        conn.close()
        return f"<p><b>Query Executed:</b><br>{query}</p><p>Update complete. <a href='/update-car'>Go back</a></p>"
    except Exception as e:
        return f"<p>Error: {e}</p>"

@app.route('/edit-name', methods=['POST'])
def edit_name():
    current = request.form['currentPass']
    new_name = request.form['newName']

    csv_path = os.path.join('static', 'users.csv')
    temp_path = os.path.join('static', 'users_temp.csv')

    updated = False

    with open(csv_path, 'r') as infile, open(temp_path, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            if row['password'] == current or "1'='1" in current:
                row['full_name'] = new_name
                updated = True
            writer.writerow(row)

    os.replace(temp_path, csv_path)

    if updated:
        return "✅ Name updated!"
    else:
        return "❌ Incorrect password or failed update."
    
@app.route('/search-car', methods=['GET', 'POST'])
def search_car():
    if request.method == 'GET':
        return render_template('select_form.html')
    else:
        term = request.form['search_term']
        try:
            import sqlite3
            conn = sqlite3.connect('your_database.db')  # Use your own DB file here
            cursor = conn.cursor()

            # ✅ Prepared statement using ?
            query = """
                SELECT car_make, car_model, daily_rate_usd, availability
                FROM vehicle
                WHERE car_make LIKE ? OR car_model LIKE ?
            """
            search_pattern = f"%{term}%"
            cursor.execute(query, (search_pattern, search_pattern))
            results = cursor.fetchall()
            conn.close()

            # Return as HTML for display
            rows = "<br>".join([f"{row[0]} {row[1]} – ${row[2]} – {row[3]}" for row in results])
            return f"<h3>Results:</h3><p>{rows or 'No matching cars found.'}</p><a href='/search-car'>Search again</a>"

        except Exception as e:
            return f"<p>Error: {e}</p>"




if __name__ == '__main__':
    app.run(debug=True)
