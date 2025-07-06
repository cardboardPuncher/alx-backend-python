import seed

def stream_users():
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")
    row = cursor.fetchone()
    while row:
        yield row
        row = cursor.fetchone()
    cursor.close()
    connection.close()
