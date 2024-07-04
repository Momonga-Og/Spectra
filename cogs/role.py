import discord
from discord.ext import commands
from discord import app_commands

# Define guild roles
GUILD_ROLE_OPTIONS = [
    {'name': 'ENCE', 'role_name': 'ENCE'},
    {'name': 'Olympus', 'role_name': 'Olympus'},
    {'name': 'RzeczpospolitaPolska', 'role_name': 'RzeczpospolitaPolska'},
    {'name': 'The Delian League', 'role_name': 'The Delian League'},
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
            if not role:
                # Create the role if it does not exist
                role = await interaction.guild.create_role(name=selected_role_name)
            await select_interaction.user.add_roles(role)
            await select_interaction.response.send_message(f"You have been assigned the role: {role.name}", ephemeral=True)

        select_menu.callback = select_callback

        view = discord.ui.View()
        view.add_item(select_menu)

        await interaction.response.send_message("Select your guild from the dropdown below:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleUp(bot))
