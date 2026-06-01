# 〜 Signal Processing Analyzer

> **Project 8.2 — Electronics Engineering Portfolio**
> *FFT · Digital Filters · Noise Removal · Frequency Spectrum · Waterfall Spectrogram*

[![Status](https://img.shields.io/badge/Status-Live%20Demo-brightgreen?style=flat-square)]()
[![Tech](https://img.shields.io/badge/Tech-HTML%20%2F%20CSS%20%2F%20JS-blue?style=flat-square)]()
[![DSP](https://img.shields.io/badge/DSP-FFT%20%2F%20Biquad%20IIR-cyan?style=flat-square)]()
[![Domain](https://img.shields.io/badge/Domain-Signal%20Processing-purple?style=flat-square)]()

---

## 🔬 Overview

A **fully browser-based digital signal processing analyzer** that generates, filters, and visualizes signals in real-time. Implements FFT from scratch (Cooley-Tukey), cascaded biquad IIR filters (Butterworth topology), and a live waterfall spectrogram — all in pure JavaScript with zero dependencies except Chart.js.

---

## 🚀 Features

| Feature | Description |
|---|---|
| **6 Signal Sources** | Sine · Square · Sawtooth · Triangle · Chirp · Pure Noise |
| **Harmonic Control** | Toggle 2nd & 3rd harmonics to study THD |
| **4 Filter Types** | Low-Pass · High-Pass · Band-Pass · Notch (Butterworth IIR, 1–8th order) |
| **Time Domain** | Oscilloscope-style raw vs filtered waveform overlay |
| **FFT Spectrum** | Real-time frequency spectrum with noise floor line |
| **Before/After** | Side-by-side waveform + frequency comparison |
| **Waterfall Spectrogram** | Live pseudo-color 2D time-frequency display |
| **Peak Detection** | Auto-detects dominant frequency peaks with dB labels |
| **Live Metrics** | Peak Freq, Peak Power, SNR, THD, Bandwidth, Noise Floor |
| **Export** | Download waveform or FFT data as `.csv` |

---

## 🎛️ How to Use

```bash
# No installation needed
open index.html
```

1. **Pick a signal** source (sine, square, chirp…)
2. **Tune** frequency, amplitude, and noise level
3. **Enable harmonics** to study distortion
4. **Apply a filter** (LPF, HPF, BPF, Notch) and adjust cutoff + order
5. **Switch tabs** — Time Domain → Spectrum → Before/After → Spectrogram
6. **Export** the data for MATLAB/Python post-processing

---

## 🔢 DSP Algorithms

### FFT (Cooley-Tukey)
```
DFT:  X[k] = Σ x[n]·e^{−j2πkn/N},  n=0..N-1
FFT:  O(N log₂N) divide-and-conquer, bit-reversal permutation
Window: Hanning  w[n] = 0.5·(1 − cos(2πn/(N−1)))
```

### Butterworth Biquad IIR (Bilinear Transform)
```
H(s) = 1 / (s² + s/Q + 1)   (LPF prototype)
K = tan(πfc/fs)

LPF coefficients:
  b0=b2=K²/D,  b1=2b0,  a1=2(K²-1)/D,  a2=(1-K/Q+K²)/D
  where D = 1 + K/Q + K²

Cascaded stages for N-th order:  stages = N/2
```

### SNR
```
SNR (dB) = 10·log₁₀(P_signal / P_noise)
```

### THD (Total Harmonic Distortion)
```
THD (%) = 100 · √(P₂ + P₃ + …) / P₁
```

---

## 🛠️ Tech Stack

| Tool | Role |
|------|------|
| HTML5 + CSS3 | Dark-mode glassmorphism UI, scanline animation |
| Vanilla JavaScript | Custom FFT, IIR filter engine, signal generator |
| Chart.js 4 | Time domain, spectrum, comparison charts |
| Canvas API | Waterfall spectrogram (pseudo-color rendering) |
| Google Fonts | Orbitron + Inter + JetBrains Mono |

---

## 📊 Key Learning Outcomes

- ✅ Fast Fourier Transform (Cooley-Tukey algorithm)
- ✅ Window functions and spectral leakage reduction
- ✅ IIR Butterworth filter design (bilinear transform method)
- ✅ Filter order trade-off: roll-off vs computational cost
- ✅ SNR, THD, and noise floor measurement
- ✅ Spectrogram / waterfall analysis for non-stationary signals

---

## 👨‍💻 Author

**Haris Hussain**
Space Science · University of the Punjab, Lahore
Electronics Engineering Portfolio — Project 8.2
