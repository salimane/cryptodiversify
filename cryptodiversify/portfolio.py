#!/usr/bin/env python
from .market import Market
from binance.client import Client
from binance.exceptions import BinanceAPIException
import json
import logging
import sys
import os

from time import time
log = logging.getLogger(__name__)


class Portfolio:
    def __init__(self, config, market=None):
        self.__config = config
        self.__binance_client = Client(
            self.__config['binance_api_key'],
            self.__config['binance_api_secret'],
            {"timeout": self.__config.get('binance_api_timeout', 20)})

        self.__market = Market(
            self.__config
        ).request_market() if market is not None else market
        self.__portfolio = {}
        # TODO trade https://github.com/sammchardy/python-binance/issues/139

    def get_portfolio(self):
        return self.__initialize_portfolio()

    def __initialize_portfolio(self):
        portfolio = {}
        try:
            portfolio = {
                'crypto_not_coinmarketcap': [],
                'crypto_currencies': [],
                'crypto_currencies_hash': {},
                'total_value_fiat': 0
            }
            try:
                balances = list(
                    filter(
                        lambda x: (float(x['free']) > 0 or float(x['locked']) > 0) and x['asset'] not in ['GAS'],
                        self.__binance_client.get_account()['balances']
                    )
                )
            except BinanceAPIException as e:
                print(e)
                sys.exit()

            # Create a new portfolio and save it.
            for cc in balances:
                try:
                    coin = self.__market['crypto_currencies_hash'][cc['asset']]
                except KeyError:
                    portfolio['crypto_not_coinmarketcap'].append(cc['asset'])
                    continue
                coin.update({
                    'amount': float(cc['free']),
                    'value_fiat': coin['price_usd'] * float(cc['free']),
                    'percentage_optimal': 0,
                    'percentage_current': 0,
                    'amount_optimal': 0,
                    'value_optimal': 0,
                    'divergence': 0,
                    'divergence_percentage': 0,
                    'last_change': int(time())
                })
                portfolio['crypto_currencies_hash'][coin['symbol']] = coin
                portfolio['crypto_currencies'].append(coin)
                portfolio['total_value_fiat'] += coin['value_fiat']

            portfolio['last_updated'] = int(time())

            with open("data/portfolio.json", 'w') as f:
                json.dump(portfolio, f, sort_keys=True, indent=4)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error("Exception in requesting portfolio: {} {}: {}".format(exc_type, fname, exc_tb.tb_lineno))
            log.warning("No data from web source. Loading file")
            # Get last data from file
            with open(self.__config['portfolio_data_path'], 'r') as f:
                portfolio = json.load(f)

        return portfolio

    def evaluate_portfolio(self, allocations, portfolio, market, config):
        crypto_currencies = []
        for coin in allocations:
            percentage_optimal = coin['cap_ratio'] * 100
            amount_optimal = portfolio['total_value_fiat'] * coin['cap_ratio'] / coin['price_usd']
            value_optimal = portfolio['total_value_fiat'] * coin['cap_ratio']
            divergence = amount_optimal
            divergence_percentage = 100

            if portfolio['crypto_currencies_hash'].get(coin['symbol'], None):
                if portfolio['crypto_currencies_hash'][coin['symbol']].get('amount', 0) > 0:
                    divergence = amount_optimal - portfolio['crypto_currencies_hash'][coin['symbol']]['amount']
                    divergence_percentage = (
                        divergence / portfolio['crypto_currencies_hash'][coin['symbol']]['amount']) * 100
                else:
                    portfolio['crypto_currencies_hash'][coin['symbol']]['amount'] = 0
                    portfolio['crypto_currencies_hash'][coin['symbol']]['value_fiat'] = 0
            else:
                portfolio['crypto_currencies_hash'][coin['symbol']] = coin
                portfolio['crypto_currencies_hash'][coin['symbol']]['amount'] = 0
                portfolio['crypto_currencies_hash'][coin['symbol']]['value_fiat'] = 0

            percentage_current = portfolio['crypto_currencies_hash'][coin['symbol']]['amount'] * \
                portfolio['crypto_currencies_hash'][coin['symbol']]['price_usd'] * 100 / portfolio['total_value_fiat']

            coin.update({
                'percentage_optimal': percentage_optimal,
                'percentage_current': percentage_current,
                'amount_optimal': amount_optimal,
                'value_optimal': value_optimal,
                'divergence': divergence,
                'divergence_percentage': divergence_percentage,
                'value_fiat': coin['price_usd'] * portfolio['crypto_currencies_hash'][coin['symbol']]['amount']
            })

            portfolio['crypto_currencies_hash'][coin['symbol']].update(coin)

        portfolio['total_value_fiat'] = 0
        for _, value in portfolio['crypto_currencies_hash'].items():
            crypto_currencies.append(value)
            portfolio['total_value_fiat'] += value['value_fiat']

        portfolio['crypto_currencies'] = list(
            sorted(
                crypto_currencies,
                key=lambda alloc: -
                alloc['market_cap_usd']))
        for i in range(len(portfolio['crypto_currencies'])):
            if i < (config['top_size']):
                continue
            portfolio['crypto_currencies'][i]['percentage_optimal'] = 0
            portfolio['crypto_currencies'][i]['percentage_current'] = portfolio['crypto_currencies'][i]['amount'] * \
                portfolio['crypto_currencies'][i]['price_usd'] * 100 / portfolio['total_value_fiat']
            portfolio['crypto_currencies'][i]['amount_optimal'] = 0
            portfolio['crypto_currencies'][i]['value_optimal'] = 0
            portfolio['crypto_currencies'][i]['divergence'] = - portfolio['crypto_currencies'][i]['amount']
            portfolio['crypto_currencies'][i]['divergence_percentage'] = - 100
            portfolio['crypto_currencies_hash'][portfolio['crypto_currencies']
                                                [i]['symbol']] = portfolio['crypto_currencies'][i]

        portfolio['last_updated'] = int(time())

        return portfolio
