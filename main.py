import nextcord as discord
from discord.ext.commands import Bot
import time
import json_ops
from lobby_creator import create_teams

TOKEN = open("token.txt", "r").read()

lobby_creator_dict = {}
shadow_ban_dict = {}
shadow_ban_wait = 2.5

shadow_ban_dict = json_ops.load_list_from_json("shadow_ban_list.json")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True

bot = Bot(command_prefix=".", intents=intents)

@bot.event
async def on_connect():
  print("Bot Connected")

#region shadow ban

@bot.command(name="shadow_ban",help="Shadow bans a user from chat")
async def shadow_ban(ctx: discord.message, member: discord.Member):

  if shadow_ban_dict.keys().__contains__(str(ctx.message.guild.id)):
    old = shadow_ban_dict[str(ctx.message.guild.id)]
  else:
    old = []

  if old.__contains__(member.id):
    await ctx.send(f"{member.name} is already shadow banned!")
    return

  shadow_ban_dict[str(ctx.message.guild.id)] = []
  shadow_ban_dict[str(ctx.message.guild.id)].extend(old)
  shadow_ban_dict[str(ctx.message.guild.id)].append(member.id)

  json_ops.save_list_to_json("shadow_ban_list.json", shadow_ban_dict)

  await ctx.send(f"{member.name} has been shadow banned from chat!")

@bot.command(name="unshadow_ban",help="Unshadow bans a user from chat")
async def unshadow_ban(ctx, member: discord.Member):
  shadow_ban_dict[str(ctx.message.guild.id)].remove(member.id)
  json_ops.save_list_to_json("shadow_ban_list.json", shadow_ban_dict)

  await ctx.send(f"{member.name} has been unshadow banned from chat!")

#endregion

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if shadow_ban_dict.keys().__contains__(str(message.guild.id)):
    if message.author.id in shadow_ban_dict[str(message.guild.id)]:
      time.sleep(shadow_ban_wait)
      await message.delete()
      return
  await bot.process_commands(message)

#region lobby creator

@bot.command(name="add",help="Adds a member to the lobby")
async def add(ctx, member = None):
  if member == None:
    member = ctx.message.author

  if member == 'all':
    for i in ctx.guild.members:
      if not lobby_creator_dict[str(ctx.message.guild.id)].__contains__(i.id):
        lobby_creator_dict[str(ctx.message.guild.id)].append(i.id)
    await ctx.send("All members added to the lobby!")
    return

  if not member in ctx.guild.members:
    await ctx.send("Member not found!")
    return

  if not lobby_creator_dict.keys().__contains__(str(ctx.message.guild.id)):
    lobby_creator_dict[str(ctx.message.guild.id)] = []

  if lobby_creator_dict[str(ctx.message.guild.id)].__contains__(member.id):
    await ctx.send(f"{member.name} is already in the lobby!")
    return
  
  lobby_creator_dict[str(ctx.message.guild.id)].append(member.id)
  await ctx.send(f"{member.name} added to the lobby!")

@bot.command(name="remove",help="Removes a member from the lobby")
async def remove(ctx, member = None):
  if member == None:
    await ctx.send("Member not found!")
    return
  
  if lobby_creator_dict[str(ctx.message.guild.id)].__contains__(member.id):
    lobby_creator_dict[str(ctx.message.guild.id)].remove(member.id)

    await ctx.send(f"{member.name} removed frome the lobby!")
  else:
    await ctx.send(f"{member.name} is not in the lobby!")

@bot.command(name="clear",help="Clears the lobby")
async def clear(ctx):
  lobby_creator_dict[str(ctx.message.guild.id)] = []
  await ctx.send("Lobby cleared!")

@bot.command(name="lobby",help="Shows the lobby")
async def lobby(ctx):
  if lobby_creator_dict.keys().__contains__(str(ctx.message.guild.id)):
    
    if len(lobby_creator_dict[str(ctx.message.guild.id)]) <= 0:
      await ctx.send("Lobby is empty!")
      return
    
    embed = discord.Embed(title="Teams", description="Lobby of lobby creator",color=0x00ff00)
    embed.set_author(name="Lobby Creator")

    members_list = []
    for i in lobby_creator_dict[str(ctx.message.guild.id)]:
      members_list.append(ctx.guild.get_member(i).mention)


    embed.add_field(name="Lobby".format(i + 1), value=members_list, inline=False)

    await ctx.send(embed=embed)

  else:
    await ctx.send("Lobby is empty!")
    return



@bot.command(name="teams",help="Creates teams")
async def teams(ctx, team_number = 2):
  teams = create_teams(lobby_creator_dict[str(ctx.message.guild.id)], team_number)
  members_list = []
  for i in range(team_number):
    members_list.append([])
    for j in range(len(teams[i])):
      members_list[i].append(ctx.guild.get_member(teams[i][j]).mention)

  await ctx.send("Teams created!")

  embed = discord.Embed(title="Teams", description="Teams created by the lobby creator",color=0x00ff00)
  embed.set_author(name="Lobby Creator")

  for i in range(team_number):
    embed.add_field(name="Team {}".format(i + 1), value=members_list[i], inline=False)
  
  await ctx.send(embed=embed)

#endregion

@bot.command(name="join",help="Joins the voice channel")
async def join(ctx):
  if not ctx.message.author.voice:
    await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
    return
  else:
    channel = ctx.message.author.voice.channel
    await channel.connect()    
           

@bot.command(name="leave",help="Leaves the voice channel")
async def leave(ctx):
  try:
    await ctx.voice_client.disconnect()
  except:
    await ctx.send("The bot is not connected to a voice channel.")

#@bot.command(name="help",help="Help Command")
#async def help(ctx):
#  embed = discord.Embed(title="Help", description="Commands for the bot",color=0x00ff00)
#  embed.set_author(name="Help")
#
#  for i in bot.commands:
#    embed.add_field(name=i.name, value=i.help, inline=False)
#  
#  await ctx.send(embed=embed)

bot.run(TOKEN)