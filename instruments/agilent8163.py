"""
Driver for Agilent 8163 Lightwave Multimeter.

This instrument contains two main modules:
- A tunable laser source (slot-controlled)
- A power meter channel (slot+channel controlled)

Author: Georgios Charalampous
Created: 2025-06-01
Dependencies: pyvisa
"""
from instruments.scpi_instrument import SCPIInstrument
from instruments.laser_base import BaseLaserSource
from instruments.power_base import BasePowerMeter
from utils.logger import setup_logger
import pyvisa as visa

logger = setup_logger(__name__)

class Agilent8163Multimeter(SCPIInstrument, BaseLaserSource, BasePowerMeter):
    """
    Agilent 8163 Lightwave Multimeter

    Parameters:
    - laser_slot (int): Slot number for the tunable laser module.
    - power_slot (int): Slot number for the power meter module.
    - power_channel (int): Channel number (typically 1 or 2) for power measurement.

    Note:
    - Wavelength is set in nanometers.
    - Power is returned in Watts.
    """


    def __init__(
        self,
        address='GPIB0::20::INSTR',
        laser_slot=1,
        power_slot=2,
        power_channel=1,
        resource_manager=None
    ):
        self.address = address
        self.laser_slot = laser_slot
        self.power_slot = power_slot
        self.power_channel = power_channel
        self.connected = False
        self.main = None

        self.rm = resource_manager or visa.ResourceManager()
        self._owns_rm = resource_manager is None
        try:
            self.main = self.rm.open_resource(address)
            self.id = self.main.query('*IDN?').strip()
            self.opt = self.main.query('*OPT?').strip()
            self.connected = True
            logger.info(f"Connected to {self.id} at {self.address}")
            logger.info(f"Options: {self.opt}")
        except visa.VisaIOError as e:
            logger.error(f"Error connecting to instrument at {address}: {e}")
            raise

    def initialize(self):
        if not self.connected:
            raise RuntimeError("Cannot initialize: Instrument not connected.")
        self.main.write("*CLS")
        self.main.write(f"sour{self.laser_slot}:pow:stat 1")
        logger.info("Laser module initialized.")

    def set_wavelength(self, wavelength: float):
        if not self.connected:
            raise RuntimeError("Cannot set wavelength: Instrument not connected.")
        self.main.write(f'sour{self.laser_slot}:wav {wavelength}NM')
        logger.debug(f"Wavelength set to {wavelength} nm.")

    def measure_power(self) -> float:
        if not self.connected:
            raise RuntimeError("Cannot measure power: Instrument not connected.")
        response = self.main.query(
            f'fetch{self.power_slot}:chan{self.power_channel}:pow?'
        )
        try:
            power = float(response)
            logger.debug(f"Measured power: {power} W")
            return power
        except ValueError:
            logger.warning(f"Invalid power reading: {response}")
            raise RuntimeError(f"Invalid power reading: {response}")

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


    def turn_off(self):
            if not self.connected:
                raise RuntimeError("Cannot turn off laser: Instrument not connected.")
            self.main.write(f"sour{self.laser_slot}:pow:stat 0")
            logger.info("Laser turned off")


    def __str__(self):
        status = "connected" if self.connected else "disconnected"
        return f"Agilent8163Multimeter(id={self.id}, address={self.address}, status={status})"