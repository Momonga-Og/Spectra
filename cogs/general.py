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

    @app_commands.command(name="pick_s", description="Pick a random item from a comma-separated list")
    async def pick_s(self, interaction: discord.Interaction, choices: str):
        try:
            choice_list = choices.split(',')
            choice = random.choice(choice_list)
            await interaction.response.send_message(f'You should pick: {choice.strip()}')
        except Exception as e:
            logging.exception("Error in pick_s command")
            await interaction.response.send_message("An error occurred while processing your command.")

    @app_commands.command(name="cname", description="Change a member's nickname")
    async def cname(self, interaction: discord.Interaction, member: discord.Member, nickname: str):
        try:
            await member.edit(nick=nickname)
            await interaction.response.send_message(f'Nickname was changed to: {nickname}')
        except Exception as e:
            logging.exception("Error in cname command")
            await interaction.response.send_message("An error occurred while processing your command.")

    @app_commands.command(name="mhelp", description="Send help message")
    async def mhelp(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message('Help message')
        except Exception as e:
            logging.exception("Error in mhelp command")
            await interaction.response.send_message("An error occurred while processing your command.")

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        try:
            responses = [
                "It is certain.",
                "It is decidedly so.",
                "Without a doubt.",
                "Yes – definitely.",
                "You may rely on it.",
                "As I see it, yes.",
                "Most likely.",
                "Outlook good.",
                "Yes.",
                "Signs point to yes.",
                "Reply hazy, try again.",
                "Ask again later.",
                "Better not tell you now.",
                "Cannot predict now.",
                "Concentrate and ask again.",
                "Don't count on it.",
                "My reply is no.",
                "My sources say no.",
                "Outlook not so good.",
                "Very doubtful."
            ]
            response = random.choice(responses)
            await interaction.response.send_message(f"🎱 {response}")
        except Exception as e:
            logging.exception("Error in 8ball command")
            await interaction.response.send_message("An error occurred while processing your command.")

    @app_commands.command(name="trivia", description="Start a trivia game")
    async def trivia(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message('Starting trivia game...')
        except Exception as e:
            logging.exception("Error in trivia command")
            await interaction.response.send_message("An error occurred while processing your command.")

    @app_commands.command(name="color", description="Change the color")
    async def color(self, interaction: discord.Interaction, color: str):
        try:
            await interaction.response.send_message(f'Color changed to: {color}')
        except Exception as e:
            logging.exception("Error in color command")
            await interaction.response.send_message("An error occurred while processing your command.")

async def setup(bot):
    cog = General(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('pick'):
        bot.tree.add_command(cog.pick)
    if not bot.tree.get_command('pick_s'):
        bot.tree.add_command(cog.pick_s)
    if not bot.tree.get_command('cname'):
        bot.tree.add_command(cog.cname)
    if not bot.tree.get_command('mhelp'):
        bot.tree.add_command(cog.mhelp)
    if not bot.tree.get_command('8ball'):
        bot.tree.add_command(cog.eight_ball)
    if not bot.tree.get_command('trivia'):
        bot.tree.add_command(cog.trivia)
    if not bot.tree.get_command('color'):
        bot.tree.add_command(cog.color)
