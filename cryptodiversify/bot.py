#!/usr/bin/env python

import threading
import logging
import json

from time import sleep

from .market import Market
from .portfolio import Portfolio

log = logging.getLogger(__name__)


class CryptoDiversify:
    def __init__(self, config):
        self.__config = config
        self.__threads = []

        self.__market_obj = Market(config)
        self.__market = self.__market_obj.request_market()
        self.__portfolio_obj = Portfolio(config, self.__market)
        self.__portfolio = {}

    @staticmethod
    def buy_sell(divergence, divergence_percentage, amount,
                 amount_optional, swap_threshold_percentage):
        result = {'buy': '', 'sell': ''}
        if abs(divergence_percentage) > swap_threshold_percentage:
            if amount < amount_optional:
                result['buy'] = divergence
            else:
                result['sell'] = abs(divergence)

        return result

    def start(self):
        log.info("Starting CryptoDiversify...")
        log.debug("Creating threads.")
        t_market_updater = threading.Thread(
            name="MarketUpdater",
            target=self.__MarketUpdater
        )
        t_market_updater.daemon = True
        self.__threads.append(t_market_updater)
        t_portfolio_updater = threading.Thread(
            name="PortfolioUpdater",
            target=self.__PortfolioUpdater
        )
        t_portfolio_updater.daemon = True
        self.__threads.append(t_portfolio_updater)
        t_run_bot = threading.Thread(name="CryptoDiversify", target=self.__Run)
        t_run_bot.daemon = True
        self.__threads.append(t_run_bot)

        log.debug("Starting threads.")
        t_market_updater.start()
        t_portfolio_updater.start()
        t_run_bot.start()

        log.debug("Threads started: {}".format(self.__threads))
        return True

    def __MarketUpdater(self):
        while True:
            self.__market = self.__market_obj.request_market()
            log.debug("Market updated.")
            sleep(10)

    def __PortfolioUpdater(self):
        sleep(1)
        while True:
            self.__portfolio = self.__portfolio_obj.evaluate_portfolio(
                self.__market_obj.calc_allocations(
                    self.__config,
                    self.__market_obj.get_top_market(
                        self.__market, self.__config
                    )
                ),
                self.__portfolio_obj.get_portfolio(),
                self.__market,
                self.__config
            )
            with open(self.__config['portfolio_data_path'], 'w') as f:
                json.dump(self.__portfolio, f, sort_keys=True, indent=4)

            log.debug("Portfolio updated.")
            sleep(10)

    def __Run(self):
        sleep(5)
        swap_threshold_percentage = self.__config['swap_threshold_percentage']
        while True and self.__portfolio.get('crypto_currencies', None):
            log.debug("CryptoDiversify running.")
            print("\n{:<17} {:<10} {:<10} {:<20} {:<15} {:<20} {:<20} \n".format(
                'Coin', '% Optimal', '% Current', 'Optimal Amount',
                '% Divergence', 'BUY', 'SELL'
            )
            )
            for coin in self.__portfolio['crypto_currencies']:
                decision = self.buy_sell(
                    coin['divergence'],
                    coin['divergence_percentage'],
                    coin['amount'],
                    coin['amount_optimal'],
                    swap_threshold_percentage
                )
                print("{:<17} {:<10.2f} {:<10.2f} {:<20} {:<15.2f} {:<20} {:<20} ".format(
                    coin['id'],
                    coin['percentage_optimal'],
                    coin['percentage_current'],
                    coin['amount_optimal'],
                    coin['divergence_percentage'],
                    decision['buy'],
                    decision['sell']
                )
                )
            print("\n{:<25} ${:<18}".format(
                'Estimated Total Value:', self.__portfolio['total_value_fiat']
            )
            )
            print("\n")
            sleep(30)
