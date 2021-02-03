import pytest
import brownie

from brownie.convert import to_address as checksum

from utils.types import Action, CallType
from utils.utils import signAndExecute

import utils.utils as utils
import utils.constants as C

web3 = brownie.web3

def test_dcall_empty(msig, mock, usrs):
    action = Action(CallType.DELEGATECALL, mock.address, C.ZERO_ADDRESS, 3000, 0, C.EMPTY_BYTES)
    tx = signAndExecute(msig, usrs, action)
    call = utils.last_call_log(tx.logs, mock.abi)
    assert msig.nonce() == 1
    assert call['src'] == tx.sender
    assert checksum(call['context']) == msig.address
    assert call['gas'] <= action.gas
    assert call['val'] == action.value
    assert call['data'] == action.data

def test_dcall_empty_target(msig, usrs):
    action = Action(CallType.DELEGATECALL, C.ADDRESS_EMPTY, C.ZERO_ADDRESS, 3000, 0, '0xdeadbeefab')
    signAndExecute(msig, usrs, action)
    assert msig.nonce() == 1

def test_dcal_value_and_data(msig, mock, usrs):
    value = 100
    action = Action(CallType.DELEGATECALL, mock.address, C.ZERO_ADDRESS, 4000, value, '0xdeadbeef')
    tx = signAndExecute(msig, usrs, action, {'value': value})
    call = utils.last_call_log(tx.logs, mock.abi)
    assert msig.balance() == value
    assert msig.nonce() == 1
    assert call['src'] == tx.sender
    assert checksum(call['context']) == msig.address
    assert call['gas'] <= action.gas
    assert call['val'] == action.value
    assert call['data'] == action.data

def test_two_dcalls(msig, usrs):
    signAndExecute(msig, usrs, Action(CallType.DELEGATECALL))
    signAndExecute(msig, usrs, Action(CallType.DELEGATECALL))
    assert msig.nonce() == 2

def test_fail_insufficient_sigs(msig, usrs):
    action = Action(CallType.DELEGATECALL)
    with brownie.reverts():
        signAndExecute(msig, usrs[0:C.THRESHOLD-1], action)

def test_fail_unmatched_value(msig, usrs):
    value = 100
    action = Action(CallType.DELEGATECALL, C.ADDRESS_EMPTY, C.ZERO_ADDRESS, 3000, value, C.EMPTY_BYTES)
    with brownie.reverts():
        signAndExecute(msig, usrs, action)
    with brownie.reverts():
        signAndExecute(msig, usrs, action, {'value': value + 1})
