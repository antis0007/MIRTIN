import asyncio
from asyncio import sleep

import yt_dlp
#from yt_dlp import YoutubeDL
import discord
from discord.ext import tasks, commands

import requests
import bs4
from bs4 import BeautifulSoup
import json
import time
import threading
import math
import random
import datetime
import copy

yt_dlp.utils.bug_reports_message = lambda: ''

token = (open("token.txt")).readline()
if(token == ""):
    print("No token found! Be sure to add your discord bot token on the first line of the token.txt file")
    input("Waiting for input to exit program...")
    quit()
try:
    loop = asyncio.get_event_loop()
except:
    loop = asyncio.new_event_loop()

asyncio.set_event_loop(loop)

opus = False
headers = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
}


# ytdl_format_options = {
#     'format': 'bestaudio/best',
#     'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
#     'restrictfilenames': True,
#     'noplaylist': True,
#     'nocheckcertificate': True,
#     'ignoreerrors': False,
#     'logtostderr': False,
#     'quiet': True,
#     'no_warnings': True,
#     'default_search': 'auto',
#     'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
# }

#https://ffmpeg.org/ffmpeg-filters.html
def load_custom(filename,filter):
    #filters = open(filename).readlines()
    #for line in filters:
        #line_list = line.strip().split(",")
        #if line_list[0] == filter
            #custom = line_list[1]
            #docs = line_list[2]
    return()
filter_dict = {
    "compressor": ["acompressor",["mode: (upward, downward)","ratio: (1-20)","mix: (0-1)"]],
    "contrast" : ["acontrast",["contrast: (0-100)"]],
    "crusher": ["acrusher",["bits: (bit reduction)","mix: (mix amount)","mode: (lin, log)"]], #mode = "lin" or "log"
    "declick": ["adeclick",["w (window): (10-100)", "o (overlap): (50-95)", "t (threshold): (1-100)"]],
    #"dyn_equalizer": ["adynamicequalizer",[]],
    "dyn_smooth": ["adynamicsmooth",[]],
    "echo": ["aecho",["in_gain: (def = 0.6)", "out_gain: (def = 0.3)", "delays: (in ms)", "decays: (loudness of echos, def=0.5)"]],
    "exciter": ["aexciter",[]],
    "fft_denoise": ["afftdn",[]],
    "freq_shift": ["afreqshift",["shift: (-inf to inf)", "level: (0-1)", "order: (1-16)"]],
    #"wavelet_denoise": ["afwtdn",[]],
    "limiter": ["alimiter",[]],
    "allpass": ["allpass",[]],
    "phaser": ["aphaser",[]],
    "psy_clip": ["apsyclip",[]],
    "pulsator": ["apulsator",[]],
    "reverse": ["areverse",[]],
    "rate": ["asetrate",["r: (new sample rate, def = 44100)"]],
    "soft_clip": ["asoftclip",[]],
    "sub_boost": ["asubboost",[]],
    "sub_cut": ["asubcut",[]],
    "super_cut": ["asupercut",[]],
    "super_pass": ["asuperpass",[]],
    "super_stop": ["asuperstop",[]],
    "tempo": ["atempo",["tempo: (multiplier of tempo)"]],
    "tilt": ["atilt",[]],
    "bandpass": ["bandpass",[]],
    "bandreject": ["bandreject",[]],
    "bass": ["bass",[]],
    "chorus": ["chorus",[]],
    "compand": ["compand",[]],
    "crossfeed": ["crossfeed",[]],
    "crystalizer": ["crystalizer",[]],
    #"enhance_dialogue": ["dialoguenhance",[]],
    #"dyn_normalize": ["dynaudnorm",[]],
    "earwax": ["earwax",[]],
    "equalizer": ["equalizer",[]],
    "extra_stereo": ["extrastereo",[]],
    "flanger": ["flanger",["delay", "depth", "speed"]],
    "haas": ["haas",[]],
    "headphone": ["headphone",[]],
    "highpass": ["highpass",[]],
    "loudnorm": ["loudnorm",[]],
    "lowpass": ["lowpass",[]],
    "mult_compress": ["mcompand",[]],
    "rubberband": ["rubberband",[]],
    "stereowiden": ["stereowiden",[]],
    "surround": ["surround",[]],
    "treble": ["treble",[]],
    "tremolo": ["tremolo",["f = frequency (5)", "d = depth (0.5)"]],
    "vibrato": ["vibrato",["f = frequency (5)", "d = depth (0.5)"]],
    "custom": []
}

