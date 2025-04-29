from flask import Flask, render_template, jsonify
import pandas as pd
import os
import sqlite3


app = Flask(__name__)

# Route for the Home Page
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Route for the Profile Page
@app.route('/profile')
def profile():
    return render_template('profile-page.html')

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
    csv_path = os.path.join('static', 'Car_rental_combined_data.csv')
    df = pd.read_csv(csv_path)
    cars = df[['car_make', 'car_model', 'daily_rate_usd', 'rental_start_date', 'rental_end_date', 'availability']].drop_duplicates().to_dict(orient='records')
    return jsonify(cars)

def get_db_connection():
    conn = sqlite3.connect('your_database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route to Update Availability
@app.route('/update-availability', methods=['POST'])
def update_availability():
    data = request.get_json()
    car = data['car']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = f"""
            UPDATE vehicle
            SET availability = 'Unavailable'
            WHERE (make || ' ' || model) = '{car}';
        """

        cursor.execute(query)
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        print("🔥 SERVER ERROR:", e)  # <-- add this
        return jsonify({'success': False}), 500




if __name__ == '__main__':
    app.run(debug=True)
