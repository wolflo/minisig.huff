import pytest
import brownie
import json

from utils.types import Action, CallType

import utils.utils as utils
import utils.constants as C
import utils.external.gnosis.gnosis as gnosis

web3 = brownie.web3

def test_benchmark_gnosis(deployer, usr_ids, usrs):
    threshold = C.THRESHOLD
    tx_value = 100
    action = Action(CallType.CALL, C.ADDRESS_EMPTY, C.ZERO_ADDRESS, 2300, tx_value, C.EMPTY_BYTES)

    # deploy Safe and Minisig
    (msig, msig_deploy_gas) = utils.new_msig(deployer, threshold, usr_ids)
    (safe, safe_deploy_gas) = gnosis.new_safe(deployer, threshold, usr_ids)

    # give each contract initial balance
    deployer.transfer(msig.address, amount=tx_value)
    deployer.transfer(safe.address, amount=tx_value)
    deployer.transfer(action.target, amount=1) # ensure account is non-empty

    # Execute transactions
    signers = usrs[-threshold:]
    msig_exec_tx = utils.signAndExecute(msig, usrs, action)
    safe_exec_tx = gnosis.exec(safe, usrs, action)

    summarize('DEPLOYMENT', 'GnosisSafe', safe_deploy_gas, msig_deploy_gas)
    summarize('EXCEUTION', 'GnosisSafe', safe_exec_tx.gas_used, msig_exec_tx.gas_used)


def summarize(category, challenger_name, challenger_gas, msig_gas):
    diff = challenger_gas - msig_gas
    diff_relative = diff / challenger_gas * 100
    print('\n==========')
    print(category)
    print(f'{challenger_name}: {challenger_gas}')
    if challenger_gas > 15000000:
        print('***** Over block gas limit *****')
    print(f'Minisig: {msig_gas}')
    if msig_gas > 15000000:
        print('***** Over block gas limit *****')
    print(f'Gas saved: {diff}')
    print(f'% saved: {diff_relative} %')