ytdl_format_options = {
    #'format': 'bestaudio',
    'format': 'ba/b',
    'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    #'preferredcodec': 'wav',
    #'preferredquality': '256',
    }],
    'outtmpl': 'song.%(ext)s',
    #'external-downloader': 'aria2c',
    #'external-downloader-args': "-x 16 -s 16 -k 1M",
    'restrictfilenames': True,
    'default_search':"auto",

    #'noplaylist': True,
    'skip_download': True,
    'flat-playlist': True,
    #'no-flat-playlist': True,
    'extract_flat': True,

    'nocheckcertificate': True,
    #'ignoreerrors': False,
    #'logtostderr': False,
    #'quiet': True,
    #'no_warnings': True,
    #'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes

}
ytdl_playlist_format_options = {
    #'format': 'bestaudio',
    #'format': 'ba/b',
    'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    #'preferredcodec': 'wav',
    #'preferredquality': '256',
    }],
    #'outtmpl': 'song.%(ext)s',
    #'external-downloader': 'aria2c',
    #'external-downloader-args': "-x 16 -s 16 -k 1M",
    'restrictfilenames': True,

    'default_search':"auto",
    'skip_download': True,
    #'flat-playlist': False,
    'flat-playlist': True, #ORIGINAL FOR FASTER LOADING!
    #'no-flat-playlist': True,
    'extract_flat': True,
    'nocheckcertificate': True,
    #'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn ',


    #FILTER SYNTAX:
    #-filter:a <filter>= <var>=<val>:<var2>=<val2>

    #-filter:a vibrato=f=5:d=1
    #-filter:a vibrato=f=5:d=0.7
    #-filter:a aecho
    #-bsf noise=0.1
    #-bsf noise=0.1
    #-af bs2b=profile=cmoy
    #-af bs2b
    #aecho
    #afreqshift
    #-h filter=aecho
    #-h filter=aecho

    #WORKS:
    #-filter:a volume=replaygain=track
    #
    #https://www.reddit.com/r/ffmpeg/comments/t0klxx/how_do_i_apply_the_replaygain_filter/
    #http://ffmpeg.org/ffmpeg-filters.html#Filtergraph-syntax-1
    #https://ffmpeg.org/ffmpeg-filters.html
    #
    # Make it sound as if there are twice as many instruments as are actually playing:
    #
    # aecho=0.8:0.88:60:0.4
    #
    # If delay is very short, then it sounds like a (metallic) robot playing music:
    #
    # aecho=0.8:0.88:6:0.4
    #
    # A longer delay will sound like an open air concert in the mountains:
    #
    # aecho=0.8:0.9:1000:0.3
    #
    # Same as above but with one more mountain:
    #
    # aecho=0.8:0.9:1000|1800:0.3|0.25


    "before_options": "-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    # 'reconnect': '1',
    # 'reconnect_streamed': '1',
    # 'reconnect_delay_max': '4'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)
ytdl_playlist = yt_dlp.YoutubeDL(ytdl_playlist_format_options)

