import discord
import ffmpeg
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import youtube_dl
from youtube_dl import YoutubeDL
from requests import get
import asyncio
import os
# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        #'preferredcodec': 'flac',
        'preferredquality': '256'
        #'preferredquality': '192'
    }],
    #'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'outtmpl': 'song.mp3',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

loop = asyncio.get_event_loop()
token = ''
prefix = '-'
bot = commands.Bot(command_prefix=prefix)
queue_dict = {}
async def delsong(ctx, server, member):
    global queue_dict
    serverid = server.id
    del(queue_dict[str(serverid)][0])
    try:
        if os.path.exists("song.mp3"):
            os.remove("song.mp3")
        else:
            print("The file does not exist!")
    except:
        print("Already in use")
    bot.loop.create_task(nextsong(ctx, server, member))
#Asynchronus play song task:
async def nextsong(ctx, server, member):
    global queue_dict
    
    channel = member.voice.channel
    voice_channel = server.voice_client
    serverid = server.id
    if len(queue_dict) == 0:
        print("End of queue")
        await ctx.send("End of queue")
        return
    url = queue_dict[str(serverid)]
    print(url)
    print(url[0])
    YDL_OPTIONS = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '256',
        }],
        'outtmpl': 'song.%(ext)s',
    }
    ytdl = youtube_dl.YoutubeDL(YDL_OPTIONS)
    ytdl.download(url)
    
    #voice_channel.play(FFmpegPCMAudio("song.mp3"))
    
    await ctx.send(f"Now playing: {url[0]}")
    #await ctx.send(f'Now playing: {title}')
    voice_channel.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print(f'Player error: {e}') if e else bot.loop.create_task((delsong(ctx, server, member))))
def search(arg):
    YDL_OPTIONS = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.%(ext)s',
    }
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            get(arg) 
        except:
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(arg, download=False)

    return video
@bot.command()
async def ping(ctx):
    await ctx.send('pong')
    
@bot.command(name = 'queue', aliases = ['q','Q','Queue'], brief="Lists Queue")
async def queue(ctx):
    global queue_dict
    print(queue_dict)
    queuestr = str("```"+str(queue_dict)+"```")
    await ctx.send("Queue:")
    await ctx.send(queuestr)
    
@bot.command(name = 'play', aliases = ['p','P','Play'], brief="Plays a song")
async def play(ctx, *args):
    global queue_dict
    search_term = " ".join(args[:])
    print(search_term)
    try:
        server = ctx.message.guild
        serverid = server.id
        print(server)
        print(serverid)
        member = ctx.author
        channel = member.voice.channel
        
        try:
            if channel: # If user is in a channel
                await channel.connect() # Connect
                await ctx.send("User is connected to a channel, joining...")
        except:
            await ctx.send("I am already connected to a channel.") # If the bot is already connected
    except:
        await ctx.send("User is not in a channel, can't connect.") # Error message]
        return
    stats = search(search_term)
    title = stats["title"]
    message = ("Playing:",title)
    message = "".join(map(str, message))
    url = ("https://www.youtube.com/watch?v=",stats["id"])
    url = "".join(map(str, url))
    print(url)
    print(message)
    print(title)
    #await ctx.send(url)
    #await ctx.send(message)
    print(queue_dict)
    try:
        if len(queue_dict[str(serverid)]) == 0:
            queue_dict[str(serverid)][0] = [str(url)]
        else:
            queue_dict[str(serverid)].append(str(url))
        print("Added to Queue")
    except:
        print("First Queue")
        queue_dict[str(serverid)] = []
        queue_dict[str(serverid)].append(str(url))
    
    print(queue_dict)
    #await ctx.send(queue_dict)
    voice_channel = server.voice_client
    if not voice_channel.is_playing():
        await nextsong(ctx, server, member)
    else:
        print("Song added to queue!")
        await ctx.send("Song added to queue!")
@bot.command(name = 'skip', aliases = ['s','S','Skip'], brief="Skips a song")
async def skip(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    if not voice_channel.is_playing():
        await nextsong(ctx, server, member)
    else:
        print("Skipping...")
        await ctx.send("Skipping...")
        server = ctx.message.guild
        serverid = server.id
        print(server)
        print(serverid)
        member = ctx.author
        channel = member.voice.channel
        voice_channel = server.voice_client
        voice_channel.stop()
        bot.loop.create_task((delsong(ctx, server, member)))
@bot.command(name = 'clear', aliases = ['c','C','Clear'], brief="Clear songs queue")
async def clear(ctx):
    global queue_dict
    server = ctx.message.guild
    serverid = server.id
    queue_dict[str(serverid)] = []
    await ctx.send("Cleared Queue")
@bot.command(name = 'pause', aliases = ['Pause'], brief="Pause song player")
async def pause(ctx):
    global queue_dict
    server = ctx.message.guild
    serverid = server.id
    voice_channel = server.voice_client
    if voice_channel.is_paused():
        await ctx.send("Unpausing...")
        voice_channel.resume()
    elif not voice_channel.is_paused():
        await ctx.send("Paused...")
        voice_channel.pause()
@bot.command(name = 'join', aliases = ['j','J','Join'], brief="Join VC")
async def join(ctx):
    member = ctx.author
    channel = member.voice.channel
    server = ctx.message.guild
    serverid = server.id
    voice_channel = server.voice_client
    if voice_channel is None:
        voice_channel = await channel.connect()
    else:
        await voice_channel.move_to(channel)
    await ctx.send("Moved to user's current VC")
bot.run(token)

