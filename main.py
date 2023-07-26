import discord
from discord.ext.commands import Bot
import diffuser_control
import os

TOKEN = open("token.txt", "r").read()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True

bot = Bot(intents=intents,command_prefix="$")



@bot.event
async def on_connect():
  print("Bot Connected")



bot.run(TOKEN)