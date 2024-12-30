import discord
from discord.ext import commands
from discord import app_commands
import logging

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Create a poll")
    async def poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str):
        try:
            embed = discord.Embed(title="Poll", description=question, color=0x00ff00)
            embed.add_field(name="Option 1", value=option1, inline=False)
            embed.add_field(name="Option 2", value=option2, inline=False)
            
            # Acknowledge the interaction first
            await interaction.response.defer()
            
            # Send the poll message using followup
            message = await interaction.followup.send(embed=embed)
            
            # Add reactions to the message
            await message.add_reaction("1️⃣")
            await message.add_reaction("2️⃣")
        except Exception as e:
            logging.exception("Error in poll command")
            await interaction.followup.send("An error occurred while processing your command.", ephemeral=True)

    @app_commands.command(name="pm", description="Send a private message")
    async def pm(self, interaction: discord.Interaction, member: discord.Member, message: str):
        try:
            # Check if the bot can send a DM to the member
            if member.dm_channel is None:
                await member.create_dm()
            
            await member.send(message)
            await interaction.response.send_message(f'PM sent to {member.display_name}.', ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                f"Unable to send a DM to {member.display_name}. They may have DMs disabled or blocked the bot.",
                ephemeral=True
            )
        except Exception as e:
            logging.exception("Error in pm command")
            await interaction.response.send_message("An error occurred while processing your command.", ephemeral=True)

async def setup(bot):
    cog = Poll(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('poll'):
        bot.tree.add_command(cog.poll)
    if not bot.tree.get_command('pm'):
        bot.tree.add_command(cog.pm)
