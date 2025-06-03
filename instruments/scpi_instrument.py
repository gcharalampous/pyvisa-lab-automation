# scpi_instrument.py
class SCPIInstrument:
    def __init__(self, suppress_print=False):
        self.suppress_print = suppress_print
        self.connected = False
        self.main = None

    def write(self, command: str):
        if not self.connected or self.main is None:
            raise RuntimeError("Instrument not connected.")
        if not self.suppress_print:
            print(f">>> {command}")
        self.main.write(command)

    def query(self, command: str) -> str:
        if not self.connected or self.main is None:
            raise RuntimeError("Instrument not connected.")
        if not self.suppress_print:
            print(f">>> {command}")
        response = self.main.query(command)
        if not self.suppress_print:
            print(f"<<< {response.strip()}")
        return response.strip()
