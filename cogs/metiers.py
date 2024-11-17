import discord
from discord.ext import commands
from discord import app_commands
import pandas as pd

class Metiers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = './metiers.xlsx'  # Ensure this file exists and is correctly located
        self.professions = pd.ExcelFile(self.file_path).sheet_names

    @app_commands.command(name="metiers", description="Afficher les professions disponibles")
    async def metiers(self, interaction: discord.Interaction):
        # Restrict command to specific server and channel
        if interaction.guild.id != 1300093554064097400 or interaction.channel.id != 1300093555217268800:
            await interaction.response.send_message(
                "Cette commande n'est disponible que dans un canal spécifique.",
                ephemeral=True
            )
            return

        # Create select options from Excel sheet names
        profession_options = [
            discord.SelectOption(label=profession, value=profession) for profession in self.professions
        ]
        view = MetiersView(profession_options, self.file_path)
        await interaction.response.send_message("Choisissez une profession :", view=view, ephemeral=True)

class MetiersView(discord.ui.View):
    def __init__(self, profession_options, file_path):
        super().__init__()
        self.add_item(MetiersSelect(profession_options, file_path))

class MetiersSelect(discord.ui.Select):
    def __init__(self, profession_options, file_path):
        super().__init__(placeholder="Sélectionnez une profession", min_values=1, max_values=1, options=profession_options)
        self.file_path = file_path

    async def callback(self, interaction: discord.Interaction):
        selected_profession = self.values[0]
        try:
            # Load data for the selected sheet
            df = pd.read_excel(self.file_path, sheet_name=selected_profession)
            player_info = df.to_string(index=False)
            await interaction.response.send_message(
                f"Joueurs avec la profession {selected_profession}:\n```{player_info}```",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Erreur lors du chargement des données pour {selected_profession}: {e}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Metiers(bot))
