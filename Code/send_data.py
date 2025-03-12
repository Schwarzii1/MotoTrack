import requests  # Für HTTP-Anfragen
import random  # Für Zufallswerte
import time  # Für Wartezeiten zwischen Messpunkten
import json  # Für JSON-Datenverarbeitung
from datetime import datetime  # Für Zeitstempel

# Globale Variablen für Fahrt-ID und Messpunkt-Intervall
fahrtID = None
messpunktInterval = None

def neue_fahrt():
    """
    Erstellt eine neue Fahrt, indem eine HTTP-Anfrage an den Server gesendet wird.
    Falls erfolgreich, wird die Fahrt-ID gespeichert und die Messpunkterfassung gestartet.
    """
    global fahrtID  # Zugriff auf die globale Variable
    
    # Benutzer wird aufgefordert, einen Fahrtnamen einzugeben
    fahrt_name = input("Bitte einen Fahrtnamen eingeben: ").strip()
    
    if not fahrt_name:
        print("Bitte einen Fahrtnamen eingeben!")
        return
    
    # Senden einer HTTP-POST-Anfrage an den Server zur Erstellung einer neuen Fahrt
    response = requests.post("http://135.236.212.233:80/add_fahrt", json={"FahrtName": fahrt_name})
    
    if response.ok:
        # Wenn die Anfrage erfolgreich war, wird die Fahrt-ID aus der Antwort extrahiert
        data = response.json()
        fahrtID = data.get("FahrtID")
        print(f'Fahrt "{fahrt_name}" gestartet! ID: {fahrtID}')
        
        # Startet die kontinuierliche Erfassung von Messpunkten
        starte_messpunkte()
    else:
        print("Fehler beim Erstellen der Fahrt!")

def starte_messpunkte():
    """
    Sendet kontinuierlich jede Sekunde Messpunkte an den Server,
    solange eine gültige Fahrt läuft.
    """
    global messpunktInterval
    
    if messpunktInterval is not None:
        print("Messpunkte sind bereits aktiv.")
        return
    
    print("Messpunkte werden alle 1 Sekunde gesendet...")
    
    # Endlosschleife zur Messpunkterfassung (läuft, solange fahrtID existiert)
    while fahrtID:
        # Aktueller Zeitstempel
        jetzt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Zufällige Sensordaten generieren
        beschleunigung = round(random.uniform(0, 10), 2)  # Zufällige Beschleunigung (0 bis 10 m/s²)
        laengengrad = round(52.0 + random.uniform(0, 1), 6)  # Zufällige GPS-Koordinaten (Berlin-Bereich)
        breitengrad = round(13.0 + random.uniform(0, 1), 6)
        neigungX = round(random.uniform(-1, 1), 2)  # Zufällige Neigungswerte in 3 Achsen
        neigungY = round(random.uniform(-1, 1), 2)
        neigungZ = round(random.uniform(-1, 1), 2)
        beschlX = round(random.uniform(-1, 1), 2)  # Zufällige Beschleunigungswerte in 3 Achsen
        beschlY = round(random.uniform(-1, 1), 2)
        beschlZ = round(random.uniform(-1, 1), 2)
        
        # HTTP-POST-Anfrage, um den generierten Messpunkt an den Server zu senden
        response = requests.post(
            "http://135.236.212.233:80/add_messpunkt",
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
        
        # 1 Sekunde warten, bevor der nächste Messpunkt gesendet wird
        time.sleep(1)

def stoppe_fahrt():
    """
    Stoppt die aktuelle Fahrt und beendet die Messpunktaufzeichnung.
    """
    global messpunktInterval
    
    if messpunktInterval is None:
        print("Keine Fahrt läuft derzeit.")
    else:
        messpunktInterval = None  # Fahrt beenden
        print("Fahrt gestoppt!")

if __name__ == "__main__":
    """
    Hauptprogramm: Stellt dem Nutzer ein Menü zur Steuerung der Fahrt zur Verfügung.
    """
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
