import sqlite3
import os
from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS

# Datenbank-Datei
DB_FILE = "fahrten.db"

# Flask-App initialisieren
app = Flask(__name__)
CORS(app)  # Erlaubt API-Zugriffe von anderen Domains

# Datenbank erstellen, falls nicht vorhanden
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabelle Fahrt
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Fahrt (
            FahrtID INTEGER PRIMARY KEY AUTOINCREMENT,
            FahrtName TEXT NOT NULL
        )
    ''')

    # Tabelle Messpunkt
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Messpunkt (
            MesspunktID INTEGER PRIMARY KEY AUTOINCREMENT,
            Zeitpunkt TEXT NOT NULL,
            Beschleunigung REAL NOT NULL,
            FahrtID INTEGER NOT NULL,
            Längengrad REAL,
            Breitengrad REAL,
            NeigungX REAL,
            NeigungY REAL,
            NeigungZ REAL,
            BeschlX REAL,
            BeschlY REAL,
            BeschlZ REAL,
            FOREIGN KEY (FahrtID) REFERENCES Fahrt(FahrtID)
        )
    ''')

    conn.commit()
    conn.close()

# API-Route zum Hinzufügen einer Fahrt
@app.route("/add_fahrt", methods=["POST"])
def add_fahrt():
    data = request.get_json()
    fahrt_name = data.get("FahrtName")

    if not fahrt_name:
        return jsonify({"error": "FahrtName erforderlich"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Fahrt (FahrtName) VALUES (?)", (fahrt_name,))
    conn.commit()
    fahrt_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Fahrt hinzugefügt", "FahrtID": fahrt_id})

# API-Route zum Hinzufügen eines Messpunkts
@app.route("/add_messpunkt", methods=["POST"])
def add_messpunkt():
    data = request.get_json()
    
    # Pflichtfelder
    required_fields = ["Zeitpunkt", "Beschleunigung", "FahrtID"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Fehlende Pflichtfelder"}), 400

    # Daten extrahieren
    zeitpunkt = data["Zeitpunkt"]  # Format: "YYYY-MM-DD HH:MM:SS"
    beschleunigung = data["Beschleunigung"]
    fahrt_id = data["FahrtID"]
    längengrad = data.get("Längengrad")
    breitengrad = data.get("Breitengrad")
    neigung_x = data.get("NeigungX")
    neigung_y = data.get("NeigungY")
    neigung_z = data.get("NeigungZ")
    beschl_x = data.get("BeschlX")
    beschl_y = data.get("BeschlY")
    beschl_z = data.get("BeschlZ")

    # Einfügen in die Datenbank
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Messpunkt 
        (Zeitpunkt, Beschleunigung, FahrtID, Längengrad, Breitengrad, NeigungX, NeigungY, NeigungZ, BeschlX, BeschlY, BeschlZ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (zeitpunkt, beschleunigung, fahrt_id, längengrad, breitengrad, neigung_x, neigung_y, neigung_z, beschl_x, beschl_y, beschl_z))
    
    conn.commit()
    messpunkt_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Messpunkt hinzugefügt", "MesspunktID": messpunkt_id})

# API-Route zum Abrufen von Messpunkten einer bestimmten Fahrt nach einer Uhrzeit
@app.route("/get_messpunkte/<int:fahrt_id>", methods=["GET"])
def get_messpunkte(fahrt_id):
    after = request.args.get("after")  # Optionaler Parameter

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if after:
        try:
            # Prüfen, ob das Datum gültig ist
            datetime.strptime(after, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"error": "Ungültiges Zeitformat, erwarte 'YYYY-MM-DD HH:MM:SS'"}), 400

        cursor.execute('''
            SELECT * FROM Messpunkt WHERE FahrtID = ? AND Zeitpunkt > ? ORDER BY Zeitpunkt ASC
        ''', (fahrt_id, after))
    else:
        cursor.execute('''
            SELECT * FROM Messpunkt WHERE FahrtID = ? ORDER BY Zeitpunkt ASC
        ''', (fahrt_id,))
    
    messpunkte = cursor.fetchall()
    conn.close()

    # Daten als JSON zurückgeben
    messpunkte_list = [
        {
            "MesspunktID": row[0],
            "Zeitpunkt": row[1],
            "Beschleunigung": row[2],
            "FahrtID": row[3],
            "Längengrad": row[4],
            "Breitengrad": row[5],
            "NeigungX": row[6],
            "NeigungY": row[7],
            "NeigungZ": row[8],
            "BeschlX": row[9],
            "BeschlY": row[10],
            "BeschlZ": row[11],
        }
        for row in messpunkte
    ]

    return jsonify(messpunkte_list)

# Server starten
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, ssl_context=("cert.pem", "key.pem"))
