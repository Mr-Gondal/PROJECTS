# Electronics & Engineering Portfolio Projects
### Haris Hussain — GIS Analyst | Space Science | Python Developer

---

---

# 1. Circuit Simulator Dashboard

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-free-orange) ![Status](https://img.shields.io/badge/Status-Portfolio%20Project-green)

## Overview
An interactive web-based circuit simulator that models basic electronic components — resistors, capacitors, and inductors — and visualizes voltage/current waveforms in real time.

## Features
- Simulate series and parallel RC, RL, and RLC circuits
- Plot voltage and current waveforms using Plotly
- Adjust component values via sliders and see live updates
- Calculate impedance, resonance frequency, and phase angle
- Export waveform data as CSV

## Tech Stack
| Tool | Purpose |
|------|---------|
| Python | Core logic and calculations |
| NumPy | Signal mathematics |
| SciPy | Circuit equation solving |
| Plotly | Interactive waveform charts |
| Streamlit | Web dashboard UI |
| Schemdraw | Circuit diagram rendering |

## Installation
```bash
pip install streamlit numpy scipy plotly schemdraw
streamlit run circuit_simulator.py
```

## How It Works
1. User selects circuit type (RC / RL / RLC)
2. Inputs component values (R in Ω, C in μF, L in mH)
3. App solves differential equations using SciPy
4. Waveforms rendered live with Plotly

## Learning Outcomes
- Understanding of transient and steady-state circuit behavior
- Hands-on with impedance and frequency response
- Python-based scientific computing workflow

---

---

# 2. Signal Processing Analyzer

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![SciPy](https://img.shields.io/badge/SciPy-free-brightgreen) ![Status](https://img.shields.io/badge/Status-Portfolio%20Project-green)

## Overview
A signal processing tool that applies Fast Fourier Transform (FFT), digital filters, and noise removal to audio or sensor data — a core skill in electronics and communications engineering.

## Features
- Load audio (.wav) or synthetic sensor signal data
- Visualize raw signal in time domain
- Perform FFT and display frequency spectrum
- Apply low-pass, high-pass, and band-pass filters
- Compare before/after filtering side by side
- Detect dominant frequencies automatically

## Tech Stack
| Tool | Purpose |
|------|---------|
| Python | Core processing |
| SciPy | FFT and digital filtering |
| NumPy | Signal array operations |
| Matplotlib | Time and frequency plots |
| Streamlit | Interactive UI |

## Installation
```bash
pip install numpy scipy matplotlib streamlit
streamlit run signal_analyzer.py
```

## Sample Use Cases
- Remove noise from a sensor data stream
- Identify dominant frequency in a vibration signal
- Visualize audio frequency spectrum

## Learning Outcomes
- Fourier analysis and frequency domain understanding
- Digital filter design (Butterworth, Chebyshev)
- Real-world signal denoising techniques

---

---

# 3. PCB Thermal Heatmap Simulator

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![NumPy](https://img.shields.io/badge/NumPy-free-blue) ![Status](https://img.shields.io/badge/Status-Portfolio%20Project-green)

## Overview
Simulates heat distribution across a printed circuit board (PCB) layout using the finite difference method. Identifies thermal hotspots that could damage components — a critical task in electronics hardware design.

## Features
- Define custom PCB grid with heat-generating components
- Simulate steady-state thermal diffusion using finite differences
- Visualize temperature distribution as a color heatmap
- Mark hotspot zones above a user-defined threshold
- Adjust material thermal conductivity and boundary conditions

## Tech Stack
| Tool | Purpose |
|------|---------|
| Python | Simulation logic |
| NumPy | Grid-based finite difference computation |
| Matplotlib | Heatmap and contour visualization |
| Streamlit | Interactive parameter input UI |

## Installation
```bash
pip install numpy matplotlib streamlit
streamlit run pcb_thermal.py
```

## How It Works
```
PCB Grid → Place heat sources → Solve heat equation iteratively → Render heatmap
```
The heat equation `∇²T = 0` is solved iteratively using Gauss-Seidel relaxation over a 2D grid.

## Learning Outcomes
- Finite difference method for solving PDEs
- Thermal management principles in PCB design
- Scientific visualization with Matplotlib

---

---

# 4. Digital Modulation Visualizer

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Communications](https://img.shields.io/badge/Domain-RF%20%26%20Comms-purple) ![Status](https://img.shields.io/badge/Status-Portfolio%20Project-green)

## Overview
Simulates and visualizes digital modulation and demodulation schemes — AM, FM, PSK, and QAM — complete with constellation diagrams and Bit Error Rate (BER) analysis under AWGN noise.

## Features
- Simulate modulation schemes: AM, FM, BPSK, QPSK, 16-QAM
- Visualize modulated waveform in time domain
- Plot IQ constellation diagrams
- Add Gaussian noise (AWGN) and observe signal degradation
- Calculate and plot Bit Error Rate (BER) vs SNR curve
- Side-by-side comparison of modulation schemes

## Tech Stack
| Tool | Purpose |
|------|---------|
| Python | Core modulation logic |
| NumPy | Complex baseband signal math |
| Matplotlib | Waveform and constellation plots |
| Streamlit | Interactive scheme selector and SNR slider |

## Installation
```bash
pip install numpy matplotlib streamlit
streamlit run modulation_visualizer.py
```

## Key Concepts Demonstrated
- In-phase (I) and quadrature (Q) signal representation
- Noise immunity and bandwidth efficiency trade-offs
- BER degradation at low SNR

## Learning Outcomes
- Deep understanding of digital communications fundamentals
- Practical RF signal simulation
- Relevant to satellite and wireless communications engineering

---

---

# 5. Satellite Link Budget Calculator

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Space Science](https://img.shields.io/badge/Domain-Space%20Science-darkblue) ![Status](https://img.shields.io/badge/Status-Portfolio%20Project-green)

## Overview
An engineering tool that calculates the end-to-end signal budget for a satellite communication link — from transmitter to receiver — computing path loss, SNR, and link margin. Built at the intersection of Space Science and RF engineering.

## Features
- Input transmitter power, frequency, antenna gains, and distances
- Calculate Free Space Path Loss (FSPL) using Friis equation
- Compute EIRP, received power, noise floor, and SNR
- Evaluate link margin with pass/fail indication
- Support for LEO, MEO, and GEO orbit distances
- Generate a formatted link budget report (PDF/CSV)

## Tech Stack
| Tool | Purpose |
|------|---------|
| Python | Engineering calculations |
| NumPy | dB and linear unit conversions |
| Streamlit | Interactive parameter input |
| Plotly | SNR vs distance sensitivity plots |
| ReportLab | PDF budget report export |

## Installation
```bash
pip install numpy streamlit plotly reportlab
streamlit run link_budget.py
```

## Key Equations Used
```
FSPL (dB) = 20·log10(d) + 20·log10(f) + 20·log10(4π/c)
SNR = EIRP + Gr - FSPL - k·T·B (all in dB)
Link Margin = SNR - Required SNR threshold
```

## Learning Outcomes
- Satellite communication system design fundamentals
- RF link analysis and antenna engineering
- Bridging Space Science background with electronics

---

---

# 6. Arduino / ESP32 Circuit Simulator (Wokwi)

![Wokwi](https://img.shields.io/badge/Platform-Wokwi%20Free-red) ![C++](https://img.shields.io/badge/Language-C%2B%2B-blue) ![Status](https://img.shields.io/badge/Status-Portfolio%20Project-green)

## Overview
A collection of browser-simulated Arduino/ESP32 circuits built on the free Wokwi platform. Covers core embedded systems concepts — sensor reading, display output, PWM control, and serial communication — all with fully functional firmware code.

## Simulated Projects

| # | Circuit | Description |
|---|---------|-------------|
| 1 | Temperature Monitor | DHT22 sensor → LCD display with alert LED |
| 2 | Traffic Light Controller | Timed LED sequence with pedestrian button interrupt |
| 3 | PWM Motor Speed Control | Potentiometer-controlled DC motor via PWM |
| 4 | Ultrasonic Distance Meter | HC-SR04 → Serial monitor + buzzer alert |
| 5 | GPS Data Logger | GPS module parsing NMEA sentences → SD card |

## Tech Stack
| Tool | Purpose |
|------|---------|
| Wokwi | Free browser-based circuit + firmware simulator |
| C++ (Arduino) | Embedded firmware code |
| GitHub | Code and circuit JSON storage |

## How to Run
1. Visit [wokwi.com](https://wokwi.com) — no account needed for basic use
2. Open the `diagram.json` + `sketch.ino` files from this repo
3. Click the Play button to simulate

## File Structure
```
wokwi-projects/
├── temperature-monitor/
│   ├── sketch.ino
│   └── diagram.json
├── traffic-light/
│   ├── sketch.ino
│   └── diagram.json
...
```

## Learning Outcomes
- Embedded C++ programming fundamentals
- Sensor interfacing and hardware protocols (I2C, SPI, UART)
- Real-world microcontroller project structure

---

---

# 7. IoT Sensor Data Dashboard

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![IoT](https://img.shields.io/badge/Domain-IoT-teal) ![Status](https://img.shields.io/badge/Status-Portfolio%20Project-green)

## Overview
Simulates a real-time IoT sensor network — temperature, humidity, air pressure, and GPS location — and streams data into a live monitoring dashboard with threshold alerts and historical trend analysis.

## Features
- Simulated sensor streams (no hardware needed)
- Real-time data ingestion and display
- Line charts for temperature, humidity, and pressure trends
- Map-based GPS track visualization using Folium
- Anomaly detection with color-coded alert system
- Export sensor logs to CSV

## Tech Stack
| Tool | Purpose |
|------|---------|
| Python | Sensor simulation and data logic |
| Streamlit | Live-updating dashboard |
| Pandas | Time-series data management |
| Plotly | Real-time trend charts |
| Folium | GPS track map |
| NumPy | Sensor noise simulation |

## Installation
```bash
pip install streamlit pandas plotly folium numpy
streamlit run iot_dashboard.py
```

## Sensor Simulation Model
```python
# Temperature with realistic noise
temperature = 25 + 5 * np.sin(t / 50) + np.random.normal(0, 0.3)
humidity    = 60 + 10 * np.cos(t / 70) + np.random.normal(0, 1.0)
```

## Learning Outcomes
- IoT architecture and data pipeline design
- Real-time dashboard development
- Sensor data modeling and anomaly detection

---

---

# 8. Fault Detection in Power Systems (ML)

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Machine Learning](https://img.shields.io/badge/ML-Random%20Forest-orange) ![Status](https://img.shields.io/badge/Status-Portfolio%20Project-green)

## Overview
A machine learning model that classifies electrical faults in power transmission lines using current and voltage measurements. Detects fault types (LG, LL, LLG, LLL) using Random Forest and LSTM models trained on the IEEE power systems dataset from Kaggle.

## Features
- Binary fault detection (fault / no fault)
- Multi-class fault type classification (LG, LL, LLG, LLL faults)
- Feature importance visualization
- Confusion matrix and classification report
- LSTM-based time-series fault detection
- Interactive prediction interface

## Tech Stack
| Tool | Purpose |
|------|---------|
| Python | Core ML pipeline |
| Scikit-learn | Random Forest classifier |
| TensorFlow / Keras | LSTM time-series model |
| Pandas | Data preprocessing |
| Matplotlib / Seaborn | Evaluation plots |
| Google Colab | Free GPU training environment |

## Dataset
- **Source**: [Kaggle — Electrical Fault Detection Dataset](https://www.kaggle.com/)
- **Features**: Ia, Ib, Ic (phase currents), Va, Vb, Vc (phase voltages)
- **Labels**: Normal, LG Fault, LL Fault, LLG Fault, LLL Fault

## Installation
```bash
pip install scikit-learn tensorflow pandas matplotlib seaborn
```

## Model Performance
| Model | Accuracy |
|-------|----------|
| Random Forest | ~97% |
| LSTM | ~95% |

## Learning Outcomes
- Power systems fundamentals (faults, protection)
- Supervised classification for engineering applications
- Time-series modeling with LSTM

---

---

# 9. Electronic Component Image Classifier

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Deep Learning](https://img.shields.io/badge/Deep%20Learning-CNN-red) ![Status](https://img.shields.io/badge/Status-Portfolio%20Project-green)

## Overview
A Convolutional Neural Network (CNN) trained to identify electronic components — resistors, capacitors, inductors, ICs, transistors, and LEDs — from images. Demonstrates the intersection of computer vision and electronics engineering.

## Features
- Classifies 6+ component types from images
- Transfer learning with MobileNetV2 (pre-trained on ImageNet)
- Upload any component photo and get instant prediction
- Confidence score bar chart for all classes
- Training accuracy and loss curves visualization

## Tech Stack
| Tool | Purpose |
|------|---------|
| Python | Core pipeline |
| TensorFlow / Keras | CNN model training |
| MobileNetV2 | Transfer learning base model |
| OpenCV | Image preprocessing |
| Streamlit | Upload and prediction UI |
| Google Colab | Free GPU for training |

## Dataset
- **Source**: Scraped from open image datasets + Kaggle
- **Classes**: Resistor, Capacitor, Inductor, IC Chip, Transistor, LED
- **Size**: ~500–1000 images per class

## Installation
```bash
pip install tensorflow opencv-python streamlit numpy pillow
streamlit run component_classifier.py
```

## Model Architecture
```
Input (224x224x3)
→ MobileNetV2 (frozen base)
→ GlobalAveragePooling2D
→ Dense(128, relu)
→ Dropout(0.3)
→ Dense(6, softmax)
```

## Learning Outcomes
- Transfer learning and CNN fine-tuning
- Computer vision applied to electronics
- Practical image classification pipeline

---

---

## Summary Table

| # | Project | Domain | Tools | Difficulty |
|---|---------|--------|-------|-----------|
| 1 | Circuit Simulator Dashboard | Electronics | Python, Streamlit, SciPy | ⭐⭐ |
| 2 | Signal Processing Analyzer | Electronics / DSP | Python, SciPy, NumPy | ⭐⭐ |
| 3 | PCB Thermal Heatmap | Electronics / Hardware | Python, NumPy | ⭐⭐⭐ |
| 4 | Digital Modulation Visualizer | RF / Communications | Python, NumPy | ⭐⭐⭐ |
| 5 | Satellite Link Budget Calculator | Space Science / RF | Python, Streamlit | ⭐⭐ |
| 6 | Arduino Simulator (Wokwi) | Embedded Systems | C++, Wokwi | ⭐⭐ |
| 7 | IoT Sensor Dashboard | IoT / Software | Python, Streamlit | ⭐⭐ |
| 8 | Fault Detection in Power Systems | Power Engineering / ML | Python, Sklearn, LSTM | ⭐⭐⭐ |
| 9 | Component Image Classifier | Computer Vision / Electronics | Python, TensorFlow | ⭐⭐⭐ |

---

*All projects are 100% free to build — no paid tools, APIs, or hardware required.*
*Built by Haris Hussain | Space Science, University of the Punjab, Lahore*
