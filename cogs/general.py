import discord
from discord.ext import commands
from discord import app_commands
import random
import logging

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f'Logged in as {self.bot.user}')
        try:
            synced = await self.bot.tree.sync()
            logging.info(f"Synced {len(synced)} commands")
        except Exception as e:
            logging.exception("Failed to sync commands")

    @commands.Cog.listener()
    async def on_unload(self):
        logging.info("Unloading General cog")

    @app_commands.command(name="pick", description="Pick a random item from two choices")
    async def pick(self, interaction: discord.Interaction, choice1: str, choice2: str):
        try:
            choice = random.choice([choice1, choice2])
            await interaction.response.send_message(f'You should pick: {choice}')
        except Exception as e:
            logging.exception("Error in pick command")
            await interaction.response.send_message("An error occurred while processing your command.")

    # ... other commands ...

async def setup(bot):
    cog = General(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('pick'):
        bot.tree.add_command(cog.pick)
    # ... other command checks ...
