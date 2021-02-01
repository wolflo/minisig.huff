pragma solidity ^0.6.0;

contract TargetMock {

    address immutable internal me = address(this);

    event Call(
        address src,
        address context,
        uint256 gas,
        uint256 val,
        bytes data
    );

    modifier logs() { _log(); _; }

    function _log() internal {
        uint256 gas = gasleft();
        emit Call(msg.sender, address(this), gas, msg.value, msg.data);
    }

    function store(uint256 key, uint256 val) external logs {
        assembly { sstore(key, val) }
    }

    function fail() external { revert(); }

    receive() external payable logs {}
    fallback() external payable logs {}
}
