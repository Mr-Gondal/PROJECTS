# 🔥 PCB Thermal Heatmap Simulator

**Project 8.3 · Electronics Engineering Portfolio**

> An interactive, browser-based PCB thermal analysis tool that simulates real-time 2D heat diffusion across a printed circuit board using the finite difference method (Gauss-Seidel relaxation). Place components, observe thermal gradients evolve, detect hotspots, and export professional heatmaps — all with zero backend required.

---

## 📸 Features at a Glance

| Feature | Description |
|---|---|
| 🖼 **Interactive PCB Grid** | 30×20 clickable canvas grid. Left-click places components; right-click removes them |
| 🌡 **Real-Time Heat Diffusion** | Gauss-Seidel 2D finite difference with 100 iterations/frame, running continuously |
| 🎨 **Pseudo-Color Heatmap** | 7-stop color gradient (cool blue → cyan → green → yellow → orange → red → white) |
| ⚠️ **Hotspot Detection** | User-defined threshold slider; cells above threshold get animated pulsing red border |
| 🧩 **Component Presets** | CPU (3×3 high), MOSFET (2×2 medium), Resistor/LED (1×1 low), Heat Source |
| 🎛 **Control Panel** | Thermal conductivity, ambient temp, power, threshold sliders; pause/resume; clear |
| 📊 **Live Metrics** | Max, min, average temperature; hotspot count; thermal gradient; iteration counter |
| 🌈 **Color Scale Legend** | Vertical gradient bar with labeled temperature tick marks |
| 📈 **Profile Chart** | Real-time Chart.js line chart of temperature along the center cross-section row |
| 🖱 **Cursor Tooltip** | Exact temperature, cell coordinates, component type, and hotspot status on hover |
| 💾 **PNG Export** | Exports the current heatmap canvas as a timestamped PNG file |
| ✨ **Animations** | Floating heat-wave particles, grid pulse, new-source glow burst, hotspot pulsing |

---

## 🧮 Physics & Mathematics

### Heat Equation (Continuous Form)

