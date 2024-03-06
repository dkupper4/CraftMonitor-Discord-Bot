from discord.ext import commands, tasks
import discord
import requests
import json
from python_mcstatus import JavaStatusResponse, statusJava
import minestat

BOT_TOKEN = "MTIxNDcwNjA4MTg2MzgzMTYyNA.GO1cEQ.caW0Ubzl7LtsRkctIDlXzi2V21Rp7FVMIfj3k0"
CHANNEL_ID = 847240244637859850

bot = commands.Bot(command_prefix="*", intents=discord.Intents.all())

'''@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")
'''

host = '64.121.202.133'
port = 25567
query = True 


#Initialize data when bot starts
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
    player_names = "None"

async def embed(status,host,players_online):
    if status == True:
        status = str("ONLINE")
    else:
        status = str("OFFLINE")
    
    embed=discord.Embed(title=f"Status for {host}",
                        description=f"Server Status: __**{status}**__ \nPlayers online: {players_online}\n Latency: {latency}ms",
                        color=discord.Color.dark_green()
                            )
    channel = bot.get_channel(CHANNEL_ID)
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
async def on_ready():
    await embed(status,host,players_online)
    check_data.start()

#Continually runs the bot
bot.run(BOT_TOKEN) #looping function 

