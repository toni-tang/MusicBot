#Harper Bot
import youtube_dl
import asyncio
import discord
import os
from discord.ext import commands
from myQueue import Queue

my_secret = os.environ['token']

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '!', intents = intents)

q = Queue()

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


def my_after(ctx):
    coro = check_queue(ctx)
    fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
    try:
        fut.result()
    except:
        print(f'Error Occured')
        fut.cancel()
        pass


async def check_queue(ctx):
    if q.front is None and q.size == 0:
        return
    else:
        q.pop()
        if q.front is not None and q.size > 0:
            ctx.voice_client.play(q.peek(), after=lambda e: f'Error Occured {e}'if e else my_after(ctx))
            await ctx.send(f'Playing song: {q.peek().title}')
        else:
            return

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
        if not ctx.voice_client.is_playing() and q.size == 0:
            q.push(player)
            ctx.voice_client.play(q.peek(), after=lambda e: f'Error Occured {e}'if e else my_after(ctx))
            await ctx.send(f'Playing song: {q.peek().title}')
        else:
            q.push(player)
            await ctx.send(f'Queuing song: {player.title}')                        

@client.command(pass_context = True)
async def pause(ctx):
    if ctx.voice_client.is_playing():
       ctx.voice_client.pause()
       await ctx.send(f'Pausing song: {q.peek().title}')

@client.command(pass_context = True)
async def skip(ctx):
    if ctx.voice_client.is_playing():
       ctx.voice_client.stop()
       await ctx.send(f'Skipping song: {q.peek().title}')
       my_after(ctx)

@client.command(pass_context = True)
async def resume(ctx):
    if ctx.voice_client.is_paused():
       ctx.voice_client.resume()
       await ctx.send(f'Resuming song: {q.peek().title}')

@client.command(pass_context = True)
async def queue(ctx):
    if q.size > 0:
        node = q.front
        await ctx.send(f'Queue: ')
        while node:
            await ctx.send(f'{node.data.title}')
            node = node.next
    else:
        await ctx.send(f'Queue is empty.')

client.run(my_secret)
