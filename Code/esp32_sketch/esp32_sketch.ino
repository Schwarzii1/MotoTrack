#include <TinyGPS++.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_MPU6050.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <LiquidCrystal_I2C.h>
#include <deque>

#define BUTTON_UP 12
#define BUTTON_DOWN 14
#define BUTTON_SELECT 27
#define BUTTON_BACK 26
#define BUTTON_ENTER 25

TinyGPSPlus gps;
HardwareSerial gpsSerial(1);
Adafruit_MPU6050 mpu;
LiquidCrystal_I2C lcd(0x27, 16, 2);

String availableNetworks[20];
int networkCount = 0;
int selectedNetwork = 0;
String enteredPassword = "";
bool passwordEntryMode = false;
bool connected = false;
int alphabetIndex = 0;
const String alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

const char* serverURL = "http://135.236.212.233:80/data";
std::deque<String> dataBuffer;

unsigned long lastButtonPress = 0;

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(9600, SERIAL_8N1, 13, 15);

  pinMode(BUTTON_UP, INPUT_PULLUP);
  pinMode(BUTTON_DOWN, INPUT_PULLUP);
  pinMode(BUTTON_SELECT, INPUT_PULLUP);
  pinMode(BUTTON_BACK, INPUT_PULLUP);
  pinMode(BUTTON_ENTER, INPUT_PULLUP);

  lcd.init();
  lcd.backlight();

  if (!mpu.begin()) {
    lcd.print("MPU6050 Error");
    while (1);
  }

  lcd.clear();
  lcd.print("Scanning WiFi...");
  networkCount = WiFi.scanNetworks();
  networkCount = min(networkCount, 20);  // Prevent buffer overflow

  for (int i = 0; i < networkCount; i++) {
    availableNetworks[i] = WiFi.SSID(i);
  }

  lcd.clear();
}

void loop() {
  if (!connected) {
    handleMenu();
  } else {
    collectAndSendData();
  }
}

bool isButtonPressed(int pin) {
  if (digitalRead(pin) == LOW && millis() - lastButtonPress > 200) {
    lastButtonPress = millis();
    return true;
  }
  return false;
}

void handleMenu() {
  lcd.clear();
  lcd.print(availableNetworks[selectedNetwork].substring(0, 16));

  if (isButtonPressed(BUTTON_UP)) {
    selectedNetwork = (selectedNetwork - 1 + networkCount) % networkCount;
  }

  if (isButtonPressed(BUTTON_DOWN)) {
    selectedNetwork = (selectedNetwork + 1) % networkCount;
  }

  if (isButtonPressed(BUTTON_SELECT)) {
    lcd.clear();
    lcd.print("Enter Password:");
    enteredPassword = "";
    passwordEntryMode = true;
    alphabetIndex = 0;

    while (passwordEntryMode) {
      lcd.clear();
      lcd.print("Password:");
      lcd.setCursor(0, 1);
      lcd.print(enteredPassword + "_" + alphabet[alphabetIndex]);

      if (isButtonPressed(BUTTON_UP)) alphabetIndex = (alphabetIndex + 1) % alphabet.length();
      if (isButtonPressed(BUTTON_DOWN)) alphabetIndex = (alphabetIndex - 1 + alphabet.length()) % alphabet.length();
      if (isButtonPressed(BUTTON_SELECT)) enteredPassword += alphabet[alphabetIndex];
      if (isButtonPressed(BUTTON_BACK) && enteredPassword.length() > 0) enteredPassword.remove(enteredPassword.length() - 1);
      if (isButtonPressed(BUTTON_ENTER)) passwordEntryMode = false;
    }

    WiFi.begin(availableNetworks[selectedNetwork].c_str(), enteredPassword.c_str());
    lcd.clear();
    lcd.print("Connecting...");

    for (int i = 0; i < 30 && WiFi.status() != WL_CONNECTED; i++) {
      delay(500);
      lcd.print(".");
    }

    connected = (WiFi.status() == WL_CONNECTED);
    lcd.clear();
    lcd.print(connected ? "Connected!" : "Failed to Connect");
    delay(1000);
  }
}

void collectAndSendData() {
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  if (gps.location.isValid() && gps.location.isUpdated()) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    String timestamp = String(millis());

    String payload = "{";
    payload += "\"timestamp\": " + timestamp + ", ";
    payload += "\"latitude\": " + String(gps.location.lat(), 6) + ", ";
    payload += "\"longitude\": " + String(gps.location.lng(), 6) + ", ";
    payload += "\"speed\": " + String(gps.speed.kmph()) + ", ";
    payload += "\"acceleration_x\": " + String(a.acceleration.x) + ", ";
    payload += "\"acceleration_y\": " + String(a.acceleration.y) + ", ";
    payload += "\"acceleration_z\": " + String(a.acceleration.z) + ", ";
    payload += "\"gyroscope_x\": " + String(g.gyro.x) + ", ";
    payload += "\"gyroscope_y\": " + String(g.gyro.y) + ", ";
    payload += "\"gyroscope_z\": " + String(g.gyro.z) + "}";

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverURL);
      http.addHeader("Content-Type", "application/json");
      int httpResponseCode = http.POST(payload);
      http.end();

      while (!dataBuffer.empty()) {
        http.begin(serverURL);
        http.addHeader("Content-Type", "application/json");
        http.POST(dataBuffer.front());
        dataBuffer.pop_front();
        http.end();
      }
    } else {
      dataBuffer.push_back(payload);  // Save data when offline
    }
  }
  delay(1000);
}
