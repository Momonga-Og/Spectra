import discord
from discord.ext import commands
from discord import app_commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Create a poll")
    async def poll(self, interaction: discord.Interaction, question: str, *options: str):
        embed = discord.Embed(title="Poll", description=question, color=0x00ff00)
        for i, option in enumerate(options, 1):
            embed.add_field(name=f'Option {i}', value=option, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pm", description="Send a private message")
    async def pm(self, interaction: discord.Interaction, member: discord.Member, message: str):
        await member.send(message)
        await interaction.response.send_message(f'PM sent to {member.display_name}.')

async def setup(bot):
    cog = Poll(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.poll)
    bot.tree.add_command(cog.pm)
