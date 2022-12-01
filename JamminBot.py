# JamminBot.py
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
import youtube_dl
from requests import get
from discord.utils import get

import dice
import asyncio
import functools
from typing import Dict
import asyncio

from utilsModels import Playlist

#Create Spell Class
class Spell:
    def __init__(self, name, cast_time, range, components, duration, description):
        self.name = name
        self.cast_time = cast_time
        self.range = range
        self.components = components
        self.duration = duration
        self.description = description
    def __str__(self):
        return f"{self.name}\n{self.cast_time}\n{self.range}\n{self.components}\n{self.duration}\n{self.description}"

#Create Character Class
class Character:
    def __init__(self, first, last, level, character_class):
        self.first = first
        self.last = last
        self.level = level
        self.character_class = character_class
    def __str__(self):
        return f"{self.first }{self.last }{self.level }{self.character_class}"

#Spell List
Eldritch_Blast = Spell('Eldritch Blast', '1 action' , '120 feet' , 'V,S' , 'Instantaneous' , 'A beam of crackling energy streaks toward a creature within range. Make a ranged spell attack against the target. On a hit, the target takes 1d10 force damage. The spell creates more than one beam when you reach higher levels - two beams at 5th level, three beams at 11th level, and four beams at 17th level. you can direct the beams at the same target or at different ones. Make a separate attack roll for each beam.')
Mage_Hand = Spell('Mage Hand' , '1 action' , '30 feet' , 'V,S' , '1 minute' , "A spectral, floating hand appears at a point you choose within range. The hand lasts for the duration or until you dismiss it as an action. The hand vanishes if it is ever more than 30 feet away from you or if you cast this spell again. You can use your action to control the hand. You can use the hand to manipulate an object, open an unlocked door or container, stow or retrieve an item from an open container, or pour the contents out of a vial. You can move the hand up to 30 feet each time you use it. The hand can't attack, activate magical items, or carry more than 10 pounds.")
Minor_Illusion = ('Minor Illusion' , '1 action' , '30 feet' , 'S,M' , '1 minute' , "You create a sound or an image of an object within range that lasts for the duration. The illusion also ends if you dismiss it as an action or cast this spell again. If you create a sound, its volume can range from a whisper to a scream. It can be your voice, someone else's voice, a lion's roar, a beating of drums, or any other sound you choose. The sound continues unabated throughout the duration, or you can make discrete sounds at different times before the spell ends. If you create an image of an object - such as a chair, muddy footprints, or a small chest - it must be no larger than a 5-foot cube. The image can't create sound, light, smell, or any other sensory effect. Physical interaction with the image reveals it to be an illusion, because things can pass through it. If a creature uses its action to examine the sound or image, the creature can determine that it is an illusion with a successful Intelligence (Investigation) check against your spell save DC. If a creature discerns the illusion for what it is, the illusion becomes faint to the creature.")
Expeditious_Retreat = Spell('Expeditious Retreat' , '1 bonus action' , 'Self' , 'V,S' , 'Concentration, up to 10 minutes' , "This spell allows you to move at an incredible pace. When you cast this spell, and then as a bonus action on each of your turns until the spell ends, you can take the Dash action.")
Invisiblity = Spell('Invisibility' , '1 action' , 'Touch' , 'V,S,M' , 'Concentration, up to 1 hour' , "A creature you touch becomes invisible until the spell ends. Anything the target is wearing or carrying is invisible as long as it is on the target's person. The spell ends for a target that attacks or casts a spell. At Higher Levels: When you cast this spell using a spell slot of 3rd level or higher, you can target one additional creature for each slot level above 2nd.")
Misty_Step = Spell('Misty Step' , '1 bonus action' , 'Self' , 'V' , 'Instantaneous' , "Briefly surrounded by silvery mist, you teleport up to 30 feet to an unoccupied space that you can see.")
Shatter = Spell('Shatter' , '1 action' , '60 feet' , 'V,S,M' , 'Instantaneous' , "A sudden loud ringing noise, painfully intense, erupts from a point of your choice within range. Each creature in a 10-foot-radius sphere centered on that point must make a Constitution saving throw. A creature takes 3d8 thunder damage on a failed save, or half as much damage on a successful one. A creature made of inorganic material such as stone, crystal, or metal has disadvantage on this saving throw. A nonmagical object that isn't being worn or carried also takes the damage if it's in the spell's area. At Higher Levels: When you cast this spell using a spell slot of 3rd level or higher, the damage increases by 1d8 for each slot level above 2nd.")
Blink = Spell('Blink' , '1 action' , 'Self' , 'V,S' , '1 minutes' , "Roll a d20 at the end of each of your turns for the duration of the spell. On a roll of 11 or higher, you vanish from your current plane of existence and appear in the Ethereal Plane (the spell fails and the casting is wasted if you were already on that plane). At the start of you next turn, and when the spell ends if you are on the Ethereal Plane, you return to an unoccupied space of your choice that you can see within 10 feet of the space you vanished from. If no unoccupied space is available within that range, you appear in the nearest unoccupied space (chosen at random if more than one space is equally near). You can dismiss this spell as an action. While on the Ethereal Plane, you can see and hear the plane you originated from, which is cast in shades of gray, and you can't see anything more than 60 feet away. You can only affect and be affected by other creatures on the Ethereal Plane. Creature that aren't there can't perceive you or interact with you, unless they have the ability to do so.")
Plant_Growth = Spell('Plant Growth' , '1 action or 8 hours' , '150 feet' , 'V,S' , 'Instantaneous' , "This spell channels vitality into plants within a specific area. There are two possible uses for the spell, granting either immediate or long-term benefits. If you cast this spell using 1 action, choose a point within range. All normal plants in a 100-foot radius centered on that point become thick and overgrown. A creature moving through the area must spend 4 feet of movement for every 1 foot it moves. You can exclude one or more areas of any size within the spell's area from being affected. If you cast this spell over 8 hours, you enrich the land. All plants in a half-mile radius centered on a point within range become enriched for 1 year. The plants yield twice the normal amount of food when harvested.")
Summon_Fey = Spell('Summon Fey' , '1 action' , '90 feet' , 'V,S,M' , 'Concentration, up to 1 hour' , "You call forth a fey spirit. It manifests in an unoccupied space that you can see within range. This corporeal form uses the Fey Spirit stat block. When you cast the spell, choose a mood: Fuming, Mirthful, or Tricksy. The creature resembles a fey creature of your choice marked by the chosen mood, which determines one of the traits in its stat block. The creature disappears when it drops to 0 hit points or when the spell ends. The creature is an ally to you and your companions. In combat, the creature shares your initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don't issue any, it takes the Dodge action and uses its move to avoid danger. At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, use the higher level wherever the spell's level appears in the stat block.")
Green_Flame_Blade = Spell('Green Flame Blade' , '1 action' , 'Self 5-foot radius' , 'S,M' , 'Instantaneous' , "You brandish the weapon used in the spell's casting and make a melee attack with it against one creature within 5 feet of you. On a hit, the target suffers the weapon attack's normal effects, and you can cause green fire to leap from the target to a different creature of your choice that you can see within 5 feet of it. The second creature takes fire damage equal to your spellcasting ability modifier. This spell's damage increases when you reach certain levels. At 5th level, the melee attack deals an extra 1d8 fire damage to the target on a hit, and the fire damage to the second creature increases to 1d8 + your spellcasting ability modifier. Both damage rolls increase by 1d8 at 11th level (2d8 and 2d8) and 17th level (3d8 and 3d8).")
Lightning_Lure = Spell('Lightning Lure' , '1 action' , 'Self 15-foot radius' , 'V' , 'Instantaneous' , "You create a lash of lightning energy that strikes at one creature of your choice that you can see within 15 feet of you. The target must succeed on a Strength saving throw or be pulled up to 10 feet in a straight line toward you and then take 1d8 lightning damage if it is within 5 feet of you. This spell's damage increases by 1d8 when you reach 5th level (2d8), 11th level (3d8), and 17th level (4d8).")
Absorb_Elements = Spell('Absorb Elements' , '1 reaction, when you take acid, cold, fire, lightning, or thunder damage' , 'Self' , 'S' , '1 round' , "The spell captures some of the incoming energy, lessening its effect on you and storing it for your next melee attack. You have resistance to the triggering damage type until the start of your next turn. Also, the first time you hit with a melee attack on your next turn, the target takes an extra 1d6 damage of the triggering type, and the spell ends. At Higher Levels. When you cast this spell using a spell slot of 2nd level or higher, the extra damage increases by 1d6 for each slot level above 1st.")
Catapult = Spell('Catapult' , '1 action' , '60 feet' , 'S' , 'Instantaneous' , "Choose one object weighing 1 to 5 pounds within range that isn't being worn or carried. The object flies in a straight line up to 90 feet in a direction you choose before falling to the ground, stopping early if it impacts against a solid surface. If the object would strike a creature, that creature must make a Dexterity saving throw. On a failed save, the object strikes the target and stops moving. When the object strikes something, the object and what it strikes each take 3d8 bludgeoning damage. At Higher Levels. When you cast this spell using a spell slot of 2nd level or higher, the maximum weight of objects that you can target with this spell increases by 5 pounds, and the damage increases by 1d8, for each slot level above 1st.")
Faerie_Fire = Spell('Faerie Fire' , '1 action' , '60 feet' , 'V' , 'Concentration up to 1 minute' , "Each object in a 20-foot cube within range is outlined in blue, green, or violet light (your choice). Any creature in the area when the spell is cast is also outlined in light if it fails a Dexterity saving throw. For the duration, objects and affected creatures shed dim light in a 10-foot radius. Any attack roll against an affected creature or object has advantage if the attacker can see it, and the affected creature or object can't benefit from being invisible.")
False_Life = Spell('False Life' , '1 action' , 'Self' , 'V,S,M' , '1 hour' , "Bolstering yourself with a necromantic facsimile of life, you gain 1d4+4 temporary hit points for the duration. At Higher Levels: When you cast this spell using a spell slot of 2nd level or higher, you gain 5 additional temporary hit points for each slot level above 1st.")
Magic_Missile = Spell('Magic Misslie' , '1 action' , '120 feet' , 'V,S' , 'Instantaneous' , "You create three glowing darts of magical force. Each dart hits a creature of your choice that you can see within range. A dart deals 1d4+1 force damage to its target. The darts all strike simultaneously and you can direct them to hit one creature or several. At Higher Levels: When you cast this spell using a spell slot of 2nd level or higher, the spell creates one more dart for each slot above 1st.")
Identify = Spell('Indentify' , '1 minute or ritual' , 'Touch' , 'V,S,M' , 'Instantaneous' , "You choose one object that you must touch throughout the casting of the spell. If it is a magic item or some other magic-imbued object, you learn its properties and how to use them, whether it requires attunement to use, and how many charges it has, if any. You learn whether any spells are affecting the item and what they are. If the item was created by a spell, you learn which spell created it. If you instead touch a creature throughout the casting, you learn what spells, if any, are currently affecting it.")
Thunderwave = Spell('Thunderwave' , '1 action' , 'Self 15-foot cube' , 'V,S' , 'Instantaneous' , "A wave of thunderous force sweeps out from you. Each creature in a 15-foot cube originating from you must make a Constitution saving throw. On a failed save, a creature takes 2d8 thunder damage and is pushed 10 feet away from you. On a successful save, the creature takes half as much damage and isn't pushed. In addition, unsecured objects that are completely within the area of effect are automatically pushed 10 feet away from you by the spell's effect, and the spell emits a thunderous boom audible out to 300 feet. At Higher Levels: When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d8 for each slot level above 1st.")
Arcane_Lock = Spell('Arcane Lock' , '1 action' , 'Touch' , 'V,S,M' , 'Until dispelled' , "You touch a closed door, window, gate, chest, or other entryway, and it becomes locked for the duration. You and the creatures you designate when you cast this spell can open the object normally. You can also set a password that, when spoken within 5 feet of the object, suppresses this spell for 1 minute. Otherwise, it is impassable until it is broken or the spell is dispelled or suppressed. Casting knock on the object suppresses arcane lock for 10 minutes. While affected by this spell, the object is more difficult to break or force open; the DC to break it or pick any locks on it increases by 10.")
Lesser_Restoration = Spell('Lesser Restoration' , '1 action' , 'Touch' , 'V,S' , 'Instantaneous' , "You touch a creature and can end either one disease or one condition afflicting it. The condition can be blinded, deafened, paralyzed, or poisoned.")
Mirror_Image = Spell('Mirror Image' , '1 action' , 'Self' , 'V,S' , '1 minute' , "Three illusory duplicates of yourself appear in your space. Until the spell ends, the duplicates move with you and mimic your actions, shifting position so it's impossible to track which image is real. You can use your action to dismiss the illusory duplicates. Each time a creature targets you with an attack during the spell's duration, roll a d20 to determine whether the attack instead targets one of your duplicates. If you have three duplicates, you must roll a 6 or higher to change the attack's target to a duplicate. With two duplicates, you must roll an 8 or higher. With one duplicate, you must roll an 11 or higher. A duplicate's AC equals 10 + your Dexterity modifier. If an attack hits a duplicate, the duplicate is destroyed. A duplicate can be destroyed only by an attack that hits it. It ignores all other damage and effects. The spell ends when all three duplicates are destroyed. A creature is unaffected by this spell if it can't see, if it relies on senses other than sight, such as blindsight, or if it can perceive illusions as false, as with truesight.")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents().all()
bot = commands.Bot(command_prefix = '$', intents=intents)

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
        for key,value in playlist():
            await ctx.send(key, ':', value)
    
    #Remove an Item From Playlist Method FIX WIP
    @commands.command(name = 'remove')
    async def remove(self, ctx: commands.Context, arg: int):
        playlist = self.playlists.get(ctx.guild.id)
        int = arg
        playlist.pop(int)
        await ctx.send(f"Playlist item {int} removed from playlist")

    @commands.command(name = 'play')
    async def play(self, ctx: commands.Context, *, url: str):
        if ctx.voice_client is None:
            voice_channel = ctx.author.voice.channel
            if ctx.author.voice is None:
                await ctx.send("`You are not in a voice channel!`")
            if (ctx.author.voice):
                await voice_channel.connect()
        else: 
            pass
        FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options' : '-vn'}
        YDL_OPTIONS = {'format':'bestaudio', 'default_search':'auto'}

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)

            if 'entries' in info:
                url2 = info['entries'][0]['formats'][0]['url']
                title = info['entries'][0]['title']
            elif 'formats' in  info:
                url2 = info['formats'][0]['url']
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
            song, title = playlist.get_song()
        else:
            await ctx.send("No more songs in the playlist")
            return await ctx.guild.voice_client.disconnect()
        await ctx.send(f"Now playing: {title}")
        
        ctx.guild.voice_client.play(song, after=functools.partial(lambda x: self.bot.loop.create_task(self.check_play(ctx))))
        # for the above code, instead of functools.partial, you could also create_task on the next line, I just find using the `after` kwargs much better
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('MusicPlayer module has successfully been initialized.')

