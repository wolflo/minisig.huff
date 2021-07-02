import pytest
import brownie
import json

from utils.types import Action, CallType

import utils.utils as utils
import utils.constants as C
import utils.external.gnosis.gnosis as gnosis
import utils.external.SilentCicero.silent_cicero as silent_cicero

web3 = brownie.web3

def test_benchmark_gnosis(deployer, usr_ids, usrs):
    threshold = C.THRESHOLD
    action = Action(CallType.CALL, C.ADDRESS_EMPTY, C.ZERO_ADDRESS, 2300, 100, C.EMPTY_BYTES)

    # deploy Safe and Minisig
    (msig, msig_deploy_gas) = utils.new_msig(deployer, threshold, usr_ids)
    (safe, safe_deploy_gas) = gnosis.new_safe(deployer, threshold, usr_ids)

    # give each contract initial balance
    deployer.transfer(msig.address, amount=action.value)
    deployer.transfer(safe.address, amount=action.value)
    deployer.transfer(action.target, amount=1) # ensure account is non-empty
    target_bal0 = web3.eth.getBalance(action.target)

    # Execute transactions
    signers = usrs[:threshold]
    msig_exec_tx = utils.signAndExecute(msig, signers, action)
    safe_exec_tx = gnosis.signAndExecute(safe, signers, action)
    assert web3.eth.getBalance(action.target) - target_bal0 == 2 * action.value

    print('\nGnosis Safe')
    summarize('DEPLOYMENT', 'GnosisSafe', safe_deploy_gas, msig_deploy_gas)
    summarize('EXCEUTION', 'GnosisSafe', safe_exec_tx.gas_used, msig_exec_tx.gas_used)

def test_benchmark_silent_cicero(deployer, usr_ids, usrs):
    threshold = C.THRESHOLD
    action = Action(CallType.CALL, C.ADDRESS_EMPTY, C.ZERO_ADDRESS, 100000, 100, C.EMPTY_BYTES)

    # deploy Yul Wallet and Minisig
    (msig, msig_deploy_gas) = utils.new_msig(deployer, threshold, usr_ids)
    (yul_wallet, yul_deploy_gas) = silent_cicero.new_yul_wallet(deployer, threshold, usr_ids)

    # Yul Wallet can only delegatecall, so we need a helper contract to actually send funds
    yul_helper = brownie.YulWalletHelper.deploy({'from': deployer})

    # give each contract initial balance
    deployer.transfer(msig.address, amount=action.value)
    deployer.transfer(yul_wallet.address, amount=action.value)
    deployer.transfer(action.target, amount=1) # ensure account is non-empty
    target_bal0 = web3.eth.getBalance(action.target)

    # Execute transactions
    signers = usrs[:threshold]
    msig_exec_tx = utils.signAndExecute(msig, signers, action)
    yul_exec_tx = silent_cicero.signAndExecute(yul_wallet, yul_helper, signers, action)
    assert web3.eth.getBalance(action.target) - target_bal0 == 2 * action.value

    print('\nSilent Cicero\'s Yul Multisig')
    summarize('DEPLOYMENT', 'Yul Wallet', yul_deploy_gas, msig_deploy_gas)
    summarize('EXCEUTION', 'Yul Wallet', yul_exec_tx.gas_used, msig_exec_tx.gas_used)

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

