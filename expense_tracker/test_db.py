import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="4885"
    )
    print("Connected to PostgreSQL! ✅")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")