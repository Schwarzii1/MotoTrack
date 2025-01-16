#include <TinyGPS++.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_MPU6050.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Define GPS and MPU6050
TinyGPSPlus gps;
HardwareSerial gpsSerial(1); // Using Serial1 for GPS
Adafruit_MPU6050 mpu;

// Wi-Fi credentials
const char* ssid = "iPhoneJanik";
const char* password = "12345678AA";

// Azure server URL
const char* serverURL = "http://135.236.212.233:5000/data";

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(9600, SERIAL_8N1, 13, 15); // RX, TX pins for GPS

  // Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1);
  }

  Serial.println("MPU6050 Found!");

  // Connect to Wi-Fi
  Serial.print("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {  // Increase attempts
    delay(1000);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Connected to Wi-Fi");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Wi-Fi connection failed");
    Serial.print("Wi-Fi Status: ");
    Serial.println(WiFi.status()); // Show status code
    while (1); // Halt the program if no connection
  }
}

void loop() {
  Serial.println("In loop...");
  
  // Read GPS data
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  if (gps.location.isUpdated()) {
    Serial.println("GPS data updated");
    Serial.print("Latitude: ");
    Serial.println(gps.location.lat(), 6);
    Serial.print("Longitude: ");
    Serial.println(gps.location.lng(), 6);
    Serial.print("Speed: ");
    Serial.println(gps.speed.kmph());
  }

  // Get MPU6050 data
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // Prepare JSON payload
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

  // Send data to Azure VM
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    // Send POST request
    int httpResponseCode = http.POST(payload);
    Serial.print("HTTP Response Code: ");
    Serial.println(httpResponseCode);

    // Check the HTTP response code
    if (httpResponseCode > 0) {
      Serial.println("Data sent successfully");
      String response = http.getString();  // Get the server response
      Serial.println("Server response: " + response);
    } else {
      Serial.println("Error in sending data. HTTP Response Code: " + String(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("Wi-Fi not connected");
  }

  delay(1000); // Delay between data sends
}
