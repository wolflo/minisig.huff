import pytest
import brownie

from utils.types import Action, CallType
from utils.utils import signAndExecute

import utils.utils as utils
import utils.constants as C

web3 = brownie.web3

def test_call_empty(msig, mock, usrs):
    action = Action(CallType.CALL, mock.address, C.ZERO_ADDRESS, 3000, 0, C.EMPTY_BYTES)
    tx = signAndExecute(msig, usrs, action)
    executed = tx.events[-1]
    assert msig.nonce() == 1
    assert executed['src'] == msig.address
    assert executed['context'] == action.target
    assert executed['gas'] <= action.gas
    assert executed['val'] == action.value
    assert executed['data'] == action.data

def test_call_value_and_data(msig, mock, usrs):
    action = Action(CallType.CALL, mock.address, C.ZERO_ADDRESS, 3000, 1, '0xabababab')
    tx_value = 10
    tx = signAndExecute(msig, usrs, action, {'value': tx_value})
    call = tx.events[-1]
    assert msig.nonce() == 1
    assert call['src'] == msig.address
    assert call['context'] == action.target
    assert call['gas'] <= action.gas + 2300
    assert call['val'] == action.value
    assert call['data'] == action.data
    assert msig.balance() == tx_value - action.value

def test_call_empty_target(msig, usrs, anyone):
    value = 100
    tx_value = 150
    action = Action(CallType.CALL, C.ADDRESS_EMPTY, C.ZERO_ADDRESS, 3000, value, '0xabababab')
    signAndExecute(msig, usrs, action, {'value': tx_value})
    assert web3.eth.getBalance(C.ADDRESS_EMPTY) == value
    assert msig.balance() == tx_value - value

def test_call_value_no_callvalue(msig, usrs, anyone):
    bal0 = 1000
    value = 200
    action = Action(CallType.CALL, C.ADDRESS_EMPTY, C.ZERO_ADDRESS, 3000, value)
    anyone.transfer(msig.address, amount=bal0)
    signAndExecute(msig, usrs, action)
    assert web3.eth.getBalance(C.ADDRESS_EMPTY) == value
    assert msig.balance() == bal0 - value

def test_two_calls(msig, usrs):
    signAndExecute(msig, usrs, Action(CallType.CALL))
    signAndExecute(msig, usrs, Action(CallType.CALL))
    assert msig.nonce() == 2

def test_first_threshold_signers(mock, deployer, usrs, usr_ids):
    threshold = len(usrs) - 1
    action = Action(CallType.CALL, mock.address, C.ZERO_ADDRESS, 3000, 0, C.EMPTY_BYTES)
    (msig, _) = utils.new_msig(deployer, threshold, usr_ids)
    signAndExecute(msig, usrs[:threshold], action)
    assert msig.nonce() == 1

def test_last_threshold_signers(mock, deployer, usrs, usr_ids):
    threshold = len(usrs) - 1
    action = Action(CallType.CALL, mock.address, C.ZERO_ADDRESS, 3000, 0, C.EMPTY_BYTES)
    (msig, _) = utils.new_msig(deployer, threshold, usr_ids)
    signAndExecute(msig, usrs[-threshold:], action)
    assert msig.nonce() == 1

def test_non_sequential_signers(mock, deployer, usrs, usr_ids):
    threshold = len(usrs) - 1
    action = Action(CallType.CALL, mock.address, C.ZERO_ADDRESS, 3000, 0, C.EMPTY_BYTES)
    signers = usrs.copy()
    signers.pop(threshold // 2)
    (msig, _) = utils.new_msig(deployer, threshold, usr_ids)
    signAndExecute(msig, signers, action)
    assert msig.nonce() == 1

def test_with_source(msig, mock, deployer, anyone, usrs):
    action = Action(CallType.CALL, mock.address, deployer.address, 3000, 0, C.EMPTY_BYTES)
    signAndExecute(msig, usrs, action, {'from': deployer})

def test_fail_wrong_source(msig, mock, deployer, anyone, usrs):
    action = Action(CallType.CALL, mock.address, deployer.address, 3000, 0, C.EMPTY_BYTES)
    with brownie.reverts():
        signAndExecute(msig, usrs, action, {'from': anyone})

def test_fail_insufficient_sigs(msig, usrs):
    action = Action(CallType.CALL)
    with brownie.reverts():
        signAndExecute(msig, usrs[0:C.THRESHOLD-1], action)

def test_fail_bad_signer(msig, usrs, any_signers):
    bad_usrs = usrs.copy()
    bad_usrs[C.THRESHOLD-1] = any_signers[0]
    with brownie.reverts():
        signAndExecute(msig, bad_usrs, Action(CallType.CALL))

def test_fail_unordered_sigs(msig, usrs):
    bad_usrs = usrs.copy()
    bad_usrs[0], bad_usrs[1] = bad_usrs[1], bad_usrs[0]
    action = Action(CallType.CALL)
    nonce = msig.nonce()
    digest = utils.encode_digest(msig, nonce, action)
    sigs = utils.allSign(bad_usrs, digest)
    with brownie.reverts():
        msig.execute(
            action.source,
            action.target,
            action.type,
            action.gas,
            action.value,
            action.data,
            sigs
        )

