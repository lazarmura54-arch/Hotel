from flask import Flask, jsonify, render_template
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="Hotel Management",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Route to render the main page
@app.route('/')
def home():
    return render_template('index.html')

# API to get hotels
@app.route('/hotels')
def get_hotels():
    cursor.execute("SELECT * FROM hotels_table")
    rows = cursor.fetchall()
    result = [{'Hotel_Id': row[0], 'Hotel_Name': row[1], 'Create_Date': row[2]} for row in rows]
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
