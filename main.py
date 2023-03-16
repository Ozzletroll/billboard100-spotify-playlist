import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify authentication
client_id = os.environ["SPOTIPY_CLIENT_ID"]
client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
redirect_uri = os.environ["SPOTIPY_REDIRECT_URI"]

scope = "playlist-modify-private"
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        show_dialog=True,
    )
)

user_id = sp.current_user()["id"]

# Query user for the date they wish to scrape data from, and check the formatting is correct.
get_date = True
while get_date:
    date = input("Choose a date to travel back to (YYYY-MM-DD):\n")
    try:
        formatted_date = datetime.strptime(date, "%Y-%m-%d")
        print("Date valid")
        get_date = False
    except ValueError:
        print("Date invalid")

# Get webpage from Billboard 100 on target date
formatted_date = formatted_date.date()
target_url = f"https://www.billboard.com/charts/hot-100/{formatted_date}"

response = requests.get(url=target_url)
response.encoding = "utf-8"
webpage = response.text

# Format top 100 songs as list
soup = BeautifulSoup(webpage, "html.parser")
top_100 = soup.find_all(name="div", class_="o-chart-results-list-row-container")
song_list = []
for entry in top_100:
    song_title = entry.find(name="h3", id="title-of-a-story")
    artist = song_title.findNext("span")
    song_entry = {
        "artist": artist.getText().strip(),
        "title": song_title.getText().strip(),
    }

