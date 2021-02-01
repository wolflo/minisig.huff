from dataclasses import dataclass

import utils.constants as C

class CallType:
    CALL = 0
    DELEGATECALL = 1

@dataclass
class Action:
    type: CallType
    target: str = C.ZERO_ADDRESS
    gas: int = 2300
    value: int = 0
    data: str = C.EMPTY_BYTES
