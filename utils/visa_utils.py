import pyvisa
from utils.logger import setup_logger

logger = setup_logger(__name__)


def _parse_interface(resource_str: str) -> str:
    r = resource_str.upper()
    if r.startswith("GPIB"):
        return "GPIB"
    if r.startswith("USB"):
        return "USB"
    if r.startswith("TCPIP"):
        return "TCP/IP (LAN)"
    if r.startswith("ASRL") or r.startswith("COM"):
        return "Serial (RS-232)"
    if r.startswith("PXI"):
        return "PXI"
    return "Unknown"


def list_gpib_resources(
    query_idn: bool = True,
    query_opt: bool = True,
    timeout_ms: int = 2000,
    scan_addresses: bool = True,
    boards: tuple[int, ...] = (0,),
    address_range: range = range(1, 31),
) -> list[dict]:
    """
    Enumerate GPIB instruments only (filters out ASRL/USB/TCPIP/etc).

    Parameters
    ----------
    scan_addresses : bool
        If True, actively probe every primary address on each board (1-30 by
        default). Required with pyvisa-py because list_resources() does not
        walk the GPIB bus.
    boards : tuple of int
        GPIB board indices to scan (e.g. (0,) for /dev/gpib0). Default (0,).
    address_range : range
        Primary addresses to probe. Default range(1, 31).
    """
    results = []

    try:
        rm = pyvisa.ResourceManager("@py")
    except Exception as e:
        logger.error(f"Failed to create ResourceManager: {e}")
        return results

    # Build the candidate resource list.
    if scan_addresses:
        candidates = [
            f"GPIB{b}::{a}::INSTR" for b in boards for a in address_range
        ]
    else:
        # Trust list_resources() — works only with NI-VISA, not pyvisa-py.
        candidates = list(rm.list_resources("GPIB?*::INSTR"))

    if not candidates:
        logger.warning("No GPIB resources to probe.")
        rm.close()
        return results

    logger.info(f"Probing {len(candidates)} GPIB resource(s)...")
    logger.info("-" * 60)

    for resource_str in candidates:
        entry = {
            "resource":  resource_str,
            "interface": _parse_interface(resource_str),
            "idn":       None,
            "options":   None,
        }

        inst = None
        try:
            inst = rm.open_resource(resource_str)
            inst.timeout = timeout_ms

            if query_idn:
                try:
                    entry["idn"] = inst.query("*IDN?").strip()
                except pyvisa.VisaIOError:
                    # Nothing at this address — skip silently when scanning.
                    if scan_addresses:
                        continue
                    entry["idn"] = "IDN error"

                if query_opt:
                    try:
                        opt = inst.query("*OPT?").strip()
                        entry["options"] = opt if opt else "(none reported)"
                    except pyvisa.VisaIOError as e:
                        entry["options"] = f"OPT error: {e}"

        except pyvisa.VisaIOError as e:
            if scan_addresses:
                continue
            entry["idn"] = f"Could not open: {e}"
        finally:
            if inst is not None:
                try:
                    inst.close()
                except Exception:
                    pass

        logger.info(f"Resource : {resource_str}")
        logger.info(f"IDN      : {entry['idn']}")
        if query_opt:
            logger.info(f"Options  : {entry['options']}")
        logger.info("-" * 60)
        results.append(entry)

    rm.close()
    return results