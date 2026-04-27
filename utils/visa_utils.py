import pyvisa
from utils.logger import setup_logger

logger = setup_logger(__name__)


def _parse_interface(resource_str: str) -> str:
    """Infer interface type from the VISA resource string prefix."""
    r = resource_str.upper()
    if r.startswith("GPIB"):
        return "GPIB"
    elif r.startswith("USB"):
        return "USB"
    elif r.startswith("TCPIP"):
        return "TCP/IP (LAN)"
    elif r.startswith("ASRL") or r.startswith("COM"):
        return "Serial (RS-232)"
    elif r.startswith("PXI"):
        return "PXI"
    else:
        return "Unknown"


def list_visa_resources(
    query_idn: bool = True,
    query_opt: bool = True,
    timeout_ms: int = 2000,
) -> list[dict]:
    """
    Enumerate all VISA resources and optionally query each for identity info.

    Parameters
    ----------
    query_idn : bool
        Send *IDN? to every resource that responds to open(). Default True.
    query_opt : bool
        Send *OPT? after *IDN? to list installed options. Default True.
    timeout_ms : int
        Per-resource query timeout in milliseconds. Default 2000.

    Returns
    -------
    list of dict, one entry per resource, each with keys:
        'resource'   – VISA resource string
        'interface'  – inferred interface type
        'idn'        – *IDN? response, or None / error message
        'options'    – *OPT? response, or None / error message
    """
    results = []

    try:
        rm = pyvisa.ResourceManager()
    except Exception as e:
        logger.error(f"Failed to create ResourceManager: {e}")
        return results

    resources = rm.list_resources()
    if not resources:
        logger.warning("No VISA resources found.")
        return results

    logger.info(f"Found {len(resources)} VISA resource(s). Probing...")
    logger.info("-" * 60)

    for resource_str in resources:
        interface = _parse_interface(resource_str)
        entry = {
            "resource":  resource_str,
            "interface": interface,
            "idn":       None,
            "options":   None,
        }

        if not query_idn:
            logger.info(f"[{interface}] {resource_str}")
            results.append(entry)
            continue

        inst = None
        try:
            inst = rm.open_resource(resource_str)
            inst.timeout = timeout_ms

            # --- Identity ---
            try:
                idn = inst.query("*IDN?").strip()
                entry["idn"] = idn
            except pyvisa.VisaIOError as e:
                entry["idn"] = f"IDN error: {e}"

            # --- Options ---
            if query_opt:
                try:
                    opt = inst.query("*OPT?").strip()
                    entry["options"] = opt if opt else "(none reported)"
                except pyvisa.VisaIOError as e:
                    entry["options"] = f"OPT error: {e}"

        except pyvisa.VisaIOError as e:
            entry["idn"] = f"Could not open: {e}"
        finally:
            if inst:
                try:
                    inst.close()
                except Exception:
                    pass

        # --- Pretty log ---
        logger.info(f"Resource : {resource_str}")
        logger.info(f"Interface: {interface}")
        logger.info(f"IDN      : {entry['idn']}")
        if query_opt:
            logger.info(f"Options  : {entry['options']}")
        logger.info("-" * 60)

        results.append(entry)

    rm.close()
    return results