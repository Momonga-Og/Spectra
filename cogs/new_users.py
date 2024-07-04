import discord
from discord.ext import commands
import logging

GUILD_IDS = {
    1218809218342326313: {'roles': ['hero', 'member'], 'channel': 'greeting'},
    1258016370314969148: {'roles': ['hero', 'member'], 'channel': 'greeting'}
}

class NewUsers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_config = GUILD_IDS.get(member.guild.id)
        if guild_config:
            try:
                # Send a welcome message to the new user with the server name
                await member.send(
                    f"Hello and welcome to {member.guild.name}! Please reply to me with your in-game name so I can update your server name and assign your permissions."
                )
            except discord.Forbidden:
                logging.error(f"Cannot send a DM to {member}. They may have DMs disabled.")
                # Notify the greeting channel in the respective server
                channel = discord.utils.get(member.guild.text_channels, name=guild_config['channel'])
                if channel:
                    await channel.send(
                        f"Welcome {member.mention}! Please enable DMs so the bot can set your in-game name and permissions. Alternatively, reply here with your in-game name."
                    )

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            member = message.author
            in_game_name = message.content.strip()
            current_guild = None
            other_guild = None

            for guild_id in GUILD_IDS.keys():
                guild = self.bot.get_guild(guild_id)
                if guild and guild.get_member(member.id):
                    current_guild = guild
                else:
                    other_guild = self.bot.get_guild(guild_id)

            if current_guild and other_guild:
                # Find the role in the other guild
                config = GUILD_IDS[other_guild.id]
                target_role = None
                for role_name in config['roles']:
                    role = discord.utils.get(other_guild.roles, name=role_name)
                    if role:
                        target_role = role
                        break

                try:
                    # Update the user's nickname in the other server
                    await other_guild.get_member(member.id).edit(nick=in_game_name)

                    # Assign the appropriate role to the user in the other server
                    if target_role:
                        await other_guild.get_member(member.id).add_roles(target_role)

                    await member.send(f"Your in-game name has been updated to '{in_game_name}' and you have been assigned the '{target_role.name}' role in {other_guild.name}.")
                except Exception as e:
                    logging.exception(f"Error updating nickname and assigning role: {e}")
                    await member.send("There was an error updating your nickname or assigning your role. Please contact an admin.")

async def setup(bot):
    cog = NewUsers(bot)
    await bot.add_cog(cog)
