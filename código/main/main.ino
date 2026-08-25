#include <Arduino_LSM6DSOX.h>
#include <WiFiNINA.h>

#define THRESHOLD 0.5
#define CALIBRATION_SAMPLES 50

float baseX, baseY, baseZ;
bool phonePickedUp = false;

void setup() {
  delay(500);
  Serial.begin(115200);

  pinMode(LEDR, OUTPUT);
  pinMode(LEDG, OUTPUT);
  pinMode(LEDB, OUTPUT);

  // Verde = a estudar
  digitalWrite(LEDR, HIGH);
  digitalWrite(LEDG, LOW);
  digitalWrite(LEDB, HIGH);

  if (!IMU.begin()) {
    Serial.println("Erro ao iniciar o IMU!");
    while (1);
  }

  // Calibração automática
  Serial.println("A calibrar... não mexas no Arduino!");
  float sumX = 0, sumY = 0, sumZ = 0;
  int count = 0;

  while (count < CALIBRATION_SAMPLES) {
    float x, y, z;
    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(x, y, z);
      sumX += x;
      sumY += y;
      sumZ += z;
      count++;
      delay(50);
    }
  }

  baseX = sumX / CALIBRATION_SAMPLES;
  baseY = sumY / CALIBRATION_SAMPLES;
  baseZ = sumZ / CALIBRATION_SAMPLES;

  Serial.println("Calibração concluída! A monitorizar...");
}

void loop() {
  float x, y, z;

  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);

    float diffX = abs(x - baseX);
    float diffY = abs(y - baseY);
    float diffZ = abs(z - baseZ);

    if (diffX > THRESHOLD || diffY > THRESHOLD || diffZ > THRESHOLD) {
      if (!phonePickedUp) {
        phonePickedUp = true;

        // Vermelho = distração
        digitalWrite(LEDR, HIGH);
        digitalWrite(LEDG, LOW);
        digitalWrite(LEDB, LOW);

        Serial.println("DISTRACAO_INICIO");
      }
    } else {
      if (phonePickedUp) {
        phonePickedUp = false;

        // Verde = a estudar
        digitalWrite(LEDR, LOW);
        digitalWrite(LEDG, HIGH);
        digitalWrite(LEDB, LOW);

        Serial.println("DISTRACAO_FIM");
      }
    }
  }

  delay(100);
}