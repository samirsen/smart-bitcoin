#!/usr/bin/env python

"""Run prediction on bitcoin data from OKCoin using Bayesian Regression Model"""

import requests
import argparse
from datetime import datetime
from pymongo import MongoClient
import logging

_version_string = "samirsen_06_22_17"

client = MongoClient()
database = client['okcoindb']
collection = database['historical_data']

_btc_url = "https://www.okcoin.com/api/v1/ticker.do?symbol=btc_usd"
_ltc_url = "https://www.okcoin.com/api/v1/ticker.do?symbol=ltc_usd"
_eth_url = "https://www.okcoin.com/api/v1/ticker.do?symbol=eth_usd"

# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-10s %(message)s',
                    datefmt='%m-%d-%Y %H:%M:%S',
                    filename="debug.log",
                    filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logging.info('Log file established')
logging.info('Version: ' + _version_string)

_help_intro = """btc-predict is a script that predicts bitcoin prices."""


def help_formatter(prog):
    """ So formatter_class's max_help_position can be changed. """
    return argparse.HelpFormatter(prog, max_help_position=40)


def set_args():
    parser = argparse.ArgumentParser(description=_help_intro,
                                     formatter_class=help_formatter)
    subparsers = parser.add_subparsers(help=(
        'subcommands; add "-h" or "--help" '
        'after a subcommand for its parameters'),
        dest='subparser_name'
    )

    index_parser = subparsers.add_parser(
        'index',
        help='creates index of price data from OKCoin'
    )
    predict_parser = subparsers.add_parser(
        'predict',
        help=('predicts cryptocurrency price using bayesian regression')
    )


def collect_data():
    """Gather market data from OKCoin Spot Price API and insert them into a
       MongoDB collection."""
    ticker = requests.get('https://www.okcoin.com/api/v1/ticker.do?symbol=btc_usd').json()
    depth = requests.get('https://www.okcoin.com/api/v1/depth.do?symbol=btc_usd&size=60').json()
    date = datetime.fromtimestamp(int(ticker['date']))
    price = float(ticker['ticker']['last'])
    v_bid = sum([bid[1] for bid in depth['bids']])
    v_ask = sum([ask[1] for ask in depth['asks']])
    collection.insert({'date': date, 'price': price, 'v_bid': v_bid, 'v_ask': v_ask})
    print(date, price, v_bid, v_ask)


def main():
    """Run tick() at the interval of every ten seconds."""
    set_args()
    collect_data()


if __name__ == '__main__':
    main()