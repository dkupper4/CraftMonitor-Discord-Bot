from discord.ext import commands, tasks
import discord
import requests
import json
from python_mcstatus import JavaStatusResponse, statusJava
import minestat
import sqlite3

#SQL Database
con = sqlite3.connect("guilds.db")
cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS guilds
                    (guildId integer PRIMARY KEY, channelId integer, messageId integer, serverId text)''')

con.commit()

BOT_TOKEN = "MTIxNDcwNjA4MTg2MzgzMTYyNA.GnLF0j.tRQC4OGF_1ppLdvwAMDHRIDZ_Z7Gheo2834Y8o"
CHANNEL_ID = 847240244637859850

bot = commands.Bot(command_prefix="*", intents=discord.Intents.all())

global status


#Initialize data when bot starts
ms = minestat.MineStat('64.121.202.133', 25567)
latency = ms.latency
r = requests.get("https://api.mcstatus.io/v2/status/java/64.121.202.133:25567")
data = json.loads(r.text)
status = data['online']
print(status)
host = data['host']
if status == True:
    players_online = data['players']['online']
    player_lst = data['players']['list']
    player_names = []
    for i in range(len(player_lst)):
        player_names += [player_lst[i]['name_clean']]
else:
    players_online = 0
    player_names = "None"

if status == True:
    status = str("ONLINE")
else:
    status = str("OFFLINE")

@bot.command()
async def serverstatus(ctx):
    embed=discord.Embed(title=f"Status for {host}",
                        description=f"Server Status: __**{status}**__ \nPlayers online: {players_online}\n Latency: {latency}ms",
                        color=discord.Color.dark_green()
                            )
    
    channel_id = await get_channelId(ctx.guild.id)
    channel = ctx.guild.get_channel(channel_id)
    global message
    message = await channel.send(embed = embed)


#Bot commands
@bot.command()
async def players(ctx):
    await ctx.send(f"Player list: {player_names}")

#Update data for bot to display
#JavaStatusResponse = statusJava(host, port, query)

@tasks.loop(minutes=.5)
async def check_data():
    ms = minestat.MineStat('64.121.202.133', 25567)
    latency = ms.latency
    r = requests.get("https://api.mcstatus.io/v2/status/java/64.121.202.133:25567")
    data = json.loads(r.text)
    status = data['online']
    host = data['host']
    if status == True:
        players_online = data['players']['online']
        player_lst = data['players']['list']
        player_names = []
        for i in range(len(player_lst)):
            player_names += [player_lst[i]['name_clean']]
    else:
        players_online = 0
    


    if status == True:
        status = str("ONLINE")
    else:
        status = str("OFFLINE")

    new_embed=discord.Embed(title=f"Status for {host}",
                        description=f"Server Status: __**{status}**__ \nPlayers online: {players_online}\n Latency: {latency}ms",
                        color=discord.Color.dark_green()
                            )
    await message.edit(embed=new_embed)


#Runs when bot initalizes
@bot.event
async def on_guild_join(guild):
    guild_id = guild.id
    channel = guild.system_channel
    channel_id = channel.id

    cur.execute(f"INSERT INTO guilds (guildId, channelId) VALUES ('{guild_id}', '{channel_id}')")
    con.commit()

@bot.event
async def on_ready():
    print("Bot is online")

async def get_channelId(guildId):
    cur.execute(f'SELECT channelId FROM guilds WHERE guildId = ?', (guildId,))
    result = cur.fetchone()

    return result[0] if result else None

#Continually runs the bot
bot.run(BOT_TOKEN) #looping function 

