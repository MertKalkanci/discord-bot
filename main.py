import nextcord as discord
from discord.ext.commands import Bot
import time
import json_ops
from lobby_creator import create_teams
from server_checker import minecraft_server_checker

TOKEN = open("token.txt", "r").read()

lobby_creator_dict = {}
shadow_ban_dict = {}
minecraft_server_dict = {}
shadow_ban_wait = 0.5

shadow_ban_dict = json_ops.load_dict_from_json("shadow_ban_list.json")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True

bot = Bot(command_prefix="$", intents=intents)

@bot.event
async def on_connect():
  print("Bot Connected")

#region shadow ban

@bot.command(name="shadow_ban",help="Shadow bans a user from chat")
async def shadow_ban(ctx: discord.message, member: discord.Member):

  if ctx.message.author.guild_permissions.administrator == False:
    await ctx.send("You do not have permission to do that!")
    return

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

  json_ops.save_dict_to_json("shadow_ban_list.json", shadow_ban_dict)

  await ctx.send(f"{member.name} has been shadow banned from chat!")

@bot.command(name="shadow_ban_list",help="Lists users shadow baned from chat")
async def shadow_ban_list(ctx):
  
    if ctx.message.author.guild_permissions.administrator == False:
      await ctx.send("You do not have permission to do that!")
      return
  
    if shadow_ban_dict.keys().__contains__(str(ctx.message.guild.id)):
      shadow_ban_list = shadow_ban_dict[str(ctx.message.guild.id)]
    else:
      shadow_ban_list = []
  
    if len(shadow_ban_list) <= 0:
      await ctx.send("No one is shadow banned!")
      return
  
    embed = discord.Embed(title="Shadow Ban List", description="List of users shadow banned from chat",color=0x00ff00)
    embed.set_author(name="Shadow Ban")
  
    members_list = []
    for i in shadow_ban_list:
      members_list.append(ctx.guild.get_member(i).mention)
  
    embed.add_field(name="Shadow Ban List", value=members_list, inline=False)
  
    await ctx.send(embed=embed)

@bot.command(name="unshadow_ban",help="Unshadow bans a user from chat")
async def unshadow_ban(ctx, member: discord.Member):

  if ctx.message.author.guild_permissions.administrator == False:
    await ctx.send("You do not have permission to do that!")
    return
  
  shadow_ban_dict[str(ctx.message.guild.id)].remove(member.id)
  json_ops.save_dict_to_json("shadow_ban_list.json", shadow_ban_dict)

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

#region minecraft_checker

@bot.command(name="minecraft_status",help="Shows the status of the minecraft server")
async def minecraft_status(ctx):
  minecraft_server_dict = json_ops.load_dict_from_json("minecraft_server.json")

  if not minecraft_server_dict.keys().__contains__(str(ctx.message.guild.id)):
    return
  
  embed = discord.Embed(title="Minecraft Server Status", description="Status of the minecraft server",color=0x00ff00)
  embed.set_author(name="Minecraft Server")

  embed.add_field(name="Status",
    value=minecraft_server_checker(minecraft_server_dict[str(ctx.message.guild.id)][0], minecraft_server_dict[str(ctx.message.guild.id)][1]),
    inline=False)
  
  await ctx.send(embed=embed)

@bot.command(name="minecraft_set",help="Sets the minecraft server")
async def minecraft_set(ctx, ip, port = 25565):
  if ctx.message.author.guild_permissions.administrator == False:
    await ctx.send("You don't have permission to do that!")
    return
  
  if not minecraft_server_dict.keys().__contains__(str(ctx.message.guild.id)):
    minecraft_server_dict[str(ctx.message.guild.id)] = []
    
  minecraft_server_dict[str(ctx.message.guild.id)] = [ip, port]
  json_ops.save_dict_to_json("minecraft_server.json", minecraft_server_dict)

  await ctx.send(f"Minecraft server {ip}, with port :{port} set!")

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