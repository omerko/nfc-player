import subprocess

class Player:

    def play(album):
        player = subprocess.Popen(["vlc","--play-and-exit","/home/pi/music/album1.mp3"])

    def stop():
        ...
