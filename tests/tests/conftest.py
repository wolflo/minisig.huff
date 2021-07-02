import pytest
import brownie

import utils.constants as C
import utils.utils as utils

web3 = brownie.web3

MINISIG_HUFF_BYTECODE = open('../out/minisig.bin', 'r').readline().rstrip()

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
    return sorted(unsorted, key = lambda x: int(x.address, 16))

@pytest.fixture(scope="module")
def usr_ids(usrs):
    return [ u.address for u in usrs ]

@pytest.fixture(scope="module")
def any_signers():
    unsorted = utils.derive_accts(C.OTHER_MNEMONIC, C.NUM_SIGNERS)
    return sorted(unsorted, key = lambda x: x.address)

@pytest.fixture(scope="module")
def anyone(accounts):
    return accounts[0]

@pytest.fixture(scope="module")
def MinisigHuff(IMinisig, deployer):
    web3.eth.defaultAccount = deployer.address
    return web3.eth.contract(
        abi=IMinisig.abi,
        bytecode=MINISIG_HUFF_BYTECODE
    )

@pytest.fixture(scope="module")
def msig(IMinisig, MinisigHuff, deployer, anyone, usr_ids):
    init_code = MinisigHuff.constructor(C.THRESHOLD, usr_ids).data_in_transaction
    tx = deployer.transfer(data=init_code)
    return IMinisig.at(tx.contract_address, tx=tx, owner=anyone)
