I think this is exactly the right first milestone. At this stage, don't worry about plugins, Jellyfin, or state management. Just prove that the basic interaction works:

> **Place NFC tag → media starts**
> **Remove NFC tag → media stops**

Once you have that, everything else is an implementation detail.

## I'd structure the prototype like this

```
nfc-player/
│
├── main.py
├── player.py
├── albums.json
├── music/
│   ├── album1.mp3
│   └── album2.mp3
└── youtube/
```

---

## Step 1 - Read an album ID

Instead of reading only the UID, you'll eventually read something like:

```
album://album1
```

For now you can even fake it:

```python
album_id = "album1"
```

until you've written data to an NFC tag.

---

## Step 2 - Album database

Keep it very simple.

```json
{
    "album1": {
        "type": "local",
        "path": "/home/pi/nfc-player/music/album1.mp3"
    },

    "album2": {
        "type": "youtube",
        "url": "https://www.youtube.com/watch?v=xxxxxxxx"
    }
}
```

Later this can become:

```
Spotify URI

Jellyfin ID

Local path

Podcast

...
```

---

## Step 3 - One Player class

Something like:

```python
class Player:

    def play(album):
        ...

    def stop():
        ...
```

Then your NFC code doesn't know anything about YouTube or MP3s.

It simply does:

```python
player.play(album)
```

---

# Testing local MP3

For local files I'd actually use **VLC**.

Install:

```bash
sudo apt install vlc
```

Then in Python:

```python
import subprocess

player = subprocess.Popen([
    "vlc",
    "--play-and-exit",
    "/home/pi/music/album1.mp3"
])
```

Stopping:

```python
player.terminate()
```

That's literally enough for a first prototype.

---

# Testing YouTube

I'd avoid opening Chromium.

Instead use **yt-dlp + VLC**.

Install:

```bash
sudo apt install yt-dlp
```

Get the direct stream URL:

```bash
yt-dlp -g https://youtube.com/...
```

Then give that URL directly to VLC.

Advantages:

* no browser
* no ads
* easy to stop
* one process to manage

---

# Detecting removal

You already have:

```python
uid = pn532.read_passive_target(timeout=0.5)
```

So your loop can simply become:

```python
current_tag = None

while True:

    uid = pn532.read_passive_target(timeout=0.2)

    if uid:

        if uid != current_tag:

            current_tag = uid

            player.play(album)

    else:

        if current_tag is not None:

            player.stop()

            current_tag = None
```

That's basically the behavior you described.

---

# Even simpler state machine

I always like drawing these.

```
          No Tag
             │
             │ tag detected
             ▼
       Lookup Album
             │
             ▼
      Start Playback
             │
             │ tag removed
             ▼
      Stop Playback
             │
             └─────────────┐
                           │
                    new tag detected
```

This is probably only 50–100 lines of Python.

---

# One thing I'd change from your original plan

You mentioned:

> "open a media playing app or browser"

For the prototype, I'd try to **avoid browsers completely**.

Browsers are surprisingly awkward to control programmatically:

* opening tabs
* focusing windows
* stopping playback
* autoplay restrictions

Instead, use a media player like **VLC**. It gives you:

* one process to start
* one process to stop
* local files
* YouTube streams (via `yt-dlp`)
* network streams
* playlists

That means your code doesn't care whether the source is an MP3 or a YouTube URL. It simply tells VLC what to play.

Later, when you add Spotify or Jellyfin plugins, those plugins can decide whether they launch VLC, use a native API, or use another playback engine—but your NFC logic stays exactly the same. I think that's a cleaner separation of concerns for the architecture you're aiming for.
