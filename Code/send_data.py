import requests
import random
import time
import json
from datetime import datetime

fahrtID = None
messpunktInterval = None

def neue_fahrt():
    global fahrtID
    fahrt_name = input("Bitte einen Fahrtnamen eingeben: ").strip()

    if not fahrt_name:
        print("Bitte einen Fahrtnamen eingeben!")
        return

    # HTTP POST Anfrage, um eine neue Fahrt zu starten
    response = requests.post("http://135.236.212.233:5000/add_fahrt", json={"FahrtName": fahrt_name})

    if response.ok:
        data = response.json()
        fahrtID = data.get("FahrtID")
        print(f'Fahrt "{fahrt_name}" gestartet! ID: {fahrtID}')
        starte_messpunkte()
    else:
        print("Fehler beim Erstellen der Fahrt!")

def starte_messpunkte():
    global messpunktInterval
    if messpunktInterval is not None:
        print("Messpunkte sind bereits aktiv.")
        return

    print("Messpunkte werden alle 1 Sekunde gesendet...")
    while fahrtID:
        jetzt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        beschleunigung = round(random.uniform(0, 10), 2)
        laengengrad = round(52.0 + random.uniform(0, 1), 6)
        breitengrad = round(13.0 + random.uniform(0, 1), 6)
        neigungX = round(random.uniform(-1, 1), 2)
        neigungY = round(random.uniform(-1, 1), 2)
        neigungZ = round(random.uniform(-1, 1), 2)
        beschlX = round(random.uniform(-1, 1), 2)
        beschlY = round(random.uniform(-1, 1), 2)
        beschlZ = round(random.uniform(-1, 1), 2)

        # HTTP POST Anfrage, um einen Messpunkt zu senden
        response = requests.post(
            "http://135.236.212.233:5000/add_messpunkt",
            json={
                "Zeitpunkt": jetzt,
                "Beschleunigung": beschleunigung,
                "FahrtID": fahrtID,
                "Längengrad": laengengrad,
                "Breitengrad": breitengrad,
                "NeigungX": neigungX,
                "NeigungY": neigungY,
                "NeigungZ": neigungZ,
                "BeschlX": beschlX,
                "BeschlY": beschlY,
                "BeschlZ": beschlZ
            }
        )

        if not response.ok:
            print("Fehler beim Senden des Messpunkts.")
        
        time.sleep(1)

def stoppe_fahrt():
    global messpunktInterval
    if messpunktInterval is None:
        print("Keine Fahrt läuft derzeit.")
    else:
        messpunktInterval = None
        print("Fahrt gestoppt!")

if __name__ == "__main__":
    while True:
        print("\nWählen Sie eine Option:")
        print("1. Neue Fahrt starten")
        print("2. Fahrt beenden")
        print("3. Beenden")
        wahl = input("Ihre Wahl: ").strip()

        if wahl == "1":
            neue_fahrt()
        elif wahl == "2":
            stoppe_fahrt()
        elif wahl == "3":
            print("Programm beendet.")
            break
        else:
            print("Ungültige Wahl, bitte erneut versuchen.")
