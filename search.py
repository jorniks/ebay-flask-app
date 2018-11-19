#!/usr/bin/env python

import os
import sys
import pprint
import locale
import time
import datetime
import isodate
import ebaysdk
from ebaysdk.finding import Connection as finding
from ebaysdk.exception import ConnectionError
from bs4 import BeautifulSoup

from flask import Flask
from flask import request, render_template, jsonify


HTML_OUTPUT = """
    <div class=\"col-lg-6\">
        <div class=\"box wow fadeInLeft\">
            <div class=\"icon"><i class=\"ion-ios-stopwatch-outline\"></i></div>
            <h4 class=\"title\">%s</h4>
            <ul>
                <li>Price: $ %s</li>
                <li>Seller: %s</li>
                <li>Condition: %s</li>
                <li>Listing Type: %s</li>
            </ul>
            <small><a href="%s" target="_blank">Go to site</a></small>
        </div>
    </div><br>"""

# Instantiate our Flask class.
app = Flask(__name__)


# Decide which URL will trigger everything...
@app.route('/')
def ebay_serve_page():
    return render_template("index.html")


def file_clear_html():
    file = open("static/result.html", 'r+')
    contents = file.read().split("\n")
    file.seek(0)
    file.truncate()
    file.close()


def file_write_html(items_to_write):
    file_clear_html()
    with open("static/result.html", 'w') as f:
        for item in items_to_write:
            f.write("%s" % item)

# Grab search string entered by user...
@app.route('/ebay_page_post', methods=['GET', 'POST'])
def ebay_page_post():
    if request.method == 'POST':

        #Get json format of the text sent by Ajax
        search = request.json['search']

        try:
            #ebaysdk code starts here
            api = finding(appid='JohnOkek-hybridse-PRD-5c2330105-9bbb62f2', config_file = None)
            api_request = {'keywords':search, 'outputSelector': 'SellerInfo', 'categoryId': '293'}
            response = api.execute('findItemsAdvanced', api_request)
            soup = BeautifulSoup(response.content, 'lxml')

            items = soup.find_all('item')

            # This will be returned
            items_found = []

            for item in items:
                cat = item.categoryname.string.lower()
                title = item.title.string.strip()
                price = float(item.currentprice.string)
                url = item.viewitemurl.string.lower()
                seller = item.sellerusername.text
                listingtype = item.listingtype.string
                condition = item.conditiondisplayname.string

                print ('____________________________________________________________')
                
                # Adding the item found in the collection
                items_found.append(HTML_OUTPUT % (title,
                                                price,
                                                seller,
                                                condition,
                                                listingtype,
                                                url))

            file_write_html(items_found)
            return "1"

        except ConnectionError as e:
            return jsonify(e)



if __name__ == '__main__':
    app.run(debug = True)
