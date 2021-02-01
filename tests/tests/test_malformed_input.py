import pytest
import brownie

from utils.types import Action, CallType
from utils.utils import signAndExecute

import utils.utils as utils
import utils.constants as C

# TODO
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
        msig.execute(action.target, action.type, action.gas, action.value, action.data, sigs)

def test_fail_bad_calltype(msig, usrs):
    with brownie.reverts():
        signAndExecute(msig, usrs, Action(CallType.INVALID))
