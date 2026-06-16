# PCB Thermal Heatmap Simulator

Status: **Planned rebuild**

## Purpose

Build a small PCB thermal awareness project that shows how heat can spread across a circuit board and why component placement matters. This is not a replacement for professional thermal simulation; it is an entry-level learning tool.

## Engineering Skills To Show

- Power dissipation awareness
- Thermal hotspot identification
- PCB layout thinking
- Grid-based simulation
- Boundary conditions
- Design tradeoffs between component placement and temperature rise

## First Version Scope

Minimum features:

- Display a simple rectangular PCB grid
- Add components with power values
- Estimate local heat contribution
- Generate a color heatmap
- Mark the hottest point on the board
- Show a basic "safe/warning/hot" status

## Evidence To Capture

- Screenshot of a board with one heat source
- Screenshot of multiple heat sources
- Short explanation of why hotspots form
- Note about project limitations

## Entry-Level Job Value

This project supports electronics design assistant, hardware support, and PCB learning roles. It shows awareness that electronics design is not only schematic logic; heat, placement, and reliability also matter.

## Build Files To Add Later

```text
PCB Thermal Heatmap Simulator/
|-- README.md
|-- index.html
|-- screenshots/
|-- examples/
```

## Next Step

Create the board grid and one adjustable heat source. Add multiple components after the first heatmap works.
