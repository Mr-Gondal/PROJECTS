# 📡 Digital Modulation Visualizer
### Project 8.4 — Electronics Engineering Portfolio

> An interactive, browser-based RF signal analyzer and digital modulation visualizer — designed to teach, simulate, and compare AM, FM, BPSK, QPSK, and 16-QAM modulation schemes in real-time.

---

## 🖼️ Preview

Dark mode RF test-equipment aesthetic with glassmorphism panels, animated starfield, neon purple/magenta/gold palette, and a professional status bar — all in a single self-contained HTML file.

---

## ✨ Features

| Feature | Description |
|---|---|
| **5 Modulation Schemes** | AM · FM · BPSK · QPSK · 16-QAM — switchable via tabbed interface |
| **Time Domain Waveform** | Real-time Chart.js line chart of the modulated carrier |
| **Constellation Diagram** | Custom Canvas IQ scatter plot with glowing, color-coded symbols per quadrant |
| **BER vs Eb/N₀ Curve** | Theoretical (dashed) and Monte Carlo simulated BER on a log scale |
| **Frequency Spectrum** | FFT (Cooley-Tukey with Hann window) displayed as a bar chart |
| **AWGN Noise Slider** | 0–30 dB SNR control — spreads constellation, raises BER in real-time |
| **Live Metrics Panel** | Bits/symbol, spectral efficiency, bandwidth, theoretical & simulated BER |
| **Bit Stream Visualizer** | Animated scrolling binary stream with symbol-group color coding |
| **Comparison Mode** | Toggle to overlay BER curves of multiple schemes simultaneously |
| **Educational Tooltips** | Inline explanations for each visualization panel |
| **Professional Status Bar** | Live readout of scheme, SNR, BER, bandwidth efficiency |

---

## 📊 Modulation Scheme Comparison

| Scheme | Bits/Symbol | Spectral Efficiency | BER Formula | Bandwidth | Use Case |
|--------|:-----------:|:-------------------:|:-----------:|-----------|---------|
| **AM** | — | < 1 b/s/Hz | Analog (SNR-based) | 2·f_m | Broadcast radio |
| **FM** | — | < 1 b/s/Hz | Analog (SNR-based) | 2·(f_d + f_m) | FM radio, analog voice |
| **BPSK** | 1 | 1 b/s/Hz | Q(√(2Eb/N₀)) | 2·R_s | Deep space comms, GPS |
| **QPSK** | 2 | 2 b/s/Hz | Q(√(2Eb/N₀)) | 2·R_s | Satellite TV, LTE UL |
| **16-QAM** | 4 | 4 b/s/Hz | (3/8)·erfc(√(4Eb/10N₀)) | 2·R_s | Cable modem, 4G/5G |

