class LengthUnits:
    
    _defs = {
        # <symbol>: (<mm_conversion_factor>, <display_decimals>, <step>)
        'mm': (1, 2, 1),
        'cm': (10, 3, 0.1),
        'm': (1000, 5, 0.001),
        'in': (25.4, 3, 0.05),
        'ft': (304.8, 4, 0.005),
    }

    _instances = {}

    def __init__(self, symbol: str):
        mm_factor, display_decimals, step = self._defs[symbol]
        self.symbol = symbol
        self.mm_factor = mm_factor
        self.display_decimals = display_decimals
        self.step = step
        
    def from_mm(self, value: float) -> float:
        return value / self.mm_factor

    def to_mm(self, value: float) -> float:
        return value * self.mm_factor
        
    @staticmethod
    def symbols() -> tuple:
        return tuple(LengthUnits._defs.keys())
    
    @staticmethod
    def get(symbol: str) -> 'LengthUnits':
        if not symbol in LengthUnits._instances:
            LengthUnits._instances[symbol] = LengthUnits(symbol)
        return LengthUnits._instances[symbol]