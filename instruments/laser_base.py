from abc import ABC, abstractmethod

class BaseLaserSource(ABC):
    """Abstract base class for tunable laser sources."""

    @abstractmethod
    def initialize(self):
        """Prepare the laser for operation."""
        pass

    @abstractmethod
    def set_wavelength(self, wavelength: float, slot=None, verbose: bool = False):
        """Set the laser output wavelength in nanometers."""
        pass

    @abstractmethod
    def turn_on(self):
        """Turn the laser on."""
        pass
    
    @abstractmethod
    def turn_off(self):
        """Turn the laser off."""
        pass
    
    @abstractmethod
    def close(self):
        """Close the connection and clean up resources."""
        pass