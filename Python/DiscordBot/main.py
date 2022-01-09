#Harper Bot
import youtube_dl
import asyncio
import discord
import os
from discord.ext import commands
from myQueue import Queue

TOKEN = os.environ['token']

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '!', intents = intents)
client.remove_command("help")

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
        return cls(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename, **ffmpeg_options)), data=data)

def my_after(ctx):
    fut = asyncio.run_coroutine_threadsafe(check_queue(ctx), client.loop)
    try:
        fut.result()
    except:
        print(f'Error Occured')
        pass

async def check_queue(ctx):
    if q.front is None or q.size == 0:
        return
    else:
        q.pop()
        if q.front is not None and q.size > 0:
            ctx.voice_client.play(q.peek(), after=lambda e: f'Error Occured {e}'if e else my_after(ctx))
            embed = discord.Embed(
                title = 'Now playing:', 
                description = f'[{q.peek().title}]({q.peek().url})', 
                color = discord.Color.blue()
                )
            await ctx.send(embed=embed)
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
            embed = discord.Embed(
                title = 'Now playing:', 
                description = f'[{q.peek().title}]({q.peek().url})', 
                color = discord.Color.blue()
                )
            await ctx.send(embed=embed)
        else:
            q.push(player)
            embed = discord.Embed(
                title = 'Now queuing:', 
                description = f'[{player.title}]({player.url})', 
                color = discord.Color.green()
                )
            await ctx.send(embed=embed)                        

@client.command(pass_context = True)
async def skip(ctx): 
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        embed = discord.Embed(
            title = 'Now skipping:', 
            description = f'[{q.peek().title}]({q.peek().url})', 
            color = discord.Color.red()
            )
        await ctx.send(embed=embed) 

@client.command(pass_context = True)
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        embed = discord.Embed(
            title = 'Now pausing:', 
            description = f'[{q.peek().title}]({q.peek().url})', 
            color = discord.Color.dark_grey()
            )
        await ctx.send(embed=embed) 

@client.command(pass_context = True)
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        embed = discord.Embed(
            title = 'Now resuming:', 
            description = f'[{q.peek().title}]({q.peek().url})', 
            color = discord.Color.dark_grey()
            )
        await ctx.send(embed=embed)

@client.command(pass_context = True)
async def queue(ctx):
    if q.size > 0:
        position = 1
        node = q.front
        embed = discord.Embed(
            title = f'Current Song: {node.data.title}', 
            color = discord.Color.dark_grey()
            )
        node = node.next
        while node:
            
            if position == 1:
                embed.add_field(name='Queue:', value=f'{position}. [{node.data.title}]({node.data.url})', inline=False)
            else:
                embed.add_field(name='\u200b', value=f'{position}. [{node.data.title}]({node.data.url})', inline=False)
            node = node.next
            position += 1
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title = 'Queue is empty',
            color = discord.Color.dark_grey()
        )
        await ctx.send(embed=embed)

@client.command(pass_context = True)
async def volume(ctx, new_volume: float):
    async with ctx.typing():
        new_volume = new_volume/100
        if 0 <= new_volume <= 1.0:
            ctx.voice_client.source.volume = new_volume
            embed = discord.Embed(
                title = f'Volume set to {(int)(new_volume*100)}%', 
                color = discord.Color.dark_grey()
                )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title = f'Volume is out of range', 
                color = discord.Color.dark_grey()
                )
            await ctx.send(embed=embed)

@client.command(pass_context = True)
async def help(ctx):
    embed = discord.Embed(
        title = 'Bot Commands -',
        color = discord.Color.dark_grey()
    )
    embed.add_field(name="!join", value="Join voice channel.", inline=True)
    embed.add_field(name="!leave", value="Leave voice channel.", inline=True)
    embed.add_field(name="!play", value="Play/Queue song.", inline=True)
    embed.add_field(name="!skip", value="Skip song", inline=True)
    embed.add_field(name="!queue", value="Check song queue.", inline=True)
    embed.add_field(name="!pause", value="Pause song.", inline=True)
    embed.add_field(name="!resume", value="Resume song.", inline=True)
    embed.add_field(name="!volume", value="Change song's volume.", inline=True)
    embed.add_field(name="!help", value="Displays bot commands.", inline=True)
    await ctx.send(embed=embed)

client.run(TOKEN)