class MIRTIN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.queue = {}

        #Players structure:
        #Dict with key-values
        #Key :  Discord Server ID
        #Value : [Player, Timer]

        #Queue Structure:
        #Dict with key-values
        #Key :  Discord Server ID
        #Value: Queue Objects

        #Loops Structure:
        #Dict with key-values
        #Key :  Discord Server ID
        #Value: loop = asyncio.get_event_loop()


    async def handle(self, ctx):
        server_id = ctx.guild.id
        if server_id not in self.queue:
            self.queue[server_id] = Queue()
        if server_id not in self.players:
            self.players[server_id] = [0,timer(0)]

    async def spotify(self, url):
        req = requests.get(url, 'html.parser') #, headers=headers
        soup = BeautifulSoup( req.content , 'html.parser')
        #Print Debug HTML:
        #print(soup.html)
        type_var = soup.find("meta", attrs={'property': 'og:type'})["content"]
        print(type_var)
        if not type_var:
            return(None)

        if(type_var == "music.playlist"):
            #songs = soup.findAll("meta", attrs={'name':'music:song'})
            songs = soup.findAll("button", attrs={'data-testid':"entity-row-v2-button"})
            songs = list(songs)
            song_list = []

            count = 0
            for song in songs:
                print(song)
                count +=1
                song_list.append(" : ".join(song.get_text("‽").split("‽")))
            return(song_list)
        if(type_var == "music.song"):
            title = str(soup.find("meta", attrs={'property': 'og:title'})["content"])
            desc = str(soup.find("meta", attrs={'property': 'og:description'})["content"])
            return([title+" : "+desc])


    async def search(self, ctx, query):
        stream = True
        songs = []
        if query.startswith("https://") or query.startswith("http://") or query.startswith("www.") or query.startswith("[url]"): #Proper URL
            if query.startswith("[url]"):
                query = query[5:] #trim URL tag
            #Proper URL
            url = query
        else: #Search Required
            ytdl_data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{query}", download=not stream))
            url = ytdl_data["entries"][0]["url"]

        ytdl_data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in ytdl_data:
            #await ctx.send("Loading Playlist...")
            return(ytdl_data['entries'])
        else: #Song:
            return([ytdl_data])

    async def del_song(self,ctx):
        server_id = ctx.message.guild.id
        self.queue[server_id].last_song = (self.queue[server_id].queue).pop(0)
        self.bot.loop.create_task(self.play_next(ctx))

    async def play_next(self,ctx):
        server_id = ctx.message.guild.id
        if len(self.queue[server_id].queue) >= 1:
            url = self.queue[server_id].queue[0].ytdl_data["url"]
            stream = True
            #If opus == True, volume commands will not work.
            if opus:
                self.players[server_id][0] = discord.FFmpegOpusAudio(url, **ffmpeg_options)
            if not opus:
                self.players[server_id][0] = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **ffmpeg_options))

            if (ctx.message.guild.voice_client).is_connected() == False:
                await (ctx.message.guild.voice_client).connect(reconnect = True,timeout = 60.0)

            if ctx.voice_client.is_playing():
                pass
            elif not ctx.voice_client.is_playing():
                self.players[server_id][1] = timer(self.queue[server_id].queue[0])
                ctx.voice_client.play(self.players[server_id][0], after=lambda e: print(f'Player error: {e}') if e else self.bot.loop.create_task(self.del_song(ctx)))
                await ctx.send('Now playing: {}'.format(self.queue[server_id][0].ytdl_data["title"]))


        else:
            print("End of queue")
            await ctx.send("End of queue")


    @commands.command()
    async def join(self, ctx, *args):
        """Joins a voice channel"""
        await self.handle(ctx)
        voice = ctx.author.voice
        if not voice:
            return await ctx.send("Not connected to a voice channel.")
        channel = voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect(timeout=60.0, reconnect=True)

    @commands.command()
    async def leave(self, ctx, *args):
        """Leaves a voice channel"""
        await self.handle(ctx)
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()
            return await ctx.send("Disconnected")
        else:
            return await ctx.send("Not connected to a voice channel.")

    async def generate_song(self, ctx, search):
        """Generates a song object from a search query"""
        data = await self.search(ctx, search)
        id = data["id"]
        url = "https://youtube.com/watch?v="+id
        stream = True
        ytdl_data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        song = Song(ytdl_data, data)
        return(song)

    @commands.command(aliases = ['pp'])
    async def play_priority(self, ctx, *, search=""):
        """Puts a song in queue right after the current one"""
        await asyncio.gather(self.play(ctx, query=search))
        await self.insert_last(ctx)

    async def insert_last(self, ctx, pos=1):
        """Inserts the last song in queue to a position"""
        server = ctx.message.guild
        voice_channel = server.voice_client
        server_id = server.id
        new_song = self.queue[server_id].queue.pop(-1)
        if len(self.queue[server_id].queue) <= 1:
            await self.queue[server_id].add(new_song)
        else:
            await self.queue[server_id].insert(pos,new_song)

    @commands.command(aliases = ['prev'])
    async def previous(self, ctx):
        server_id = ctx.message.guild.id
        server = ctx.message.guild
        voice_channel = server.voice_client
        if not voice_channel:
            await self.join(ctx)
            voice_channel = ctx.message.guild.voice_client
            if not voice_channel:
                return
        if len(self.queue[server_id].queue)>0:
            current = self.queue[server_id].queue[0]
            await self.queue[server_id].add(current)
            await self.insert_last(ctx)
        if self.queue[server_id].last_song == None:
            await ctx.send("Invalid Song")
            return
        await self.queue[server_id].add(self.queue[server_id].last_song)
        await self.insert_last(ctx)
        voice_channel.stop()

        #await self.queue[server_id].insert(1,new_song)
    @commands.command(aliases = ['p'])
    async def play(self, ctx, *, query=""):
        """Processes a song request and passes it to the queue, starts playing if empty queue"""
        await self.handle(ctx)
        server_id = ctx.guild.id
        voice_client = ctx.voice_client
        voice_channel = ctx.message.guild.voice_client
        async with ctx.typing():
            if not voice_channel:
                await self.join(ctx)
                voice_channel = ctx.message.guild.voice_client
            if len(query) == 0:

                if voice_channel.is_paused():
                    await ctx.send("Unpausing...")
                    voice_channel.resume()
                    return
                if voice_channel.is_playing():
                    await ctx.send("Already Playing...")
                    voice_channel.resume()
                    return
                else:
                    await ctx.send("Playing...")
                    await self.play_next(ctx)
                    return

            if not ctx.author.voice:
                await ctx.send("User is not in a voice channel")
                return()

            url_flag = ""
            #yt_url_check = ["youtube.com/watch?v=", "http://youtube.com/watch?v=", "https://youtube.com/watch?v="]
            spot_url_check = ["https://open.spotify.com/"]


            for i in spot_url_check:
                if i in query:
                    url_flag = "spot"

            if url_flag == "spot": #SPOTIFY LINK
                songs_list = await self.spotify(query)
                print("Completed Spotify Load")
                if not songs_list:
                    print("Unknown Spotify Error")
                    await ctx.send("Unknown Spotify Error")
                    return
                total = len(songs_list)
                count = 0
                #Progress Bar for Playlists:
                prog_size = 10
                prog_char = "█"
                incomp_char   = "░"

                prog_frac = (count/total)
                prog_num = math.floor(prog_frac*prog_size)
                prog_str = str("["+str(prog_char*prog_num)+str(incomp_char*(prog_size-prog_num))+"] "+str(round((prog_frac*100), 1))+"%")
                prog_msg = await ctx.send(prog_str)

                for name in songs_list:

                    song_data = await self.search(ctx, name)
                    song = Song(song_data[0]) #NO PLAYLIST
                    await asyncio.gather(self.queue[server_id].add(song))
                    #await (self.queue[server_id]).add(song)
                    count += 1
                    prog_frac = (count/total)
                    prog_num = math.floor(prog_frac*prog_size)
                    prog_str = str("["+str(prog_char*prog_num)+str(incomp_char*(prog_size-prog_num))+"] "+str(round((prog_frac*100), 1))+"%")
                    await prog_msg.edit(content = prog_str)
                    if not voice_channel.is_playing() and (len(self.queue[server_id].queue) == 1): #Play first song if not playing
                        await self.play(ctx)

            else: #All other playlists
                songs_data = await self.search(ctx, query)
                #Progress Bar for Playlists:
                count = 0
                total = len(songs_data)
                prog_size = 10
                prog_char = "█"
                incomp_char   = "░"
                prog_frac = (count/total)
                prog_num = math.floor(prog_frac*prog_size)
                prog_str = str("["+str(prog_char*prog_num)+str(incomp_char*(prog_size-prog_num))+"] "+str(round((prog_frac*100), 1))+"%")
                prog_msg = await ctx.send(prog_str)
                prog_msg_id = prog_msg.id
                #print(songs_data)
                stream = True
                #async with ctx.typing(): #NOT WORKING BECAUSE OF AUTOPLAY
                for song_data in songs_data:
                    id = song_data["id"]
                    url = song_data["url"]
                    if url.startswith("https://www.youtube.com"):
                        ytdl_data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
                        song = Song(ytdl_data)
                    else:
                        song = Song(song_data)
                    #DO THIS BECAUSE PLAYLIST EXTRACTION FAILS ON YOUTUBE
                    await asyncio.gather(self.queue[server_id].add(song))
                    count += 1
                    prog_frac = (count/total)
                    prog_num = math.floor(prog_frac*prog_size)
                    prog_str = str("["+str(prog_char*prog_num)+str(incomp_char*(prog_size-prog_num))+"] "+str(round((prog_frac*100), 1))+"%")
                    await prog_msg.edit(content = prog_str)
                    if not voice_channel.is_playing() and (len(self.queue[server_id].queue) == 1): #Play first song if not playing
                        await self.play(ctx)

        if len(self.queue[server_id].queue) == 1:
            print("First song in Queue...")
            await self.play_next(ctx)
        else:
            print("Added to queue!")
            await ctx.send("Added to queue!")

    @commands.command(aliases = ['s'], brief="Skips a song")
    async def skip(self, ctx):
        """Skips a song"""
        await self.handle(ctx)
        server = ctx.message.guild
        voice_channel = server.voice_client
        server_id = ctx.message.guild.id
        if not voice_channel:
            await self.join(ctx)
            voice_channel = ctx.message.guild.voice_client
            if not voice_channel:
                return
        if not voice_channel.is_playing() and len(self.queue[server_id].queue)>0:
            await self.play_next(ctx)
        elif len(self.queue[server_id].queue)==0:
            print("Queue is Empty")
            await ctx.send("Queue is Empty")
        else:
            print("Skipping...")
            await ctx.send("Skipping...")
            voice_channel.stop()


    @commands.command()
    async def filter_complex(self, ctx, *filter_str):
        """Applies a filter: -filter:a <filter>=<var>=<val>:<var2>=<val2>"""
        await self.handle(ctx)
        server_id = ctx.message.guild.id
        url = self.queue[server_id][0].ytdl_data["url"]
        stream=True
        #id = (self.queue[server_id])[0].ytdl_data["id"]
        #url = "https://youtube.com/watch?v="+id
        #print("FILTER:")
        #print(url)
        filter_str = ' '.join(filter_str)
        current_time = (self.players[server_id][1]).get()
        current_time = time.strftime('%H:%M:%S.', time.gmtime(current_time)) + (str(current_time).split(".")[1])[0:2]
        print(current_time)
        ffmpeg_options_custom = ffmpeg_options.copy()
        ffmpeg_options_custom['options'] = ffmpeg_options['options'] + filter_str
        ffmpeg_options_custom['before_options'] = ffmpeg_options['before_options'] + f" -ss {current_time}"
        voice_channel = ctx.message.guild.voice_client
        if voice_channel is None:
            voice_channel = await ctx.author.voice.channel.connect()
        else:
            await voice_channel.move_to(ctx.author.voice.channel)
        print(ffmpeg_options_custom)

        #if ctx.voice_client.is_playing():
            #ctx.voice_client.stop()
        #player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True, ffmpeg_options = ffmpeg_options_custom)#
        #ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        #ctx.voice_client.resume()

        song = self.queue[server_id][0] #Get playing song
        voice_channel.stop() #We will need to re-insert song into queue
        if (ctx.message.guild.voice_client).is_connected() == False:
            await (ctx.message.guild.voice_client).connect(reconnect = True,timeout = 60.0)

        #self.players[server_id][0] = discord.FFmpegOpusAudio(url, **ffmpeg_options)
        self.players[server_id][0] = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **ffmpeg_options_custom))
        prev = self.players[server_id][1].get()
        #self.players[server_id][1].move_back(prev)
        self.players[server_id][1].move_forward(prev)

        ctx.voice_client.play(self.players[server_id][0], after=lambda e: print(f'Player error: {e}') if e else self.bot.loop.create_task(self.del_song(ctx)))
        self.queue[server_id].queue.insert(0,song)

    @commands.command()
    async def seek(self, ctx, *args):
        """Seeks to a certain time in the current song"""
        await self.handle(ctx)
        server_id = ctx.message.guild.id
        voice_channel = ctx.message.guild.voice_client
        url = self.queue[server_id][0].ytdl_data["url"]
        stream=True
        argslist = list(args)
        print(argslist)
        for i in range(0,len(argslist)):
            argslist[i] = argslist[i].zfill(2)
        print(argslist)

        if len(argslist)== 1:
            if(":" in argslist[0]): #interpret as colon seperated
                timestamp = (argslist[0].split(":"))
                if len(timestamp) == 3:
                    timestamp = (str(":".join(timestamp))+".00")

            elif argslist[0].isnumeric(): #interpret as sec
                argslist = str(datetime.timedelta(seconds=int(argslist[0]))).split(":")
                argslist.append("00")
                print(argslist)
                for i in range(0,len(argslist)):
                    argslist[i] = argslist[i].zfill(2)
                print(argslist)
                timestamp = str(argslist[0]+":"+argslist[1]+":"+argslist[2]+"."+argslist[3])
                print(timestamp)

            else:
                await ctx.send("No timestamp provided ('H M S' or colon seperated)")
                return

        elif len(argslist) == 2: #interpret as min, sec
            argslist.insert(0, "00")
            argslist.append("00")
            print(argslist)
            timestamp = str(argslist[0]+":"+argslist[1]+":"+argslist[2]+"."+argslist[3])
            print(timestamp)

        elif len(argslist) == 3: #interpret as hours, min, sec
            argslist.append("00")
            print(argslist)
            timestamp = str(argslist[0]+":"+argslist[1]+":"+argslist[2]+"."+argslist[3])
            print(timestamp)

        else:
            await ctx.send("No timestamp provided (HH MM SS or colon seperated)")
            return

        time_seconds = int(argslist[0])*3600 + int(argslist[1])*60 + int(argslist[2]) + float(argslist[3])
        print(timestamp)
        print(time_seconds)
        ffmpeg_options_custom = ffmpeg_options.copy()
        ffmpeg_options_custom['options'] = ffmpeg_options['options']
        ffmpeg_options_custom['before_options'] = ffmpeg_options['before_options'] + f" -ss {timestamp}"

        if voice_channel is None:
            voice_channel = await ctx.author.voice.channel.connect()
        else:
            await voice_channel.move_to(ctx.author.voice.channel)
        song = self.queue[server_id][0] #Get playing song
        voice_channel.stop() #We will need to re-insert song into queue
        if (ctx.message.guild.voice_client).is_connected() == False:
            await (ctx.message.guild.voice_client).connect(reconnect = True,timeout = 60.0)
        #If opus == True, volume commands will not work.
        if opus:
            self.players[server_id][0] = discord.FFmpegOpusAudio(url, **ffmpeg_options_custom)
        if not opus:
            self.players[server_id][0] = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **ffmpeg_options_custom))

        ctx.voice_client.play(self.players[server_id][0], after=lambda e: print(f'Player error: {e}') if e else self.bot.loop.create_task(self.del_song(ctx)))
        print(self.players[server_id][1].elapsed())
        self.players[server_id][1].ongoing = time_seconds
        self.players[server_id][1].reset()
        self.queue[server_id].queue.insert(0,song)
        await ctx.send(f"Seeking to: {timestamp}")


    @commands.command()
    async def elapsed(self,ctx):
        await self.handle(ctx)
        server_id = ctx.message.guild.id
        voice_channel = ctx.message.guild.voice_client
        if voice_channel.is_paused():
            self.players[server_id][1].reset()
        prog1 = str(round((self.players[server_id][1]).elapsed()))+" / "+str(round(self.queue[server_id][0].duration))
        percent = "("+str(round(self.players[server_id][1].elapsed()/self.queue[server_id][0].duration*100))+"%)"
        mins_remaining = str(round((self.queue[server_id][0].duration-self.players[server_id][1].elapsed())/60,2))
        await ctx.send(prog1+ " "+percent+" "+mins_remaining+" minutes remaining...")

    @commands.command()
    async def filter(self, ctx, *filter_lists):
        """Filter audio: help to see all, help <filtername> to see specific"""
        """https://ffmpeg.org/ffmpeg-filters.html"""
        #FILTER SYNTAX:
        #-filter:a <filter>= <var>=<val>:<var2>=<val2>

        await self.handle(ctx)
        server_id = ctx.message.guild.id
        print("START TIMER ELAPSED:")


        ffmpeg_options_custom = ffmpeg_options.copy()
        #ffmpeg_options_custom['options'] += "-filter:a "
        #ffmpeg_options_custom['options'] += "-af:a "
        filter_lists = str(' '.join(filter_lists))
        print(filter_lists)
        filter_lists = filter_lists.split(",")
        print("FILTER LISTS:")
        print(filter_lists)
        if len(self.queue[server_id].queue)>=1:
            current_time = (self.players[server_id][1]).elapsed()
            print(current_time)
            self.queue[server_id].queue[0].speed = 1
        filter_str = ""
        for filter_list in filter_lists:
            filter_list = filter_list.strip(" ").split(" ")
            print(filter_list)
            if len(filter_list)>=1:
                filter_type = filter_list.pop(0)
                print(filter_type)
                if filter_type == "rate":
                    print(filter_list)
                    speed = float(filter_list[0])
                    self.queue[server_id].queue[0].speed = speed
                    print(speed)
                    speed=speed*44100
                    print(speed)
                    filter_list[0] = str(round(speed))
                    print(filter_list)
                if filter_type == "tempo":
                    print(filter_list)
                    speed = float(filter_list[0])
                    self.queue[server_id].queue[0].speed = speed
                if filter_type not in filter_dict:
                    if filter_type == "help":
                        if len(filter_list) == 0:
                            await ctx.send("ALL FILTERS:")
                            await ctx.send("```"+str(list(filter_dict.keys()))+"```")
                            return
                            #for i in list(filter_dict.keys()):
                                #await ctx.send(str(i))
                        elif (len(filter_list) == 1) and (filter_list[0] in filter_dict):
                            embed_desc = ""
                            for i in filter_dict[filter_list[0]][1]:
                                embed_desc+=i+"\n"
                            embed=discord.Embed(title=filter_list[0]+" info:", description=embed_desc)
                            await ctx.send(embed=embed)
                            return
                        else:
                            await ctx.send("UNSUPPORTED FILTER")
                            return
                    elif filter_type == "":
                        filter_str = ""
                        break
                    else:
                        await ctx.send("UNSUPPORTED FILTER")
                        return

                filter_parts = filter_dict[filter_type]
                #filter_parts:
                #0: Complex Name
                #1: Supported Variables
                #2: (ONLY SOME) Hints/Details
                filter_str += (str(filter_parts[0]))

                #filter_syntax = "var" #most filters take variable name parameters with values
                #filter_syntax = "seq" #some filters take sequential parameters without variable names: (eg: aecho)

                if len(filter_list) >= 1:
                    filter_str += "="+':'.join(filter_list)
                filter_str += ","

        url = self.queue[server_id][0].ytdl_data["url"]
        stream=True
        #ffmpeg_options_custom['options'] += '"' + filter_str.strip(",")+ '"'
        if len(filter_str) > 0:
            ffmpeg_options_custom['options'] += "-af:a "
            ffmpeg_options_custom['options'] += filter_str.strip(",")
        print(ffmpeg_options_custom)
        current_time_str = time.strftime('%H:%M:%S.', time.gmtime(current_time)) + (str(current_time).split(".")[1])[0:2]
        print(current_time_str)
        ffmpeg_options_custom['before_options'] = ffmpeg_options['before_options'] + f" -ss {current_time_str}"
        voice_channel = ctx.message.guild.voice_client
        if voice_channel is None:
            voice_channel = await ctx.author.voice.channel.connect()
        else:
            await voice_channel.move_to(ctx.author.voice.channel)
        #print(ffmpeg_options_custom)

        #if ctx.voice_client.is_playing():
            #ctx.voice_client.stop()
        #player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True, ffmpeg_options = ffmpeg_options_custom)#
        #ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        #ctx.voice_client.resume()

        song = self.queue[server_id][0] #Get playing song
        voice_channel.stop() #We will need to re-insert song into queue
        if (ctx.message.guild.voice_client).is_connected() == False:
            await (ctx.message.guild.voice_client).connect(reconnect = True,timeout = 60.0)

        #If opus == True, volume commands will not work.
        if opus:
            self.players[server_id][0] = discord.FFmpegOpusAudio(url, **ffmpeg_options_custom)
        if not opus:
            self.players[server_id][0] = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **ffmpeg_options_custom))



        ctx.voice_client.play(self.players[server_id][0], after=lambda e: print(f'Player error: {e}') if e else self.bot.loop.create_task(self.del_song(ctx)))
        print(self.players[server_id][1].elapsed())
        self.queue[server_id].queue.insert(0,song)


    @commands.command(aliases = ['q'], brief="Lists the queue")
    async def queue(self, ctx, opts=""):
        await self.handle(ctx)
        server_id = ctx.message.guild.id
        count = 1
        lensongs = 5
        if opts == "all":
            lensongs = len(self.queue[server_id].queue)
        elif opts != "":
            opts = int(opts)
            lensongs = opts

        if lensongs > len(self.queue[server_id].queue):
            lensongs = len(self.queue[server_id].queue)
        if len(self.queue[server_id].queue) > 0:
            embed = discord.Embed(title="Queue:",description=f"Showing up to next {lensongs} tracks, {len(self.queue[server_id].queue)} songs in total",colour=ctx.author.colour)
            embed.add_field(name="Currently playing:",value="[1] "+self.queue[server_id].queue[0].ytdl_data["title"], inline=False)
        else:
            embed = discord.Embed(title="Queue:",description=f"Empty",colour=ctx.author.colour)
        if len(self.queue[server_id].queue) > 1:
            val = ""
            for i in range(1, lensongs):
                val += f"[{i+1}] " + self.queue[server_id][i].ytdl_data["title"] + "\n"

            embed.add_field(
                name="Next up:",
                #value=("\n".join(self.queue[server_id][i].ytdl_data["title"] for i in range(1, lensongs))),
                value=val,
                inline=False
            )
            if len(self.queue[server_id].queue) > lensongs:
                embed.set_footer(text="And " + str(len(self.queue[server_id].queue)-lensongs) + " more...")
        msg = await ctx.send(embed=embed)
        #PERFORM REACTION VALIDATION USING EMBED TITLE
        #await msg.add_reaction("⏮️")
        #await msg.add_reaction("⏯️")
        #await msg.add_reaction("⏭️")
        await asyncio.gather(msg.add_reaction("⏮️"),msg.add_reaction("⏯️"),msg.add_reaction("⏭️"))


    @commands.command(aliases = ['v'], brief="Changes bot volume for everyone")
    async def volume(self, ctx, volume: int):
        """Changes global bot volume"""
        await self.handle(ctx)
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        if ctx.voice_client.is_playing():
            ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command(aliases = ['change', 'alternatives', 'alternative'], brief="Gives alternatives to a search query")
    async def alt(self, ctx, *, query=""):
        """Gives alternatives to a search query"""
        if query == "":
            await ctx.send("Please provide a search term to find alternatives")
            return
        stream = True
        ytdl_data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch5:{query}", download=not stream))
        search_data = ytdl_data["entries"]
        embed_desc = ""
        for i in search_data:
            embed_desc+=i["title"]+"\n"
        embed=discord.Embed(title="Alternatives:", description=embed_desc)
        await ctx.send(embed=embed)
        #ytdl_data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

    @commands.command()
    async def stop(self, ctx):
        """Stops playback and leaves the voice channel"""
        await self.handle(ctx)
        await ctx.voice_client.disconnect()

    @commands.command()
    async def pause(self, ctx):
        """Pauses/Resumes playback"""
        await self.handle(ctx)
        server = ctx.message.guild
        voice_channel = server.voice_client
        if not voice_channel:
            await self.join(ctx)
            voice_channel = ctx.message.guild.voice_client
            if not voice_channel:
                return
        if voice_channel.is_paused():
            await ctx.send("Unpausing...")
            voice_channel.resume()
        elif not voice_channel.is_paused():
            await ctx.send("Paused...")
            voice_channel.pause()

    @commands.command()
    async def shuffle(self, ctx):
        await self.handle(ctx)
        server_id = ctx.message.guild.id
        self.queue[server_id].shuffle()
        await ctx.send("Shuffled Queue")

    @commands.command(aliases = ['c'])
    async def clear(self, ctx):
        """Removes all songs in queue after current song"""
        await self.handle(ctx)
        server_id = ctx.message.guild.id
        current = self.queue[server_id].queue[0]
        self.queue[server_id].queue = []
        self.queue[server_id].queue.append(current)
        await ctx.send("Cleared Queue")

    @commands.command(aliases = ['r'])
    async def remove(self, ctx, index=-1):
        """Removes a song in queue"""
        await self.handle(ctx)
        server_id = ctx.message.guild.id
        if(((index-1)<=0) or ((index-1)>len(self.queue[server_id].queue)-1)):
            await ctx.send("INVALID POSITION")
            return()
        title = self.queue[server_id].queue[index-1].ytdl_data["title"]
        self.queue[server_id].remove(index-1)
        await ctx.send("Removed "+title+" from Queue")

    @play.before_invoke
    async def ensure_voice(self, ctx):
        await self.handle(ctx)
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        #elif ctx.voice_client.is_playing():
            #ctx.voice_client.stop()

