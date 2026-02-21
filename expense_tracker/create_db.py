import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="postgres",      # connect to default db first
    user="postgres",
    password="4885"  # your PostgreSQL password
)
conn.autocommit = True
cursor = conn.cursor()
cursor.execute("CREATE DATABASE expense_tracker")
print("Database 'expense_tracker' created! ✅")
conn.close()