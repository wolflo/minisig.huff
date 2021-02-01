import pytest
import brownie

from brownie.convert.datatypes import HexString

import utils.utils as utils
import utils.constants as C

web3 = brownie.web3

def test_success(msig, usr_ids):
    immutables = utils.parse_immutables(msig)
    assert msig.nonce() == 0
    assert immutables.threshold == C.THRESHOLD
    assert immutables.domain_separator == utils.encode_dom_sep(msig)
    assert immutables.signers == usr_ids

def test_deploy_with_value(MinisigHuff, deployer, usr_ids):
    value = 100
    init_code = MinisigHuff.constructor(C.THRESHOLD, usr_ids).data_in_transaction
    tx = deployer.transfer(data=init_code, amount=value)
    assert web3.eth.getBalance(tx.contract_address) == value

def test_fail_zero_head(MinisigHuff, deployer, usr_ids):
    bad_usr_ids = usr_ids.copy()
    bad_usr_ids.insert(0, C.ZERO_ADDRESS)
    init_code = MinisigHuff.constructor(C.THRESHOLD, bad_usr_ids).data_in_transaction
    with brownie.reverts():
        deployer.transfer(data=init_code)

def test_fail_unordered_signers(MinisigHuff, deployer, usr_ids):
    bad_usr_ids = usr_ids.copy()
    bad_usr_ids[0], bad_usr_ids[1] = bad_usr_ids[1], bad_usr_ids[0]
    init_code = MinisigHuff.constructor(C.THRESHOLD, bad_usr_ids).data_in_transaction
    with brownie.reverts():
        deployer.transfer(data=init_code)

def test_fail_insufficient_signers(MinisigHuff, deployer, usr_ids):
    init_code = MinisigHuff.constructor(len(usr_ids) + 1, usr_ids).data_in_transaction
    with brownie.reverts():
        deployer.transfer(data=init_code)
