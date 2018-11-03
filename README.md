# cryptodiversify

[![Build Status](https://travis-ci.org/salimane/cryptodiversify.svg?branch=master)](https://travis-ci.org/salimane/cryptodiversify)
[![Maintenance](https://img.shields.io/maintenance/yes/2018.svg)](https://github.com/salimane/cryptodiversify/commits/master)

Automatically check your portfolio on the [Binance](https://www.binance.com/?ref=22709520) exchange and advice you on rebalancing your portfolio into the top 20 cryptocurrencies by [market capitalization](https://coinmarketcap.com/).

## Example

```shell

Coin              % Optimal  % Current  Optimal Amount       % Divergence    BUY                  SELL

bitcoin           10.00      10.57      0.008319037083134169  -5.42                                0.0004768099168658307
ethereum          10.00      9.50       0.11374289215895854   5.27            0.005694237158958537
ripple            10.00      9.83       88.94362214163014     1.74
bitcoin-cash      10.00      10.40      0.05405687847437973   -3.89
eos               10.00      10.60      3.769455245585323     -5.68                                0.2268937544146773
cardano           7.15       7.05       151.62943088392988    1.47
litecoin          6.46       6.33       0.32924505647911273   2.04
stellar           6.24       6.11       108.6101863258544     2.08
iota              4.30       4.23       16.255542418832175    1.70
tron              4.24       4.17       384.5150471381602     1.56
neo               3.85       3.79       0.3801398616726232    1.74
monero            3.07       2.99       0.09344853195578331   2.79
dash              2.96       2.91       0.04699815459345396   1.83
nem               2.88       2.83       52.63475007774783     1.71
vechain           1.72       1.67       3.0749170564285194    2.60
ethereum-classic  1.64       1.61       0.5931927386020068    1.85
qtum              1.46       1.44       0.5179110625799085    1.65
omisego           1.38       1.36       0.596776023220714     1.49
icon              1.35       1.33       2.264647249669606     1.46
binance-coin      1.29       1.27       0.6669483114341143    1.87

Estimated Total Value:    $788.0573914630499
```

## How does it work ?

The algorithm takes the top 20 coins by [market capitalization](https://coinmarketcap.com/) and assign each coin a % allocation based on their weighted market capitalization.

Then it caps every coin to be at most 10% of the total portfolio value. Anything above 10% gets redistributed to all the coins below by weighted market capitalization until the entire sum of the portfolio adds up to 100%.

It then fetches your current portofolio on the [Binance](https://www.binance.com/?ref=22709520) exchange and suggests a buy and sell strategy based on the divergence of the % allocated if the divergence is greater than 10%.

## Cost / Benefit

For a long term cryptocurrency strategy, you want to keep your portfolio at a similar risk profile to the original design. If you don’t “reset”, one asset can overwhelm your entire portfolio. This is a starting point for users who want to make a bet on the entire crypto market.

Don’t bet it all on one coin, you should bet on the long-term success of the whole cryptocurrency market.

## Which exchange does it support ?

It only currently supports the [Binance](https://www.binance.com/?ref=22709520) exchange

## How can I trust this with my API Keys?

The code runs on your computer, the API keys are on your computer. The APIs keys should be trade-only and are only used to fetch your current [Binance](https://www.binance.com/?ref=22709520) portfolio.

## Prerequisites

* Binance Account. If you haven't set up an account yet,register [here](https://www.binance.com/?ref=22709520).
* Trade-only API Keys, [generate an API Key](https://www.binance.com/userCenter/createApi.html) and assign relevant permissions. Only enable trade-only permissions.
* $200 USD in Cryptocurrencies (The minimum $200 protects investors from Binance's minimum trading limit and make sure that diversified portfolios can be created properly.)
* Git
* A working [Python](https://www.python.org/) 3.6.5 installation with [virtualenv](https://virtualenv.pypa.io/en/stable/) and [pip](https://pypi.python.org/pypi/pip).
    ** 
    ```shell
    # Mac OS X
    brew update
    brew install pyenv pyenv-virtualenv
    pyenv install 3.6.5
    ```

## Setup

* Clone repository with ``git clone https://github.com/salimane/cryptodiversify.git``
* Copy ``config/config.py.example``,and save as ``config/config.py``
* Edit ``config/config.py``, customize configuration and add your trade-only binance api keys
* Run ``make setup``

## Running

* Run in console with ``python hodl.py``

## TODO

* Online trading via APIs
* Multiple exchanges

## Contributing

Our goal is for this project to be used by the cryptocurrency community to maximize their investment, so we'd love your input! Got a question or an idea? Create an issue or a pull-request.

## Maintainers

* [Salimane Adjao Moustapha - @salimane](https://github.com/salimane)

## Copyright Notice

Copyright (C) 2018 Salimane Adjao Moustapha, authors, and contributors. Licensed under the [MIT License](/LICENSE).
