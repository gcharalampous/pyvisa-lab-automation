"""
laser_sweep.py

Handles sweeping the tunable laser using Agilent 8164.
"""
from instruments.laser_base import BaseLaserSource
from instruments.power_base import BasePowerMeter
from tqdm.auto import tqdm
import numpy as np
import time
import sys
from typing import List, Tuple

def perform_laser_sweep(
    laser: BaseLaserSource,
    powermeter: BasePowerMeter,
    start_wl: float = 1.549,
    stop_wl: float = 1.551,
    step: float = 0.01,
    delay: float = 0.1,
    verbose_wavelength_updates: bool = False,
) -> Tuple[Tuple[str, str], List[Tuple[float, float]]]:
    """
    Sweep the laser wavelength from `start_wl` to `stop_wl` in steps of `step` nm.

    For each wavelength, set the laser, measure the output power, and optionally log the result.
    Progress is shown with a progress bar. Returns a tuple containing column headers and a list
    of (wavelength, power) measurement tuples.

    Args:
        laser (BaseLaser): Laser instrument object.
        powermeter (BasePowerMeter): Power meter instrument object.
        start_wl (float): Starting wavelength in nm.
        stop_wl (float): Ending wavelength in nm.
        step (float): Wavelength increment in nm.
        delay (float): Delay in seconds between measurements.
        verbose_wavelength_updates (bool): If True, logs each wavelength set at INFO level.

    Returns:
        Tuple[Tuple[str, str], List[Tuple[float, float]]]: 
            - Column headers ("Wavelength (nm)", "Power (dBm)")
            - List of (wavelength, power) tuples.

    Raises:
        Exception: Propagates exceptions from laser control or measurement.
    """
    try:
        laser.initialize()
        laser.turn_on()
        results = []
        wavelengths = np.arange(start_wl, stop_wl + step / 2, step)
        pbar = tqdm(
            total=len(wavelengths),
            desc=f"Sweeping {start_wl:.3f} → {stop_wl:.3f} nm",
            unit="nm",
            file=sys.stdout,
            dynamic_ncols=True,
            leave=True,
        )
        
        for wl in wavelengths:
            laser.set_wavelength(wl, verbose=verbose_wavelength_updates)
            power = powermeter.measure_power()
            results.append((wl, power))
            time.sleep(delay)
            pbar.update(1)


        pbar.close()
        return ("Wavelength (nm)", "Power (dBm)"), results
    finally:
        laser.turn_off()