> **Key insight**: Higher-order modulation encodes more bits per symbol but requires higher SNR to achieve the same BER. BPSK and QPSK share identical BER formulas because QPSK is two orthogonal BPSK channels.

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Structure** | Semantic HTML5 |
| **Logic** | Vanilla JavaScript (ES2020+) |
| **Charts** | [Chart.js 4.4](https://www.chartjs.org/) via CDN |
| **Constellation** | Custom HTML5 Canvas 2D rendering |
| **FFT** | Cooley-Tukey radix-2 DIT (pure JS) |
| **Fonts** | Google Fonts — Orbitron · Inter · JetBrains Mono |
| **Styling** | Vanilla CSS (glassmorphism, CSS variables, animations) |
| **Deployment** | Zero dependencies — single `index.html` file |

---

## 🚀 How to Use

1. **Open** `index.html` in any modern browser (Chrome, Firefox, Edge, Safari).
2. **Select** a modulation scheme using the tab bar at the top.
3. **Adjust parameters** using the sliders in the side panel (carrier frequency, modulation index, symbol rate, etc.).
4. **Move the SNR slider** to add AWGN noise — watch the constellation spread and BER rise.
5. **Toggle Comparison Mode** to overlay BER curves for multiple schemes.
6. **Observe** the four live panels update in real-time:
   - Time domain waveform
   - IQ constellation diagram
   - BER vs Eb/N₀ curve
   - Frequency spectrum (FFT)

> No installation, no backend, no build step required.

---

## 🧠 Key Concepts

### IQ Representation (In-phase / Quadrature)
Every bandpass signal can be decomposed into two orthogonal components:
- **I (In-phase)**: projection onto cos(2πf_c t)
- **Q (Quadrature)**: projection onto sin(2πf_c t)

The constellation diagram plots I vs Q, showing symbol positions in 2D signal space.

### AWGN (Additive White Gaussian Noise)
Real RF channels add thermal noise modeled as zero-mean Gaussian with variance N₀/2 per dimension. AWGN shifts constellation points from their ideal positions, causing symbol decision errors.

**Model**: r(t) = s(t) + n(t), where n(t) ~ N(0, σ²)

The signal-to-noise ratio is expressed as **Eb/N₀** (energy per bit to noise spectral density), in dB.

### BER (Bit Error Rate)
The probability that a transmitted bit is decoded incorrectly at the receiver.

- **Theoretical BER** is derived analytically from the modulation geometry and the Q-function.
- **Simulated BER** uses Monte Carlo simulation — transmitting thousands of random symbols, adding AWGN, decoding, and counting errors.

The Q-function: Q(x) = (1/2) · erfc(x/√2)

### Bandwidth Efficiency
Also called **spectral efficiency**, measured in bits per second per Hz (b/s/Hz). Higher-order QAM achieves greater spectral efficiency but at the cost of noise immunity.

---

## 📐 Mathematical Details

### AM Signal
s(t) = A_c · [1 + μ·m(t)] · cos(2πf_c t)  
where μ is the modulation index (0 ≤ μ ≤ 1), m(t) is the normalized message.

### FM Signal
s(t) = A_c · cos(2πf_c t + 2πf_d ∫m(τ)dτ)  
where f_d is the frequency deviation. The modulation index β = f_d / f_m.

### BPSK
Symbols: s₀ = A·cos(2πf_c t), s₁ = -A·cos(2πf_c t)  
BER = Q(√(2Eb/N₀))

### QPSK
Symbols at phases 45°, 135°, 225°, 315° — each encodes 2 bits.  
BER = Q(√(2Eb/N₀)) (same as BPSK due to Gray coding)

### 16-QAM
16 symbols on a 4×4 rectangular grid with I,Q ∈ {±1, ±3}.  
BER ≈ (3/8) · erfc(√(4Eb / 10N₀))

---

## 🎓 Learning Outcomes

After using this visualizer, students will be able to:

- [ ] Explain the difference between analog (AM, FM) and digital (PSK, QAM) modulation
- [ ] Interpret constellation diagrams and IQ signal representations
- [ ] Understand how AWGN noise affects symbol detection
- [ ] Compare modulation schemes by spectral efficiency and noise robustness
- [ ] Predict BER performance from the Eb/N₀ operating point
- [ ] Explain the trade-off between data rate and link reliability in RF systems

---

## 👨‍💻 Author

| Field | Details |
|-------|---------|
| **Name** | Haris Hussain |
| **Program** | Space Science |
| **Institution** | University of the Punjab, Lahore |
| **Project** | 8.4 — Digital Modulation Visualizer |
| **Portfolio** | Electronics Engineering Series |
| **Year** | 2025 |

---

## 📁 File Structure

```
Digital Modulation Visualizer/
├── index.html      ← Complete self-contained app (HTML + CSS + JS)
└── README.md       ← This file
```

---

## 📜 License

This project is created for educational and portfolio purposes.  
Free to use, modify, and share with attribution.

---

*Built with vanilla JS, Chart.js, and a love for RF engineering* 📡
