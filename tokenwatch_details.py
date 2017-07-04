#!/usr/bin/env python

"""
tokenwatch_details.py: An application to download the details pages for each entry from the tokenwatch.net all assets table data

Dependencies:

$ virtualenv env
$ pip install beautifulsoup4 lxml numpy pandas requests tabulate

Usuage:

$ python tokenwatch_details.py

History:

07-03-2017 : Created script
"""

# NOTES:
# Sometimes the main page doesn't have a symbol but the sub-page does. See TransActive Grid
# https://tokenmarket.net/blockchain/ethereum/assets/transactive-grid/

# All have names but some don't have symbols, status, whitepapers or blogs
# Do all have web sites?
#
# Not having a status can mean they are running. Are they trading? Not sure
# Some have no status, do have a ticker and a token but don't have a whitepaper. See https://www.openledger.info/

# Some whitepapers are not pdf links
# See https://hackernoon.com/musicoin-free-creations-while-rewarding-creators-2832f7d2bd33

# Other useful links;
# website, blog, whitepaper, facebook, twitter, linkedin, slack, telegram chat, github

# Some pages have a marketing video

import os
import requests
import shutil
import tabulate
import time
import tokenwatch as t
from bs4 import BeautifulSoup


def make_dir(name):
    # Put everything in a `data` subdirectory. This could be a setting grabbed from an environment variable
    path = "data/" + name
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_dir(name):
    return make_dir(name)


def get_details_tables(url):
    html = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, "lxml")
    tables = soup.findAll("table", {"class": "table-asset-data"})
    return tables


def get_details_table(url):
    tables = get_details_tables(url)
    # the last table on the page looks to be the one we want
    table = tables[-1]
    return table


def get_table_details(table):
    details = {}
    for td in table.find_all('td'):
        key = td.text.strip().split(' ')[0].lower()
        vals = td.find_all('a')
        if vals:
            value = vals[0]['href']
        else:
            value = '-'
        details[key] = value
    return details


def download_file(filename, url):
    try:
        r = requests.get(url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    except:
        print "Error trying to download: " + url
    return filename


def get_whitepaper(name, details):
    try:
        whitepaper_link = details['whitepaper']
        if whitepaper_link != '-':
            # only download if the link has a pdf in it
            print whitepaper_link
            head = requests.head(whitepaper_link, headers={'User-agent': 'Mozilla/5.0'})
            # Some servers doesn't return the applcation/pdf type properly
            # As a double check look at the url
            if head.headers['Content-Type'] == 'application/pdf' or head.url.find(".pdf") > 0:
                whitepaper_filename = get_dir(name) + "/" + name + "-whitepaper.pdf"
                download_file(whitepaper_filename, whitepaper_link)
                print whitepaper_filename
            else:
                print "Unknown whitepaper type: " + whitepaper_link
        else:
            print "Unavailable whitepaper for " + name
    except:
        print "No whitepaper link in dictionary"


def save_details(name, details):
    str = tabulate.tabulate([(k, v) for k, v in details.items()])
    filename = get_dir(name) + "/details.txt"
    file = open(filename, "w")
    file.write(str)
    file.close()


def process_row(row):
    details_link = row['LINK']
    name = row['NAME'].replace(' ', '-').lower()
    print name, details_link
    table = get_details_table(details_link)
    details = get_table_details(table)
    print details
    save_details(name, details)
    get_whitepaper(name, details)


def get_details(df):
    for index, row in df.iterrows():
        process_row(row)
        print "Waiting 60 seconds"
        time.sleep(60)


def run():
    df = t.process().sort_values(['NAME'])
    get_details(df)


if __name__ == '__main__':
    run()
