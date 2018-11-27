#!/usr/bin/env python
import json
import logging
import requests
import sys
import os

from time import time
logging.getLogger("requests").setLevel(logging.WARNING)
log = logging.getLogger(__name__)


class Market:
    def __init__(self, config):
        self.__config = config

    def get_market(self):
        return self.request_market()

    def get_top_market(self, market, config):
        return list(sorted(market['crypto_currencies'], key=lambda alloc: alloc['rank']))[
            :config['top_size']]

    def calc_allocations(self, config, top_market):
        """Figure out ideal allocations for a given date"""

        total_cap = sum([coin['market_cap_usd'] for coin in top_market])

        for i in range(len(top_market)):
            top_market[i]['cap_ratio'] = (
                top_market[i]['market_cap_usd'] / total_cap)

        allocations = list(
            sorted(
                top_market,
                key=lambda alloc: -
                alloc['cap_ratio']))  # sort by descending ratio

        for i in range(len(allocations)):
            alloc = allocations[i]

            if alloc['cap_ratio'] > config['cap_ratio_limit']:
                # the amount of % that needs to be spread to the other coins
                overflow = alloc['cap_ratio'] - config['cap_ratio_limit']
                alloc['cap_ratio'] = config['cap_ratio_limit']

                remaining_allocs = allocations[i + 1:]

                # market cap of the remaining coins
                total_nested_cap = sum([n_alloc['market_cap_usd']
                                        for n_alloc in remaining_allocs])
                new_allocs = list()

                for n_alloc in remaining_allocs:
                    # percentage of the remainder this makes up (sums to 100%)
                    cap_fraction = n_alloc['market_cap_usd'] / total_nested_cap
                    n_alloc['cap_ratio'] += overflow * \
                        cap_fraction             # weighted
                    new_allocs.append(n_alloc)

                allocations = allocations[:i + 1] + new_allocs

        return allocations

    def request_market(self):
        try:
            response = requests.get("https://api.coinmarketcap.com/v1/ticker/")
            data = json.loads(response.content)

            # Convert data json into dict
            log.debug("Data obtained from web source.")
            market = {
                'crypto_currencies': [],
                'crypto_currencies_hash': {},
                'last_updated': int(time())
            }

            for d in data:
                d.update({
                    'symbol': self.get_binance_symbol(d['symbol']),
                    'price_btc': float(d['price_btc']),
                    'price_usd': float(d['price_usd']),
                    'rank': int(d['rank']),
                    'last_updated': int(d['last_updated']),
                    '24h_volume_usd': float(d['24h_volume_usd']) if d['24h_volume_usd'] else 0.00,
                    'market_cap_usd': float(d['market_cap_usd']) if d['market_cap_usd'] else 0.00,
                    'percent_change_1h': float(d['percent_change_1h']) if d['percent_change_1h'] else 0.00,
                    'percent_change_24h': float(d['percent_change_24h']) if d['percent_change_24h'] else 0.00,
                    'percent_change_7d': float(d['percent_change_7d']) if d['percent_change_7d'] else 0.00
                })
                if d['symbol'] not in self.__config.get('crypto_not_binance', []):
                    market['crypto_currencies'].append(d)
                    market['crypto_currencies_hash'][d['symbol']] = d

            # Output collected data into file
            with open(self.__config['market_data_path'], 'w') as f:
                log.debug("Dumping Data to data/market.json.")
                json.dump(market, f, sort_keys=True, indent=4)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error("Exception in requesting market: {} {}: {}".format(exc_type, fname, exc_tb.tb_lineno))
            log.warning("No data from web source. Loading file")
            # Get last data from file
            with open(self.__config['market_data_path'], 'r') as f:
                market = json.load(f)

        return market

    @staticmethod
    def get_binance_symbol(symbol):
        if symbol == 'BCH':
            return 'BCHABC'
        if symbol == 'BSV':
            return 'BCHSV'
        if symbol == 'MIOTA':
            return 'IOTA'

        return symbol
