import os, re, json, urllib.request, urllib.parse

user = os.environ["LASTFM_USER"]
key = os.environ["LASTFM_API_KEY"]

url = "https://ws.audioscrobbler.com/2.0/?" + urllib.parse.urlencode({
    "method": "user.getrecenttracks",
    "user": user,
    "api_key": key,
    "format": "json",
    "limit": 1,
})
with urllib.request.urlopen(url, timeout=20) as r:
    data = json.load(r)

track = data["recenttracks"]["track"]
if isinstance(track, list):
    track = track[0]

artist = track["artist"]["#text"]
title = track["name"]
playing = track.get("@attr", {}).get("nowplaying") == "true"
label = "now_playing:" if playing else "last_played:"

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

new_text = f"{label}\n> {artist} - {title}"
readme = re.sub(r"(?:now_playing|last_played):\n> .*", lambda m: new_text, readme)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
