#!/usr/bin/env python

import os
import sys
import pprint
import locale
import time
import datetime
import ebaysdk
from ebaysdk.finding import Connection as finding
from ebaysdk.exception import ConnectionError
from bs4 import BeautifulSoup

from flask import Flask
from flask import request, render_template, jsonify


HTML_OUTPUT = """
    <div class=\"col-lg-6\">
        <div class=\"box wow fadeInLeft\">
            <h4 class=\"title\">%s</h4>
            <ul>
                <li>Price: $ %s | &#8358; %s </li>
                <li>Condition: %s</li>
                <li>Listing Type: %s</li>
            </ul>
            <small><a href="%s" target="_blank">Go to site</a></small>
        </div>
    </div>"""

# Instantiate our Flask class.
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


# Decide which URL will trigger everything...
@app.route('/')
def ebay_serve_page():
    empty_folder()
    return render_template("index.html")

def empty_folder():
    folder = 'static'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

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

            if response.reply.ack == 'Success':
                for item in items:
                    pic = item.pictureURLLarge
                    title = item.title.string.strip()
                    price = float(item.currentprice.string)
                    url = item.viewitemurl.string.lower()
                    seller = item.sellerusername.text
                    listingtype = item.listingtype.string
                    condition = item.conditiondisplayname.string
                    naira = price * 365

                    print ('____________________________________________________________')
                    
                    # Adding the item found in the collection
                    items_found.append(HTML_OUTPUT % (title,
                                                    price,
                                                    naira,
                                                    condition,
                                                    listingtype,
                                                    url))

                f = open("static/"+search+".html", 'w+')
                for item in items_found:
                    f.write("%s" % item)
                f.close()
                return "1"
            else:
                return "Search failed, please make sure you are searching for electronic products only."

        except ConnectionError as e:
            return jsonify(e)



if __name__ == '__main__':
    app.run(debug = True)
