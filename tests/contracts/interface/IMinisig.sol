pragma solidity 0.6.6;

contract IMinisig {
    constructor(uint8, address[] memory) public payable {}
    receive() external payable {}
    function nonce() external view returns (uint256) {}
    function threshold() external view returns (uint8) {}
    function DOMAIN_SEPARATOR() external view returns (bytes32) {}
    function execute(address, address, uint8, uint256, uint256, bytes calldata, bytes calldata) external payable {}
    function allSigners() external view returns (address[] memory) {}
}
