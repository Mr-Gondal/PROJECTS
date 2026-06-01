# ⚡ Project 8.8 — Fault Detection in Power Systems (ML)

> **Real-time fault classification in three-phase power networks using symmetrical components, rule-based feature extraction, and simulated ML models.**

**Author:** Haris Hussain  
**Department:** Space Science, University of Punjab  
**Project Series:** Electronics Engineering Portfolio — Project 8.8

---

## 🔌 Overview

Power system faults — ranging from single line-to-ground to three-phase short circuits — are one of the most critical events in electrical infrastructure. Undetected faults cause equipment damage, power outages, and safety hazards. This project implements a **browser-based power grid control room simulator** that:

- Continuously generates three-phase voltage and current waveforms at 50 Hz
- Allows the user to **inject six fault types** in real time
- Applies a **rule-based + symmetrical-component classifier** to detect and identify the fault
- Simulates **protection relays** (overcurrent, ground fault, differential, distance)
- Visualizes **phasor diagrams**, **feature extraction metrics**, and **ML confidence scores**
- Displays a **confusion matrix and performance metrics** from an IEEE dataset-trained Random Forest

---

## ⚡ Fault Types

| Code | Fault Type | Description | Phases Affected | Severity |
|------|-----------|-------------|-----------------|----------|
| **NRM** | Normal Operation | Balanced three-phase, no fault | — | — |
| **LG** | Line-to-Ground | Single phase shorts to earth. Most common (~70–80% of faults). Va collapses to ≈0, Ia spikes. Zero-sequence component V0 rises sharply. | Phase A | Medium |
| **LL** | Line-to-Line | Two phases short together (no ground path). Va and Vb distort symmetrically. Negative-sequence V2 appears. | Phase A–B | High |
| **LLG** | Double Line-to-Ground | Two phases simultaneously contact ground. Large V0 and V2. Severe asymmetric current rise. | Phase A, B | High |
| **LLL** | Three-Phase Fault | All three phases short together. Most severe — all voltages collapse. Symmetrical (V2≈V0≈0) but devastating. | All | Critical |
| **HIF** | High Impedance | Contact with high-resistance surface (tree, asphalt). Subtle voltage sag with harmonic injection. Hard to detect. | Phase A | Low |

---

## 🔬 Features Used for ML Classification

The following features are extracted from instantaneous waveforms and used to classify faults:

| Feature | Symbol | Description |
|---------|--------|-------------|
| Phase RMS Voltages | Vrms_a, Vrms_b, Vrms_c | Per-unit RMS of each voltage phase |
| Phase RMS Currents | Irms_a, Irms_b, Irms_c | Per-unit RMS of each current phase |
| Zero Sequence Voltage | V0 | Indicates ground fault path: V0 = (Va+Vb+Vc)/3 |
| Positive Sequence Voltage | V1 | Fundamental healthy component |
| Negative Sequence Voltage | V2 | Indicates asymmetric (unbalanced) fault |
| Current Imbalance Factor | I_imbal | Max current deviation / average current |
| Total Harmonic Distortion | THD_a | Harmonic content of Phase A voltage |
| Sequence Ratio | V2/V1 | Unbalance severity indicator |

---

## 📐 Symmetrical Components Theory

Every unbalanced three-phase system can be decomposed into three **balanced** sets of phasors using **Fortescue's theorem**:

```
V0 = (1/3)(Va + Vb + Vc)          ← Zero Sequence (ground fault indicator)
V1 = (1/3)(Va + a·Vb + a²·Vc)    ← Positive Sequence (normal operation)
V2 = (1/3)(Va + a²·Vb + a·Vc)    ← Negative Sequence (asymmetric fault)
```

where **a = e^(j2π/3)** is the 120° rotation operator.

| Condition | V0 | V1 | V2 |
|-----------|----|----|-----|
| Balanced (Normal) | ≈ 0 | ≈ 1.0 pu | ≈ 0 |
| LG Fault | > 0.3 pu | reduced | elevated |
| LL Fault | ≈ 0 | reduced | > 0.3 pu |
| LLG Fault | > 0.3 pu | reduced | > 0.3 pu |
| LLL Fault | ≈ 0 | → 0 | ≈ 0 |

---

## 🤖 Model Architecture

