#importing required libraries
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from time import sleep
import smtplib

pricedict = {}

#search for my user agent in your browser and replace it after "User-Agent:" inside quotes
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

#to send email alerts about price drops
# i referred https://www.geeksforgeeks.org/send-mail-gmail-account-using-python/
def send_email(new_price, price_diff, name):

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.login("senders_email@gmail", "senders password")
    message = f"Price of {name} has gone down to {new_price}, a difference of {price_diff}."
    s.sendmail("sender_email@gmail", "receivers_mail@gmail.com", message)
    s.quit()

#to track change in price
def track_change_in_price():

    watchlist = get_watchlist()

    if watchlist == {}:
        print("\nNo item in watchlist.")
    else:

        for item in watchlist:
            page = get_pages(watchlist[item]["url"])
            new_price = current_price(page)
            price_diff = new_price - watchlist[item]["price"]

            if new_price != watchlist[item]["price"]:
                if new_price < watchlist[item]["price"]:
                    print(watchlist[item]["name"], " price down to", new_price, ", difference of ", price_diff)
                    watchlist[item]["price"] = new_price
                    watchlist[item]["last checked"] = str(datetime.now())[:19]
                    send_email(new_price, price_diff, watchlist[item]["name"])
                    print("Sent email alert.")
                    watchlist.update(watchlist)
                    write_watchlist(watchlist)
                else:
                    print(watchlist[item]["name"], " price has gone up to", new_price, ", difference of ", price_diff)
                    watchlist[item]["price"] = new_price
                    watchlist[item]["last checked"] = str(datetime.now())[:19]
                    watchlist.update(watchlist)
                    write_watchlist(watchlist)
            
            else:
                print("\nNo change in price so far for ", watchlist[item]["name"])

#to show watchlist
def show_watchlist():

    watchlist = get_watchlist()
    
    if watchlist == {}:
        print("Your watchlist is empty.")
    else:
        print("Items on your watchlist are:\n")

        for item in watchlist:
            print(watchlist[item]["name"]," priced at ", watchlist[item]["price"], " as of ",watchlist[item]["last checked"])
            print()

#to get webpages
def get_pages(url):

    try:
        page = requests.get(url, headers = headers)
        return page
    
    except:
        print("Page not found!", page.status_code)

#to get current price from webpage
def current_price(page):

    price_page = BeautifulSoup(page.content, 'html.parser')

    try:
        if price_page.find(id = "priceblock_ourprice"):
            price = price_page.find(id = "priceblock_ourprice").get_text()
        else:
            price = price_page.find(id = "priceblock_dealprice").get_text()

        price= price.replace(',','').replace('₹','').replace(' ','').strip()
        price = float(price)

        return price

    except:
        print("Could not retreive price")
        return 0

#to load watchlist from watchlist.json
def get_watchlist():

    with open('watchlist.json') as rf:
        watchlist = json.load(rf)
    return watchlist

#to write watchlist into watchlist.json
def write_watchlist(price_dict):
    
    with open('watchlist.json', 'w') as wf:
        watchlist = json.dump(price_dict, wf, indent = 4)

#to add item to watchlist
def add_to_watchlist():

    name = str(input("Enter name of the product:"))
    url = input("Enter amazon url of product:")
    name_in_lower = name.lower()

    page = get_pages(url)
    price = current_price(page)
    print("\n",name,"added to your watchlist.")

    pricedict[name_in_lower] ={}
    pricedict[name_in_lower]["name"] = name
    pricedict[name_in_lower]["url"] = url
    pricedict[name_in_lower]["price"] = price
    pricedict[name_in_lower]["last checked"] = str(datetime.now())[:19]

    watchlist = get_watchlist()
    watchlist.update(pricedict)
    write_watchlist(watchlist)

#to remove item from watchlist
def remove_from_watchlist():
    
    name = input("Enter name of the product:")
    name_lower = name.lower()

    watchlist = get_watchlist()

    try:
        del(watchlist[name_lower])
        watchlist.update(watchlist)
        write_watchlist(watchlist)
        print("\n", name, " removed from your watchlist.")
    except:
        print("Item not found!")

#main
if __name__ == "__main__":
    
    while True:
        print()
        print("-"*10, end = "")
        print("Amazon Price Tracker", end = "")
        print("-"*10)
        print("\n\t   1.Track")
        print("\t   2.Add to watchlist")
        print("\t   3.Show watchlist")
        print("\t   4.Remove from watchlist")
        print("\t   5.Exit")
        ch = int(input("\nEnter your option:"))

        if ch == 1:
            track_change_in_price()
        
        if ch == 2:
            add_to_watchlist()

        if ch == 3:
            show_watchlist()
    
        if ch == 4:
            remove_from_watchlist()

        if ch == 5:
            exit()