The transient 2D heat conduction equation (Fourier's Law):

$$\frac{\partial T}{\partial t} = \alpha \left( \frac{\partial^2 T}{\partial x^2} + \frac{\partial^2 T}{\partial y^2} \right) + \frac{Q}{\rho c_p}$$

Where:
- `T` = temperature field (°C)
- `α = k / (ρ·cₚ)` = thermal diffusivity (m²/s)
- `k` = thermal conductivity (W/m·K)
- `Q` = volumetric heat generation (W/m³)
- `ρ` = density (kg/m³), `cₚ` = specific heat capacity (J/kg·K)

### Finite Difference Discretization (Steady-State)

At steady state `∂T/∂t = 0`, the Laplacian discretizes on a uniform grid (Δx = Δy = h):

$$\frac{T_{i+1,j} - 2T_{i,j} + T_{i-1,j}}{h^2} + \frac{T_{i,j+1} - 2T_{i,j} + T_{i,j-1}}{h^2} = 0$$

Rearranged to the Gauss-Seidel update rule:

$$\boxed{T_{i,j}^{(k+1)} = \frac{T_{i+1,j}^{(k)} + T_{i-1,j}^{(k+1)} + T_{i,j+1}^{(k)} + T_{i,j-1}^{(k+1)}}{4}}$$

### Boundary Conditions

- **Dirichlet (fixed)**: All edges held at ambient temperature `T_ambient`
- **Heat sources**: Fixed-temperature Dirichlet nodes — `T_source = T_ambient + P·R_th`
- **Thermal resistance** approximation: `R_th ∝ 1/k`

### Source Temperature Model

Heat source node temperature is estimated as:

$$T_{\text{source}} = T_{\text{ambient}} + \frac{P \cdot 0.16}{k}$$

Where `P` is component power (W) and `k` is thermal conductivity (W/m·K). The coefficient `0.16` represents a lumped thermal resistance scale factor.

---

## 🛠 Technology Stack

| Layer | Technology | Role |
|---|---|---|
| **Structure** | HTML5 Semantic | Layout and DOM |
| **Styling** | Vanilla CSS3 | Glassmorphism, animations, dark theme |
| **Logic** | Vanilla JavaScript (ES6+) | Simulation engine, event handling |
| **Rendering** | HTML5 Canvas API | PCB heatmap, cell drawing, glow effects |
| **Charting** | Chart.js 4.4 (CDN) | Temperature cross-section line chart |
| **Typography** | Google Fonts | Orbitron, Inter, JetBrains Mono |
| **Backend** | None | 100% client-side, zero dependencies |

---

## 🚀 How to Use

### Getting Started

1. Open `index.html` in any modern browser (Chrome, Firefox, Edge recommended)
2. The simulation starts automatically with the board at ambient temperature
3. Use the **Component Type** dropdown to select a component
4. **Left-click** on the PCB grid to place the selected component
5. Observe thermal gradients diffusing in real time

### Controls Reference

| Action | Result |
|---|---|
| Left-click grid | Place selected component |
| Right-click grid | Remove heat source from cell |
| Click + drag | Paint heat sources (single-cell types) |
| **Thermal Conductivity** slider | Higher k → faster, more uniform diffusion |
| **Ambient Temperature** slider | Sets board baseline temperature |
| **Heat Source Power** slider | Controls source node temperature |
| **Hotspot Threshold** slider | Red-pulse alert threshold |
| **Pause / Resume** button | Freeze or continue simulation |
| **Clear** button | Reset all sources and temperatures |
| **Export PNG** button | Download current heatmap as image |

### Component Power Reference

| Component | Size | Relative Power |
|---|---|---|
| Heat Source | 1×1 | 100% of slider |
| Resistor | 1×1 | 30% |
| LED | 1×1 | 25% |
| MOSFET | 2×2 | 65% per cell |
| CPU | 3×3 | 100% per cell |

### Reading the Display

- **Cool Blue** (`#001aff`) = ≤ 0°C (or very cool regions)
- **Cyan** (`#00e5ff`) = ~10–15°C
- **Green** (`#39ff14`) = ~20–35°C
- **Yellow** (`#ffd700`) = ~40–55°C
- **Orange** (`#ff6b00`) = ~60–75°C
- **Red** (`#ff0000`) = ~80–90°C
- **White** (`#ffffff`) = ≥ 100°C (critical)

Cells with a **pulsing red border** have exceeded the hotspot threshold.

---

## 📐 Design Aesthetic

- **Color Palette**: Deep black `#050a0f` background with neon orange `#ff6b00`, neon red `#ff2244`, and neon yellow `#ffd700` — mirroring real infrared camera imagery
- **Glassmorphism**: Frosted-glass panel cards with subtle backdrop-blur and gradient borders
- **Typography**: Orbitron for headers (futuristic), Inter for body (clean), JetBrains Mono for values (technical)
- **Animations**: Floating heat-wave particles, grid pulse, component glow-burst on placement, hotspot shimmer
- **Responsive**: Three-panel layout adapts for smaller screens

---

## 🎓 Learning Outcomes

After exploring this simulator, students will understand:

1. **Numerical PDE solving** — How continuous differential equations are discretized for computation
2. **Gauss-Seidel iterative methods** — In-place relaxation vs. Jacobi; convergence properties
3. **Thermal management in PCB design** — Why hotspots form, role of thermal conductivity
4. **Boundary conditions** — Dirichlet vs. Neumann conditions in finite-difference grids
5. **Color mapping / scientific visualization** — Mapping scalar fields to perceptually meaningful color gradients
6. **Canvas API rendering** — Efficient per-frame drawing, `ImageData` manipulation
7. **Real-time simulation in JavaScript** — `requestAnimationFrame` loop, performance considerations

---

## 📁 Project Structure

```
PCB Thermal Heatmap Simulator/
├── index.html      ← Complete self-contained app (HTML + CSS + JS)
└── README.md       ← This file
```

---

## 👤 Author

| Field | Details |
|---|---|
| **Name** | Haris Hussain |
| **Program** | Space Science |
| **Institution** | University of Punjab |
| **Project** | 8.3 — PCB Thermal Heatmap Simulator |
| **Category** | Electronics Engineering Portfolio |
| **Stack** | Vanilla HTML/CSS/JS · Canvas API · Chart.js |

---

## 📜 License

This project is created for educational and portfolio purposes.

---

*Built with precision and passion for engineering education.*
