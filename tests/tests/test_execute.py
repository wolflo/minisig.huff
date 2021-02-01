import pytest
import brownie

from brownie.network.event import eth_event, EventDict
from brownie.convert import to_address as checksum

from utils.types import Action, CallType
from utils.utils import signAndExecute

import utils.utils as utils
import utils.constants as C

def test_empty_call(msig, mock, usrs):
    action = Action(CallType.CALL, mock.address, 3000, 0, C.EMPTY_BYTES)
    tx = signAndExecute(msig, usrs, action)
    executed = tx.events[-1]
    assert msig.nonce() == 1
    assert executed['src'] == msig.address
    assert executed['context'] == action.target
    assert executed['gas'] <= action.gas
    assert executed['val'] == action.value
    assert executed['data'] == action.data

def test_call_w_value_and_data(msig, mock, usrs):
    action = Action(CallType.CALL, mock.address, 3000, 1, '0xabababab')
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

def test_two_calls(msig, usrs):
    signAndExecute(msig, usrs, Action(CallType.CALL))
    signAndExecute(msig, usrs, Action(CallType.CALL))
    assert msig.nonce() == 2

def test_delegatecall(msig, mock, usrs):
    action = Action(CallType.DELEGATECALL, mock.address, 3000, 0, C.EMPTY_BYTES)
    tx = signAndExecute(msig, usrs, action)
    call = utils.last_call_log(tx.logs, mock.abi)
    assert msig.nonce() == 1
    assert call['src'] == tx.sender
    assert checksum(call['context']) == msig.address # must checksum address
    assert call['gas'] <= action.gas
    assert call['val'] == action.value
    assert call['data'] == action.data

def test_fail_insufficient_sigs(msig, usrs):
    action = Action(CallType.CALL)
    with brownie.reverts():
        signAndExecute(msig, usrs[0:C.THRESHOLD-1], action)
