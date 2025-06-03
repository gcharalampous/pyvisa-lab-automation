# pyvisa-lab-automation

A modular Python toolkit for automating photonics lab instrumentation using PyVISA.

## Overview

This project provides a unified and extensible interface to control laboratory instruments frequently used in silicon photonics test setups. Built around the PyVISA library, it enables fast prototyping, streamlined data collection, and measurement automation via scripting or notebooks.

### Supported Instrument Types
- Source meters (e.g., Keithley 2400)
- Optical power meters
- Tunable laser sources
- Lightwave multimeters

## Features

- PyVISA-based SCPI instrument abstraction
- Modular, object-oriented design for easy extensibility
- Predefined routines: IV sweeps, laser wavelength sweeps, LIV measurements
- YAML-based configuration support
- Integration with Jupyter notebooks
- GPIB communication supported

## Project Structure

```
pyvisa-lab-automation/
├── configs/           # YAML configuration files
├── controllers/       # Measurement automation scripts
├── data/              # Raw experimental data
├── instruments/       # Modular instrument drivers
├── plots/             # Auto-generated result visualizations
├── utils/             # Logger, config loader, plot utilities
├── main.ipynb         # Example MZI notebook (consider renaming)
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/gcharalampous/pyvisa-lab-automation.git
cd pyvisa-lab-automation
```

2. (Optional) Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

You can use the toolkit in either Python scripts or Jupyter notebooks.

### Example: Keithley 2400 IV Measurement

```python
from instruments.keithley2400 import Keithley2400SourceMeter

keithley = Keithley2400SourceMeter()
keithley.initialize()
resistance = keithley.read_resistance_configured()
keithley.close()
```

### Jupyter Notebook

The included notebook `main.ipynb` (rename recommended) demonstrates full experiment orchestration using YAML configuration and controller classes.

## Extending the Toolkit

To add support for new instruments:
- Create a new class in `instruments/`, subclassing `SCPIInstrument` or one of the existing abstract base classes like `BaseSourceMeter`.

## License

MIT License – see [`LICENSE`](LICENSE) for details.