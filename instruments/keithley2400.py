"""
Keithley 2400 SourceMeter Control Class

This module defines a high-level interface for communicating with the Keithley 2400
SourceMeter using SCPI commands via PyVISA. It supports resistance measurements,
voltage sourcing, current readings, and safe instrument shutdown procedures.

Author: Georgios Charalampous
Created: 2025-06-01
Dependencies: pyvisa, numpy, time
"""
import numpy as np
import pyvisa as visa
import time

from instruments.scpi_instrument import SCPIInstrument
from instruments.sourcemeter_base import BaseSourceMeter
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Keithley2400SourceMeter(SCPIInstrument, BaseSourceMeter):
    def __init__(self, address='GPIB0::24::INSTR', suppress_print=False, debug=False, resource_manager=None):
        self.address = address
        self.suppress_print = suppress_print
        self.debug = debug
        self.connected = False
        self.main = None
        self.id = None
        self.rm = resource_manager or visa.ResourceManager()
        self._owns_rm = resource_manager is None
        try:
            self.main = self.rm.open_resource(self.address)
            self.id = self.main.query('*IDN?').strip()
            self.opt = self.main.query('*OPT?').strip()
            self.connected = True
            logger.info(f"Connected to {self.id} at {self.address}")
            logger.info(f"Options: {self.opt}")
        except visa.VisaIOError as e:
            logger.error(f"Error connecting to Keithley2400 at {address}: {e}")
            raise            
        if self.debug:
            self.debug_err()
            
                        
    def initialize(self, wire_mode: int = 2):
        if not self.connected:
            raise RuntimeError("Cannot initialize: Instrument not connected.")
        # self.main.write("*SRE 0")  # Query ID to ensure communication
        self.main.write("*CLS")
        self.main.write("*RST")  # Reset the device
        self.main.write(":OUTP OFF")
        if wire_mode == 2:
            self.main.write(":SYST:RSEN OFF")  # Disable remote sensing
        elif wire_mode == 4:
            self.main.write(":SYST:RSEN ON")
        else:
            raise ValueError("Invalid wire mode. Use 2 for 2-wire or 4 for 4-wire mode.")
        logger.info("Source meter is initialized.")
          
            
    def read_resistance_auto(self, resistance_range: float = 20E3) -> np.ndarray:
        """Measure resistance in ohms using a single-point measurement."""
        if not self.connected:
            raise RuntimeError("Instrument not connected.")
        self.main.write(":SOUR:FUNC VOLT")  # Source voltage
        self.main.write(":SOUR:VOLT 0.1")  # Apply a small voltage to stimulate current
        self.main.write(':SENS:FUNC "RES"')  # Preferred full form
        self.main.write(":SENS:RES:MODE AUTO")  # Set to auto mode
        self.main.write(f":SENS:RES:RANG {resistance_range}")  # Set resistance range
        self.main.write(":FORM:ELEM RES")  # Only return resistance
        self.main.write(":OUTP ON")  # Enable output
        resistance = self.main.query(":READ?")
        self.main.write(":OUTP OFF")  # Disable output after reading
        try:
            # Usually one value, but safely split in case of unexpected formatting
            resistance_values = [float(val) for val in resistance.strip().split(',') if val]
            return np.array(resistance_values)
        except ValueError:
            raise ValueError(f"Could not parse resistance value from: {resistance}")
    
    
    def read_resistance_configured(self,
                                resistance_range: float = 20E3,
                                mode: str = "AUTO",
                                offset_comp: str = "OFF",
                                voltage_prot: float = 2.0,
                                current_prot: float = 0.01,
                                source_func: str = "VOLT",
                                source_level: float = 0.05,
                                wire_mode: int = 2,
                                delay: float = 0.1) -> np.ndarray:
        if not self.connected:
            raise RuntimeError("Instrument not connected.")
        
        if mode == "AUTO":
            res_auto = self.read_resistance_auto(resistance_range)
            return res_auto
        
        
        self.main.write(f":SENS:RES:RANG {resistance_range}")
        self.main.write(f":SENS:RES:MODE {mode}")
        self.main.write(f":SENS:RES:OCOM {offset_comp}")
        self.main.write(f":SENS:VOLT:PROT {voltage_prot}")
        self.main.write(f":SENS:CURR:PROT {current_prot}")
        self.main.write(f":SOUR:FUNC {source_func}")

        if source_func.upper() == "VOLT":
            self.main.write(f":SOUR:VOLT {source_level}")
            self.main.write(f":SYST:RSEN {'ON' if wire_mode == 4 else 'OFF'}")

        elif source_func.upper() == "CURR":
            self.main.write(":SOUR:FUNC CURR")
            self.main.write(f":SOUR:CURR:RANGE {source_level}")  
            self.main.write(f":SOUR:CURR {source_level}")
            
        self.main.write(":FORM:ELEM RES")
        self.main.write(":OUTP ON")
        time.sleep(delay)
        resistance = self.main.query(":READ?")
        self.main.write(":OUTP OFF")

        try:
            return np.array([float(resistance.strip())])
        except ValueError:
            logger.warning(f"Could not parse response: {resistance}")
            return np.array([np.nan])

           
    def source_voltage_and_read_current(
        self,
        source_voltage_level: float,
        source_voltage_range: float,
        measure_current_range: float = 1E-3,
        current_limit: float = 0.01,
        delay: float = 0.1
    ) -> np.ndarray:
        """
        Sources a specified DC voltage using the Keithley 2400 and measures the resulting current.

        Parameters:
            source_voltage_level (float): The voltage level to source in volts (V).
            source_voltage_range (float): The voltage range to use for sourcing in volts (V).
            measure_current_range (float, optional): The measurement range for current in amperes (A). Default is 1E-3 A.
            current_limit (float, optional): The compliance (protection) current limit in amperes (A). Default is 0.01 A.

        Returns:
            np.ndarray: Array of measured current values in amperes (A).

        Raises:
            RuntimeError: If the instrument is not connected.
        """
        if not self.connected:
            raise RuntimeError("Instrument not connected.")

        self.main.write(":SOUR:FUNC VOLT")
        self.main.write(":SOUR:VOLT:MODE FIXED")
        self.main.write(f":SOUR:VOLT:RANG {source_voltage_range}")
        self.main.write(f":SOUR:VOLT:LEV {source_voltage_level}")
        self.main.write(f":SENS:CURR:PROT {current_limit}")
        self.main.write(":SENS:FUNC 'CURR'")
        self.main.write(f":SENS:CURR:RANG {measure_current_range}")
        self.main.write(":FORM:ELEM CURR")
        self.main.write(":OUTP ON")
        time.sleep(delay)
        current_response = self.main.query(":READ?")
        # self.main.write(":OUTP OFF")
        current_values = [float(val) for val in current_response.strip().split(',') if val]
        return np.array(current_values)
     
     
     
     
     
    def source_current_and_read_voltage(
        self,
        source_current_level: float,
        source_current_range: float,
        measure_voltage_range: float = 1.0,
        voltage_limit: float = 1.0,
        delay: float = 0.1
    ) -> np.ndarray:
        """
        Sources a specified DC current using the Keithley 2400 and measures the resulting voltage.

        Parameters:
            source_current_level (float): The current level to source in amperes (A).
            source_current_range (float): The current range to use for sourcing in amperes (A).
            measure_voltage_range (float, optional): The measurement range for voltage in volts (V). Default is 1.0 V.
            voltage_limit (float, optional): The compliance (protection) voltage limit in volts (V). Default is 1 V.
            delay (float, optional): Delay in seconds before reading the measurement. Default is 0.1 s.

        Returns:
            np.ndarray: Array of measured voltage values in volts (V).

        Raises:
            RuntimeError: If the instrument is not connected.
        """
        if not self.connected:
            raise RuntimeError("Instrument not connected.")

        self.main.write(":SOUR:FUNC CURR")
        self.main.write(":SOUR:CURR:MODE FIXED")
        self.main.write(":SENS:FUNC 'VOLT'")
        self.main.write(f":SOUR:CURR:RANG {source_current_range}")
        self.main.write(f":SOUR:CURR:LEV {source_current_level}")
        self.main.write(f":SENS:VOLT:PROT {voltage_limit}")
        self.main.write(f":SENS:VOLT:RANG {measure_voltage_range}")
        self.main.write(":FORM:ELEM VOLT")
        self.main.write(":OUTP ON")
        time.sleep(delay)
        current_response = self.main.query(":READ?")
        # self.main.write(":OUTP OFF")
        current_values = [float(val) for val in current_response.strip().split(',') if val]
        return np.array(current_values) 
     
     
     
       
    def turn_off(self):
        """
        Ensure the source meter is safely turned off.
        This method disables the output of the instrument.
        """
        if not self.connected:
            raise RuntimeError("Instrument not connected.")
        
        try:
            self.main.write(":OUTP OFF")  # Disable output
            logger.info("Source meter turned off.")
        except visa.VisaIOError as e:
            logger.warning(f"Warning: Failed to turn off source meter: {e}")        
        
        
    def close(self):
        if self.main and self.connected:
            try:
                self.turn_off()
            except Exception as e:
                logger.warning(f"Error turning off source meter: {e}")

            try:
                self.main.close()
            except visa.VisaIOError as e:
                logger.warning(f"Failed to close main resource: {e}")

        if self._owns_rm and self.rm:
            try:
                self.rm.close()
            except visa.VisaIOError as e:
                logger.warning(f"Failed to close resource manager: {e}")

        self.connected = False
        logger.info("Connection closed.")




    def debug_err(self):
        if self.debug:
            err = self.main.query("SYST:ERR?")
            print(f"[DEBUG] SYST:ERR? → {err}")
