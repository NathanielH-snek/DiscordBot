# utils/models.py
import asyncio
import functools
from collections import deque
from typing import Dict

import discord
import discord.utils
import yt_dlp
from discord.ext import commands


class Playlist:
    def __init__(self, id: int):
        self.id = id
        #self.queue = Queue(maxsize=0)
        self.queue = deque()
        #self.songNames = deque()

    def add_song(self, songs: tuple):
        #self.queue.put(song)
        self.queue.append(songs)
    #def get_song(self):
        #return self.queue.get()
    

    def empty_playlist(self):
        self.queue.clear()

    def check_playlist(self):
        if len(self.queue) == 0:
            return True
        else:
            return False

    @property
    def is_empty(self):
        #return self.queue.empty()
        return Playlist.check_playlist(self)

    #@property
    #def track_count(self):
        #return self.queue.qsize()

class Requests:
    def __init__(self):
        #self.id = id
        self.queue = deque()
    
    def add_request(self, params):
        self.queue.append(params)
    
    def check_requests(self):
        if len(self.queue) == 0:
            return True
        else:
            return False
    
    def next(self):
        return self.queue.popleft()
    
    @property
    def is_empty(self):
        return Requests.check_requests(self)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlists: Dict[int, Playlist] = {}
        self.requests = Requests()
        self.is_processing = False
        
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
        if playlist is None:
            await ctx.send("`Nothing in queue`")
        elif playlist.queue is None:
            await ctx.send("`Nothing in queue`")
        elif (len(playlist.queue) == 0):
            await ctx.send("`Nothing in queue`")
        else:
            for i in playlist.queue:
                song, title = i
                list.append(f"`{playlist.queue.index(i)}: {title}`")
            list = "\n".join(list)
            list = str(list)[1:-1].replace("'", "")
            await ctx.send(f"`{list}`")

    #Remove an Item From Playlist Method FIX WIP
    @commands.command(name = 'remove')
    async def remove(self, ctx: commands.Context, arg: int):
        playlist = self.playlists.get(ctx.guild.id)
        if playlist is None:
            await ctx.send("`Nothing in queue`")
            return
        elif playlist.queue is None:
            await ctx.send("`Nothing in queue`")
            return
        elif (len(playlist.queue) == 0):
            await ctx.send("`Nothing in queue`")
            return
        else:
            try:
               int(arg)
               song, title = playlist.queue[arg]
               playlist.queue.remove((song, title))
               await ctx.send(f"`Playlist item {title} removed from playlist`")
            except:
                await ctx.send("`Invalid Argument`")
            

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
        FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options' : '-vn'}
        YDL_OPTIONS = {'format':'bestaudio', 'default_search':'auto'}
        await ctx.send("`Added Song to Search Queue`")
        self.requests.add_request((url,FFMPEG_OPTIONS,YDL_OPTIONS))
        if not self.is_processing:
            self.is_processing = True
            self.bot.loop.create_task(self._process_queue(ctx))
    
    async def _process_queue(self, ctx: commands.Context):
        while not self.requests.check_requests():
            urlsav,FFMPEG_OPTIONS,YDL_OPTIONS = self.requests.next()
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                await ctx.send("`Searching for songs(s)`")
                info = ydl.extract_info(urlsav, download=False)
                titlelist = []
                if 'entries' in info:
                    print("[DEBUG] Went to entries")
                    for i, item in enumerate(info['entries']):
                        try:
                            if i == 0:
                                url2 = info['entries'][i]['url']
                                title = info['entries'][i]['title']
                                try:
                                    source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                                except Exception as e:
                                    await ctx.send(f"`Failed to load audio source: {e}`")
                                    print(f"FFmpeg failed to load the source: {e}")
                                    continue
                                playlist = self.playlists.get(ctx.guild.id, Playlist(ctx.guild.id))
                                self.playlists[ctx.guild.id] = playlist
                                to_add = (source, title)
                                playlist.add_song(to_add)
                                await ctx.send(f"`Added {title} to the playlist.`")
                                self.bot.dispatch("play_command", ctx)
                            else:
                                url2 = info['entries'][i]['url']
                                title = info['entries'][i]['title']
                                try:
                                    source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                                except Exception as e:
                                    await ctx.send(f"`Failed to load audio source: {e}`")
                                    print(f"FFmpeg failed to load the source: {e}")
                                    continue
                                playlist = self.playlists.get(ctx.guild.id, Playlist(ctx.guild.id))
                                self.playlists[ctx.guild.id] = playlist
                                to_add = (source, title)
                                playlist.add_song(to_add)
                                await ctx.send(f"`Added {title} to the playlist.`")
                                self.bot.dispatch("play_command", ctx)
                        except Exception as e:
                            print(f"Adding Song Failed: {e}")
                            continue
                else:
                    print("[DEBUG] Went to formats")
                    url2 = info['url']
                    title = info['title']
                    try:
                        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                    except Exception as e:
                        await ctx.send(f"`Failed to load audio source: {e}`")
                        print(f"FFmpeg failed to load the source: {e}")
                    playlist = self.playlists.get(ctx.guild.id, Playlist(ctx.guild.id))
                    self.playlists[ctx.guild.id] = playlist
                    to_add = (source, title)
                    playlist.add_song(to_add)
                    await ctx.send(f"`Added {title} to the playlist.`")
                    self.bot.dispatch("play_command", ctx)
                
                
        
        self.is_processing = False
        print("[DEBUG] Finished processing the queue.")
            ###NEVER REACHES AWAIT FIX NEEDED?
            #await ctx.send(f"`Done Adding Songs`")
            #self.bot.dispatch("play_command", ctx, source, title)


    @commands.Cog.listener()
    async def on_play_command(self, ctx: commands.Context):
        if not ctx.voice_client.is_playing():
            self.bot.dispatch("track_end", ctx)

    @commands.Cog.listener()
    async def on_track_end(self, ctx: commands.Context):
        playlist = self.playlists.get(ctx.guild.id)
        if playlist and not playlist.is_empty:
            song, title = playlist.queue.popleft()
            #return await ctx.guild.voice_client.disconnect()
            await ctx.send(f"`Now playing: {title}`")
            try:
                ctx.guild.voice_client.play(song, after=functools.partial(lambda x: self.bot.loop.create_task(self.check_play(ctx))))
            except Exception as e:
                print(f"Song Failed to Play: {e}")
        
        else:
            await ctx.send("`No more songs in the playlist`")   

    @commands.Cog.listener()
    async def on_ready(self):
        print('`MusicPlayer module has successfully been initialized.`')

async def setup(bot):
  await bot.add_cog(Music(bot))
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
