"""
sourcemeter_sweep.py

Handles sweeping the sourcemeter voltage
"""
from instruments.sourcemeter_base import BaseSourceMeter
from instruments.power_base import BasePowerMeter
from instruments.laser_base import BaseLaserSource
from tqdm import tqdm
import numpy as np
import time
from typing import List, Tuple


def measure_iv_curve(
    sourcemeter: BaseSourceMeter,
    start_v: float = -1.0,
    stop_v: float = 1.0,
    step: float = 0.01,
    measure_current_range: float = 1E-3,
    current_limit: float = 0.01,
    wire_mode: int = 2,
    delay: float = 0.1,
    logger=None
) -> Tuple[Tuple[str, str], List[Tuple[float, float]]]:

    try:
        if not sourcemeter.connected:
            raise RuntimeError("Cannot perform sweep: Instrument not connected.")
    
    
        sourcemeter.initialize(wire_mode=wire_mode)
        results = []
        voltages = np.arange(start_v, stop_v + step, step)
        pbar = tqdm(total=len(voltages), desc=f"Sweeping {start_v:.3f} → {stop_v:.3f} V", unit="V")

        
        for i, v in enumerate(voltages):
            
            read_current = sourcemeter.source_voltage_and_read_current(source_voltage_level=v,
                source_voltage_range=np.abs(stop_v - start_v) + np.abs(step),
                measure_current_range=measure_current_range,  # Adjust as needed
                current_limit=current_limit,  # Adjust as needed
                delay=delay
           )
            
            if logger:
                logger.info(f"Voltage: {v:.3f} V, Current: {read_current:.3f} A")
            results.append((v, read_current))
            

            pbar.update(1)

        pbar.close()

        return (("Voltage (V)", "Current (A)"), results)
    finally:
        sourcemeter.turn_off()



def measure_liv_curve(
    sourcemeter: BaseSourceMeter,
    powermeter: BasePowerMeter,
    laser: BaseLaserSource,
    start_v: float = -1.0,
    stop_v: float = 1.0,
    step: float = 0.01,
    measure_current_range: float = 1E-3,
    current_limit: float = 0.01,
    wire_mode: int = 2,
    center_wavelength: float = 1550.0,  # Wavelength in nm
    sourcemeter_delay: float = 0.1,
    powermeter_delay: float = 0.1,
    logger=None
) -> Tuple[Tuple[str, str, str], List[Tuple[float, float, float]]]:

    try:
        if not sourcemeter.connected:
            raise RuntimeError("Cannot perform sweep: Instrument not connected.")
        if not powermeter.connected:
            raise RuntimeError("Cannot perform sweep: Power meter not connected.")
        if not laser.connected:
            raise RuntimeError("Cannot perform sweep: Laser not connected.")
    
    
        sourcemeter.initialize(wire_mode=wire_mode)
        laser.initialize()
        laser.set_wavelength(center_wavelength)  # Set wavelength to 1550 nm, adjust as needed
        # powermeter.initialize()
        results = []
        voltages = np.arange(start_v, stop_v + step, step)
        pbar = tqdm(total=len(voltages), desc=f"Sweeping {start_v:.3f} → {stop_v:.3f} V", unit="V")

        
        for i, v in enumerate(voltages):
            
            read_current = sourcemeter.source_voltage_and_read_current(source_voltage_level=v,
                source_voltage_range=np.abs(stop_v - start_v) + np.abs(step),
                measure_current_range=measure_current_range,  # Adjust as needed
                current_limit=current_limit,  # Adjust as needed
                delay=sourcemeter_delay
           )
            time.sleep(powermeter_delay)
            read_optical_power = powermeter.measure_power()  # Measure optical power
            
            if logger:
                logger.info(f"Voltage: {v:.3f} V, Current: {read_current:.3f} A, Optical Power: {read_optical_power:.3f} dBm")
            results.append((v, read_current, read_optical_power))
            

            pbar.update(1)

        pbar.close()

        return (("Voltage (V)", "Current (A)", "Optical Power (dBm)"), results)
    finally:
        sourcemeter.turn_off()
        
        
        
def measure_laser_liv_curve_by_source_current(
    sourcemeter: BaseSourceMeter,
    powermeter: BasePowerMeter,
    start_current: float = 10e-6,
    stop_current: float = 100e-6,
    step_current: float = 10e-6,
    measure_voltage_range: float = 1E-3,
    voltage_limit: float = 0.01,
    wire_mode: int = 2,
    center_wavelength: float = 1550.0,  # Wavelength in nm
    sourcemeter_delay: float = 0.1,
    powermeter_delay: float = 0.1,
    logger=None
) -> Tuple[Tuple[str, str, str], List[Tuple[float, float, float]]]:

    try:
        if not sourcemeter.connected:
            raise RuntimeError("Cannot perform sweep: Instrument not connected.")
        if not powermeter.connected:
            raise RuntimeError("Cannot perform sweep: Power meter not connected.")
            
    
        sourcemeter.initialize(wire_mode=wire_mode)
        powermeter.initialize()
        # laser.set_wavelength(center_wavelength)  # Set wavelength to 1550 nm, adjust as needed
        results = []
        currents = np.arange(start_current, stop_current + step_current, step_current)
        pbar = tqdm(total=len(currents), desc=f"Sweeping {start_current:.3f} → {stop_current:.3f} A", unit="A")

        
        for i, cur in enumerate(currents):
            
            read_voltage = sourcemeter.source_current_and_read_voltage(source_current_level=cur,
                source_current_range=np.abs(stop_current - start_current) + np.abs(step_current),
                measure_voltage_range=measure_voltage_range,  # Adjust as needed
                voltage_limit=voltage_limit,  # Adjust as needed
                delay=sourcemeter_delay
           )
            time.sleep(powermeter_delay)
            read_optical_power = powermeter.measure_power()  # Measure optical power
            
            if logger:
                logger.info(f"Voltage: {read_voltage:.3f} V, Current: {cur:.3f} A, Optical Power: {read_optical_power:.3f} dBm")
            results.append((read_voltage, cur, read_optical_power))

            pbar.update(1)

        pbar.close()

        return (("Voltage (V)", "Current (A)", "Optical Power (dBm)"), results)
    finally:
        sourcemeter.turn_off()
