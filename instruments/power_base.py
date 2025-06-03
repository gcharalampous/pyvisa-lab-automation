from abc import ABC, abstractmethod

class BasePowerMeter(ABC):
    """Abstract base class for optical power meters."""
    
    @abstractmethod
    def initialize(self):
        """Prepare the powermeter for operation."""
        pass
    
    @abstractmethod
    def measure_power(self) -> float:
        """Measure and return optical power in dBm or nW."""
        pass

    @abstractmethod
    def close(self):
        """Close the connection and clean up resources."""
        pass