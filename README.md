# Minisig.huff

A minimal EVM multisignature wallet written in [huff](https://github.com/AztecProtocol/huff.git).
See the [minisig](https://github.com/wolflo/minisig) repo for more info and alternative implementations.
This is unfinished and unaudited code, but it's complete enough to play around with.

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
