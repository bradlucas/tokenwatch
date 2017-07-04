#!/usr/bin/env python

"""
tokenwatch.py: An application to download the tokenwatch.net all-assets table data for further processing

Dependencies:

$ virtualenv env
$ pip install beautifulsoup4 lxml numpy pandas requests tabulate

Usuage:

$ python tokenwatch.py [-c|-t]

    -c Return data in csv format
    -t Return data in tabulated format

History:

07-02-2017 : Created script
"""

__author__ = "Brad Luicas"
__copyright__ = "Copyright 2017, Brad Lucas"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Brad Lucas"
__email__ = "brad@beaconhill.com"
__status__ = "Production"


import pandas as pd
import requests
from bs4 import BeautifulSoup
import tabulate
import sys


def get_table():
    url = 'https://tokenmarket.net/blockchain/all-assets'
    html = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table.table-assets")
    return table


def get_data(tds):
    link = tds[3].find("a")['href']  # tds[1].find("a")['href']
    status =  tds[2].text.strip().replace(u'\xa0', ' ')
    name =  tds[3].text.strip().split("\n")[0]
    symbol =  tds[4].text.strip()
    description =  tds[5].text.encode('ascii', 'ignore').strip().replace('\n', '')
    return [symbol, name, status, description, link]


def get_rows(table):
    return table.find_all("tr")


def get_tds(row):
    return row.find_all("td")


def process_table(table):
    rows = get_rows(table)
    cnt = 1
    rtn = []
    for row in rows[1:]:
        tds = get_tds(row)
        data = get_data(tds)
        rtn.append(data)
        cnt += 1
    return rtn


def build_dataframe(records):
    return pd.DataFrame.from_records(records, columns=['SYMBOL', 'NAME', 'STATUS', 'DESCRIPTION', 'LINK'])


def process():
    return build_dataframe(process_table(get_table()))


def report_txt():
    df = process()
    print tabulate.tabulate(df.sort_values(['STATUS'], ascending=False), showindex='false')


def report_csv():
    df = process().sort_values(['STATUS'], ascending=False)
    print df.to_csv(index=False)


if __name__ == '__main__':
    if len(sys.argv) > 0 and sys.argv[0] == '-c':
        report_csv
    else:
        report_txt()
