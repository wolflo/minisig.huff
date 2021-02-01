import brownie
import eth_abi

from eth_account.messages import encode_structured_data
from eth_account._utils.signing import sign_message_hash
from brownie.network.event import eth_event, EventDict

import utils.constants as C
web3 = brownie.network.web3

def derive_accts(mnemonic, n):
    return [ web3.eth.account.from_mnemonic(C.MNEMONIC, f"m/44'/60'/0'/0/{i}") for i in range(n) ]

def encode_dom_sep(inst):
    chain_id = brownie.network.chain.id
    preimg = eth_abi.encode_abi(
        [ 'bytes32', 'uint256', 'uint256', 'address' ],
        [
            bytes.fromhex(C.DOMAIN_SEPARATOR_TYPEHASH[2:]),
            chain_id,
            inst.tx.block_number,
            inst.address
        ]
    )
    return web3.keccak(preimg).hex()

def encode_digest(inst, nonce, target, call_type, gas, value, data):
    dom_sep = encode_dom_sep(inst)
    hash_data = web3.solidityKeccak(['bytes'], [data])
    struct_preimg = eth_abi.encode_abi(
        ['bytes32', 'address', 'uint8', 'uint256', 'uint256', 'uint256', 'bytes32' ],
        [
            bytes.fromhex(C.EXECUTE_TYPEHASH[2:]),
            target,
            call_type,
            nonce,
            gas,
            value,
            hash_data
        ]
    )
    hash_struct = web3.keccak(struct_preimg)
    digest = web3.solidityKeccak(
        [ 'bytes1', 'bytes1', 'bytes32', 'bytes32' ],
        [ '0x19', '0x01', dom_sep, hash_struct ]
    )
    return digest

def allSign(usrs, digest):
    sigs = [ bytes(u.signHash(digest).signature).hex() for u in usrs ]
    return ''.join(sigs)

def signAndExecute(inst, usrs, action, opts={}):
    nonce = inst.nonce()
    digest = encode_digest(
        inst,
        nonce,
        action.target,
        action.type,
        action.gas,
        action.value,
        action.data
    )
    sigs = allSign(usrs, digest)
    return inst.execute(action.target, action.type, action.gas, action.value, action.data, sigs, opts)

def signAndEncodeCalldata(inst, usrs, target, call_type, gas, value, data):
    nonce = inst.nonce()
    digest = encode_digest(inst, nonce, target, call_type, gas, value, data)
    sigs = allSign(usrs, digest)
    return inst.execute.encode_input(target, call_type, gas, value, data, sigs)

def last_call_log(logs, abi):
    decoded = eth_event.decode_logs(logs, eth_event.get_topic_map(abi))
    events = EventDict(decoded)
    call = events[-1]
    return call
