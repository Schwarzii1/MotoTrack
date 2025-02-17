import sqlite3

def create_database():
    conn = sqlite3.connect('motor_data.db')
    cursor = conn.cursor()

    # Tabelle für Fahrten
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            description TEXT
        )
    ''')

    # Tabelle für Messpunkte mit Bezug zur Fahrt (trip_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS motor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            latitude REAL,
            longitude REAL,
            speed REAL,
            acceleration_x REAL,
            acceleration_y REAL,
            acceleration_z REAL,
            gyroscope_x REAL,
            gyroscope_y REAL,
            gyroscope_z REAL,
            FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("Datenbank und Tabellen erstellt!")

def start_new_trip(description=""):
    """Erstellt eine neue Fahrt und gibt die Trip-ID zurück."""
    conn = sqlite3.connect('motor_data.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO trips (description) VALUES (?)', (description,))
    trip_id = cursor.lastrowid  # ID der neu erstellten Fahrt

    conn.commit()
    conn.close()
    print(f"Neue Fahrt gestartet: Trip-ID {trip_id}")
    return trip_id

def add_data_point(trip_id, latitude, longitude, speed, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z):
    """Fügt einen Messpunkt zu einer bestimmten Fahrt hinzu."""
    conn = sqlite3.connect('motor_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO motor_data (trip_id, latitude, longitude, speed, acceleration_x, acceleration_y, acceleration_z, gyroscope_x, gyroscope_y, gyroscope_z)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (trip_id, latitude, longitude, speed, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z))

    conn.commit()
    conn.close()
    print(f"Messpunkt zur Fahrt {trip_id} hinzugefügt.")

def get_trip_data(trip_id):
    """Liest alle Messpunkte einer bestimmten Fahrt aus."""
    conn = sqlite3.connect('motor_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM motor_data WHERE trip_id = ?', (trip_id,))
    data = cursor.fetchall()

    conn.close()
    return data

if __name__ == '__main__':
    create_database()
