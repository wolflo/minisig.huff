import pytest
import brownie

from utils.types import Action, CallType
from utils.utils import signAndExecute

import utils.utils as utils
import utils.constants as C

def test_fallback(msig, anyone):
    value = 100
    anyone.transfer(msig.address, amount=value)
    assert msig.balance() == value

def test_fail_fallback_w_data(msig, anyone):
    value = 100
    with brownie.reverts():
        anyone.transfer(msig.address, amount=value, data='0xbe')

def test_fail_short_calldata(msig, usrs, anyone):
    action = Action(CallType.CALL)
    cdata = utils.signAndEncodeCalldata(msig, usrs, action)
    with brownie.reverts():
        anyone.transfer(msig.address, data=cdata[:-1])

def test_fail_short_signature(msig, usrs, anyone):
    action = Action(CallType.CALL)
    nonce = msig.nonce()
    digest = utils.encode_digest(msig, nonce, action)
    lst_sigs = [ bytes(u.signHash(digest).signature).hex() for u in usrs ]
    lst_sigs[1] = lst_sigs[1][:-1]
    sigs = ''.join(lst_sigs)
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

def test_fail_bad_calltype(msig, usrs):
    with brownie.reverts():
        signAndExecute(msig, usrs, Action(CallType.INVALID))

# 4 bytes of nonmatching calldata, no value
def test_fail_nonmatching_calldata(msig, anyone):
    with brownie.reverts():
        anyone.transfer(msig.address, data='0xacabacab')
