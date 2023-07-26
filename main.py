import discord
from discord.ext.commands import Bot
import time
import json_ops

TOKEN = open("token.txt", "r").read()

shadow_ban_list = {}
shadow_ban_wait = 2.5

shadow_ban_list = json_ops.load_list_from_json("shadow_ban_list.json")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True

bot = Bot(intents=intents,command_prefix="/")

@bot.event
async def on_connect():
  print("Bot Connected")

#region shadow ban

@bot.command()
async def shadow_ban(ctx: discord.message, member: discord.Member):

  if shadow_ban_list.keys().__contains__(str(ctx.message.guild.id)):
    old = shadow_ban_list[str(ctx.message.guild.id)]
  else:
    old = []

  if old.__contains__(member.id):
    await ctx.send(f"{member.name} is already shadow banned!")
    return

  shadow_ban_list[str(ctx.message.guild.id)] = []
  shadow_ban_list[str(ctx.message.guild.id)].extend(old)
  shadow_ban_list[str(ctx.message.guild.id)].append(member.id)

  json_ops.save_list_to_json("shadow_ban_list.json", shadow_ban_list)

  await ctx.send(f"{member.name} has been shadow banned from chat!")

@bot.command()
async def unshadow_ban(ctx, member: discord.Member):
  shadow_ban_list[str(ctx.message.guild.id)].remove(member.id)
  json_ops.save_list_to_json("shadow_ban_list.json", shadow_ban_list)

  await ctx.send(f"{member.name} has been unshadow banned from chat!")


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if shadow_ban_list.keys().__contains__(str(message.guild.id)):
    if message.author.id in shadow_ban_list[str(message.guild.id)]:
      time.sleep(shadow_ban_wait)
      await message.delete()
      return
  await bot.process_commands(message)

#endregion

bot.run(TOKEN)