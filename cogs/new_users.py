import discord
from discord.ext import commands
import logging

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
        except Exception as e:
            logging.exception(f"Error sending welcome message: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            member = message.author
            in_game_name = message.content.strip()
            guild = self.bot.get_guild(YOUR_GUILD_ID)  # Replace with your server's guild ID
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
