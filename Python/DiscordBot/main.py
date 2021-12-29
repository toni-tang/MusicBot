#Harper Bot
import youtube_dl
import asyncio
import discord
import os
from discord.ext import commands

my_secret = os.environ['token']

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '!', intents = intents)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command(pass_context = True)
async def join(ctx):
  if(ctx.author.voice):
    channel = ctx.message.author.voice.channel
    await channel.connect()
  else:
    await ctx.send('You are not in a voice channel.')

@client.command(pass_context = True)
async def leave(ctx):
  if(ctx.voice_client):
    await ctx.guild.voice_client.disconnect()
  else:
    await ctx.send('I am not in a voice channel.')

@client.command(pass_context = True)
async def play(ctx, url):
    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=ctx.bot.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
    await ctx.send(f'Now playing: {player.title}')

@client.command(pass_context = True)
async def pause(ctx):
    if ctx.voice_client.is_playing():
       ctx.voice_client.pause()
       await ctx.send(f'Paused song.')

@client.command(pass_context = True)
async def stop(ctx):
    if ctx.voice_client.is_playing():
       ctx.voice_client.stop()
       await ctx.send(f'Stopped song.')

@client.command(pass_context = True)
async def resume(ctx):
    if not ctx.voice_client.is_playing():
       ctx.voice_client.resume()
       await ctx.send(f'Resumed song.')

client.run(my_secret)
