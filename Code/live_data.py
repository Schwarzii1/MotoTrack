from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import sqlite3
import time
import threading

# Flask und SocketIO initialisieren
app = Flask(__name__)
socketio = SocketIO(app)

# Funktion zum Abrufen der neuesten Daten aus der Datenbank
def get_data():
    conn = sqlite3.connect('motor_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM motor_data ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row

# Hintergrund-Thread zum Senden der Daten an die Clients
def background_thread():
    while True:
        data = get_data()
        if data:
            # Sende die Daten an alle verbundenen Clients
            socketio.emit('new_data', {
                'latitude': data[2],
                'longitude': data[3],
                'speed': data[4],
                'acceleration_x': data[5],
                'acceleration_y': data[6],
                'acceleration_z': data[7],
                'gyroscope_x': data[8],
                'gyroscope_y': data[9],
                'gyroscope_z': data[10]
            })
        time.sleep(1)  # Alle 1 Sekunde die Daten aktualisieren

# Event, wenn ein Client sich verbindet
@socketio.on('connect')
def on_connect():
    print('Client connected')
    # Starte den Hintergrund-Thread, wenn der Client verbunden ist
    socketio.start_background_task(background_thread)

# Route, um die Website zu rendern
@app.route('/')
def index():
    return render_template('index.html')

# Route für den POST-Request, um die Daten zu empfangen
@app.route('/data', methods=['POST'])
def handle_data():
    data = request.get_json()
    print(data)  # Überprüfen, ob die Daten korrekt empfangen werden
    # Hier kannst du die Daten in die Datenbank einfügen oder anderweitig verarbeiten
    conn = sqlite3.connect('motor_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO motor_data (latitude, longitude, speed, acceleration_x, acceleration_y, acceleration_z, gyroscope_x, gyroscope_y, gyroscope_z)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['latitude'], data['longitude'], data['speed'], data['acceleration_x'], data['acceleration_y'], data['acceleration_z'], data['gyroscope_x'], data['gyroscope_y'], data['gyroscope_z']))
    conn.commit()
    conn.close()
    return 'Data received successfully', 200

# Flask-Anwendung starten
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
