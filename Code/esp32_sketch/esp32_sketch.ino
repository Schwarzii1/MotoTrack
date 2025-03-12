#include <TinyGPS++.h>         // Bibliothek für GPS-Funktionen
#include <Wire.h>              // Bibliothek für I2C-Kommunikation
#include <Adafruit_Sensor.h>   // Allgemeine Sensor-Bibliothek
#include <Adafruit_MPU6050.h>  // Bibliothek für den MPU6050 Sensor
#include <WiFi.h>              // Bibliothek für WLAN-Funktionalität
#include <HTTPClient.h>        // Bibliothek für HTTP-Kommunikation

// GPS- und MPU6050-Instanzen erstellen
TinyGPSPlus gps;                 // GPS-Objekt
HardwareSerial gpsSerial(1);      // Serial1 für GPS-Kommunikation
Adafruit_MPU6050 mpu;             // MPU6050 Sensor-Objekt

// WLAN-Zugangsdaten
const char* ssid = "iPhoneJanik";       // WLAN-Name (SSID)
const char* password = "12345678AA";    // WLAN-Passwort

// URL des Servers (Azure VM)
const char* serverURL = "http://135.236.212.233:80/data";

void setup() {
  Serial.begin(115200);   // Serielle Kommunikation starten
  gpsSerial.begin(9600, SERIAL_8N1, 13, 15); // GPS-Modul über Serial1 an Pins 13 (RX) und 15 (TX) anschließen

  // MPU6050 initialisieren
  if (!mpu.begin()) {
    Serial.println("MPU6050 nicht gefunden!"); 
    while (1); // Programm stoppen, falls Sensor nicht erkannt wird
  }

  Serial.println("MPU6050 erfolgreich initialisiert!");

  // Verbindung zum WLAN herstellen
  Serial.print("Verbinde mit WLAN...");
  WiFi.begin(ssid, password);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {  // Max. 30 Versuche
    delay(1000);
    Serial.print(".");
    attempts++;
  }

  // Überprüfung der WLAN-Verbindung
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Verbunden mit WLAN!");
    Serial.print("IP-Adresse: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WLAN-Verbindung fehlgeschlagen!");
    Serial.print("WLAN-Status: ");
    Serial.println(WiFi.status()); // Zeigt den Status-Code für Fehleranalyse an
    while (1); // Stoppt das Programm, falls keine Verbindung hergestellt werden kann
  }
}

void loop() {
  Serial.println("Starte Loop-Durchlauf...");

  // GPS-Daten lesen
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());  // GPS-Daten dekodieren
  }

  // Falls neue GPS-Daten vorhanden sind, auf die serielle Konsole ausgeben
  if (gps.location.isUpdated()) {
    Serial.println("Neue GPS-Daten empfangen!");
    Serial.print("Breitengrad: ");
    Serial.println(gps.location.lat(), 6);
    Serial.print("Längengrad: ");
    Serial.println(gps.location.lng(), 6);
    Serial.print("Geschwindigkeit: ");
    Serial.println(gps.speed.kmph());
  }

  // Sensordaten des MPU6050 auslesen
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // JSON-Datenstring für die Serverübertragung erstellen
  String payload = "{";
  payload += "\"latitude\": " + String(gps.location.lat(), 6) + ", ";
  payload += "\"longitude\": " + String(gps.location.lng(), 6) + ", ";
  payload += "\"speed\": " + String(gps.speed.kmph()) + ", ";
  payload += "\"acceleration_x\": " + String(a.acceleration.x) + ", ";
  payload += "\"acceleration_y\": " + String(a.acceleration.y) + ", ";
  payload += "\"acceleration_z\": " + String(a.acceleration.z) + ", ";
  payload += "\"gyroscope_x\": " + String(g.gyro.x) + ", ";
  payload += "\"gyroscope_y\": " + String(g.gyro.y) + ", ";
  payload += "\"gyroscope_z\": " + String(g.gyro.z);
  payload += "}";

  // Prüfen, ob WLAN verbunden ist, bevor Daten gesendet werden
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);                   // Verbindung zum Server herstellen
    http.addHeader("Content-Type", "application/json"); // Header für JSON setzen

    // HTTP-POST-Anfrage mit den Sensordaten senden
    int httpResponseCode = http.POST(payload);
    Serial.print("HTTP-Antwortcode: ");
    Serial.println(httpResponseCode);

    // Serverantwort ausgeben, falls die Übertragung erfolgreich war
    if (httpResponseCode > 0) {
      Serial.println("Daten erfolgreich gesendet!");
      String response = http.getString();  // Serverantwort abrufen
      Serial.println("Serverantwort: " + response);
    } else {
      Serial.println("Fehler beim Senden der Daten. HTTP Code: " + String(httpResponseCode));
    }

    http.end(); // Verbindung schließen
  } else {
    Serial.println("WLAN nicht verbunden, Daten werden nicht gesendet.");
  }

  delay(1000); // Eine Sekunde warten, bevor die nächsten Daten gesendet werden (sollte theoretisch auch in kürzeren Intervallen möglich sein)
}
