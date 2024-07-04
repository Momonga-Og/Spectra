import discord
from discord.ext import commands
import logging

GUILD_ID = 1217700740949348443  # Replace with your server's guild ID

class NewUsers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            # Send a welcome message to the new user
            await member.send(
                "Hello and welcome to the server! Please reply to me with your in-game name so I can update your server name and assign your permissions."
            )
        except discord.Forbidden:
            logging.error(f"Cannot send a DM to {member}. They may have DMs disabled.")
            # You can also notify a specific channel in your server if you prefer
            channel = discord.utils.get(member.guild.text_channels, name='general')  # Replace 'general' with the desired channel
            if channel:
                await channel.send(
                    f"Welcome {member.mention}! Please enable DMs so the bot can set your in-game name and permissions. Alternatively, reply here with your in-game name."
                )

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            member = message.author
            in_game_name = message.content.strip()
            guild = self.bot.get_guild(GUILD_ID)
            ally_role = discord.utils.get(guild.roles, name="ally")  # Replace with the exact role name

            try:
                # Update the user's nickname in the server
                await guild.get_member(member.id).edit(nick=in_game_name)

                # Assign the "ally" role to the user
                if ally_role:
                    await guild.get_member(member.id).add_roles(ally_role)

                await member.send(f"Your in-game name has been updated to '{in_game_name}' and you have been assigned the 'ally' role.")
            except Exception as e:
                logging.exception(f"Error updating nickname and assigning role: {e}")
                await member.send("There was an error updating your nickname or assigning your role. Please contact an admin.")

async def setup(bot):
    cog = NewUsers(bot)
    await bot.add_cog(cog)
