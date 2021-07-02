import brownie
import json

import utils.constants as C

import utils.utils as utils

web3 = brownie.network.web3

CONTRACT_DATA_PATH = 'tests/utils/external/gnosis/gnosis.json'
contracts = json.load(open(CONTRACT_DATA_PATH, 'r'))

def new_safe(deployer, threshold, signers):
    callback_handler = get_contract(deployer, 'DefaultCallbackHandler')
    impl = get_contract(deployer, 'GnosisSafe')
    proxy_factory = get_contract(deployer, 'ProxyFactory')

    # encode initialization data for proxy
    setup_data = impl.setup.encode_input(
        signers,
        threshold,
        C.ZERO_ADDRESS,
        C.EMPTY_BYTES,
        callback_handler.address,
        C.ZERO_ADDRESS,
        0,
        C.ZERO_ADDRESS
    )

    # deploy proxy
    tx = proxy_factory.createProxyWithNonce(
        impl.address,
        setup_data,
        web3.keccak(C.EMPTY_BYTES), # salt
        {'from': deployer}
    )
    proxy = brownie.Contract.from_abi(
        'Proxy',
        tx.new_contracts[0],
        contracts['GnosisSafe']['abi'],
        owner=deployer
    )

    return (proxy, tx.gas_used)

def signAndExecute(inst, signers, action, opts={}):
    nonce = inst.nonce()
    digest = inst.getTransactionHash(
        action.target,
        action.value,
        action.data,
        action.type,
        action.gas,
        0, 0, C.ZERO_ADDRESS, C.ZERO_ADDRESS, # refund for executor
        nonce
    )
    sigs = utils.allSign(signers, digest)
    return inst.execTransaction(
        action.target,
        action.value,
        action.data,
        action.type,
        action.gas,
        0, 0, C.ZERO_ADDRESS, C.ZERO_ADDRESS, # refund for executor
        sigs,
        opts
    )

def get_contract(deployer, name):
    tx = deployer.transfer(data=contracts[name]['bytecode'])
    return brownie.Contract.from_abi(name, tx.contract_address, contracts[name]['abi'])
