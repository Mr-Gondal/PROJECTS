# 🌐 IoT Sensor Data Dashboard — Project 8.7

<div align="center">

![IoT Banner](https://img.shields.io/badge/Project-8.7%20IoT%20Dashboard-00ffd5?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTEyIDJhMTAgMTAgMCAxIDAgMTAgMTBBMTAgMTAgMCAwIDAgMTIgMm0wIDE4YTggOCAwIDEgMSA4LTggOCA4IDAgMCAxLTggOCIvPjwvc3ZnPg==)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chart.js&logoColor=white)
![Status](https://img.shields.io/badge/Status-Live%20Simulation-00ff88?style=for-the-badge)

**A portfolio-grade Industrial IoT Monitoring Console with live sensor simulation, real-time charts, GPS tracking, and anomaly detection — all in a single HTML file.**

*Haris Hussain · Space Science · University of Punjab · 2026*

</div>

---

## 📋 Overview

This dashboard simulates a real-world **Industrial Internet-of-Things (IIoT)** monitoring system, demonstrating the full data pipeline from sensor reading to visualization and alert management. Built entirely in HTML/CSS/JavaScript with no backend or build step, it runs instantly in any modern browser.

The system monitors **6 environmental sensors** across **4 virtual network nodes**, applies threshold-based anomaly detection, tracks GPS position in real time, and allows full user control over simulation parameters.

---

## ✨ Features Table

| # | Feature | Description | Technology |
|---|---------|-------------|------------|
| 1 | **Live Sensor Simulation** | 6 sensors updating every 500ms with physics-based equations | `setInterval` + Math |
| 2 | **Sensor Hero Cards** | Large value cards with sparklines, status badges, trend arrows | Canvas 2D API |
| 3 | **Real-Time Line Charts** | 5 scrolling time-series charts with gradient fills | Chart.js v4 |
| 4 | **Anomaly Detection** | Threshold-based WARNING/CRITICAL detection with alert log | Pure JS |
| 5 | **GPS Track Map** | Canvas-drawn route with pulsing position dot and grid overlay | Canvas 2D API |
| 6 | **Alert Log Panel** | Scrolling timestamped event log, color-coded by severity | DOM manipulation |
| 7 | **Control Panel** | Rate selector, pause/resume, threshold sliders, visibility toggles | HTML form elements |
| 8 | **Statistics Summary** | Per-sensor Min/Max/Mean/Std Dev, updated every 10 readings | JS Math |
| 9 | **Network Status Panel** | 4 sensor nodes with signal strength, battery, online/offline status | Animated DOM |
| 10 | **Export CSV** | Download all sensor readings as a timestamped CSV file | Blob API |
| 11 | **Network BG Animation** | 55-node particle network topology visualization | Canvas requestAnimationFrame |
| 12 | **System Status Bar** | Live uptime counter, node count, data points, PKT timestamp | Sticky header DOM |

---

## 🔬 Sensor Simulation Model

Each sensor value is generated using a **sinusoidal base signal** (modeling diurnal or environmental cycles) combined with **Gaussian white noise** (modeling measurement uncertainty).

### Equations

| Sensor | Formula | Frequency | Noise σ |
|--------|---------|-----------|---------|
| **Temperature** | `T(t) = 25 + 5·sin(t/50) + N(0, 0.3)` | High | Low |
| **Humidity** | `H(t) = 60 + 10·cos(t/70) + N(0, 1.0)` | Medium | Medium |
| **Air Pressure** | `P(t) = 1013 + 2·sin(t/100) + N(0, 0.5)` | Low | Low |
| **Air Quality (AQI)** | `AQI(t) = 45 + 20·sin(t/80) + N(0, 3)` | Medium | High |
| **UV Index** | `UV(t) = max(0, 5 + 3·sin(t/60) + N(0, 0.5))` | Medium | Low |
| **Battery** | `B(t) = B(t-1) − 0.01 + N(0, 0.05), B ∈ [20, 95]` | Monotone | Low |

Where:
- `t` = simulation tick (integer, increments each interval)
- `N(μ, σ)` = Gaussian noise using **Box-Muller transform**: `N = σ · √(−2 ln u₁) · cos(2π u₂)`
- All sine/cosine arguments are in **radians** (unitless tick index)

```
Temperature Cycle (approximate):
t=0   → 25.0°C  (mid)
t=78  → 30.0°C  (max)  ~sin(78/50) = sin(1.56) ≈ 1.0
t=157 → 25.0°C  (mid)
t=235 → 20.0°C  (min)  ~sin(235/50) = sin(4.71) ≈ -1.0
Period ≈ 50·2π ≈ 314 ticks = 157 seconds at 500ms
```

---

## ⚠️ Anomaly Detection Logic

Anomalies are detected using a **dual-threshold system** (Warning → Critical) with **5-second cooldown** per sensor per severity level to prevent alert flooding.

```
┌─────────────────────────────────────────────────────────────┐
│                  ANOMALY DETECTION ENGINE                    │
├────────────┬──────────────┬──────────────┬──────────────────┤
│  SENSOR    │  WARN LOW    │  WARN HIGH   │  CRIT HIGH       │
├────────────┼──────────────┼──────────────┼──────────────────┤
│ Temp (°C)  │  < 15°C      │  > 33°C      │  > 38°C          │
│ Humidity % │  < 30%       │  > 80%       │  > 95%           │
│ Pressure   │  < 1005 hPa  │  > 1025 hPa  │  > 1030 hPa      │
│ AQI        │  —           │  > 100       │  > 150           │
│ UV Index   │  —           │  > 6.0       │  > 8.0           │
│ Battery    │  < 30%       │  —           │  < 15%           │
└────────────┴──────────────┴──────────────┴──────────────────┘

Status: NORMAL → WARN → CRITICAL (also applied as card color coding)
```

All thresholds are **user-adjustable** via the Control Panel sliders in real time.

---

## 🛠️ Tech Stack

| Technology | Version | Role |
|------------|---------|------|
| **HTML5** | Living Standard | Structure & semantic markup |
| **CSS3** | — | Styling, glassmorphism, animations |
| **JavaScript (ES6+)** | — | Simulation engine, event handling |
| **Chart.js** | 4.4.0 (CDN) | Real-time scrolling line charts |
| **Canvas 2D API** | Native | GPS map, sparklines, network background |
| **Google Fonts** | CDN | Orbitron, Inter, JetBrains Mono |
| **Blob API** | Native | CSV export/download |
| **Box-Muller Transform** | Custom JS | Gaussian noise generation |

**Zero dependencies installed** — runs offline after initial Google Fonts/Chart.js CDN load.

---

## 🚀 How to Use

### Run Locally
```bash
# No build step required. Just open the file:
start "c:\Users\HP\Desktop\portfolio\CLI\8_Electronics_Engineering\IoT Sensor Data Dashboard\index.html"

# Or serve with a simple local server (optional):
npx serve .
# Then open http://localhost:3000
```

### Controls
| Control | Action |
|---------|--------|
| **⏸ PAUSE** | Freeze simulation; resumes from current state |
| **▶ RESUME** | Continue simulation |
| **🗑 CLEAR** | Reset all history and GPS track |
| **📥 EXPORT CSV** | Download all current readings as `.csv` |
| **Update Rate** | Switch between 500ms / 1s / 2s / 5s intervals |
| **Sensor Checkboxes** | Hide/show individual sensors from cards + charts |
| **Threshold Sliders** | Adjust WARNING/CRITICAL levels dynamically |

---

## 🏗️ IoT Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        IoT SYSTEM ARCHITECTURE                      │
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │  Node-1  │    │  Node-2  │    │  Node-3  │    │  Node-4  │      │
│  │ Sensor   │    │ Sensor   │    │ Sensor   │    │ Sensor   │      │
│  │ Cluster  │    │ Cluster  │    │ Cluster  │    │ Cluster  │      │
│  │ [88% 🔋] │    │ [62% 🔋] │    │ [45% 🔋] │    │ [31% 🔋] │      │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘      │
│       │               │               │               │             │
│       └───────────────┴───────────────┴───────────────┘             │
│                               │                                      │
│                    ┌──────────▼──────────┐                          │
│                    │   MQTT / LoRa / WiFi │                          │
│                    │   (Simulated 500ms)  │                          │
│                    └──────────┬──────────┘                          │
│                               │                                      │
│                    ┌──────────▼──────────┐                          │
│                    │    DATA PIPELINE     │                          │
│                    │  ┌───────────────┐   │                          │
│                    │  │ Sensor Sim JS │   │                          │
│                    │  │ + Noise Model │   │                          │
│                    │  └──────┬────────┘   │                          │
│                    │         │             │                          │
│                    │  ┌──────▼────────┐   │                          │
│                    │  │ Anomaly Detect│   │                          │
│                    │  │ Threshold Eng.│   │                          │
│                    │  └──────┬────────┘   │                          │
│                    └─────────┼────────────┘                          │
│                              │                                        │
│            ┌─────────────────┼───────────────────────┐               │
│            │                 │                        │               │
│   ┌────────▼──────┐  ┌──────▼──────┐  ┌────────────▼──┐            │
│   │  Chart.js     │  │  Alert Log  │  │  GPS Canvas   │            │
│   │  Line Charts  │  │  Panel      │  │  Map          │            │
│   │  (5 sensors)  │  │  (Anomalies)│  │  (Live Track) │            │
│   └───────────────┘  └─────────────┘  └───────────────┘            │
│                                                                      │
│                     ┌──────────────────┐                             │
│                     │  Statistics      │                             │
│                     │  Min/Max/Mean/σ  │                             │
│                     │  CSV Export      │                             │
│                     └──────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📐 GPS Track Bounding Box

The simulated GPS performs a **random walk** constrained to a bounding box around **Lahore, Pakistan**:

```
Latitude:   31.514°N → 31.526°N
Longitude:  74.349°E → 74.371°E

Random walk: Δlat ~ N(0, 0.0002°), Δlon ~ N(0, 0.0002°)
Speed derived from: |Δlat·111km + Δlon·95km| × 3600 km/h
Heading: atan2(Δlon, Δlat) → degrees
```

---

## 🎓 Learning Outcomes

By studying and running this project, you will understand:

1. **Sensor Physics Modeling** — How real IoT sensors can be approximated with sinusoidal + stochastic models
2. **Real-Time Data Streaming** — The `setInterval` → Chart.js streaming update pattern for live dashboards
3. **Anomaly Detection** — Simple threshold-based alerting systems used in industrial SCADA systems
4. **Canvas 2D API** — Drawing interactive maps, sparklines, and animated backgrounds
5. **Gaussian Noise Simulation** — Box-Muller transform for generating normally distributed random variables
6. **GPS Data Handling** — Converting lat/lon coordinates to canvas pixel coordinates
7. **Glassmorphism UI Design** — Modern dark-mode interface techniques using CSS backdrop-filter and gradients
8. **Data Export** — Browser Blob API for client-side CSV generation without any backend

---

## 📁 Project Structure

```
IoT Sensor Data Dashboard/
├── index.html      ← Complete self-contained dashboard (single file)
└── README.md       ← This file
```

---

## 👤 Author

| Field | Detail |
|-------|--------|
| **Name** | Haris Hussain |
| **Program** | B.Sc. Space Science |
| **University** | University of Punjab, Lahore |
| **Project** | 8.7 — IoT Sensor Data Dashboard |
| **Category** | Electronics Engineering / Embedded Systems |
| **Year** | 2026 |

---

## 📄 License

This project is created for educational and portfolio purposes. Free to use and adapt with attribution.

---

<div align="center">
<sub>Built with ⚡ by Haris Hussain · IoT Sensor Data Dashboard · Project 8.7</sub>
</div>
