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
    song_list.append(song_entry)

# Create spotify playlist using scraped songs
playlist_name = f"Billboard 100: {formatted_date}"
playlist_desc = f"The top 100 songs as of {formatted_date}."

playlist_uris = []

for song in song_list:
    query = f"{song['title']} {song['artist']}"
    query = query.replace(" ", "%20").lower()
    search = sp.search(
        q=query,
        type="track",
    )

    # Test to see if spotify actually has the songs available and append them to playlist_uris.
    try:
        uri = search["tracks"]["items"][0]["uri"]
    except IndexError:
        print("No song found.")
    else:
        playlist_uris.append(uri)

# Create playlist based on playlist_uris list
playlist = sp.user_playlist_create(
    user=user_id,
    name=playlist_name,
    public=False,
    description=playlist_desc,
)

playlist_id = playlist["id"]
# Add all playlist songs to final playlist
sp.playlist_add_items(
    playlist_id=playlist_id,
    items=playlist_uris,
)
