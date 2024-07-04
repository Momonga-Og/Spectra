import discord
from discord.ext import commands
from discord import app_commands

# Define guild roles
GUILD_ROLE_OPTIONS = [
    {'name': 'Guild 1', 'role_name': 'guild_1_tag'},
    {'name': 'Guild 2', 'role_name': 'guild_2_tag'},
    {'name': 'Guild 3', 'role_name': 'guild_3_tag'},
    {'name': 'Guild 4', 'role_name': 'guild_4_tag'},
    {'name': 'Guild 5', 'role_name': 'guild_5_tag'},
    {'name': 'Guild 6', 'role_name': 'guild_6_tag'},
]

class RoleUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="role-up", description="Assign a guild role to a user.")
    async def role_up(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        # Create select menu options
        options = [
            discord.SelectOption(label=option['name'], value=option['role_name'])
            for option in GUILD_ROLE_OPTIONS
        ]

        select_menu = discord.ui.Select(placeholder="Choose your guild", options=options)

        async def select_callback(select_interaction: discord.Interaction):
            selected_role_name = select_interaction.data['values'][0]
            role = discord.utils.get(interaction.guild.roles, name=selected_role_name)
            if role:
                await select_interaction.user.add_roles(role)
                await select_interaction.response.send_message(f"You have been assigned the role: {role.name}", ephemeral=True)
            else:
                await select_interaction.response.send_message("Role not found. Please contact an admin.", ephemeral=True)

        select_menu.callback = select_callback

        view = discord.ui.View()
        view.add_item(select_menu)

        await interaction.response.send_message("Select your guild from the dropdown below:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleUp(bot))
