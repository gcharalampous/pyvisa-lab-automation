# scpi_instrument.py
class SCPIInstrument:
    def __init__(self):
        self.connected = False
        self.main = None

    def write(self, command: str):
        if not self.connected or self.main is None:
            raise RuntimeError("Instrument not connected.")
        self.main.write(command)

    def query(self, command: str) -> str:
        if not self.connected or self.main is None:
            raise RuntimeError("Instrument not connected.")
        response = self.main.query(command)
        return response.strip()
