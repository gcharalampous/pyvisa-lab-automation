# PyVISA Lab Automation

A modular Python toolkit for automating photonics and electronics lab instrumentation using PyVISA.

## Overview

This project provides a unified and extensible interface to control laboratory instruments frequently used in silicon photonics test setups. Built around the PyVISA library, it enables fast prototyping, streamlined data collection, and measurement automation via scripting or notebooks.


## Features

- PyVISA-based SCPI instrument abstraction
- Modular, object-oriented design for easy extensibility
- Predefined routines: IV sweeps, laser wavelength sweeps, LIV measurements
- YAML-based configuration support
- Integration with Jupyter notebooks
- GPIB communication supported



## Measurement Notebooks

| Notebook File | Description |
|---------------|-------------|
| [`mzi_phase_shifter.ipynb`](./mzi_phase_shifter.ipynb) | Measures transmission of an MZI phase shifter using laser sweep and powermeter readout. |
| [`ring_resonator.ipynb`](./ring_resonator.ipynb) | Sweeps wavelength across a ring resonator and logs optical power response. |

---

## Shared Components

| Folder | Description |
|--------|-------------|
| `instruments/` | Instrument drivers (Keithley, laser source, powermeter, etc.) |
| `utils/`       | Common utilities for plotting, logging, sweeping, etc. |
| `config/`      | Device-specific YAML config files |
| `results/`     | Automatically saved CSVs, logs, and plots |

---

## Dependencies

Install via pip:
```bash
pip install -r requirements.txt
```


---

## Getting Started

1. Connect your instruments.
2. Click on the notebook corresponding to the device you want to measure.
3. Modify config parameters as needed.
4. Run the notebook.

---

## License

MIT License

