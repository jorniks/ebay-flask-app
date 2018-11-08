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


# Instantiate our Flask class.
app = Flask(__name__)


# Decide which URL will trigger everything...
@app.route('/')
def ebay_serve_page():
    return render_template("index.html")

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

            totalentries = int(soup.find('totalentries').text)
            items = soup.find_all('item')

            # This will be returned
            itemsFound = {}

            # This index will be incremented 
            # each time an item is added
            index = 0

            for item in items:
                cat = item.categoryname.string.lower()
                title = item.title.string.lower().strip()
                price = int(round(float(item.currentprice.string)))
                url = item.viewitemurl.string.lower()
                seller = item.sellerusername.text.lower()
                listingtype = item.listingtype.string.lower()
                condition = item.conditiondisplayname.string.lower()

                print ('____________________________________________________________')
                 
                #return json format of the result for Ajax processing
            #return jsonify(cat + '|' + title + '|' + str(price) + '|' + url + '|' + seller + '|' + listingtype + '|' + condition)

                # Adding the item found in the collection
                # index is the key and the item json is the value
                itemsFound[index] = jsonify(cat + '|' + title + '|' + str(price) + '|' + url + '|' + seller + '|' + listingtype + '|' + condition + '#')

                # Increment the index for the next items key
                index+=1

            for key in itemsFound:
                return itemsFound[key]

        except ConnectionError as e:
            return jsonify(e)
        
    #return jsonify(search)



if __name__ == '__main__':
    app.run(debug=True)