import pytest
import brownie

import utils.utils as utils
import utils.constants as C

def test_success(msig, usr_ids):
    assert msig.nonce() == 0
    assert msig.threshold() == C.THRESHOLD
    assert msig.allSigners() == usr_ids
    assert msig.DOMAIN_SEPARATOR() == utils.encode_dom_sep(msig)

def test_fail_zero_head(MinisigHuff, usr_ids):
    bad_usr_ids = usr_ids.copy()
    bad_usr_ids.insert(0, C.ZERO_ADDRESS)
    with pytest.raises(ValueError) as err:
        MinisigHuff.constructor(C.THRESHOLD, bad_usr_ids).transact()
    assert C.VM_ERR_MSG in str(err)

def test_fail_unordered_signers(MinisigHuff, usr_ids):
    bad_usr_ids = usr_ids.copy()
    bad_usr_ids[0], bad_usr_ids[1] = bad_usr_ids[1], bad_usr_ids[0]
    with pytest.raises(ValueError) as err:
        MinisigHuff.constructor(C.THRESHOLD, bad_usr_ids).transact()
    assert C.VM_ERR_MSG in str(err)

def test_fail_insufficient_signers(MinisigHuff, usr_ids):
    with pytest.raises(ValueError) as err:
        MinisigHuff.constructor(len(usr_ids) + 1, usr_ids).transact()
    assert C.VM_ERR_MSG in str(err)
