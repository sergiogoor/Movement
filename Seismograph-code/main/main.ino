#include <Wire.h>
#include <Arduino.h>

#define MPU6050_ADDR 0x68
#define PWR_MGMT_1 0x6B
#define ACCEL_XOUT_H 0x3B

// Variables para almacenar los offsets de calibración
int16_t accXOffset = 0;
int16_t accYOffset = 0;
int16_t accZOffset = 0;

void setupMPU6050();
void readAcceleration(int16_t &accX, int16_t &accY, int16_t &accZ);
void calibrateAccelerometer(int samples = 1000);
void readAndPrintAcceleration();
void checkForRecalibrationCommand();

unsigned long lastTime = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin(4, 5); // SDA -> GPIO4, SCL -> GPIO5
  setupMPU6050();
  delay(2000);
  calibrateAccelerometer();
}

void loop() {
  checkForRecalibrationCommand();
  readAndPrintAcceleration();
  delay(1000/900);
}

void setupMPU6050() {
  // Despertar el MPU6050
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(PWR_MGMT_1);
  Wire.write(0);
  if (Wire.endTransmission(true) != 0) {
    Serial.println("Error al iniciar el MPU6050");
  } else {
    Serial.println("MPU6050 iniciado correctamente");
  }
}

void readAcceleration(int16_t &accX, int16_t &accY, int16_t &accZ) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(ACCEL_XOUT_H);
  if (Wire.endTransmission(false) != 0) {
    Serial.println("Error al solicitar datos del MPU6050");
    return;
  }
  
  Wire.requestFrom((uint8_t)MPU6050_ADDR, (uint8_t)6, (uint8_t)true);
  if (Wire.available() == 6) {
    accX = Wire.read() << 8 | Wire.read();
    accY = Wire.read() << 8 | Wire.read();
    accZ = Wire.read() << 8 | Wire.read();
  } else {
    Serial.println("No se recibieron suficientes datos del MPU6050");
  }
}

void calibrateAccelerometer(int samples) {
  //Serial.println("Calibrando el acelerómetro...");
  int32_t accXSum = 0;
  int32_t accYSum = 0;
  int32_t accZSum = 0;
  
  for (int i = 0; i < samples; i++) {
    int16_t accX, accY, accZ;
    readAcceleration(accX, accY, accZ);
    accXSum += accX;
    accYSum += accY;
    accZSum += accZ;
    delay(10); // Esperar un poco entre muestras
  }
  
  accXOffset = accXSum / samples;
  accYOffset = accYSum / samples;
  accZOffset = accZSum / samples;
  /*
  Serial.print("Calibración completa: Offsets -> X: ");
  Serial.print(accXOffset);
  Serial.print(", Y: ");
  Serial.print(accYOffset);
  Serial.print(", Z: ");
  Serial.println(accZOffset);
  */
}

void readAndPrintAcceleration() {
  int16_t accX, accY, accZ;
  readAcceleration(accX, accY, accZ);
  
  // Compensar los valores con los offsets de calibración
  accX -= accXOffset;
  accY -= accYOffset;
  accZ -= accZOffset;
  
  // Mostrar los datos en la consola
  Serial.print(accX);
  Serial.print(" ");
  Serial.print(accY);
  Serial.print(" ");
  Serial.println(accZ);
}

void checkForRecalibrationCommand() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Eliminar espacios en blanco al principio y al final
    if (command == "recalibrar") {
      Serial.println("Recalibrando el acelerómetro...");
      calibrateAccelerometer();
    }
  }
}
