import discord
from discord.ext import commands
from discord import app_commands

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverstats", description="Displays statistics about the server")
    async def serverstats(self, interaction: discord.Interaction):
        guild = interaction.guild
        num_channels = len(guild.channels)
        num_roles = len(guild.roles)
        num_members = guild.member_count

        embed = discord.Embed(title="Server Statistics", color=discord.Color.blue())
        embed.add_field(name="Total Channels", value=num_channels, inline=False)
        embed.add_field(name="Total Roles", value=num_roles, inline=False)
        embed.add_field(name="Total Members", value=num_members, inline=False)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    cog = ServerStats(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('serverstats'):
        bot.tree.add_command(cog.serverstats)
