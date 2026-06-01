# 〜 Satellite Link Budget Calculator

> **Project 8.5 — Electronics Engineering Portfolio**
> *RF Link Analysis · Friis Equation · FSPL · SNR · Link Margin · LEO/MEO/GEO Orbits*

[![Status](https://img.shields.io/badge/Status-Live%20Demo-brightgreen?style=flat-square)]()
[![Tech](https://img.shields.io/badge/Tech-HTML%20%2F%20CSS%20%2F%20JS-blue?style=flat-square)]()
[![Domain](https://img.shields.io/badge/Domain-Satellite%20Communications-navy?style=flat-square)]()
[![Physics](https://img.shields.io/badge/Physics-RF%20%2F%20Antenna%20Theory-cyan?style=flat-square)]()

---

## 🛰️ Overview

A **fully browser-based satellite link budget calculator** that computes the complete RF signal chain from transmitter to receiver — EIRP, free-space path loss, received power, noise floor, SNR, and link margin — in real-time as you adjust parameters. Features animated orbit visualizations, preset scenarios (ISS, GPS, NOAA, Iridium), and interactive Chart.js plots.

---

## 🚀 Features

| Feature | Description |
|---|---|
| **3 Orbit Types** | LEO (500 km), MEO (20,200 km), GEO (35,786 km) with animated satellite |
| **Full Link Budget** | EIRP → FSPL → Pr → Noise → SNR → Link Margin in one chain |
| **PASS / FAIL Gauge** | Semicircle gauge + color badge showing margin health |
| **5 Frequency Bands** | UHF · L · S · X · Ku-Band with wavelength and use-case info |
| **4 Preset Scenarios** | ISS ARISS · GPS L1 · NOAA Weather · Iridium SBD |
| **3 Interactive Charts** | SNR vs Distance · FSPL vs Frequency · Margin vs Elevation |
| **Antenna Polar Plot** | Canvas-drawn dish gain pattern with target direction |
| **Live Equation** | All formulas shown with real numbers substituted in real-time |
| **CSV Export** | Download full link budget report |

---

## 📐 Key Equations

### Free-Space Path Loss (Friis)
```
FSPL (dB) = 20·log₁₀(d) + 20·log₁₀(f) + 20·log₁₀(4π/c)
           = 20·log₁₀(d_km) + 20·log₁₀(f_GHz) + 92.45
```

### EIRP (Effective Isotropic Radiated Power)
```
EIRP (dBW) = 10·log₁₀(Pt) + Gt − Ll
```

### Received Power
```
Pr (dBW) = EIRP + Gr − FSPL − La
```

### Noise Power
```
N (dBW) = k·T·B  →  −228.6 + 10·log₁₀(T_K) + 10·log₁₀(B_Hz)
```
where k = 1.38×10⁻²³ J/K (Boltzmann constant)

### Signal-to-Noise Ratio & Link Margin
```
SNR (dB)         = Pr − N
Link Margin (dB) = SNR − SNR_required
```
> Link Margin > 0 dB → **PASS** ✅  
> Link Margin < 0 dB → **FAIL** ❌

---

## 📡 Frequency Bands

| Band | Frequency | Wavelength | Typical Use |
|------|-----------|------------|-------------|
| UHF | 400 MHz | 75 cm | Amateur satellite, NOAA APT |
| L-Band | 1.5 GHz | 20 cm | GPS L1, Iridium |
| S-Band | 2.4 GHz | 12.5 cm | Weather satellites, deep space |
| X-Band | 8 GHz | 3.75 cm | Military comms, Earth observation |
| Ku-Band | 12 GHz | 2.5 cm | Direct broadcast TV, VSAT |

---

## 🎯 Preset Scenarios

| Scenario | Orbit | Frequency | Typical Link Margin |
|----------|-------|-----------|---------------------|
| ISS Amateur Radio (ARISS) | LEO 400 km | UHF 145 MHz | ~5–15 dB |
| GPS L1 | MEO 20,200 km | L-Band 1.575 GHz | ~6 dB |
| NOAA Weather Satellite | LEO 850 km | UHF 137 MHz | ~10 dB |
| Iridium SBD | LEO 780 km | L-Band 1.6 GHz | ~8 dB |

---

## 🛠️ Tech Stack

| Tool | Role |
|------|------|
| HTML5 + CSS3 | Dark-mode space UI, glassmorphism, animated starfield |
| Vanilla JavaScript | Real-time calculation engine, equation renderer |
| Chart.js 4 | SNR vs Distance, FSPL vs Frequency, Margin vs Elevation |
| Canvas API | Antenna polar pattern, animated orbit diagram |
| Google Fonts | Orbitron + Inter + JetBrains Mono |

---

## 🎓 Learning Outcomes

- ✅ Friis transmission equation and free-space path loss
- ✅ EIRP, antenna gain, and cable loss budgeting
- ✅ Receiver noise temperature and noise power density
- ✅ SNR vs link margin distinction
- ✅ Orbit altitude vs path loss trade-off (LEO/MEO/GEO)
- ✅ Frequency band selection for different applications

---

## 👨‍💻 Author

**Haris Hussain**
Space Science · University of the Punjab, Lahore
Electronics Engineering Portfolio — Project 8.5
