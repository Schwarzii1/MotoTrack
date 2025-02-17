from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
import time
import threading

# Flask und SocketIO initialisieren
app = Flask(__name__)
socketio = SocketIO(app)

# Funktion zum Abrufen der neuesten Daten einer bestimmten Fahrt
def get_data(trip_id=None):
    conn = sqlite3.connect('motor_data.db')
    cursor = conn.cursor()

    if trip_id:
        cursor.execute("SELECT * FROM motor_data WHERE trip_id = ? ORDER BY timestamp DESC", (trip_id,))
    else:
        cursor.execute("SELECT * FROM motor_data ORDER BY timestamp DESC LIMIT 1")
    
    rows = cursor.fetchall()
    conn.close()
    return rows

# Letzte gestartete Fahrt abrufen
def get_last_trip():
    conn = sqlite3.connect('motor_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM trips ORDER BY start_time DESC LIMIT 1")
    last_trip = cursor.fetchone()
    conn.close()
    return last_trip[0] if last_trip else None

# Hintergrund-Thread zum Senden der neuesten Daten an Clients
def background_thread():
    while True:
        last_trip_id = get_last_trip()
        data = get_data(last_trip_id)
        if data:
            latest_data = data[0]  # Neuesten Messpunkt nehmen
            socketio.emit('new_data', {
                'trip_id': latest_data[1],
                'latitude': latest_data[3],
                'longitude': latest_data[4],
                'speed': latest_data[5],
                'acceleration_x': latest_data[6],
                'acceleration_y': latest_data[7],
                'acceleration_z': latest_data[8],
                'gyroscope_x': latest_data[9],
                'gyroscope_y': latest_data[10],
                'gyroscope_z': latest_data[11]
            })
        time.sleep(1)  # Daten alle 1 Sekunde aktualisieren

# Event, wenn ein Client sich verbindet
@socketio.on('connect')
def on_connect():
    print('Client connected')
    socketio.start_background_task(background_thread)

# Route für die Website
@app.route('/')
def index():
    return render_template('index.html')

# Route für den POST-Request zum Empfangen von Sensordaten
@app.route('/data', methods=['POST'])
def handle_data():
    data = request.get_json()
    print("Empfangene Daten:", data)

    trip_id = data.get('trip_id')
    if trip_id is None:
        trip_id = get_last_trip()
        if trip_id is None:
            return jsonify({"error": "Kein aktiver Trip vorhanden!"}), 400

    conn = sqlite3.connect('motor_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO motor_data (trip_id, latitude, longitude, speed, acceleration_x, acceleration_y, acceleration_z, gyroscope_x, gyroscope_y, gyroscope_z)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (trip_id, data['latitude'], data['longitude'], data['speed'], 
          data['acceleration_x'], data['acceleration_y'], data['acceleration_z'], 
          data['gyroscope_x'], data['gyroscope_y'], data['gyroscope_z']))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Data received successfully", "trip_id": trip_id}), 200

# Route für das Abrufen aller Daten einer bestimmten Fahrt
@app.route('/trip/<int:trip_id>', methods=['GET'])
def get_trip_data(trip_id):
    data = get_data(trip_id)
    if not data:
        return jsonify({"error": "Keine Daten für diese Fahrt gefunden"}), 404
    
    return jsonify([
        {
            "timestamp": row[2],
            "latitude": row[3],
            "longitude": row[4],
            "speed": row[5],
            "acceleration_x": row[6],
            "acceleration_y": row[7],
            "acceleration_z": row[8],
            "gyroscope_x": row[9],
            "gyroscope_y": row[10],
            "gyroscope_z": row[11]
        }
        for row in data
    ])

# Flask-Anwendung starten
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
