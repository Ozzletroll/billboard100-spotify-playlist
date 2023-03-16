import requests
from bs4 import BeautifulSoup
import datetime

get_date = True
while get_date:
    year = input("Choose a date to travel back to (YYYY-MM-DD):\n")

    try:
        InvDate = datetime.datetime.strptime(year, "%Y-%m-%d")
        print("Date valid")
        get_date = False
    except ValueError:
        print("Date invalid")
