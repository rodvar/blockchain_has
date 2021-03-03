pragma solidity >=0.4.0 <0.5.0;

contract rodricoin_ico {
    uint public max_coins = 1000000;
    uint public usd_to_rodricoin = 1000;
    uint public total_rodricoins_bought = 0;
    
    mapping(address => uint) equity_rodricoin;
    mapping(address => uint) equity_usd;
    
    modifier can_buy_rodricoins(uint usd_invested) {
        require(usd_invested * usd_to_rodricoin + total_rodricoins_bought <= max_coins, "The buy can't exceed the available supply");
        _;
    }
    
    function equty_in_rodricoin(address investor) external constant returns(uint) {
        return equity_rodricoin[investor];
    }
    
    function equty_in_usd(address investor) external constant returns(uint) {
        return equity_usd[investor];
    }
    
}