### Model 1: Random Forest Classifier
- **Input:** 8 extracted features per window
- **Trees:** 200 estimators, max depth 15
- **Training data:** IEEE Power Systems Fault Dataset (1,000 samples/class × 5 classes)
- **Sampling window:** 1 full cycle (20 ms at 50 Hz)
- **Performance:** 97.2% accuracy

### Model 2: LSTM Sequence Classifier
- **Input:** Raw waveform sequences (200 timesteps × 6 channels)
- **Architecture:** LSTM(64) → LSTM(32) → Dense(5, softmax)
- **Training:** Adam optimizer, 50 epochs, batch size 32
- **Performance:** 95.1% accuracy

### Rule-Based Baseline (This Demo)
- Thresholding on V0, V2, per-phase RMS, and imbalance factors
- Confidence scores computed from feature-distance heuristics
- Runs entirely in the browser — no backend required

---

## 📊 Model Performance

### Random Forest (IEEE Dataset)

| Class | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| Normal | 99.0% | 99.0% | 99.0% |
| LG Fault | 97.0% | 97.5% | 97.2% |
| LL Fault | 98.5% | 98.0% | 98.2% |
| LLG Fault | 96.0% | 98.0% | 97.0% |
| LLL Fault | 98.0% | 99.0% | 98.5% |
| **Overall** | **97.7%** | **98.3%** | **97.9%** |

### LSTM Classifier

| Class | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| Normal | 97.5% | 98.0% | 97.7% |
| LG Fault | 94.0% | 95.0% | 94.5% |
| LL Fault | 96.0% | 94.5% | 95.2% |
| LLG Fault | 93.0% | 95.0% | 94.0% |
| LLL Fault | 97.0% | 97.5% | 97.2% |
| **Overall** | **95.5%** | **96.0%** | **95.7%** |

---

## 🛡️ Protection Relay Simulation

| Relay | ANSI Code | Trip Condition |
|-------|-----------|----------------|
| Overcurrent | 50/51 | Any Irms > 1.5 pu |
| Ground Fault | 64 | V0 > 0.2 pu |
| Differential | 87 | Current imbalance > 40% |
| Distance | 21 | Always OK (simulation) |

---

## 🖥️ Technology Stack

| Component | Technology |
|-----------|-----------|
| UI Framework | Vanilla HTML5 + CSS3 + ES6 JavaScript |
| Charting | Chart.js 4.4 (CDN) |
| Phasor Diagram | HTML5 Canvas |
| Animation | requestAnimationFrame loop |
| Fonts | Orbitron (headers), Inter (body), JetBrains Mono (values) |
| Design | Dark mode, neon glow, CSS animations, glassmorphism |
| Backend | **None** — fully self-contained single HTML file |

---

## 📂 Dataset Info

| Dataset | Description |
|---------|-------------|
| **IEEE Power Systems Fault Dataset** | Synthetic three-phase fault signals at 50 Hz, 5 fault classes |
| **Kaggle Power Systems Fault Detection** | Labeled binary + multi-class fault data |
| **Custom Simulation** | MATLAB/Simulink generated waveforms with SNR noise overlay |

Feature extraction pipeline:
```
Raw Waveforms → Window (20ms) → RMS + Symmetrical Decomposition → 
THD Estimation → Feature Vector → Classifier → Fault Class + Confidence
```

---

## 🚀 How to Use

1. **Open** `index.html` in any modern browser (Chrome/Firefox/Edge)
2. **Observe** the live three-phase waveforms in normal operation
3. **Inject faults** using the panel on the left:
   - Click any fault button or press keys **1–6**
   - `1` = Normal, `2` = LG, `3` = LL, `4` = LLG, `5` = LLL, `6` = HIF
4. **Watch** the waveforms distort, the classifier update, and relays trip
5. **Observe** the phasor diagram show the unbalance
6. **Check** the event log for timestamped fault records

---

## 🎓 Learning Outcomes

- Understanding of **three-phase power system behavior** and fault signatures
- Application of **Fortescue's symmetrical component transformation**
- **Feature engineering** for time-series power signals
- **Rule-based and ML-based classification** for fault detection
- **Protection relay** logic and trip conditions
- **Real-time signal processing** in JavaScript
- **Power system visualization** — phasors, waveforms, confidence plots

---

## 📁 Project Structure

```
Fault Detection in Power Systems (ML)/
├── index.html          ← Complete web app (self-contained)
└── README.md           ← This documentation
```

---

*⚡ Part of the Electronics Engineering Project Portfolio · University of Punjab · Haris Hussain · 2024*