async def setup(bot):
    await bot.add_cog(Music(bot))

#Startup Tasks, Prints Connected Guild(s) and User(s) in guilds, also loads opus
@bot.event
async def on_ready():
    await setup(bot)
    discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.3.1/lib/libopus.0.dylib')
    for guild in bot.guilds:
         print(
          f'{bot.user} is connected to the following guild:\n'
          f'{guild.name}(id: {guild.id})'
         )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

#Mike Oxlong bot meme
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
        
    if message.content.lower() == 'mike':
        meme_answer = 'Oxlong'
        response = meme_answer
        await message.channel.send(response)
    
    await bot.process_commands(message)

#Join Command: Adds bot to voice channel if user is in voice channel
@bot.command(name = 'join')
async def join(ctx):
    if ctx.author.voice is None:
        return await ctx.send("You are not connected to a voice channel")
    else:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Connected to voice channel: '{channel}'")

@bot.command(name = 'leave')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if ctx.author.voice is None:
        return await ctx.send("You are not connected to a voice channel")  
    elif voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name = 'pause')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    if not voice_channel.is_playing():
        await ctx.send('No music is playing') 
    else:               
        voice_channel.pause()
        await ctx.send('Music paused')

@bot.command(name = 'resume')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    if voice_channel.is_paused():             
        voice_channel.resume()
        await ctx.send('Music resumed')
    else:
        await ctx.send('Nothing to resume!')

