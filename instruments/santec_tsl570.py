"""
Driver for SANTEC TSL-570 Tunable Laser Source.

Standalone tunable laser with continuous/step sweep capability.
No slot or channel addressing required.

Command set: Legacy (forced on init via :SYST:COMM:CODE LEGACY).
  - Wavelength values are bare floats in nm.
  - Power values are bare floats in dBm (or mW, depending on :POW:UNIT setting).
  - Frequency values are bare floats in THz.
  SCPI command set is intentionally NOT used, as bare numeric values sent
  without a unit suffix are interpreted as metres (wavelength) or Hz
  (frequency), which silently fall outside the instrument's range.

Author: Georgios Charalampous
Dependencies: pyvisa
Reference: TSL-570 Operation Manual v1.7
"""

import pyvisa as visa
from instruments.scpi_instrument import SCPIInstrument
from instruments.laser_base import BaseLaserSource
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Valid sweep speed options per manual (nm/s)
_VALID_SWEEP_SPEEDS = {1, 2, 5, 10, 20, 50, 100, 200}

# Sweep mode integer codes per manual
SWEEP_MODE = {
    "step_oneway":       0,
    "continuous_oneway": 1,
    "step_twoway":       2,
    "continuous_twoway": 3,
}


class SantecTSL570(SCPIInstrument, BaseLaserSource):
    """
    SANTEC TSL-570 Tunable Laser Source.

    Parameters
    ----------
    address : str
        VISA resource string, e.g. 'GPIB0::1::INSTR'.
    resource_manager : pyvisa.ResourceManager, optional
        Shared resource manager. A new one is created if not provided.
    """

    # ------------------------------------------------------------------
    # Construction & connection
    # ------------------------------------------------------------------

    def __init__(
        self,
        address: str = 'GPIB0::1::INSTR',
        resource_manager=None,
    ):
        self.address = address
        self.connected = False
        self.main = None
        self.id = None

        self.rm = resource_manager or visa.ResourceManager()
        self._owns_rm = resource_manager is None

        try:
            self.main = self.rm.open_resource(self.address)
            self.id = self.main.query('*IDN?').strip()
            self.connected = True
            logger.info(f"Connected to {self.id} at {self.address}")
        except visa.VisaIOError as e:
            logger.error(f"Error connecting to instrument at {address}: {e}")
            raise

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def initialize(self):
        """
        Clear status, force Legacy command set, and confirm the mode.

        Must be called before any other methods if the instrument's command
        set is unknown, because in SCPI mode a bare wavelength value is
        interpreted as metres and silently ignored.
        """
        self._require_connected("initialize")
        self.main.write('*CLS')
        # Force Legacy command set (bare nm / THz / dBm values)
        self.main.write(':SYST:COMM:CODE LEGACY')
        mode = self.main.query(':SYST:COMM:CODE?').strip()
        logger.info(f"TSL-570 initialized. Command set: {mode}")

    # ------------------------------------------------------------------
    # Wavelength control
    # ------------------------------------------------------------------

    def set_wavelength(self, wavelength: float, verbose: bool = False):
        """
        Set the output wavelength (Legacy mode: bare float in nm).

        Parameters
        ----------
        wavelength : float
            Target wavelength in nanometers.
        verbose : bool
            Log at INFO level when True, DEBUG otherwise.
        """
        self._require_connected("set_wavelength")
        self.main.write(f':WAV {wavelength:.4f}')
        msg = f"Wavelength set to {wavelength} nm."
        logger.info(msg) if verbose else logger.debug(msg)

    def get_wavelength(self) -> float:
        """
        Query the current wavelength setpoint.

        Returns
        -------
        float
            Wavelength in nanometers (Legacy mode returns nm directly).
        """
        self._require_connected("get_wavelength")
        return float(self.main.query(':WAV?').strip())

    def get_wavelength_range(self) -> tuple[float, float]:
        """
        Query the instrument's minimum and maximum configurable wavelengths.

        Returns
        -------
        tuple of (min_nm, max_nm)
        """
        self._require_connected("get_wavelength_range")
        wmin = float(self.main.query(':WAV? MIN').strip())
        wmax = float(self.main.query(':WAV? MAX').strip())
        return wmin, wmax

    # ------------------------------------------------------------------
    # Power control
    # ------------------------------------------------------------------

    def set_power(self, power_dbm: float, verbose: bool = False):
        """
        Set the output power level.

        Parameters
        ----------
        power_dbm : float
            Target power in dBm (range: -15 to +13 dBm, step 0.01 dB).
            Requires power unit to be set to dBm (default). Use
            set_power_unit() if needed.
        verbose : bool
            Log at INFO level when True, DEBUG otherwise.
        """
        self._require_connected("set_power")
        self.main.write(f':POW {power_dbm:.2f}')
        msg = f"Power set to {power_dbm} dBm."
        logger.info(msg) if verbose else logger.debug(msg)

    def get_power(self) -> float:
        """
        Query the power level setpoint.

        Returns
        -------
        float
            Power in dBm (or mW if unit was changed with set_power_unit).
        """
        self._require_connected("get_power")
        return float(self.main.query(':POW?').strip())

    def get_actual_power(self) -> float:
        """
        Read the actual optical power from the built-in power monitor.

        This reflects the live measured output, not the setpoint.

        Returns
        -------
        float
            Measured power in dBm (or mW if unit was changed).
        """
        self._require_connected("get_actual_power")
        return float(self.main.query(':POW:ACT?').strip())

    def set_power_unit(self, unit: str):
        """
        Set the power display and command unit.

        Parameters
        ----------
        unit : str
            'dBm' (default) or 'mW'.
        """
        self._require_connected("set_power_unit")
        unit = unit.lower()
        if unit == 'dbm':
            self.main.write(':POW:UNIT 0')
        elif unit == 'mw':
            self.main.write(':POW:UNIT 1')
        else:
            raise ValueError(f"Invalid power unit '{unit}'. Use 'dBm' or 'mW'.")
        logger.info(f"Power unit set to {unit}.")

    # ------------------------------------------------------------------
    # Attenuation control
    # ------------------------------------------------------------------

    def set_attenuation(self, attenuation_db: float, verbose: bool = False):
        """
        Set the internal attenuator value.

        Parameters
        ----------
        attenuation_db : float
            Attenuation in dB (range: 0–30 dB, step 0.01 dB).
        verbose : bool
            Log at INFO level when True, DEBUG otherwise.
        """
        self._require_connected("set_attenuation")
        self.main.write(f':POW:ATT {attenuation_db:.2f}')
        msg = f"Attenuation set to {attenuation_db} dB."
        logger.info(msg) if verbose else logger.debug(msg)

    def get_attenuation(self) -> float:
        """
        Query the current attenuator setting.

        Returns
        -------
        float
            Attenuation in dB.
        """
        self._require_connected("get_attenuation")
        return float(self.main.query(':POW:ATT?').strip())

    def set_auto_power_control(self, enabled: bool):
        """
        Enable or disable automatic power control (APC) mode.

        In Auto mode the attenuator adjusts to maintain the set power level.
        In Manual mode the attenuator is fixed.

        Parameters
        ----------
        enabled : bool
            True for Auto mode, False for Manual mode.
        """
        self._require_connected("set_auto_power_control")
        self.main.write(f':POW:ATT:AUT {int(enabled)}')
        state = "Auto" if enabled else "Manual"
        logger.info(f"Power control set to {state} mode.")

    # ------------------------------------------------------------------
    # Output enable / shutter
    # ------------------------------------------------------------------

    def turn_on(self):
        """Enable laser emission (:POW:STAT 1)."""
        self._require_connected("turn_on")
        self.main.write(':POW:STAT 1')
        logger.info("Laser output turned ON.")

    def turn_off(self):
        """Disable laser emission (:POW:STAT 0)."""
        self._require_connected("turn_off")
        self.main.write(':POW:STAT 0')
        logger.info("Laser output turned OFF.")

    def get_output_state(self) -> bool:
        """
        Query whether laser emission is currently enabled.

        Returns
        -------
        bool
            True if output is on, False if off.
        """
        self._require_connected("get_output_state")
        return bool(int(self.main.query(':POW:STAT?').strip()))

    def open_shutter(self):
        """
        Open the internal optical shutter (:POW:SHUT 0).

        Note: shutter polarity is inverted relative to POW:STAT —
        0 = open, 1 = closed. Use turn_on/turn_off for normal operation.
        """
        self._require_connected("open_shutter")
        self.main.write(':POW:SHUT 0')
        logger.info("Internal shutter opened.")

    def close_shutter(self):
        """Close the internal optical shutter (:POW:SHUT 1)."""
        self._require_connected("close_shutter")
        self.main.write(':POW:SHUT 1')
        logger.info("Internal shutter closed.")

    def get_shutter_state(self) -> bool:
        """
        Query the internal shutter state.

        Returns
        -------
        bool
            True if shutter is CLOSED, False if OPEN.
        """
        self._require_connected("get_shutter_state")
        return bool(int(self.main.query(':POW:SHUT?').strip()))

    # ------------------------------------------------------------------
    # Sweep control
    # ------------------------------------------------------------------

    def configure_sweep(
        self,
        start_nm: float,
        stop_nm: float,
        speed_nm_per_s: float = 10.0,
        mode: str = 'continuous_oneway',
        cycles: int = 1,
        step_nm: float = None,
        dwell_s: float = None,
        trigger_step_nm: float = None,
    ):
        """
        Configure the built-in wavelength sweep engine.

        Parameters
        ----------
        start_nm : float
            Sweep start wavelength in nm.
        stop_nm : float
            Sweep stop wavelength in nm.
        speed_nm_per_s : float
            Sweep speed in nm/s. Must be one of: 1, 2, 5, 10, 20, 50, 100, 200.
        mode : str
            One of: 'continuous_oneway' (default), 'continuous_twoway',
            'step_oneway', 'step_twoway'.
        cycles : int
            Number of sweep repetitions (0 = repeat indefinitely).
        step_nm : float, optional
            Step width in nm for step sweep modes (range: 0.1pm to span).
        dwell_s : float, optional
            Dwell time in seconds between steps (step sweep mode only).
        trigger_step_nm : float, optional
            Trigger output interval in nm (range: 0.0001 to max span).
            Note: bare float in nm, no unit string accepted by this command.
        """
        self._require_connected("configure_sweep")

        if speed_nm_per_s not in _VALID_SWEEP_SPEEDS:
            raise ValueError(
                f"Invalid sweep speed {speed_nm_per_s} nm/s. "
                f"Must be one of: {sorted(_VALID_SWEEP_SPEEDS)}"
            )
        if mode not in SWEEP_MODE:
            raise ValueError(
                f"Invalid sweep mode '{mode}'. "
                f"Valid options: {list(SWEEP_MODE.keys())}"
            )

        self.main.write(f':WAV:SWE:STAR {start_nm:.4f}')
        self.main.write(f':WAV:SWE:STOP {stop_nm:.4f}')
        self.main.write(f':WAV:SWE:SPE {speed_nm_per_s:.1f}')
        self.main.write(f':WAV:SWE:MOD {SWEEP_MODE[mode]}')
        self.main.write(f':WAV:SWE:CYCL {cycles}')

        if step_nm is not None:
            self.main.write(f':WAV:SWE:STEP {step_nm:.4f}')
        if dwell_s is not None:
            self.main.write(f':WAV:SWE:DWEL {dwell_s:.3f}')
        if trigger_step_nm is not None:
            self.main.write(f':TRIG:OUTP:STEP {trigger_step_nm:.4f}')

        logger.info(
            f"Sweep configured: {start_nm}–{stop_nm} nm, "
            f"{speed_nm_per_s} nm/s, mode='{mode}', cycles={cycles}."
        )

    def start_sweep(self):
        """Start the configured wavelength sweep."""
        self._require_connected("start_sweep")
        self.main.write(':WAV:SWE 1')
        logger.info("Wavelength sweep started.")

    def stop_sweep(self):
        """Stop an in-progress wavelength sweep."""
        self._require_connected("stop_sweep")
        self.main.write(':WAV:SWE 0')
        logger.info("Wavelength sweep stopped.")

    def get_sweep_state(self) -> bool:
        """
        Query whether a sweep is currently active.

        Returns
        -------
        bool
            True if a sweep is running, False otherwise.
        """
        self._require_connected("get_sweep_state")
        return bool(int(self.main.query(':WAV:SWE?').strip()))

    def get_sweep_range(self) -> tuple[float, float]:
        """
        Query the valid configurable sweep range at the current speed setting.

        Returns
        -------
        tuple of (min_nm, max_nm)
        """
        self._require_connected("get_sweep_range")
        wmin = float(self.main.query(':WAV:SWE:RANG:MIN?').strip())
        wmax = float(self.main.query(':WAV:SWE:RANG:MAX?').strip())
        return wmin, wmax

    # ------------------------------------------------------------------
    # Coherence control
    # ------------------------------------------------------------------

    def set_coherence_control(self, enabled: bool):
        """
        Enable or disable coherence control (linewidth broadening).

        Parameters
        ----------
        enabled : bool
            True to enable, False to disable.
        """
        self._require_connected("set_coherence_control")
        self.main.write(f':COHC {int(enabled)}')
        state = "enabled" if enabled else "disabled"
        logger.info(f"Coherence control {state}.")

    def get_coherence_control(self) -> bool:
        """
        Query the coherence control state.

        Returns
        -------
        bool
            True if coherence control is enabled, False otherwise.
        """
        self._require_connected("get_coherence_control")
        return bool(int(self.main.query(':COHC?').strip()))

    # ------------------------------------------------------------------
    # System / diagnostics
    # ------------------------------------------------------------------

    def get_error(self) -> str:
        """
        Read and return the most recent error from the error queue.

        Returns
        -------
        str
            Error string, e.g. '0,"No error"'.
        """
        self._require_connected("get_error")
        return self.main.query(':SYST:ERR?').strip()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def close(self):
        """Turn off laser output and release VISA resources."""
        if self.main and self.connected:
            try:
                self.turn_off()
            except Exception as e:
                logger.warning(f"Error turning off laser during close: {e}")
            try:
                self.main.close()
            except visa.VisaIOError as e:
                logger.warning(f"Failed to close VISA resource: {e}")

        if self._owns_rm and self.rm:
            try:
                self.rm.close()
            except visa.VisaIOError as e:
                logger.warning(f"Failed to close resource manager: {e}")

        self.connected = False
        logger.info("Connection closed.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _require_connected(self, method_name: str):
        if not self.connected:
            raise RuntimeError(
                f"Cannot call '{method_name}': instrument not connected."
            )

    def __str__(self):
        status = "connected" if self.connected else "disconnected"
        return (
            f"SantecTSL570(id={self.id}, address={self.address}, status={status})"
        )

    def __repr__(self):
        return self.__str__()