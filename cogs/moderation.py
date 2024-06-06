import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mute", description="Mute a member")
    async def mute(self, interaction: discord.Interaction, member: discord.Member):
        await member.edit(mute=True)
        await interaction.response.send_message(f'{member.display_name} has been muted.')

    @app_commands.command(name="deafen", description="Deafen a member")
    async def deafen(self, interaction: discord.Interaction, member: discord.Member):
        await member.edit(deafen=True)
        await interaction.response.send_message(f'{member.display_name} has been deafened.')

    @app_commands.command(name="kick", description="Kick a member")
    async def kick(self, interaction: discord.Interaction, member: discord.Member):
        await member.kick()
        await interaction.response.send_message(f'{member.display_name} has been kicked.')

    @app_commands.command(name="ban", description="Ban a member")
    async def ban(self, interaction: discord.Interaction, member: discord.Member):
        await member.ban()
        await interaction.response.send_message(f'{member.display_name} has been banned.')

async def setup(bot):
    cog = Moderation(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('mute'):
        bot.tree.add_command(cog.mute)
    if not bot.tree.get_command('deafen'):
        bot.tree.add_command(cog.deafen)
    if not bot.tree.get_command('kick'):
        bot.tree.add_command(cog.kick)
    if not bot.tree.get_command('ban'):
        bot.tree.add_command(cog.ban)
