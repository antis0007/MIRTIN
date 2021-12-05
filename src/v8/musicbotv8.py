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
import random
import re
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

#options = webdriver.FirefoxOptions()
#options.add_argument('-headless')
#driver = webdriver.Firefox(executable_path=r'C:\Webdriver\bin\geckodriver.exe', options = options)

#driver.set_window_size(1440, 900)
#driver.set_window_size(1920,1080)
#driver.set_window_size(2560,1600)

#some important definitions:
loop = asyncio.get_event_loop()
token = ''
prefix = '-'
bot = commands.Bot(command_prefix=prefix)
queue_dict = {}
last_song = []
# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ''
def spotify_scan(url):
    sp_type = url.split("/")[-2]
    searchlist = []
    webpage = requests.get(url)
    content = BeautifulSoup(webpage.text,'html.parser')
    if sp_type == "album" or sp_type == "track":
        artists = ''
        for artist in content.find("h2").find_all("a"):
            if artists == '':
                artists = artist.text
            else:
                artists = artists + " and " + artist.text
    track_list = content.find("ol").find_all("li")
    for track in track_list:
        song_name = track.find("span", attrs={"class":"track-name"}).text
        if sp_type == "album" or sp_type == "track":
            track_name = song_name + " by " + artists
        else:
            artist_name = track.find("span", attrs={"class":"artists-albums"}).find("a").text
            track_name = song_name + " by " + artist_name
        searchlist.append(track_name)
    if webpage.text.find("View all on Spotify") >= 0:
        cov = len(searchlist)
    else:
        cov = 0
    return searchlist, cov
def spotify_scrape(url,covered):

    sp_type = url.split("/")[-2]
    searchlist = []
    profile = webdriver.FirefoxProfile()
    profile.set_preference('permissions.default.stylesheet', 2)
    profile.set_preference('permissions.default.image', 2)
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')

    driver = webdriver.Firefox(executable_path=r'C:\Users\mbar2\Documents\geckodriver-v0.26.0-win32\geckodriver.exe', options = options, firefox_profile = profile)
    driver.set_window_size(1000,1000)
    driver.get(url)
    timeout = 60
    pl_main = ''
    while timeout > 0:
        try:
            pl_main = driver.find_element_by_xpath("//section[@data-testid='" + sp_type + "-page']")
            timeout = 0
        except:
            time.sleep(1)
            timeout -= 1
    if pl_main != '':
        if sp_type == "track":
            trackname = pl_main.find_element_by_tag_name("h1").text
            artistname = pl_main.find_element_by_tag_name("a").text
            songname = trackname + " by " + artistname
            searchlist.append(songname)
        else:
            if sp_type == "album":
                keyword = "track-list"
            elif sp_type == "playlist":
                keyword = "playlist-tracklist"
            else:
                keyword = ''
            if keyword != '':
                pl_cont = pl_main.find_elements_by_xpath("//div[@data-testid='" + keyword + "']/div[@role='presentation']")[-1]
                offset = re.search("([0-9]+)", pl_cont.get_attribute("style")).group(0)
                driver.set_window_size(1000,100+int(offset))
                pl_rows = pl_cont.find_elements_by_xpath("./div[@role='presentation']/div[@role='row']")
                for row in pl_rows:
                    if int(row.get_attribute("aria-rowindex")) - 1 > covered:
                        song = row.find_element_by_xpath("./div[@data-testid='tracklist-row']/div[@aria-colindex='1']/div/button")
                        songname = re.sub("^Play ", "", song.get_attribute("aria-label"))
                        searchlist.append(songname)
    driver.quit()
    return(searchlist)
