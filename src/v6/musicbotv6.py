#Imports:
import discord
import ffmpeg
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import yt_dlp
from yt_dlp import YoutubeDL
from requests import get
import asyncio
import os
import time
#some important definitions:
loop = asyncio.get_event_loop()
token = ''
prefix = '-'
bot = commands.Bot(command_prefix=prefix)
queue_dict = {}
# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ''

def speed_check(s):
    speed = s.get('speed')
    ready = s.get('downloaded_bytes', 0)
    total = s.get('total_bytes', 0)    
    #if speed and speed <= 1000 * 1024 and ready >= total * 0.1:
        # if the speed is less than 77 kb/s and we have 
        # at least one tenths of the video downloaded
        #return(False)
    if speed and speed <= 100 * 1024:
        #return(False)
        raise yt_dlp.utils.DownloadError('Failed')
    print("Pass")

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
async def queue_preload(ctx):
    global queue_dict
    server = ctx.message.guild
    serverid = server.id
    if len(queue_dict[str(serverid)]) == 0:
        print("Empty Queue")
        return
    
    queueitem = queue_dict[str(serverid)][0]
    print(queueitem)
    url = queueitem[0]
    title = queueitem[1]
    yt_id = queueitem[2]
    print(url)
    print(title)
    print(yt_id)
    ext = "mp3"
    YDL_OPTIONS = {
        'format': 'bestaudio',
        #'http-chunk-size': '10M',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '256',
        }],
        'outtmpl': 'song.mp3',
    }
    #ytdl = yt_dlp.YoutubeDL(YDL_OPTIONS)
    #ytdl.add_progress_hook(speed_check)
    #trydown = True
    #while trydown == True:
        #try:
            #time.sleep(1)
            #ytdl.download(url)
            #trydown = False
        #except:
            #print("Failed")
    for i in range(0, len(queue_dict[str(serverid)])):
        queueitem = queue_dict[str(serverid)][i]
        print("TEST")
        print(i)
        print(queueitem)
        url = queueitem[0]
        title = queueitem[1]
        yt_id = queueitem[2]
        print(yt_id)        
        YDL_OPTIONS['outtmpl'] = str(yt_id)+'.mp3'
        print(YDL_OPTIONS['outtmpl'])
        if os.path.exists(str(yt_id)+'.mp3'):
            print("Already Saved: "+str(yt_id))
            #await ctx.send("Already Saved: "+str(yt_id))
        else:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ytdl:
                print("Downloaded: "+str(yt_id))
                ytdl.download((url,))
                #await ctx.send("Downloaded: "+str(yt_id))
                
    print("Preloading Complete!")
    #await ctx.send("Preloading Complete!")
    
def queue_add(ctx, stats):
    global queue_dict
    server = ctx.message.guild
    serverid = server.id
    
    title = stats["title"]
    url = ("https://www.youtube.com/watch?v=",stats["id"])
    url = "".join(map(str, url))
    yt_id = stats["id"]
    print(url)
    print(title)
    print(yt_id)
    serverid = server.id
    #queue_dict format:
    #queuedict[serverid][position][0] = url
    #queuedict[serverid][position][1] = title
    #queuedict[serverid][position][2] = id
    try:
        if len(queue_dict[str(serverid)]) == 0:
            queue_dict[str(serverid)][0] = [str(url),str(title),str(yt_id)]
        else:
            queue_dict[str(serverid)].append([str(url),str(title),str(yt_id)])
        print("Added to Queue")
    except:
        print("First Queue")
        queue_dict[str(serverid)] = []
        queue_dict[str(serverid)].append([str(url),str(title),str(yt_id)])
        
    print(queue_dict)
    
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
    #'outtmpl': 'song.mp3',
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

    
#Asynchronus function definitions:
async def nextsong(ctx, server, member):
    global queue_dict
    serverid = server.id
    if len(queue_dict[str(serverid)]) == 0:
        print("End of queue")
        await ctx.send("End of queue")
        return
    
    queueitem = queue_dict[str(serverid)][0]
    print(queueitem)
    url = queueitem[0]
    title = queueitem[1]
    yt_id = queueitem[2]
    print(url)
    print(title)
    print(yt_id)
   
##    YDL_OPTIONS = {
##        'format': 'bestaudio',
##        #'http-chunk-size': '10M',
##        'postprocessors': [{
##            'key': 'FFmpegExtractAudio',
##            'preferredcodec': 'mp3',
##            'preferredquality': '256',
##        }],
##        'outtmpl': 'song.%(ext)s',
##    }
##    ytdl = yt_dlp.YoutubeDL(YDL_OPTIONS)
    #ytdl.add_progress_hook(speed_check)
    #trydown = True
    #while trydown == True:
        #try:
            #time.sleep(1)
            #ytdl.download(url)
            #trydown = False
        #except:
            #print("Failed")
    channel = member.voice.channel
    voice_channel = server.voice_client
    #await ctx.send(f"Now playing: {url}")
    #await ctx.send(f'Now playing: {title}')
    ext = "mp3"
    await queue_preload(ctx)
    if voice_channel.is_connected() == False:
        await voice_channel.connect(reconnect = True,timeout = 60.0)
    voice_channel.play(discord.FFmpegPCMAudio(str(yt_id)+'.mp3'), after=lambda e: print(f'Player error: {e}') if e else bot.loop.create_task((del_song(ctx, server, member, 0))))
    await ctx.send(f"Now playing {title}: ```{url}```")
    
async def del_song(ctx, server, member, pos):
    global queue_dict
    #print(queue_dict)
    serverid = server.id
    #print(serverid)
    #print(queue_dict[str(serverid)])
    del(queue_dict[str(serverid)][pos])
    if pos == 0:
        bot.loop.create_task(nextsong(ctx, server, member))
    
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
                print("User is connected to a channel, joining...")
                #await ctx.send("User is connected to a channel, joining...")
        except:
            print("I am already connected to a channel.")
            #await ctx.send("I am already connected to a channel.") # If the bot is already connected
    except:
        await ctx.send("User is not in a channel, can't connect.") # Error message]
        return
    await ctx.send("Loading one for the boyz...")
    stats = search(search_term)
    print(queue_dict)
    queue_add(ctx, stats)
    
    voice_channel = server.voice_client
    if not voice_channel.is_playing():
        await nextsong(ctx, server, member)
    else:
        print("Song added to queue!")
        await ctx.send("Song added to queue!")
        await queue_preload(ctx)

        
@bot.command(name = 'playlast', aliases = ['pl','PL'])
async def playlast(ctx):
    global queue_dict
    if not voice_channel.is_playing():
        await nextsong(ctx, server, member)
    else:
        print("Song added to queue!")
        await ctx.send("Song added to queue!")

        
@bot.command(name = 'skip', aliases = ['s','S','Skip'], brief="Skips a song")
async def skip(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    member = ctx.author
    channel = member.voice.channel
    
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
        voice_channel.stop()
        voice_channel = server.voice_client
        #bot.loop.create_task((del_song(ctx, server, member, 0)))
        #await del_song(ctx, server, member, 0)
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
@bot.command(name = 'leave', aliases = ['l','L','Leave'], brief="Leave VC")
async def leave(ctx):
    member = ctx.author
    channel = member.voice.channel
    server = ctx.message.guild
    serverid = server.id
    voice_channel = server.voice_client
    if voice_channel is None:
        await ctx.send("Not in a VC") 
    else:
        await voice_channel.disconnect()
        await ctx.send("Disconnected") 
bot.run(token)

