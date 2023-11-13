# utils/models.py
from doctest import BLANKLINE_MARKER
import os
from smtplib import SMTPAuthenticationError
from syslog import LOG_USER
import discord
import discord.utils
import requests
from dotenv import load_dotenv
from discord.ext import commands
from discord import FFmpegPCMAudio
from pytube import YouTube
import yt_dlp
from requests import get
from discord.utils import get

import dice
import asyncio
import functools
from typing import Dict
import asyncio

from queue import Queue



class Playlist:
    def __init__(self, id: int):
        self.id = id
        #self.queue = Queue(maxsize=0)
        self.queue = []
        self.songNames = []

    def add_song(self, song: str):
        #self.queue.put(song)
        self.queue.append(song)
    def get_song(self):
        return self.queue.get()

    def empty_playlist(self):
        self.queue.clear()
        
    def check_playlist(list):
        if len(list) == 0:
            return True
        else:
            return False    

    @property
    def is_empty(self):
        #return self.queue.empty()
        return Playlist.check_playlist(self.queue)

    @property
    def track_count(self):
        return self.queue.qsize()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlists: Dict[int, Playlist] = {}

    async def check_play(self, ctx: commands.Context):
        client = ctx.voice_client
        while client and client.is_playing():
            await asyncio.sleep(1)
        
        self.bot.dispatch("track_end", ctx)

    #List Playlist Method FIX WIP
    @commands.command(name = 'playlist')
    async def playlist(self, ctx: commands.Context):
        playlist = self.playlists.get(ctx.guild.id)
        list = []
        if len(playlist.queue) == 0:
            await ctx.send("`Nothing in queue`")
        else:
            for i in playlist.queue:
                song, title = i
                list.append("`" + str(playlist.queue.index(i)) + ": " + str(title) + "`")
                await ctx.send(list)
    
    #Remove an Item From Playlist Method FIX WIP
    @commands.command(name = 'remove')
    async def remove(self, ctx: commands.Context, arg: int):
        playlist = self.playlists.get(ctx.guild.id)
        int = arg
        playlist.queue.pop(int)
        await ctx.send(f"`Playlist item {int} removed from playlist`")   

    @commands.command(name = 'stop')
    async def stop(self, ctx: commands.Context):
        playlist = self.playlists.get(ctx.guild.id)
        playlist.empty_playlist()
        server = ctx.message.guild
        voice_channel = server.voice_client
        if voice_channel.is_playing():             
            voice_channel.stop()
        await ctx.send('`Music stopped and playlist cleared`')

    @commands.command(name = 'play')
    async def play(self, ctx: commands.Context, *, url: str):
        if ctx.voice_client is None:
            if ctx.author.voice is None:
                return await ctx.send("`You are not connected to a voice channel`")
            else:
                voice_channel = ctx.author.voice.channel
                channel = ctx.author.voice.channel
                await voice_channel.connect()
                await ctx.send(f"`Connected to voice channel: '{channel}'`")
        else: 
            pass
        FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options' : '-vn'}
        YDL_OPTIONS = {'format':'bestaudio', 'default_search':'auto'}

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)

            if 'entries' in info:
                url2 = info['entries'][0]['url']
                title = info['entries'][0]['title']
            elif 'formats' in  info:
                url2 = info['url']
                title = info['title']
            
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            self.bot.dispatch("play_command", ctx, source, title)
        

    @commands.Cog.listener()
    async def on_play_command(self, ctx: commands.Context, song, title: str):
        playlist = self.playlists.get(ctx.guild.id, Playlist(ctx.guild.id))
        self.playlists[ctx.guild.id] = playlist
        to_add = (song, title)
        playlist.add_song(to_add)
        await ctx.send(f"`Added {title} to the playlist.`")
        if not ctx.voice_client.is_playing():
            self.bot.dispatch("track_end", ctx)

    @commands.Cog.listener()
    async def on_track_end(self, ctx: commands.Context):
        playlist = self.playlists.get(ctx.guild.id)
        if playlist and not playlist.is_empty:
            song, title = playlist.queue.pop()
        else:
            await ctx.send("`No more songs in the playlist`")
            return await ctx.guild.voice_client.disconnect()
        await ctx.send(f"`Now playing: {title}`")
        
        ctx.guild.voice_client.play(song, after=functools.partial(lambda x: self.bot.loop.create_task(self.check_play(ctx))))
        # for the above code, instead of functools.partial, you could also create_task on the next line, I just find using the `after` kwargs much better
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('`MusicPlayer module has successfully been initialized.`')

    
#Create Spell Class
###Old Class
#class Spell:
#    def __init__(self, name, cast_time, range, components, duration, description):
#        self.name = name
#        self.cast_time = cast_time
#        self.range = range
#        self.components = components
#        self.duration = duration
#        self.description = description
#    def __str__(self):
#        return f"{self.name}\n{self.cast_time}\n{self.range}\n{self.components}\n{self.duration}\n{self.description}"


#Create Character Class
class Character:
    def __init__(self, first, last, level, character_class):
        self.first = first
        self.last = last
        self.level = level
        self.character_class = character_class
    def __str__(self):
        return f"{self.first }{self.last }{self.level }{self.character_class}"