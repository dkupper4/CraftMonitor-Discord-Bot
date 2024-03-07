from discord.ext import commands,tasks
import discord 
import minestat
import sqlite3

#SETTING UP THE SQL DATABSE
con = sqlite3.connect("guilds.db")
cur = con.cursor()

#CREATE TABLE FOR DATABASE
cur.execute("CREATE TABLE IF NOT EXISTS guilds(guildId text PRIMARY KEY, channelId text, messageId text, mcserverId text, portId text)")
con.commit()

#SETTING UP THE BOT
BOT_TOKEN = "MTIxNDcwNjA4MTg2MzgzMTYyNA.GnLF0j.tRQC4OGF_1ppLdvwAMDHRIDZ_Z7Gheo2834Y8o"

bot = commands.Bot(command_prefix = "CM ", intents=discord.Intents.all())

#INITIALIZING THE BOT WHEN IT JOINS A NEW SERVER
@bot.event
async def on_guild_join(guild):
    guild_id = guild.id
    channel = guild.system_channel
    channel_id = channel.id

    await channel.send("CraftMonitor is online!")

    cur.execute(f"INSERT INTO guilds(guildId, channelId) VALUES ('{guild_id}', '{channel_id}')")
    con.commit()

#ON BOT READY 
@bot.event
async def on_ready():
    check_data.start()

async def initialize_embed(serverID,channel,guild_id, port_id=None):

    if not port_id:
        ms = minestat.MineStat(serverID)
    else:
        port_id = int(port_id)
        ms = minestat.MineStat(serverID, port_id)
        
    latency = ms.latency
    online = ms.online
    player_count = ms.current_players

    if online == True:
        status = "ONLINE"
    else:
        status = "OFFLINE"
    
    embed=discord.Embed(title=f"Status for {serverID}",
                        description=f"Server Status: __**{status}**__ \nPlayers online: {player_count}\n Latency: {latency}ms",
                        color=discord.Color.dark_green()
                            )
    message = await channel.send(embed = embed)
    cur.execute("UPDATE guilds SET messageId = ? WHERE guildId = ?", (message.id, guild_id))
    con.commit()

#LOOP TO CHECK AND UPDATE EMBED
@tasks.loop(seconds=10)
async def check_data():
    cur.execute("SELECT guildId FROM guilds")
    guilds = cur.fetchall()
        
    guildslst = []
    for i in range(len(guilds)):
        guildslst += guilds[i]

    for i in range(len(guildslst)):

        print("Checking data using params from Guild: ", guildslst[i])

        #PULL SERVER ID FROM DATABASE AND HANDLE IF IT IS FOUND OR NOT
        cur.execute(f"SELECT mcserverId FROM guilds where guildId = ?", (guildslst[i],))
        serverID = cur.fetchone()
        if serverID is not None:
            serverID = str(serverID[0])
            if serverID != 'None':
                print("Server: ", serverID)
            else:
                print("No ServerID has been set in this guild: ", guildslst[i])
                continue
        else:
            print("No ServerID has been set in this guild: ", guildslst[i])
            continue

        cur.execute(f"SELECT portId FROM guilds where guildId = ?", (guildslst[i],))
        portID = cur.fetchone()
        portID = str(portID[0])
        print("PortID: ", portID)
        

        if portID == "None":
            print("Gathering data from: ", serverID)
            ms = minestat.MineStat(serverID)
        else:
            portID = int(portID)
            ms = minestat.MineStat(serverID, portID)
        latency = ms.latency
        online = ms.online
        player_count = ms.current_players

        if online == True:
            status = "ONLINE"
        else:
            status = "OFFLINE"
        
        cur.execute(f"SELECT channelId FROM guilds where guildId = ?", (str(guildslst[i]),))
        channel = cur.fetchone()
        channel = int(channel[0])

        #SELECT A MESSAGE FROM DATABASE A GUILD i
        cur.execute(f"SELECT messageId FROM guilds WHERE guildId = ?", (str(guildslst[i]),))
        message = cur.fetchone()
        #CHECK IF MESSAGE IS NOT EMPTY (IT EXISTS)
        if message is not None:
            message = str(message[0])
            if message != 'None':
                message = int(message)
                channelobj = bot.get_channel(channel)
                
                #IF CHANNEL EXISTS, TRY AND FETCH THE MESSAGE USING THE MESSAGE ID, IF NOT PRINT 'NOT FOUND'
                if channelobj: 
                    try:
                        message2 = await channelobj.fetch_message(message)
                        new_embed=discord.Embed(title=f"Status for {serverID}",
                            description=f"Server Status: __**{status}**__ \nPlayers online: {player_count}\n Latency: {latency}ms",
                            color=discord.Color.dark_green()
                                )
                        await message2.edit(embed=new_embed)   
                    except discord.NotFound:
                        embed=discord.Embed(title=f"Status for {serverID}",
                            description=f"Server Status: __**{status}**__ \nPlayers online: {player_count}\n Latency: {latency}ms",
                            color=discord.Color.dark_green()
                            )
                        message = await channelobj.send(embed = embed)
                        cur.execute(f"UPDATE guilds SET messageId = ? WHERE guildId = ?", (message.id, str(guildslst[i])))
                        con.commit()

                        print("Message not found. Sent a new message")
            else:
                print("No message is found in the database")
                continue 
        else: 
            print("No message is found in the database")
            continue
    
    
#BOT COMMANDS

#Changes the home channel for the bot
@bot.command()
async def setchannel(ctx):
    guild_id = ctx.guild.id
    new_channelId = ctx.channel.id

    cur.execute(f"SELECT channelId FROM guilds where guildId = ?", (str(guild_id),))
    channel = cur.fetchone()
    channel = int(channel[0])

    channel = bot.get_channel(channel)

    cur.execute(f"SELECT messageId FROM guilds WHERE guildId = ?", (str(guild_id),))
    message = cur.fetchone()
    
    if message is not None:
            message = str(message[0])
            if message != 'None':
                message = int(message)
                try:
                    messageToDelete = await channel.fetch_message(message)
                    await messageToDelete.delete()
                except:
                    print("Did not find a message to delete")
            else:
                print("No message is found in the database") 
    else: 
            print("No message is found in the database")

    cur.execute(f"UPDATE guilds SET channelId = ? WHERE guildId = ?", (new_channelId, guild_id))
    con.commit()
    channelstr = ctx.channel
    await ctx.send(f"Channel ID updated to **`#{channelstr}`** for this guild.")

#Adds a server for the bot to pull data from and activates the embed feature
@bot.command()
async def serverstatus(ctx, serverID, port_id=None):
    guild_id = ctx.guild.id
   
    if not port_id:
        cur.execute("UPDATE guilds SET portId = NULL WHERE guildId = ?", (guild_id,))
        pass
    else:
        cur.execute(f"UPDATE guilds SET portId = ? WHERE guildId = ?", (port_id, guild_id))
        print(port_id)

    
    cur.execute("SELECT channelId FROM guilds WHERE guildId = ?", (guild_id,))
    result = cur.fetchone()  # Fetch the first result
    result = int(result[0])
    channel = ctx.guild.get_channel(result)
    await channel.send(f"Now monitoring server **`{serverID}`**")

    cur.execute(f"UPDATE guilds SET mcserverId = ? WHERE guildId = ?", (serverID, guild_id))
    con.commit()

    message = await initialize_embed(serverID,channel,guild_id,port_id)

#RUNS THE BOT CONTINUOSLY
bot.run(BOT_TOKEN)