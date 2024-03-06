from discord.ext import commands, tasks
import discord
import requests
import json
from python_mcstatus import JavaStatusResponse, statusJava

BOT_TOKEN = "MTIxNDcwNjA4MTg2MzgzMTYyNA.GTlGIp.Td-KhZyH9PlAy4iN9rntfQTi0tFA4TRHXxCqFs"
CHANNEL_ID = 847240244637859850

bot = commands.Bot(command_prefix="*", intents=discord.Intents.all())

'''@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")

@bot.command()
async def add(ctx, x, y):
    sum = int(x)+int(y)
    await ctx.send(f"{x} + {y} = {sum}")

@bot.command()
async def add(ctx, *arr):
    sum = 0
    for i in arr:
        sum += int(i)
    await ctx.send(f"Result: {sum}")'''

host = '64.121.202.133'
port = 25567
query = True 

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
                        description=f"Server Status: **{status}** \n{players_online} players online",
                        color = 0xFF5733
                            )
    channel = bot.get_channel(CHANNEL_ID)
    global message
    message = await channel.send(embed = embed)


@bot.command()
async def players(ctx):
    await ctx.send(f"Player list: {player_names}")

#JavaStatusResponse = statusJava(host, port, query)
@tasks.loop(minutes=.5)
async def check_data():
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

    print(status)

    new_embed=discord.Embed(title=f"Status for {host}",
                    description=f"Server Status: **{status}** \n{players_online} players online",
                    color = 0xFF5733
                        )
    await message.edit(embed=new_embed)



@bot.event
async def on_ready():
    await embed(status,host,players_online)
    check_data.start()

bot.run(BOT_TOKEN) #looping function 

