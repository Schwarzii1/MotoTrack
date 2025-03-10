# MotoTrack

MotoTrack ist eine Anwendung zur Visualisierung von Live-Sensordaten eines Motorrads, wie Geschwindigkeit, Schräglage und GPS-Position. Die Daten werden von einem Arduino Nano ESP32 erfasst und über mobile Daten direkt an eine API auf einem virtuellen Computer (Azure) gesendet. Dieser verarbeitet die Daten und stellt sie über eine Webanwendung grafisch dar.

## Features
- **Echtzeit-Visualisierung** von Geschwindigkeits-, Schräglagen- und GPS-Daten.
- **Interaktive Karten** zur Anzeige der Route.
- **Webbasiertes Interface**, das von überall erreichbar ist.
- **Cloud-Hosting** auf einer Azure-VM für hohe Verfügbarkeit und Skalierbarkeit.

## Voraussetzungen
### Hardware
- Arduino Nano ESP32 mit GPS-, Beschleunigungs- und Gyroskopsensoren.
- Motorrad zur Befestigung der Sensoren.

### Software
- Azure-Konto mit einer eingerichteten virtuellen Maschine (Linux-Distribution, z. B. Ubuntu 22.04).
- Python 3.10+ auf der VM.
- Node.js (für das Frontend, falls erforderlich).
- Flask oder FastAPI für das Backend.
- Leaflet.js oder OpenLayers für die Kartenvisualisierung im Frontend.

Zum starten der Website: sudo python3 database_and_http-api.py 

Zur Vereinfachung der Abgabe haben wir ein Python-Skript erstellt, um die Anfragen des Arduino Nano ESP32 zu simulieren. Um das Skript auszuführen, verwenden Sie den folgenden Befehl: python3 send_data.py. Anschließend können Sie eine neue Fahrt erstellen, die in Echtzeit auf der Website mototrack.de abgebildet wird. Zur Veranschaulichung haben wir ein Demo-Video (demo.mp4) eingebunden, das zeigt, wie der Prozess in der Praxis funktioniert.