##def spotify_playlist(url):
##    sp_type = url.split("/")[-2]
##    searchlist = []
##    try:
##        webpage = requests.get(url)
##        if sp_type == "track":
##            mthd = "bs4"
##        else:
##            song_count = re.search("([0-9]*) songs",webpage.text).group(1)
##            if int(song_count) <= 30:
##                mthd = "bs4"
##            else:
##                mthd = "sel"
##    except:
##        mthd = "sel"
##    if mthd == "bs4":
##        content = BeautifulSoup(webpage.text,'html.parser')
##        if sp_type == "album" or sp_type == "track":
##            artists = ''
##            for artist in content.find("h2").find_all("a"):
##                if artists == '':
##                    artists = artist.text
##                else:
##                    artists = artists + " and " + artist.text
##        track_list = content.find("ol").find_all("li")
##        for track in track_list:
##            song_name = track.find("span", attrs={"class":"track-name"}).text
##            if sp_type == "album" or sp_type == "track":
##                track_name = song_name + " by " + artists
##            else:
##                artist_name = track.find("span", attrs={"class":"artists-albums"}).find("a").text
##                track_name = song_name + " by " + artist_name
##            searchlist.append(track_name)
##    elif mthd == "sel":
##        profile = webdriver.FirefoxProfile()
##        profile.set_preference('permissions.default.stylesheet', 2)
##        profile.set_preference('permissions.default.image', 2)
##        options = webdriver.FirefoxOptions()
##        options.add_argument('-headless')
##
##        driver = webdriver.Firefox(executable_path=r'C:\Users\mbar2\Documents\geckodriver-v0.26.0-win32\geckodriver.exe', options = options, firefox_profile = profile)
##        driver.set_window_size(1000,1000)
##        driver.get(url)
##        timeout = 60
##        pl_main = ''
##        while timeout > 0:
##            try:
##                pl_main = driver.find_element_by_xpath("//section[@data-testid='" + sp_type + "-page']")
##                timeout = 0
##            except:
##                time.sleep(1)
##                timeout -= 1
##        if pl_main != '':
##            if sp_type == "track":
##                trackname = pl_main.find_element_by_tag_name("h1").text
##                artistname = pl_main.find_element_by_tag_name("a").text
##                songname = trackname + " by " + artistname
##                searchlist.append(songname)
##            else:
##                if sp_type == "album":
##                    keyword = "track-list"
##                elif sp_type == "playlist":
##                    keyword = "playlist-tracklist"
##                else:
##                    keyword = ''
##                if keyword != '':
##                    pl_cont = pl_main.find_elements_by_xpath("//div[@data-testid='" + keyword + "']/div[@role='presentation']")[-1]
##                    offset = re.search("([0-9]+)", pl_cont.get_attribute("style")).group(0)
##                    driver.set_window_size(1000,100+int(offset))
##                    pl_songs = pl_cont.find_elements_by_xpath("./div[@role='presentation']/div[@role='row']/div[@data-testid='tracklist-row']/div[@aria-colindex='1']/div/button")
##                    for song in pl_songs:
##                        songname = re.sub("^Play ", "", song.get_attribute("aria-label"))
##                        searchlist.append(songname)
##        driver.quit()
##    else:
##        searchlist.append('')
##    return(searchlist)
##def spotify_playlist(url):
##    profile = webdriver.FirefoxProfile()
##    # Disable CSS
##    profile.set_preference('permissions.default.stylesheet', 2)
##    # Disable images
##    profile.set_preference('permissions.default.image', 2)
##    # Disable Flash
##    profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
##    options = webdriver.FirefoxOptions()
##    options.add_argument('-headless')
##
##    driver = webdriver.Firefox(executable_path=r'C:\Webdriver\bin\geckodriver.exe', options = options, firefox_profile = profile)
##    driver.set_window_size(1000,1000)
##    driver.get(url)
##    searchlist = []
##    timeout = 60
##    pl_main = ''
##    sp_type = url.split("/")[-2]
##    while timeout > 0:
##        try:
##            pl_main = driver.find_element_by_xpath("//section[@data-testid='" + sp_type + "-page']")
##            timeout = 0
##        except:
##            time.sleep(1)
##            timeout -= 1
##    if pl_main != '':
##        if sp_type == "track":
##            trackname = pl_main.find_element_by_tag_name("h1").text
##            artistname = pl_main.find_element_by_tag_name("a").text
##            songname = trackname + " by " + artistname
##            searchlist.append(songname)
##        else:
##            if sp_type == "album":
##                keyword = "track-list"
##            elif sp_type == "playlist":
##                keyword = "playlist-tracklist"
##            else:
##                keyword = ''
##            if keyword != '':
##                pl_cont = pl_main.find_elements_by_xpath("//div[@data-testid='" + keyword + "']/div[@role='presentation']")[-1]
##                offset = re.search("([0-9]+)", pl_cont.get_attribute("style")).group(0)
##                driver.set_window_size(1000,100+int(offset))
##                pl_songs = pl_cont.find_elements_by_xpath("./div[@role='presentation']/div[@role='row']/div[@data-testid='tracklist-row']/div[@aria-colindex='1']/div/button")
##                for song in pl_songs:
##                    songname = re.sub("^Play ", "", song.get_attribute("aria-label"))
##                    searchlist.append(songname)
##    driver.quit()
##    return(searchlist)
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
    #queue_dict[serverid][position][0] = url
    #queue_dict[serverid][position][1] = title
    #queue_dict[serverid][position][2] = id
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
    if len(args)> 0:
        search_term = " ".join(args[:])
        print(search_term)
        stats = search(search_term)
        print(queue_dict)
        queue_add(ctx, stats)
    else:
        await ctx.send("Playing next song in queue...")
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
@bot.command(name = 'spot', brief="Add Spotify Playlist")
async def spot(ctx, url):
    await ctx.send("Adding playlist...")
    addlist, cov = spotify_scan(url)
    for i in addlist:
        stats = search(i)
        queue_add(ctx, stats)
    if cov > 0:
        addlist = spotify_scrape(url,cov)
        for i in addlist:
            stats = search(i)
            queue_add(ctx, stats)
    print("Added playlist to queue")
    await ctx.send("Added playlist to queue")
@bot.command(name = 'shuffle', brief="Shuffle Queue")
async def shuffle(ctx):
    global queue_dict
    server = ctx.message.guild
    serverid = server.id
    random.shuffle(queue_dict[str(serverid)])
    await ctx.send("Shuffled Queue...")

@bot.command(name = 'stop', aliases = ['Stop'], brief="Stop song and pause")
async def stop(ctx):
    global queue_dict
    server = ctx.message.guild
    serverid = server.id
    print(server)
    print(serverid)
    member = ctx.author
    channel = member.voice.channel
    voice_channel = server.voice_client
    del(queue_dict[str(serverid)][0])
    voice_channel.stop()
    await ctx.send("Stopped song")
    await pause(ctx)
    #await del_song(ctx, server, member, 0)


bot.run(token)
