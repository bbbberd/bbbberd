import os, re, json, sys, hashlib, urllib.request, urllib.parse

user = os.environ["LASTFM_USER"].strip()
key = os.environ["LASTFM_API_KEY"].strip()

url = "https://ws.audioscrobbler.com/2.0/?" + urllib.parse.urlencode({
    "method": "user.getrecenttracks",
    "user": user,
    "api_key": key,
    "format": "json",
    "limit": 1,
})
with urllib.request.urlopen(url, timeout=20) as r:
    data = json.load(r)

if "error" in data:
    print("Last.fm error:", data.get("message"))
    sys.exit(0)

tracks = data.get("recenttracks", {}).get("track", [])
if isinstance(tracks, dict):
    tracks = [tracks]
if not tracks:
    print("No recent tracks found, leaving README unchanged.")
    sys.exit(0)

track = tracks[0]
artist = track["artist"]["#text"]
title = track["name"]
playing = track.get("@attr", {}).get("nowplaying") == "true"
label = "now_playing:" if playing else "last_played:"

# Bars are seeded from the song name: same song, same pattern.
# When nothing is playing, the bars stay low.
blocks = "▁▂▃▄▅▆▇█"
digest = hashlib.sha256(f"{artist}{title}".encode("utf-8")).digest()
levels = [b % 8 if playing else b % 3 for b in digest[:24]]
bars = "".join(blocks[l] for l in levels)
status = "[ playing ]" if playing else "[ idle ]"

new_text = f"{label}\n> {artist} - {title}\n  {bars}  {status}"

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

pattern = r"(?:now_playing|last_played):\n> .*(?:\n {2}[\u2581-\u2588].*)?"
readme = re.sub(pattern, lambda m: new_text, readme)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
