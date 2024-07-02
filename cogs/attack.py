import discord
from discord.ext import commands
from discord import app_commands
import logging

class Attack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="perco-attack", description="Send an SOS message for Perco attack")
    async def perco_attack(self, interaction: discord.Interaction):
        try:
            message = (
                "@everyone SOS Spartans! Our Percos are under attack. "
                "It's mandatory for everyone to log in to the game and help protect our Percos. "
                "We can't let them take down what is ours."
            )
            await interaction.response.send_message(message)
        except Exception as e:
            logging.exception(f"Error in perco-attack command: {e}")
            await interaction.response.send_message("An error occurred while sending the message.")

    @app_commands.command(name="prism-attack", description="Send an SOS message for Prism attack")
    async def prism_attack(self, interaction: discord.Interaction):
        try:
            message = (
                "@everyone SOS Spartans! Our prisms are under attack. "
                "It's mandatory for everyone to log in to the game and help protect our prisms. "
                "We can't let them take down what is ours. Team number one, wake up!"
            )
            await interaction.response.send_message(message)
        except Exception as e:
            logging.exception(f"Error in prism-attack command: {e}")
            await interaction.response.send_message("An error occurred while sending the message.")

async def setup(bot):
    cog = Attack(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('perco-attack'):
        bot.tree.add_command(cog.perco_attack)
    if not bot.tree.get_command('prism-attack'):
        bot.tree.add_command(cog.prism_attack)
