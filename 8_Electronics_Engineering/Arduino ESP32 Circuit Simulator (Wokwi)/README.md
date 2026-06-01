# ⚡ Arduino / ESP32 Circuit Simulator (Wokwi)

> **Project 8.6 — Electronics Engineering Portfolio**
> *5 Interactive Embedded Circuits · Wokwi Platform · C++ Arduino Firmware*

[![Status](https://img.shields.io/badge/Status-Live%20Demo-brightgreen?style=flat-square)]()
[![Platform](https://img.shields.io/badge/Platform-Wokwi%20%2F%20Browser-red?style=flat-square)]()
[![Language](https://img.shields.io/badge/Language-C%2B%2B%20%2F%20Arduino-blue?style=flat-square)]()
[![Domain](https://img.shields.io/badge/Domain-Embedded%20Systems-green?style=flat-square)]()

---

## 🔬 Overview

A **browser-based showcase and interactive simulator** for 5 Arduino/ESP32 embedded circuits. Each project includes working C++ firmware code with syntax highlighting, SVG circuit schematics, and live in-page simulations — all without any hardware. Runs on the [Wokwi](https://wokwi.com) free simulator platform.

---

## 🚀 5 Simulated Projects

| # | Circuit | Key Components | Protocols | Difficulty |
|---|---------|---------------|-----------|------------|
| 1 | **Temperature Monitor** | DHT22, 16×2 LCD, Alert LED | I2C, 1-Wire | Beginner |
| 2 | **Traffic Light Controller** | 3× LEDs, Pushbutton | GPIO, ISR | Beginner |
| 3 | **PWM Motor Speed Control** | Potentiometer, DC Motor, L298N | PWM, ADC | Intermediate |
| 4 | **Ultrasonic Distance Meter** | HC-SR04, Buzzer | UART, GPIO | Beginner |
| 5 | **GPS Data Logger** | NEO-6M GPS, SD Card | UART, SPI | Intermediate |

---

## 🎛️ Interactive Features

| Feature | Description |
|---|---|
| **Live Simulations** | Working traffic light, LCD display, spinning motor, distance bar |
| **Syntax-Highlighted Code** | Full `.ino` sketches with keyword/function coloring + copy button |
| **SVG Circuit Diagrams** | Clean schematics with Arduino board, components, color-coded wires |
| **Serial Monitor** | Simulated scrolling serial output for each project |
| **Wokwi Links** | One-click to open each circuit in the free Wokwi simulator |
| **Component Library** | Specs, pin-outs, and descriptions for all 8 components used |
| **Key Concepts** | GPIO, PWM, ADC, I2C, UART, ISR — explained with code snippets |

---

## 🔌 How to Run on Wokwi

1. Visit [wokwi.com](https://wokwi.com) — no account required for basic use
2. Click **"New Project" → Arduino Uno**
3. Copy the `.ino` sketch from this page into the editor
4. Add components from the **Wokwi Parts Library** matching the circuit diagram
5. Click **▶ Start Simulation**

---

## 📁 File Structure

```
Arduino ESP32 Circuit Simulator (Wokwi)/
├── index.html          ← Full showcase + interactive simulator
└── README.md           ← This file

# Wokwi project files (create on platform):
temperature-monitor/
├── sketch.ino          ← DHT22 + LCD firmware
└── diagram.json        ← Wokwi circuit layout

traffic-light/
├── sketch.ino          ← Timed + interrupt-driven FSM
└── diagram.json

motor-pwm/
├── sketch.ino          ← ADC → analogWrite → L298N
└── diagram.json

ultrasonic-meter/
├── sketch.ino          ← pulseIn distance + buzzer
└── diagram.json

gps-logger/
├── sketch.ino          ← TinyGPS++ + SD logging
└── diagram.json
```

---

## 🛠️ Tech Stack

| Tool | Role |
|------|------|
| C++ / Arduino IDE | Embedded firmware development |
| Wokwi | Free browser circuit + firmware simulator |
| HTML5 + CSS3 | Showcase page UI |
| Vanilla JavaScript | Interactive simulations |
| SVG | Circuit schematics |

### Libraries Used
| Library | Project |
|---------|---------|
| `DHT.h` | Temperature Monitor |
| `LiquidCrystal_I2C.h` | Temperature Monitor |
| `TinyGPS++.h` | GPS Logger |
| `SoftwareSerial.h` | GPS Logger |
| `SD.h` | GPS Logger |

---

## 📚 Key Concepts Covered

- **GPIO & Digital I/O** — `pinMode()`, `digitalRead()`, `digitalWrite()`
- **PWM Output** — `analogWrite()`, duty cycle, 490Hz default frequency
- **ADC (Analog Read)** — 10-bit, 0–1023, `analogRead()`
- **I2C Protocol** — `Wire.h`, master/slave, 0x27 LCD address
- **UART / Serial** — `Serial.begin()`, `SoftwareSerial` for GPS
- **Interrupt Service Routines** — `attachInterrupt()`, `FALLING` edge

---

## 📊 Learning Outcomes

- ✅ Embedded C++ programming on AVR microcontrollers
- ✅ Sensor interfacing (DHT22, HC-SR04, NEO-6M GPS)
- ✅ Hardware communication protocols (I2C, SPI, UART, PWM)
- ✅ Interrupt-driven programming for real-time response
- ✅ Motor driver circuits (H-bridge, L298N)
- ✅ GPS NMEA sentence parsing with TinyGPS++

---

## 👨‍💻 Author

**Haris Hussain**
Space Science · University of the Punjab, Lahore
Electronics Engineering Portfolio — Project 8.6
