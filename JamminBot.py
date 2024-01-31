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
import yt_dlp
from requests import get
from discord.utils import get
from discord.ext.commands import CommandNotFound, CommandInvokeError
import logging

import dice
import asyncio
import functools
from typing import Dict
import asyncio

import pandas as pd

from spellchecker import SpellChecker

from utils import Playlist, Music, Character

PF = pd.read_pickle("PFspells.pkl")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents().all()
bot = commands.Bot(command_prefix = '$', intents=intents)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')


###
#TO DO
#Setup to run on rpi (package, etc)
###


async def setup(bot):
    await bot.add_cog(Music(bot))

#Startup Tasks, Prints Connected Guild(s) and User(s) in guilds, also loads opus
@bot.event
async def on_ready():
    await setup(bot)
    #discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.3.1/lib/libopus.0.dylib')
    if not discord.opus.is_loaded():
        discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.4/lib/libopus.0.dylib')
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
    
@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, CommandNotFound):
        await ctx.send("`Invalid Command: Use '$help' for a list of valid commands`")
        return
    raise error

@bot.command(name = 'leave')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if ctx.author.voice is None:
        return await ctx.send("`You are not connected to a voice channel`")  
    elif voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("`The bot is not connected to a voice channel.`")

@bot.command(name = 'pause')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    if not voice_channel.is_playing():
        await ctx.send('`No music is playing`') 
    else:               
        voice_channel.pause()
        await ctx.send('`Music paused`')

@bot.command(name = 'resume')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    if voice_channel.is_paused():             
        voice_channel.resume()
        await ctx.send('`Music resumed`')
    else:
        await ctx.send('`Nothing to resume!`')

@bot.command(name = 'skip')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    if voice_channel.is_playing():             
        voice_channel.stop()
        await ctx.send('`Music skipped`')
    else:
        await ctx.send('`Nothing to skip!`')


###Old Method
#@bot.command(name = 'roll')
#async def roll(ctx, arg):
#    if arg == '20':
#        x = dice.roll('1d20')
#        str(x)
#        await ctx.send(x)
#    else:
#       return await ctx.send('Please select a valid number from the following: \n[20]')
   
@bot.command(name = 'roll')
async def roll(ctx, arg):
    arg = str(arg) + 't'
    try:
        x = dice.roll(arg)
    except dice.DiceBaseException:
        await ctx.send('`Invalid dice roll arguments`')
    else:
        x = f"`{x}`"
        await ctx.send(x)

@bot.command(name = 'cast')
async def cast(ctx, *args):
    arguments = ' '.join(args)
    spellName = str(arguments).lower()
    spellName = spellName.replace(" ", "")
    if PF.index.str.contains(spellName, case=False).any(): 
        #await ctx.send(str(df.loc[spellName]))
        list = ''
        for name, values in PF.loc[spellName].items():
            if values.lower() == 'none':
                continue
            else:
                list = list + ('{name}: {value}'.format(name=name, value=values) + "\n")
        await ctx.send(list)
    else:
        replacement = ''
        for word in args:
            spell = SpellChecker()
            word = spell.correction(str(word))
            replacement = replacement + word + ' '
        await ctx.send(f"`No such spell. Did you mean: {replacement}?`")
'''
#!!!If using this method be sure to change cast to PFcast!!!
@bot.command(name = 'DNDcast')
async def cast(ctx, *args):
    arguments = ' '.join(args)
    spellName = str(arguments).lower()
    spellName = spellName.replace(" ", "")
    if DND.index.str.contains(spellName, case=False).any(): 
        #await ctx.send(str(df.loc[spellName]))
        list = ''
        for name, values in DND.loc[spellName].items():
            if values.lower() == 'none':
                continue
            else:
                list = list + ('{name}: {value}'.format(name=name, value=values) + "\n")
        await ctx.send(list)
    else:
        replacement = ''
        for word in args:
            spell = SpellChecker()
            word = spell.correction(str(word))
            replacement = replacement + word + ' '
        await ctx.send(f"`No such spell. Did you mean: {replacement}?`")
'''
bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
bot.run(TOKEN)
