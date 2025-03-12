import unittest
import json
import os
import sqlite3
from database_and_http_api import app, init_db, DB_FILE

class FahrtenAPITestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Initialisiert die Datenbank vor allen Tests."""
        init_db()
    
    def setUp(self):
        """Setzt die Test-Umgebung auf."""
        self.client = app.test_client()
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()
    
    def tearDown(self):
        """Bereinigt die Datenbank nach jedem Test."""
        self.conn.close()
    
    @classmethod
    def tearDownClass(cls):
        """Entfernt die Datenbank nach allen Tests."""
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
    
    def test_add_fahrt_success(self):
        """Testet das erfolgreiche Hinzufügen einer Fahrt."""
        response = self.client.post("/add_fahrt", json={"FahrtName": "Testfahrt"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("FahrtID", data)
    
    def test_add_fahrt_failure(self):
        """Testet das Fehlschlagen des Hinzufügens einer Fahrt ohne Namen."""
        response = self.client.post("/add_fahrt", json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["error"], "FahrtName erforderlich")
    
    def test_add_messpunkt_success(self):
        """Testet das erfolgreiche Hinzufügen eines Messpunkts."""
        fahrt_res = self.client.post("/add_fahrt", json={"FahrtName": "Testfahrt"})
        fahrt_id = fahrt_res.get_json()["FahrtID"]
        
        messpunkt_data = {
            "Zeitpunkt": "2024-03-12 12:00:00",
            "Beschleunigung": 9.81,
            "FahrtID": fahrt_id,
            "Längengrad": 52.52,
            "Breitengrad": 13.405,
        }
        response = self.client.post("/add_messpunkt", json=messpunkt_data)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("MesspunktID", data)
    
    def test_add_messpunkt_missing_fields(self):
        """Testet das Fehlschlagen des Hinzufügens eines Messpunkts mit fehlenden Pflichtfeldern."""
        response = self.client.post("/add_messpunkt", json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["error"], "Fehlende Pflichtfelder")
    
    def test_get_fahrten(self):
        """Testet das Abrufen aller Fahrten."""
        self.client.post("/add_fahrt", json={"FahrtName": "Testfahrt 1"})
        self.client.post("/add_fahrt", json={"FahrtName": "Testfahrt 2"})
        
        response = self.client.get("/get_fahrten")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 2)
    
    def test_get_messpunkte_success(self):
        """Testet das Abrufen der Messpunkte einer bestimmten Fahrt."""
        fahrt_res = self.client.post("/add_fahrt", json={"FahrtName": "Testfahrt"})
        fahrt_id = fahrt_res.get_json()["FahrtID"]
        
        messpunkt_data = {
            "Zeitpunkt": "2024-03-12 12:00:00",
            "Beschleunigung": 9.81,
            "FahrtID": fahrt_id
        }
        self.client.post("/add_messpunkt", json=messpunkt_data)
        
        response = self.client.get(f"/get_messpunkte/{fahrt_id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 1)
    
    def test_get_messpunkte_invalid_datetime(self):
        """Testet die Fehlerbehandlung für ungültige Zeitangaben."""
        response = self.client.get("/get_messpunkte/1?after=invalid-date")
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["error"], "Ungültiges Zeitformat, erwarte 'YYYY-MM-DD HH:MM:SS'")

if __name__ == "__main__":
    unittest.main()
