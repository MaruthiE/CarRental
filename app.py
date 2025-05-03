from flask import Flask, render_template, jsonify, request, redirect
import pandas as pd
import os
import sqlite3

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/profile')
def profile():
    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM users")
    latest_id = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM users WHERE id = ?", (latest_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        user = {
            'full_name': row[1],
            'email': row[2],
            'phone': row[3],
            'address': row[4],
            'dob': row[5]
        }
        return render_template('profile-page.html', user=user)



@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['fullName']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        dob = request.form['dob']
        password = request.form['password']

        conn = sqlite3.connect('rental.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (full_name, email, phone, address, dob, password)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (full_name, email, phone, address, dob, password))
        conn.commit()
        conn.close()

        import csv
        csv_file = 'users.csv'
        file_exists = os.path.isfile(csv_file)

        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Full Name', 'Email', 'Phone', 'Address', 'DOB', 'Password'])
            writer.writerow([full_name, email, phone, address, dob, password])

        return "New Account Created"

    return render_template('sign-up.html')



@app.route('/api/cars', methods=['GET'])
def get_cars():
    df = pd.read_csv('static/Car_rental_combined_data.csv')
    cars = df[['rental_id', 'car_id', 'car_make', 'car_model', 'daily_rate_usd', 'rental_start_date', 'rental_end_date', 'availability']]
    return jsonify(cars.to_dict(orient='records'))


@app.route('/search-car', methods=['POST'])
def search_car():
    user_input = request.form['car']
    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()


    cursor.execute("""
        SELECT * FROM vehicle
        WHERE car_make || ' ' || car_model LIKE ?
    """, ('%' + user_input + '%',))

    results = cursor.fetchall()
    conn.close()

    return jsonify([
        dict(zip([column[0] for column in cursor.description], row))
        for row in results
    ])


@app.route('/update-availability', methods=['POST'])
def update_availability():
    data = request.get_json()
    car = data.get('car')
    rental_start = data.get('start_date')

    df = pd.read_csv('static/Car_rental_combined_data.csv')
    make, model = car.split(' ', 1)

    df.loc[
        (df['car_make'] == make) &
        (df['car_model'] == model) &
        (df['rental_start_date'] == rental_start),
        'availability'
    ] = 'Unavailable'

    df.to_csv('static/Car_rental_combined_data.csv', index=False)
    return jsonify({'success': True})


@app.route('/edit-name', methods=['POST'])
def edit_name():
    current_pass = request.form['currentPass']
    new_name = request.form['newName']
    email = request.form['email']


    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, current_pass))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "Password is wrong."

    cursor.execute("UPDATE users SET full_name = ? WHERE email = ?", (new_name, email))
    conn.commit()
    conn.close()

    return f"Name changed to {new_name}!"


@app.route('/sign-in', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('rental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect('/profile')
        else:
            error = "Invalid email or password."

    return render_template('sign-in.html', error=error)


@app.route('/delete-account', methods=['POST'])
def delete_account():
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()

    # Verify the user
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "Invalid email or password. Cannot delete account."

    # DELETE operation
    cursor.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()

    return "Account deleted successfully."



if __name__ == '__main__':
    app.run(debug=True)

