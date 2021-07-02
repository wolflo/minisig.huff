pragma solidity 0.6.6;

contract YulWalletHelper {
    function call(address target, uint256 value, bytes memory data) public payable {
        assembly {
            if iszero(call(gas(), target, value, add(data, 32), mload(data), 0, 0)) {
                revert(0, 0)
            }
        }
    }
}
