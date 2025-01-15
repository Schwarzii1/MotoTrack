import sqlite3

def create_database():
    # Verbindung zur SQLite-Datenbank herstellen (wird erstellt, wenn sie nicht existiert)
    conn = sqlite3.connect('motor_data.db')
    cursor = conn.cursor()

    # Tabelle erstellen (falls sie noch nicht existiert)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS motor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            latitude REAL,
            longitude REAL,
            speed REAL,
            acceleration_x REAL,
            acceleration_y REAL,
            acceleration_z REAL,
            gyroscope_x REAL,
            gyroscope_y REAL,
            gyroscope_z REAL
        )
    ''')

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()
    print("Datenbank und Tabelle erstellt!")

if __name__ == '__main__':
    create_database()
