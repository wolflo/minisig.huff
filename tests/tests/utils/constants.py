from brownie import ZERO_ADDRESS
import brownie

# signers mnemonic
MNEMONIC = "trim amount saddle learn guitar estate body this harsh never mango swarm";

# deployment parameters
THRESHOLD = 3
NUM_SIGNERS = 3

DOMAIN_SEPARATOR_TYPEHASH = "0x0a684fcd4736a0673611bfe1e61ceb93fb09bcd288bc72c1155ebe13280ffeca"
EXECUTE_TYPEHASH = "0x9c1370cbf5462da152553d1b9556f96a7eb4dfe28fbe07e763227834d409103a"

VM_ERR_MSG = 'VM Exception while processing transaction: revert'

# no idea why this is so difficult
EMPTY_BYTES = brownie.convert.datatypes.HexString(b'', 'bytes')
