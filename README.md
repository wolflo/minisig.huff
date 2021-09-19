# Minisig.huff

A minimal EVM multisignature wallet written in [huff](https://github.com/AztecProtocol/huff.git).
See the [minisig](https://github.com/wolflo/minisig) repo for more info and alternative implementations.
This is unaudited code, but it does implement the functionality in the solidity [implementation](https://github.com/wolflo/minisig.sol/blob/main/contracts/Minisig.sol).

## Benchmarks

Compared to the Gnosis Safe, a 2 of 3 Minisig is roughly 35% cheaper to deploy and 15% cheaper per execution.
This difference grows with the number of signers. An n of 10 Minisig is 45% cheaper to deploy than the equivalent Gnosis Safe, and at n of 100 the difference is 65%.

You can see these benchmarks in the [test suite](./tests/tests/benchmark.py).

For reference, the Gnosis Safe was deployed as it is most commonly used in practice -- a proxy factory deploying a minimal delegatecall proxy which points to the implementation contract and Gnosis's default handler contract.
The Minisig was deployed as a standalone contract from an externally-owned account.

## Requirements
* [brownie](https://github.com/eth-brownie/brownie) (`pip install eth-brownie`)
* yarn (or npm)

## Build
* `yarn compile` -- writes the assembled bytecode to `out/`

## Run the tests
* `yarn test`

## Debug
* generate the runtime bytecode and calldata for a specific test by inserting: 
    * `utils.write_hevm_debug(msig, usrs, action)`
* `yarn test`
* `yarn debug` (requires [hevm](https://github.com/dapphub/dapptools))
