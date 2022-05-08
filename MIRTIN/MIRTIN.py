import asyncio
import discord
import yt_dlp
#from yt_dlp import YoutubeDL
from discord.ext import tasks, commands
import requests
import bs4
from bs4 import BeautifulSoup
import json
import time
import threading
import math
import random

yt_dlp.utils.bug_reports_message = lambda: ''

token = (open("token.txt")).readline()
if(token == ""):
    print("No token found! Be sure to add your discord bot token on the first line of the token.txt file")
    input("Waiting for input to exit program...")
    quit()
loop = asyncio.get_event_loop()
opus = False
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
filter_dict = {
    "compressor": ["acompressor",["mode: (upward, downward)","ratio: (1-20)","mix: (0-1)"]],
    "contrast" : ["acontrast",["contrast: (0-100)"]],
    "crusher": ["acrusher",["bits: (bit reduction num)","mix: (mix amount num)","mode: (lin, log)"]], #mode = "lin" or "log"
    "declick": ["adeclick",[]],
    "dyn_equalizer": ["adynamicequalizer",[]],
    "dyn_smooth": ["adynamicsmooth",[]],
    "echo": ["aecho",["in_gain: (def = 0.6)", "out_gain: (def = 0.3)", "delays: (in ms)", "decays: (loudness of echos, def=0.5)"]],
    "exciter": ["aexciter",[]],
    "fft_denoise": ["afftdn",[]],
    "freq_shift": ["afreqshift",[]],
    "wavelet_denoise": ["afwtdn",[]],
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
    "enhance_dialogue": ["dialoguenhance",[]],
    "dyn_normalize": ["dynaudnorm",[]],
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
    "tremolo": ["tremolo",["f", "d"], ["f = frequency (5), d = depth (0.5)"]],
    "vibrato": ["vibrato",["f", "d"], ["f = frequency (5), d = depth (0.5)"]],
}

ytdl_format_options = {
    'format': 'bestaudio',
    'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'wav',
    'preferredquality': '256',
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
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes

}
ytdl_playlist_format_options = {
    'format': 'bestaudio',
    'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'wav',
    'preferredquality': '256',
    }],
    'outtmpl': 'song.%(ext)s',
    #'external-downloader': 'aria2c',
    #'external-downloader-args': "-x 16 -s 16 -k 1M",
    'restrictfilenames': True,

    'default_search':"auto",
    'skip_download': True,
    'flat-playlist': True,
    #'no-flat-playlist': True,
    #'extract_flat': True,

    'nocheckcertificate': True,
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
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

class timer():
    def __init__(self):
        self.start = time.time()
        self.end = self.start
    def elapsed(self):
        self.end = time.time()
        return(self.end-self.start)
    def reset(self):
        self.start = time.time()
    async def move_back(self, prev):
        self.start = self.start - prev
    async def move_forward(self, prev):
        self.start = self.start + prev

