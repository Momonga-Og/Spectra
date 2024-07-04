import discord
from discord.ext import commands
import logging

GUILD_IDS = [1218809218342326313, 1258016370314969148]  # Add your server IDs here

class NewUsers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id in GUILD_IDS:
            try:
                # Send a welcome message to the new user
                await member.send(
                    "Hello and welcome to the server! Please reply to me with your in-game name so I can update your server name and assign your permissions."
                )
            except discord.Forbidden:
                logging.error(f"Cannot send a DM to {member}. They may have DMs disabled.")
                # Notify the greeting channel in the respective server
                channel = discord.utils.get(member.guild.text_channels, name='greeting')
                if channel:
                    await channel.send(
                        f"Welcome {member.mention}! Please enable DMs so the bot can set your in-game name and permissions. Alternatively, reply here with your in-game name."
                    )

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            member = message.author
            in_game_name = message.content.strip()
            guild = None

            for guild_id in GUILD_IDS:
                guild = self.bot.get_guild(guild_id)
                if guild and guild.get_member(member.id):
                    break

            if guild:
                hero_role = discord.utils.get(guild.roles, name="hero")
                member_role = discord.utils.get(guild.roles, name="member")
                target_role = hero_role or member_role

                try:
                    # Update the user's nickname in the server
                    await guild.get_member(member.id).edit(nick=in_game_name)

                    # Assign the appropriate role to the user
                    if target_role:
                        await guild.get_member(member.id).add_roles(target_role)

                    await member.send(f"Your in-game name has been updated to '{in_game_name}' and you have been assigned the '{target_role.name}' role.")
                except Exception as e:
                    logging.exception(f"Error updating nickname and assigning role: {e}")
                    await member.send("There was an error updating your nickname or assigning your role. Please contact an admin.")

async def setup(bot):
    cog = NewUsers(bot)
    await bot.add_cog(cog)
