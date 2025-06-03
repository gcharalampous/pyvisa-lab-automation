from abc import ABC, abstractmethod

class BaseLaserSource(ABC):
    """Abstract base class for tunable laser sources."""

    @abstractmethod
    def initialize(self):
        """Prepare the laser for operation."""
        pass

    @abstractmethod
    def set_wavelength(self, wavelength: float):
        """Set the laser output wavelength in nanometers."""
        pass
    
    @abstractmethod
    def turn_off(self):
        """Ensure the laser is safely turned off."""
        pass
    
    @abstractmethod
    def close(self):
        """Close the connection and clean up resources."""
        pass