# class YTDLSource(discord.PCMVolumeTransformer):
#     def __init__(self, source, *, data, volume=0.5):
#         super().__init__(source, volume)
#
#         self.data = data
#         self.title = data.get('title')
#         self.url = data.get('url')
#
#     @classmethod
#     async def from_url(cls, url, *, loop=None, stream=False, ffmpeg_options = ffmpeg_options):
#         loop = loop or asyncio.get_event_loop()
#         data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
#         if 'entries' in data:
#             data = data['entries'][0]
#         filename = data['url'] if stream else ytdl.prepare_filename(data)
#         return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MIRTIN(commands.Cog):
    #__slots__ = ('bot', 'players', 'queue')
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

    # async def cleanup(self, guild):
    #     try:
    #         await guild.voice_client.disconnect()
    #     except AttributeError:
    #         pass
    #
    #     try:
    #         del self.players[guild.id]
    #     except KeyError:
    #         pass
    #
    # def get_player(self, ctx):
    #     """Retrieve the guild player, or generate one."""
    #     try:
    #         player = self.players[ctx.guild.id]
    #     except KeyError:
    #         player = MusicPlayer(ctx)
    #         self.players[ctx.guild.id] = player
    #
    #     return player

    async def handle(self, ctx):
        #print("HANDLE CALLED")
        server_id = ctx.guild.id

        if server_id not in self.queue:
            #print("RESET QUEUE")
            self.queue[server_id] = Queue()

        if server_id not in self.players:
            #print("RESET PLAYING")
            self.players[server_id] = [0,timer()]

        # if server_id not in self.loops:
        #     print("RESET LOOPS")
        #     self.loops[server_id] = asyncio.new_event_loop()


    async def spotify(self, url):

        req = requests.get(url, 'html.parser')
        soup = BeautifulSoup( req.content , 'html.parser')
        type = str(soup.find("meta", property="og:type")["content"])
        if(type == "music.playlist"):
            songs = soup.find_all(type="track")
            songs = list(songs)
            song_list = []

            count = 0
            for song in songs:
                count +=1
                song_list.append(' : '.join(song.get_text("‽").split("‽")))
            print(song_list)
            return(song_list)
        if(type == "music.song"):
            title = str(soup.find("meta", property="og:title")["content"])
            desc = str(soup.find("meta", property="og:description")["content"])
            return([title+" : "+desc])



    async def search(self, ctx, query):
        stream = True
        songs = []
        if query.startswith("https://youtube.com/") or query.startswith("https://www.youtube.com/") or query.startswith("www.youtube.com/") or query.startswith("youtube.com/"): #Proper URL
            #Proper URL
            url = query
        else: #Search Required
            ytdl_data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{query}", download=not stream))
            url = ytdl_data["entries"][0]["url"]

        ytdl_data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if ytdl_data["url"].startswith("https://www.youtube.com/"): #Playlist:
            #Reprocess URL
            await ctx.send("Loading Playlist...")
            ytdl_data = await self.bot.loop.run_in_executor(None, lambda: ytdl_playlist.extract_info(ytdl_data["url"], download=not stream))
            return(ytdl_data['entries'])

        else: #Song:
            #print(ytdl_data)
            return([ytdl_data])

    async def del_song(self,ctx):
        server_id = ctx.message.guild.id
        self.queue[server_id].last_song = (self.queue[server_id].queue).pop(0)
        self.bot.loop.create_task(self.play_next(ctx))

    async def play_next(self,ctx):
        server_id = ctx.message.guild.id
        if len(self.queue[server_id].queue) >= 1:
            url = self.queue[server_id].queue[0].ytdl_data["url"]
            #print("URL YTDL DATA:")
            #print(url)
            stream = True
            #If opus == True, volume commands will not work.
            if opus:
                self.players[server_id][0] = discord.FFmpegOpusAudio(url, **ffmpeg_options)
                print("opus")
            if not opus:
                self.players[server_id][0] = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **ffmpeg_options))
                print("not opus")
            print("audio init")

            if (ctx.message.guild.voice_client).is_connected() == False:
                await (ctx.message.guild.voice_client).connect(reconnect = True,timeout = 60.0)

            if ctx.voice_client.is_playing():
                print("PASS")
                pass
            elif not ctx.voice_client.is_playing():
                print("STARTING PLAY")
                self.players[server_id][1] = timer()
                ctx.voice_client.play(self.players[server_id][0], after=lambda e: print(f'Player error: {e}') if e else self.bot.loop.create_task(self.del_song(ctx)))
                await ctx.send('Now playing: {}'.format(self.queue[server_id][0].ytdl_data["title"]))

        else:
            print("End of queue")
            await ctx.send("End of queue")

    @commands.command()
    async def join(self, ctx, *args):
        """Joins a voice channel"""
        await self.handle(ctx)
        #handle = await self.bot.loop.create_task(self.handle(ctx))
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect(timeout=60.0, reconnect=True)

    @commands.command()
    async def leave(self, ctx, *args):
        """Leaves a voice channel"""
        await self.handle(ctx)
        #handle = await self.bot.loop.create_task(self.handle(ctx))
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()
            return await ctx.send("Disconnected")
        else:
            return await ctx.send("Not in a VC")

    @commands.command(aliases = ['p','P','Play'])
    async def play(self, ctx, *, query=""):
        """Processes a song request and passes it to the queue, starts playing if empty queue"""
        await self.handle(ctx)
        server_id = ctx.guild.id
        voice_client = ctx.voice_client
        if len(query) == 0:
            voice_channel = ctx.message.guild.voice_client
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
        #if not voice_client:
        await self.join(ctx)
        url_flag = ""
        #yt_url_check = ["youtube.com/watch?v=", "http://youtube.com/watch?v=", "https://youtube.com/watch?v="]
        spot_url_check = ["https://open.spotify.com/"]
        async with ctx.typing():

            for i in spot_url_check:
                if i in query:
                    url_flag = "spot"

            if url_flag == "spot": #SPOTIFY LINK
                songs_list = await self.spotify(query)
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
                    await (self.queue[server_id]).add(song)
                    count += 1
                    prog_frac = (count/total)
                    prog_num = math.floor(prog_frac*prog_size)
                    prog_str = str("["+str(prog_char*prog_num)+str(incomp_char*(prog_size-prog_num))+"] "+str(round((prog_frac*100), 1))+"%")
                    await prog_msg.edit(content = prog_str)

            else: #All other playlists
                songs = []
                songs_data = await self.search(ctx, query)
                for song_data in songs_data:
                    songs.append(Song(song_data))

                #Progress Bar for Playlists:
                count = 0
                total = len(songs)
                prog_size = 10
                prog_char = "█"
                incomp_char   = "░"
                prog_frac = (count/total)
                prog_num = math.floor(prog_frac*prog_size)
                prog_str = str("["+str(prog_char*prog_num)+str(incomp_char*(prog_size-prog_num))+"] "+str(round((prog_frac*100), 1))+"%")
                prog_msg = await ctx.send(prog_str)
                for song in songs:
                    await (self.queue[server_id]).add(song)
                    count += 1
                    prog_frac = (count/total)
                    prog_num = math.floor(prog_frac*prog_size)
                    prog_str = str("["+str(prog_char*prog_num)+str(incomp_char*(prog_size-prog_num))+"] "+str(round((prog_frac*100), 1))+"%")
                    await prog_msg.edit(content = prog_str)

            if len(self.queue[server_id].queue) == 1:
                print("First song in Queue...")
                await self.play_next(ctx)
            else:
                print("Added to queue!")
                await ctx.send("Added to queue!")

    @commands.command(aliases = ['s','S','Skip'], brief="Skips a song")
    async def skip(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client
        if not voice_channel.is_playing():
            await self.play_next(ctx)
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
        #id = (self.queue[server_id])[0].data["id"]
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
    async def filter(self, ctx, *filter_lists):
        """Filter audio: help to see all, help <filtername> to see specific"""
        """https://ffmpeg.org/ffmpeg-filters.html"""
        #FILTER SYNTAX:
        #-filter:a <filter>= <var>=<val>:<var2>=<val2>

        await self.handle(ctx)
        operation_time = timer()
        server_id = ctx.message.guild.id
        print("START TIMER ELAPSED:")
        current_time = (self.players[server_id][1]).elapsed()
        print(current_time)
        ffmpeg_options_custom = ffmpeg_options.copy()
        #ffmpeg_options_custom['options'] += "-filter:a "
        #ffmpeg_options_custom['options'] += "-af:a "
        filter_lists = str(' '.join(filter_lists))
        print(filter_lists)
        filter_lists = filter_lists.split(",")
        print("FILTER LISTS:")
        print(filter_lists)

        filter_str = ""
        for filter_list in filter_lists:
            filter_list = filter_list.strip(" ").split(" ")
            print(filter_list)
            if len(filter_list)>=1:
                filter_type = filter_list.pop(0)
                print(filter_type)
                if filter_type not in filter_dict:
                    if filter_type == "help":
                        if len(filter_list) == 0:
                            await ctx.send("ALL FILTERS:")
                            await ctx.send("```"+str(list(filter_dict.keys()))+"```")
                            return
                            #for i in list(filter_dict.keys()):
                                #await ctx.send(str(i))
                        elif (len(filter_list) == 1) and (filter_list[0] in filter_dict):
                            await ctx.send("FILTER INFO:")
                            for i in filter_dict[filter_list[0]][1]:
                                #print(i)
                                await ctx.send(i)
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

        #self.players[server_id][0] = discord.FFmpegOpusAudio(url, **ffmpeg_options)
        self.players[server_id][0] = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **ffmpeg_options_custom))


        ctx.voice_client.play(self.players[server_id][0], after=lambda e: print(f'Player error: {e}') if e else self.bot.loop.create_task(self.del_song(ctx)))
        func_time = operation_time.elapsed()
        #self.bot.loop.create_task(self.players[server_id][1].move_back(current_time))
        #self.bot.loop.create_task(self.players[server_id][1].move_back(func_time))
        #self.bot.loop.create_task(self.players[server_id][1].move_forward(func_time))
        print(self.players[server_id][1].elapsed())
        self.queue[server_id].queue.insert(0,song)


    @commands.command(aliases = ['q','Q','Queue'], brief="Lists the queue")
    async def queue(self, ctx):
        server_id = ctx.message.guild.id
        await self.handle(ctx)
        lensongs = 5
        if lensongs > len(self.queue[server_id].queue):
            lensongs = len(self.queue[server_id].queue)
        if len(self.queue[server_id].queue) > 0:
            embed = discord.Embed(title="Queue:",description=f"Showing up to next {lensongs} tracks, {len(self.queue[server_id].queue)} songs in total",colour=ctx.author.colour)
            embed.add_field(name="Currently playing:",value=self.queue[server_id][0].ytdl_data["title"], inline=False)
        else:
            embed = discord.Embed(title="Queue:",description=f"Empty",colour=ctx.author.colour)
        if len(self.queue[server_id].queue) > 1:
            embed.add_field(
                name="Next up:",
                value=("\n".join(self.queue[server_id][i].ytdl_data["title"] for i in range(1, lensongs))),
                inline=False
            )
            if len(self.queue[server_id].queue) > lensongs:
                embed.set_footer(text="And " + str(len(self.queue[server_id].queue)-lensongs) + " more...")
        msg = await ctx.send(embed=embed)


    @commands.command(aliases = ['v','V','Volume'], brief="Changes bot volume for everyone")
    async def volume(self, ctx, volume: int):
        """Changes global bot volume? (WIP)"""
        await self.handle(ctx)
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        if ctx.voice_client.is_playing():
            #ctx.voice_client.volume = volume / 100
            ctx.voice_client.source.volume = volume / 100


        #ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

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

    @commands.command()
    async def clear(self, ctx):
        """Removes all songs in queue after current song"""
        await self.handle(ctx)
        server_id = ctx.message.guild.id
        current = self.queue[server_id].queue[0]
        self.queue[server_id].queue = []
        self.queue[server_id].queue.append(current)
        await ctx.send("Cleared Queue")

    @play.before_invoke
    #@play_next.before_invoke
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
        self.last_song = Song(0)

    def __setitem__(self, index, data):
        self.queue[index] = data
    def __getitem__(self, index):
        return self.queue[index]
    async def add(self, song):
        self.queue.append(song)
        return

    def remove(self, index):
        song = self.queue.pop(index)
        print("REMOVED:")
        print(song.ytdl_data["title"])
        print("END REMOVED, RETURNING...")
        return(song)

    def move(self, index1, index2):
        song = self.queue.pop(index)
        self.queue.insert(index2, song)
        return

    def shuffle(self):
        if len(self.queue) > 1:
            current = self.queue[0]
            random.shuffle(self.queue)
            current_pos = self.queue.index(current)
            current_new = self.queue[0]
            newpos = 0
            if len(self.queue)>1:
                current = self.queue.pop(currentpos)
                newcurrent = self.queue.pop(newpos)
                self.queue.insert(newpos, current)
                self.queue.insert(currentpos, newcurrent)

class Song(Queue):
    def __init__(self, ytdl_data):
        self.ytdl_data = ytdl_data

bot = commands.Bot(command_prefix=commands.when_mentioned_or("-"), description='MIRTIN: Music Bot')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

bot.add_cog(MIRTIN(bot))
try:
    bot.run(token)
except Exception as e:
    print(e)
    input("Waiting for input to exit program...")
    quit()
