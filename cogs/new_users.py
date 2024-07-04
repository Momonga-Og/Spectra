import discord
from discord.ext import commands
import logging

GUILD_1_ID = 1218809218342326313
GUILD_1_ROLE = 'hero'
GUILD_1_CHANNEL = 'greeting'
GUILD_1_NAME = "Server 1"

GUILD_2_ID = 1258016370314969148
GUILD_2_ROLE = 'member'
GUILD_2_CHANNEL = 'greeting'
GUILD_2_NAME = "Server 2"

class NewUsersServer1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == GUILD_1_ID:
            try:
                # Send a welcome message to the new user
                await member.send(
                    f"Hello and welcome to {GUILD_1_NAME}! Please reply to me with your in-game name so I can update your server name and assign your permissions."
                )
            except discord.Forbidden:
                logging.error(f"Cannot send a DM to {member}. They may have DMs disabled.")
                # Notify the greeting channel in the respective server
                channel = discord.utils.get(member.guild.text_channels, name=GUILD_1_CHANNEL)
                if channel:
                    await channel.send(
                        f"Welcome {member.mention}! Please enable DMs so the bot can set your in-game name and permissions. Alternatively, reply here with your in-game name."
                    )

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            member = message.author
            in_game_name = message.content.strip()
            
            guild = self.bot.get_guild(GUILD_1_ID)
            guild_member = guild.get_member(member.id) if guild else None

            if guild_member:
                role = discord.utils.get(guild.roles, name=GUILD_1_ROLE)
                try:
                    # Update the user's nickname in the server
                    await guild_member.edit(nick=in_game_name)
                    
                    # Assign the appropriate role to the user
                    if role:
                        await guild_member.add_roles(role)

                    await member.send(f"Your in-game name has been updated to '{in_game_name}' and you have been assigned the '{GUILD_1_ROLE}' role in {GUILD_1_NAME}.")
                except Exception as e:
                    logging.exception(f"Error updating nickname and assigning role: {e}")
                    await member.send("There was an error updating your nickname or assigning your role. Please contact an admin.")

class NewUsersServer2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == GUILD_2_ID:
            try:
                # Send a welcome message to the new user
                await member.send(
                    f"Hello and welcome to {GUILD_2_NAME}! Please reply to me with your in-game name so I can update your server name and assign your permissions."
                )
            except discord.Forbidden:
                logging.error(f"Cannot send a DM to {member}. They may have DMs disabled.")
                # Notify the greeting channel in the respective server
                channel = discord.utils.get(member.guild.text_channels, name=GUILD_2_CHANNEL)
                if channel:
                    await channel.send(
                        f"Welcome {member.mention}! Please enable DMs so the bot can set your in-game name and permissions. Alternatively, reply here with your in-game name."
                    )

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            member = message.author
            in_game_name = message.content.strip()
            
            guild = self.bot.get_guild(GUILD_2_ID)
            guild_member = guild.get_member(member.id) if guild else None

            if guild_member:
                role = discord.utils.get(guild.roles, name=GUILD_2_ROLE)
                try:
                    # Update the user's nickname in the server
                    await guild_member.edit(nick=in_game_name)
                    
                    # Assign the appropriate role to the user
                    if role:
                        await guild_member.add_roles(role)

                    await member.send(f"Your in-game name has been updated to '{in_game_name}' and you have been assigned the '{GUILD_2_ROLE}' role in {GUILD_2_NAME}.")
                except Exception as e:
                    logging.exception(f"Error updating nickname and assigning role: {e}")
                    await member.send("There was an error updating your nickname or assigning your role. Please contact an admin.")

async def setup(bot):
    await bot.add_cog(NewUsersServer1(bot))
    await bot.add_cog(NewUsersServer2(bot))