@bot.command(name = 'stop')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    if not voice_channel.is_playing():
        await ctx.send('No music is playing') 
    else:               
        voice_channel.stop()
        await ctx.send('Music stopped')

@bot.command(name = 'roll')
async def roll(ctx, arg):
    if arg == '20':
        x = dice.roll('1d20')
        str(x)
        await ctx.send(x)
    else:
       return await ctx.send('Please select a valid number')

@bot.command(name = 'cast')
async def cast(ctx, *args):
    arguments = ' '.join(args)
    str(arguments)
    if arguments.lower() == 'eldritch blast':
        await ctx.send(Eldritch_Blast)
    elif arguments.lower() == 'mage hand':
        await ctx.send(Mage_Hand)
    elif arguments.lower() == 'minor illusion':
        await ctx.send(Minor_Illusion)
    elif arguments.lower() == 'expeditious retreat':
        await ctx.send(Expeditious_Retreat)
    elif arguments.lower() == 'invisibility':
        await ctx.send(Invisiblity)
    elif arguments.lower() == 'misty step':
        await ctx.send(Misty_Step)
    elif arguments.lower() == 'shatter':
        await ctx.send(Shatter)
    elif arguments.lower() == 'blink':
        await ctx.send(Blink)
    elif arguments.lower() == 'plant growth':
        await ctx.send(Plant_Growth)
    elif arguments.lower() == 'summon fey':
        await ctx.send(Summon_Fey)
    elif arguments.lower() == 'green flame blade':
        await ctx.send(Green_Flame_Blade)
    elif arguments.lower() == 'lightning lure':
        await ctx.send(Lightning_Lure)
    elif arguments.lower() == 'absorb elements':
        await ctx.send(Absorb_Elements)
    elif arguments.lower() == 'catapult':
        await ctx.send(Catapult)
    elif arguments.lower() == 'faerie fire':
        await ctx.send(Faerie_Fire)
    elif arguments.lower() == 'false life':
        await ctx.send(False_Life)
    elif arguments.lower() == 'magic missile':
        await ctx.send(Magic_Missile)
    elif arguments.lower() == 'identify':
        await ctx.send(Identify)
    elif arguments.lower() == 'thunderwave':
        await ctx.send(Thunderwave)
    elif arguments.lower() == 'arcane lock':
        await ctx.send(Arcane_Lock)
    elif arguments.lower() == 'lesser restoration':
        await ctx.send(Lesser_Restoration)
    elif arguments.lower() == 'mirror image':
        await ctx.send(Mirror_Image)
    else:
        return await ctx.send('Invalid Spell Name: Make Sure Each Word In Your Spell Has a Space')

bot.run(TOKEN)