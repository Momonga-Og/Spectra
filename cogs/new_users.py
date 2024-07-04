import discord
from discord.ext import commands
import logging

GUILD_1_ID = 1218809218342326313
GUILD_1_ROLE = 'hero'
GUILD_1_CHANNEL = 'greeting'

GUILD_2_ID = 1258016370314969148
GUILD_2_ROLE = 'member'
GUILD_2_CHANNEL = 'greeting'

GUILD_NAMES = {
    GUILD_1_ID: "Server 1",
    GUILD_2_ID: "Server 2"
}

class NewUsers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id

        if guild_id in GUILD_NAMES:
            server_name = GUILD_NAMES[guild_id]
            try:
                # Send a welcome message to the new user
                await member.send(
                    f"Hello and welcome to {server_name}! Please reply to me with your in-game name so I can update your server name and assign your permissions."
                )
            except discord.Forbidden:
                logging.error(f"Cannot send a DM to {member}. They may have DMs disabled.")
                # Notify the greeting channel in the respective server
                channel = discord.utils.get(member.guild.text_channels, name=GUILD_1_CHANNEL if guild_id == GUILD_1_ID else GUILD_2_CHANNEL)
                if channel:
                    await channel.send(
                        f"Welcome {member.mention}! Please enable DMs so the bot can set your in-game name and permissions. Alternatively, reply here with your in-game name."
                    )

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            member = message.author
            in_game_name = message.content.strip()

            for guild_id in [GUILD_1_ID, GUILD_2_ID]:
                guild = self.bot.get_guild(guild_id)
                guild_member = guild.get_member(member.id) if guild else None

                if guild_member:
                    role_name = GUILD_1_ROLE if guild_id == GUILD_1_ID else GUILD_2_ROLE
                    role = discord.utils.get(guild.roles, name=role_name)

                    try:
                        # Update the user's nickname in the server
                        await guild_member.edit(nick=in_game_name)
                        
                        # Assign the appropriate role to the user
                        if role:
                            await guild_member.add_roles(role)

                        await member.send(f"Your in-game name has been updated to '{in_game_name}' and you have been assigned the '{role_name}' role in {GUILD_NAMES[guild_id]}.")
                    except Exception as e:
                        logging.exception(f"Error updating nickname and assigning role: {e}")
                        await member.send("There was an error updating your nickname or assigning your role. Please contact an admin.")
                    break

async def setup(bot):
    cog = NewUsers(bot)
    await bot.add_cog(cog)
