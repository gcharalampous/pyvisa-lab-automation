"""
laser_sweep.py

Handles sweeping the tunable laser using Agilent 8164.
"""
from instruments.laser_base import BaseLaserSource
from tqdm import tqdm
import numpy as np
import time
from typing import List, Tuple

def perform_laser_sweep(
    laser: BaseLaserSource,
    start_wl: float = 1.549,
    stop_wl: float = 1.551,
    step: float = 0.01,
    delay: float = 0.1,
    logger=None
) -> Tuple[Tuple[str, str], List[Tuple[float, float]]]:
    """
    Sweep the laser wavelength from `start_wl` to `stop_wl` in steps of `step` nm.

    For each wavelength, set the laser, measure the output power, and optionally log the result.
    Progress is shown with a progress bar. Returns a tuple containing column headers and a list
    of (wavelength, power) measurement tuples.

    Args:
        laser (BaseLaser): Laser instrument object.
        start_wl (float): Starting wavelength in nm.
        stop_wl (float): Ending wavelength in nm.
        step (float): Wavelength increment in nm.
        delay (float): Delay in seconds between measurements.
        logger (optional): Logger for measurement info.

    Returns:
        Tuple[Tuple[str, str], List[Tuple[float, float]]]: 
            - Column headers ("Wavelength (nm)", "Power (dBm)")
            - List of (wavelength, power) tuples.

    Raises:
        Exception: Propagates exceptions from laser control or measurement.
    """
    try:
        laser.initialize()
        results = []
        wavelengths = np.arange(start_wl, stop_wl + step / 2, step)
        pbar = tqdm(total=len(wavelengths), desc=f"Sweeping {start_wl:.3f} → {stop_wl:.3f} nm", unit="nm")
        
        for wl in wavelengths:
            laser.set_wavelength(wl)
            power = laser.measure_power()
            if logger:
                logger.info(f"Wavelength: {wl:.3f} nm, Power: {power:.3f} dBm")
            results.append((wl, power))
            time.sleep(delay)
            pbar.update(1)


        pbar.close()
        return ("Wavelength (nm)", "Power (dBm)"), results
    finally:
        laser.turn_off()

