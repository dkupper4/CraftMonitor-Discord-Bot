# CraftMonitor
CraftMonitor is a Discord bot that monitors and displays real-time Minecraft server statuses, including server online/offline status, player count, and latency. Built with Python, SQLite, and the discord.py library, it is ideal for communities that want live updates about their favorite Minecraft servers.

Features:
* Real-Time Updates: Fetches and updates server status every 10 seconds.
* Customizable Channels: Set the channel where updates are sent per server.
* Embedded Messages: Displays server data in sleek Discord embeds.
* Persistent Configuration: Uses SQLite to store guild-specific settings like channels and server details.
* Flexible Command System: Manage server monitoring easily using commands:
  * setchannel: Change the default channel for server status updates.
  * serverstatus <serverID> <port?>: Start tracking a server with optional port configuration.
  
Technologies:
* Python
* SQLite
* discord.py
* minestat

This application was developed for use in discord servers to see the status of servers without asking the owner.
