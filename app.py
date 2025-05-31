from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import mysql.connector
import os
import traceback
import re  # For better column name cleaning

app = Flask(__name__)
CORS(app)
[   ]
#  Upload directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',         #  Replace with your real password
    'database': 'excel_db'      #  Ensure this DB exists
}

@app.route('/')
def index():
    return " Flask Backend is Running Successfully!"

@app.route('/upload', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({'message': '❌ No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': '❌ No selected file'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        #  Read Excel file
        df = pd.read_excel(file_path)
        if df.empty:
            return jsonify({'message': '❌ Excel file is empty'}), 400

        #  Clean and sanitize column names
        cleaned_columns = []
        for col in df.columns:
            cleaned = re.sub(r'[^\w\s]', '', col)       # Remove special characters
            cleaned = re.sub(r'\s+', '_', cleaned)      # Replace spaces with _
            cleaned_columns.append(cleaned.strip())

        df.columns = cleaned_columns
        columns = df.columns.tolist()

        #  Connect to MySQL
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        #  Ensure UTF-8 compatibility
        cursor.execute("SET NAMES 'utf8mb4';")

        table_name = 'excel_data'

        #  Create Table if not exists
        create_query = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            {', '.join([f"`{col}` VARCHAR(255)" for col in columns])}
        )
        """
        cursor.execute(create_query)

        #  Insert Data
        insert_query = f"""
        INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in columns])})
        VALUES ({', '.join(['%s'] * len(columns))})
        """

        for _, row in df.iterrows():
            values = [str(val) if pd.notna(val) else '' for val in row]
            cursor.execute(insert_query, values)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': ' Excel data inserted into MySQL successfully!'})

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'message': f'❌ Error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)

