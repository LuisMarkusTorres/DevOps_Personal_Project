import mysql.connector
import os

db = mysql.connector.connect(
    host="db",
    user=os.environ.get('PROJECT_DB_USER'),
    password=os.environ.get('PROJECT_DB_PWD')
)

cursor = db.cursor()

cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.environ.get('PROJECT_DB_DB')}")
cursor.execute(f"USE {os.environ.get('PROJECT_DB_DB')}")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
)
""")

print("Database and users table created successfully.")

db.close()