class Queue(MIRTIN):
    def __init__(self):
        self.loop = False
        self.queue = []
        self.last_song = None

    def __setitem__(self, index, data):
        self.queue[index] = data
    def __getitem__(self, index):
        return self.queue[index]
    async def add(self, song):
        self.queue.append(song)
        return
    async def insert(self, index, song):
        self.queue.insert(index,song)
        return

    def remove(self, index):
        song = self.queue.pop(index)
        print("REMOVED:")
        print(song.ytdl_data["title"])
        print("END REMOVED, RETURNING...")
        return(song)

    def shuffle(self):
        if len(self.queue) > 1:
            current = self.queue[0]
            random.shuffle(self.queue)
            current_pos = self.queue.index(current)
            #current_new = self.queue[0]
            #current_new = 0
            if len(self.queue)>1:
                current = self.queue.pop(current_pos)
                current_new = self.queue.pop(0)
                self.queue.insert(0, current)
                self.queue.insert(current_pos, current_new)

class Song(Queue):
    def __init__(self, ytdl_data):
        if ytdl_data != 0:
            #ytdl_data['url'] = "'"+str("https://www.youtube.com/watch?v="+ str(ytdl_data['url']))+"'"
            #print(ytdl_data['url'])
            self.duration = ytdl_data['duration']
        else:
            self.duration = 0
        self.ytdl_data = ytdl_data

        self.elapsed = 0 #song time elapsed
        self.speed = 1
    def get_speed(self):
        return(self.speed)
    def set_speed(self, speed):
        self.speed = speed

