import os
os.system("pip uninstall discord")
os.system("pip install git+https://github.com/dolfies/discord.py-self")
os.system("pip install discord==1.7.3")
os.system("pip uninstall discord.py")
os.system("pip install PyNaCl && pip install wavelink==1.3.3")
import os
import discord
import wavelink
import time
from discord.ext import commands
import requests
import threading
import sys
import asyncio
import json
from urllib.parse import urlparse, parse_qs

bot = commands.Bot(command_prefix=".")
    
with open("music.json", "r") as f:
    settings = json.load(f)
    port = settings["port"]
    host = settings["host"]
    password = settings["password"]

with open("settings.json", "r") as f:
    data = json.load(f)
    prefix = data["prefix"]
    volume = data["volume"]
    voice_channel = data["voice_channel"]
    discord_user_token = data["discord_user_token"]
    discord.http.Route.BASE = data["discord.http.Route.BASE"]

def clear():
    os.system("clear")

def title(topic: any):
    os.system(f"title {topic}")

def validate_token(discord_user_token):
    response = requests.get("https://canary.discord.com/api/v10/users/@me", headers={"Authorization": discord_user_token})
    return response.status_code in [200, 201, 204]

if not validate_token(discord_user_token):
    print(f"[{time.strftime('%H:%M:%S')}] | [ERROR] -> Invalid token.........")
    sys.exit()

def extract_youtube_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    return None

class MusicSelfbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_vc = None
        self.current_track = None
        self.playing = False

    @commands.Cog.listener()
    async def on_connect(self):
        current_time = time.strftime("%H:%M:%S")
        print(f"[{current_time}] | [INFO] -> {self.bot.user} Connected to Discord..........")
        print(f"[{current_time}] | [INFO] -> Connecting to voice channel..........")
        await wavelink.NodePool.create_node(bot=self.bot, host=host, port=port, password=password)
        await self.connect_vc()
        current_time = time.strftime("%H:%M:%S")
        print(f"[{current_time}] | [INFO] -> Connected to voice channel..........\n\n")
        await self.play_next_song()

    async def connect_vc(self):
        idk = self.bot.get_channel(int(voice_channel))
        self.current_vc: wavelink.Player = await idk.connect(cls=wavelink.Player)
        
    async def filters(self, ctx, player, filter):
        if filter == "nightcore":
            await player.set_filter(wavelink.Equalizer.boost(0.3))
            await ctx.send("Nightcore filter has been enabled.")
        elif filter == "bass":
            await player.set_filter(wavelink.Equalizer.boost(0.3))
            await ctx.send("Bass filter has been enabled.")
        elif filter == "vaporwave":
            await player.set_filter(wavelink.Equalizer.boost(0.3))
            await ctx.send("Vaporwave filter has been enabled.")
        elif filter == "clear":
            await player.set_filter(None)
            await ctx.send("Filters have been cleared.")
        else:
            await ctx.send("Invalid filter. Available filters: nightcore, bass, vaporwave, clear")

    async def play_next_song(self):
        self.playing = False
        current_time = time.strftime("%H:%M:%S")
        song_name = input(f"[{current_time}] | [INFO] -> Enter song name or YouTube URL -> ")
        try:
            youtube_id = extract_youtube_id(song_name)
            if youtube_id:
                query = f"https://www.youtube.com/watch?v={youtube_id}"
                song = await wavelink.YouTubeTrack.search(query=query, return_first=True)
            else:
                songs = await wavelink.YouTubeTrack.search(query=song_name)
                if not songs:
                    current_time = time.strftime("%H:%M:%S")
                    print(f"[{current_time}] | [ERROR] | ): No results found. Please try again.........")
                    await self.play_next_song()
                    return
                song = songs[0]
            await self.current_vc.play(song)
            self.current_track = song
            self.playing = True
            await self.update_console()
        except Exception as e:
            print(f"Error while searching or playing the track: {e}")
            await self.play_next_song()

    async def update_console(self):
        while self.playing:
            current_time = time.strftime("%H:%M:%S")
            position = self.current_vc.position // 1000
            duration = self.current_track.length // 1000
            pos_mins, pos_secs = divmod(position, 60)
            dur_mins, dur_secs = divmod(duration, 60)
            song_time = self.current_track
            song_info = f"[{current_time}] | [INFO] -> [{pos_mins:02}:{pos_secs:02} | {dur_mins:02}:{dur_secs:02}] -> {self.current_track.title}"
            print(song_info, end="\r", flush=True)
            await asyncio.sleep(1)
        print(" " * len(song_info), end="\r")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track, reason):
        if reason == 'FINISHED':
            await self.play_next_song()

client = commands.Bot(command_prefix=prefix, case_insensitive=False, self_bot=True, intents=discord.Intents.all())
client.add_cog(MusicSelfbot(client))
loop = asyncio.get_event_loop()
loop.create_task(client.start(discord_user_token, bot=False))
threading.Thread(target=loop.run_forever).start()

while True:
    pass
