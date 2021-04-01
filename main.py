import discord
import os
# from datetime import datetime
# import json
from Pinger import StatusPing
from server import keep_alive
import discord.ext
import base64
import asyncio
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, check

LIST = []

class discordRoom:
  def __init__(self, serverId = 0, channelId = None, channelName = None, host = "", port = 0, currentStatus = False, notify = False):
    self.serverId = serverId
    self.channelId = channelId
    self.channelName = channelName
    self.host = host
    self.port = port
    self.currentStatus = currentStatus
    self.notification = notify

  def search(self, serverId):
    for server in LIST:
      if server.serverId == serverId:
        return server
    return -1

  def get_server(self, serverId):
    server = self.search(serverId)
    
    if server == -1:
      global LIST
      node = discordRoom(serverId)
      LIST.append(node)
      server = self.search(serverId)

    return server
  
  def notify(self):
    self.notification = True
    return
  
  def stop_notify(self):
    self.notification = False
    self.channelId = None
    self.channelName = None
    return


TIMEOUT = 2
# SERVERHOST = "https://Discord-Bot-for-MC.stevenrhenaldy.repl.co"
SERVERHOST = "https://DiscordMC.stevenrhenaldy.repl.co"

client = discord.Client()

client = commands.Bot(command_prefix = '/') #Prefix

@client.event
async def on_ready():
    print("Bot Online")
    print("Logged in as")
    print(client.user.name)
    print("---------------------")
    
@client.command(aliases = ["w", "Who"])
async def who(ctx):
    serverId = ctx.message.guild.id
    room = discordRoom()
    server = room.get_server(serverId)

    if(server.host == "" or server.port == -1):
      await ctx.send(">>> Please assign your server first:\n(Make sure that your server is online) \n`/assign <server address>`")
      return
    

    status = StatusPing(server.host, server.port, TIMEOUT)
    getstats = status.get_status()
    author = ctx.author

    if getstats == -1 or getstats == "Timed Out":
      embed=discord.Embed(title="Server Offline", color=0xff0000)

    elif "Offline" in getstats['version']['name']:
      embed=discord.Embed(title="Server Offline", color=0xff0000)

    else:
      plyrs = getstats['players']
      embed=discord.Embed(title="Player List", color=0x00ff00)
      try:
        players = plyrs['sample']
      except:
        players = ""

      playerList = ""
      for player in players:
        playerList += f"‣ {player['name']}\n"
      
      
      embed.description = playerList
      embed.add_field(name="Online:", value= f"{plyrs['online']}/{plyrs['max']}")

      image_data = getstats['favicon']
      image_file = f"pic/{server.host}.png" 
      if not os.path.exists(image_file):
        with open(image_file, "wb") as fh:
          fh.write(base64.b64decode(image_data.split(',')[1]))

      icon = f"{SERVERHOST}/{image_file}" #Get Picture address from webserver

      embed.set_author(name = (server.host.split('.')[0]), icon_url=icon)

      embed.set_footer(text=f"{server.host}", icon_url=author.avatar_url)
    # embed.set_footer(text=f"{HOST}", icon_url=icon) # To put icon in footer
    
    await ctx.send(embed = embed)


@client.command(aliases=["add", "assign"])
async def addserver(ctx, serveraddr: str=""):
  serverId = ctx.message.guild.id
  room = discordRoom()
  ping = StatusPing()
  server = room.get_server(serverId)

  if(serveraddr == ""):
    output = ">>> Please enter your server address.\n`/assign <server address>`"
    await ctx.send(output)
    return

  host, port = ping.lookup(serveraddr)

  if host == -1:
    output = ">>> Failed to assign server\n`Make sure that your server is online.`"
    await ctx.send(output)
    return

  server.host = host
  server.port = port
  
  status = StatusPing(server.host, server.port, TIMEOUT)
  getstats = status.get_status()

  # print(getstats)
  image_data = getstats['favicon']
  image_file = f"pic/{server.host}.png" 
  if not os.path.exists(image_file):
    with open(image_file, "wb") as fh:
      fh.write(base64.b64decode(image_data.split(',')[1]))

  icon = f"{SERVERHOST}/{image_file}" #Get Picture address from webserver
  embed=discord.Embed(title="", url=icon, color=0xffd600)
  try:
    embed.description=f"{getstats['description']['extra']}"
  except:
    try:
      embed.description=f"{getstats['description']['text']}"
    except:
      try:
        embed.description=f"{getstats['description']}"
      except:
        pass

  embed.set_author(name=(server.host.split('.')[0]))
  embed.set_thumbnail(url=icon)
  embed.add_field(name="Online", value=f"{getstats['players']['online']} / {getstats['players']['max']}", inline=True)
  embed.add_field(name="Server", value=f"{getstats['version']['name']}", inline=True)
  embed.set_footer(text=f"{server.host}:{server.port}")
  
  await ctx.send(embed=embed)
  return

