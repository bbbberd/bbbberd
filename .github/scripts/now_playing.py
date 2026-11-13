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
print(f"Last.fm says: {artist} - {title} (playing={playing})")

label = "now_playing:" if playing else "last_played:"

# Braille bars, seeded from the song name: same song, same pattern.
# Idle bars stay low.
blocks = "⣀⣤⣶⣿"
digest = hashlib.sha256(f"{artist}{title}".encode("utf-8")).digest()
levels = [b % 4 if playing else b % 2 for b in digest[:24]]
bars = "".join(blocks[l] for l in levels)
status = "[ playing ]" if playing else "[ idle ]"

new_text = f"{label}\n> {artist} - {title}\n  {bars}  {status}"

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

# Replace every non-empty line under "$ spotifyctl status"
pattern = r"(\$ spotifyctl status\n)(?:[^\n]+\n)+"
readme, count = re.subn(pattern, lambda m: m.group(1) + new_text + "\n", readme, count=1)

if count == 0:
    print("ERROR: could not find '$ spotifyctl status' in README.md")
    sys.exit(1)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
print("README updated.")
