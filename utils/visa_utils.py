import pyvisa
from utils.logger import setup_logger

logger = setup_logger(__name__)

def list_visa_resources():
    """
    Lists all available VISA resources connected to the system.

    Returns:
        list: A list of VISA resource strings.
    """
    try:
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        
        if resources:
            logger.info("Available VISA Resources:")
            for resource in resources:
                logger.info(f"  - {resource}")
        else:
            logger.warning("No VISA resources found.")
        
        return list(resources)
    
    except pyvisa.VisaIOError as e:
        logger.error(f"[VISA Error] {e}")
        return []
    
    except Exception as e:
        logger.error(f"[Unexpected Error] {e}")
        return []