@client.command(aliases=["s", "S"])
async def status(ctx):
  serverId = ctx.message.guild.id
  room = discordRoom()
  ping = StatusPing()
  server = room.get_server(serverId)

  if(server.host == "" or server.port == -1):
    await ctx.send(">>> Please assign your server first:\n(Make sure that your server is online) \n`/assign <server address>`")
    return

  status = StatusPing(server.host, server.port, TIMEOUT)
  getstats = status.get_status()

  # print(getstats)
  image_data = getstats['favicon']
  image_file = f"pic/{server.host}.png" 
  if not os.path.exists(image_file):
    with open(image_file, "wb") as fh:
      fh.write(base64.b64decode(image_data.split(',')[1]))

  icon = f"{SERVERHOST}/{image_file}" #Get Picture address from webserver

  embed=discord.Embed(title="", url=icon, color=0xffd600)

  try:
    embed.description=f"{getstats['description']['extra']}"
  except:
    try:
      embed.description=f"{getstats['description']['text']}"
    except:
      try:
        embed.description=f"{getstats['description']}"
      except:
        pass
  

  embed.set_author(name=(server.host.split('.')[0]))
  embed.set_thumbnail(url=icon)
  embed.add_field(name="Online", value=f"{getstats['players']['online']} / {getstats['players']['max']}", inline=True)
  embed.add_field(name="Server", value=f"{getstats['version']['name']}", inline=True)
  embed.set_footer(text=f"{server.host}:{server.port}")
  
  await ctx.send(embed=embed)
  return


@client.command(aliases=["n", "notif"])
async def notify(ctx):
  serverId = ctx.message.guild.id
  room = discordRoom()
  server = room.get_server(serverId)

  if(server.host == "" or server.port == -1):
    await ctx.send(">>> Please assign your server first:\n(Make sure that your server is online) \n`/assign <server address>`")
    return

  channelid = ctx.channel.id
  channelname = ctx.channel

  if server.channelId == None:
    output = f">>> Start sending notification to: \n`#{channelname}`"
  elif server.channelId == channelid:
    output = f">>> Sending notification to: \n`#{channelname}`"
  else:
    output = f">>> Stop sending notification to:\n`#{server.channelName}`\nStart sending notification to: \n`#{channelname}`"

  server.channelName = channelname
  server.channelId = channelid

  server.notify()
  
  await ctx.send(output)
  return

@client.command(aliases=["stop", "stop notify"])
async def stop_notify(ctx):
  serverId = ctx.message.guild.id
  room = discordRoom()
  server = room.get_server(serverId)

  if server.notification == True:
    output = f">>> Stop sending notification to:\n`#{server.channelName}`"
    server.stop_notify()
  else:
    output = f">>> Notification hasn't been activated"

  await ctx.send(output)
  return

async def my_background_task():
  while True:
    for node in LIST:
      if node.notification == True:
        channel = client.get_channel(int(node.channelId))
        try:
          status = StatusPing(node.host, node.port, TIMEOUT)
          getstats = status.get_status()
        except:
          getstats = -1

        if getstats != -1 and getstats != "Timed Out":
          if node.currentStatus == False:
            embed=discord.Embed(title="Server Online!", color=0x00ff00)
            embed.set_footer(text=f"{node.host}")
            node.currentStatus = True

            await channel.send(embed = embed)

        else:
          if node.currentStatus == True:
            embed=discord.Embed(title="Server Offline!", color=0xff0000)
            embed.set_footer(text=f"{node.host}")
            node.currentStatus = False
        
            await channel.send(embed = embed)

    await asyncio.sleep(20) 

@client.command()
async def test(ctx):
  inlist = ''
  output = ctx.message.guild.id
  for i in LIST:
    inlist += f"{i.serverId}\n"
  
  print(inlist)

  await ctx.send(output)
  return



client.loop.create_task(my_background_task())
keep_alive()

client.run(os.getenv("TOKEN"))
