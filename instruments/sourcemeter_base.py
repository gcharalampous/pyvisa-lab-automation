"""
Abstract base class for generic source meter instruments.

Defines the required interface for resistance measurement, voltage sourcing,
current reading, and resource management.
"""

import numpy as np
from abc import ABC, abstractmethod
class BaseSourceMeter(ABC):
    """Abstract base class for source meter instruments."""

    @abstractmethod
    def initialize(self, wire_mode: int = 2):
        """Prepare the source meter for operation."""
        pass


    @abstractmethod
    def read_resistance_auto(self, resistance_range: float = 20e3) -> np.ndarray:
        """Measure resistance in ohms and return as a numpy array."""
        pass
    
    @abstractmethod
    def read_resistance_configured(self,
                                resistance_range: float = 20E3,
                                mode: str = "AUTO",
                                offset_comp: str = "OFF",
                                voltage_prot: float = 2.0,
                                current_prot: float = 0.01,
                                source_func: str = "VOLT",
                                source_level: float = 0.05,
                                wire_mode: int = 2) -> np.ndarray:
        """Measure resistance in ohms with specific configurations and return as a numpy array."""
        pass

    @abstractmethod
    def source_voltage_and_read_current(self,
        source_voltage_level: float,
        source_voltage_range: float,
        measure_current_range: float = 1E-3,
        current_limit: float = 0.01,
        delay: float = 0.1) -> np.ndarray:
        """Source a voltage and read the resulting current, returning as a numpy array."""
        pass

    @abstractmethod
    def source_current_and_read_voltage(self,
        source_current_level: float,
        source_current_range: float,
        measure_voltage_range: float = 1E-3,
        voltage_limit: float = 1,
        delay: float = 0.1) -> np.ndarray:
        """Source a current and read the resulting voltage, returning as a numpy array."""
        pass


    @abstractmethod
    def turn_off(self):
        """Ensure the source meter is safely turned off."""
        pass

    @abstractmethod
    def close(self):
        """Close the connection and clean up resources."""
        pass

