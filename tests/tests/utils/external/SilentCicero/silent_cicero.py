import brownie

from eth_abi import encode_abi, decode_single

import utils.utils as utils
import utils.constants as C

web3 = brownie.network.web3

CONTRACT_DATA_PATH = 'tests/utils/external/SilentCicero/yul_wallet.bin'
YUL_BYTECODE = open(CONTRACT_DATA_PATH, 'r').readline().rstrip()
YUL_DOMAIN_SEPARATOR = '0xb0609d81c5f719d8a516ae2f25079b20fb63da3e07590e23fbf0028e6745e5f2' # hardcoded
YUL_TYPEHASH = '0x4a0a6d86122c7bd7083e83912c312adabf207e986f1ac10a35dfeb610d28d0b6'

def new_yul_wallet(deployer, threshold, signers):
    IYulWallet = brownie.IYulWallet
    YulWallet = web3.eth.contract(
        abi=IYulWallet.abi,
        bytecode=YUL_BYTECODE
    )
    init_code = YulWallet.constructor(threshold, signers).data_in_transaction
    tx = deployer.transfer(data=init_code)
    yul_wallet = IYulWallet.at(tx.contract_address, tx=tx, owner=deployer)
    return (yul_wallet, tx.gas_used)

def signAndExecute(inst, helper, signers, action, opts={}):
    nonce_slot = int(inst.address, 16) + 1
    nonce = int(web3.eth.getStorageAt(inst.address, nonce_slot).hex(), 16)

    # encode data for delegatecall to helper contract
    forward_data = helper.call.encode_input(action.target, action.value, action.data)
    hash_data = web3.solidityKeccak([ 'bytes' ], [ forward_data ])

    struct_preimg = encode_abi(
        [ 'bytes32', 'uint256', 'address', 'uint256', 'bytes32' ],
        [
            bytes.fromhex(YUL_TYPEHASH[2:]),
            nonce,
            helper.address, # delegatecall goes to the helper contract
            action.gas,
            hash_data
        ]
    )
    hash_struct = web3.keccak(struct_preimg)
    digest = web3.solidityKeccak(
        [ 'bytes1', 'bytes1', 'bytes32', 'bytes32' ],
        [
            '0x19',
            '0x01',
            bytes.fromhex(YUL_DOMAIN_SEPARATOR[2:]),
            hash_struct
        ]
    )
    sigs = allSignUnpacked(signers, digest)

    return inst.execute(helper.address, action.gas, forward_data, sigs)

def allSignUnpacked(signers, digest):
    sigs = [ bytes(s.signHash(digest).signature).hex() for s in signers ]
    unpacked_sigs = []
    for sig in sigs:
        unpacked_sigs.append(sig[-2:]),     # v
        unpacked_sigs.append(sig[:64]),     # r
        unpacked_sigs.append(sig[64:-2])    # s
    return unpacked_sigs