class timer(Queue):
    def __init__(self, song):
        super().__init__()
        self.start = time.time()
        self.end = self.start
        self.ongoing = 0 #ongoing
        self.song = song
    def elapsed(self):
        self.end = time.time()
        current = self.ongoing + (self.end-self.start)*self.song.get_speed()
        print(self.song.get_speed())
        self.reset()
        self.ongoing = current
        return(current)
    def reset(self):
        self.start = time.time()
    async def move_back(self, prev):
        self.start = self.start - prev
    async def move_forward(self, prev):
        self.start = self.start + prev






#Intents Setup: discord.py 2.0
intents = discord.Intents.default()
intents.message_content = True
#intents.reactions = True
#intents = discord.Intents.all()
#intents.members = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("-"),
    description='MIRTIN: Music Bot',
    case_insensitive=True,
    intents=intents
)

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    ctx = await bot.get_context(message)
    if len(message.embeds)==0:
        return
    if (message.author.id != bot.user.id) or (payload.member.id == bot.user.id):
        return
    if isinstance(channel, discord.DMChannel):
        return
    if message.embeds[0].title == "Queue:": #Queue Controls
        emoji = payload.emoji.name
        print(emoji)
        if emoji == "⏮️":
            #await channel.send("BACK")
            await bot.cogs['MIRTIN'].previous(ctx)

        if emoji == "⏯️":
            #await channel.send("PLAY/PAUSE")
            await bot.cogs['MIRTIN'].pause(ctx)

        if emoji == "⏭️":
            #await channel.send("SKIP")
            await bot.cogs['MIRTIN'].skip(ctx)

        reaction = discord.utils.get(message.reactions, emoji=emoji)
        await reaction.remove(payload.member)
    else:
        return

#New loading system
async def main():
    async with bot:
        await bot.add_cog(MIRTIN(bot))
        await bot.start(token)
try:
    asyncio.run(main())
    #bot.run(token)

except Exception as e:
    print(e)
    input("Waiting for input to exit program...")
    quit()
