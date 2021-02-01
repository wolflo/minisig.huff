import pytest
import brownie

import utils.constants as C
import utils.utils as utils

web3 = brownie.web3

minisig_huff_bytecode = ''
with open('../out/minisig.bin', 'r') as f:
    minisig_huff_bytecode = f.readline().rstrip()

@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    pass

@pytest.fixture(scope="module")
def mock(TargetMock, deployer):
    return TargetMock.deploy({'from': deployer})

@pytest.fixture(scope="module")
def deployer(accounts):
    return accounts[1]

@pytest.fixture(scope="module")
def usrs():
    unsorted = utils.derive_accts(C.MNEMONIC, C.NUM_SIGNERS)
    return sorted(unsorted, key = lambda x: x.address)

@pytest.fixture(scope="module")
def usr_ids(usrs):
    return [ u.address for u in usrs ]

@pytest.fixture(scope="module")
def anyone(accounts):
    return accounts[0]

@pytest.fixture(scope="module")
def MinisigHuff(IMinisig, deployer):
    web3.eth.defaultAccount = deployer.address
    return web3.eth.contract(
        abi=IMinisig.abi,
        bytecode=minisig_huff_bytecode
    )

@pytest.fixture(scope="module")
def msig(IMinisig, MinisigHuff, deployer, anyone, usr_ids):
    tx = MinisigHuff.constructor(C.THRESHOLD, usr_ids).transact()
    receipt = brownie.network.transaction.TransactionReceipt(tx)
    return IMinisig.at(receipt.contract_address, tx=receipt, owner=anyone)
