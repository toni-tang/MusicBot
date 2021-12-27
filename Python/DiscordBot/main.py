#Harper Bot
import discord
from discord.ext import commands
import os

my_secret = os.environ['token']

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '!', intents = intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command(pass_context = True)
async def join(ctx):
  if(ctx.author.voice):
    channel = ctx.message.author.voice.channel
    await channel.connect()
  else:
    await ctx.send("You are not in a voice channel.")

@client.command(pass_context = True)
async def leave(ctx):
  if(ctx.voice_client):
    await ctx.guild.voice_client.disconnect()
  else:
    await ctx.send('I am not in a voice channel.')

client.run(my_secret)

