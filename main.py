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

@bot.command()
async def generate(ctx, *args):
    text = ""
    for i in args:
        text += i + " "
    text = text.rstrip(text[-1])

    img = diffuser_control.generate_img(text)

    await ctx.send(content=f'{text}',file=discord.File(img))

bot.run(TOKEN)