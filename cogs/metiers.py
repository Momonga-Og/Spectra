import discord
from discord.ext import commands
from discord import app_commands
import pandas as pd

class Metiers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = './metiers.xlsx'  # Ensure this matches the uploaded file name and location
        self.professions = pd.ExcelFile(self.file_path).sheet_names

    @app_commands.command(name="metiers", description="Afficher les professions disponibles")
    async def metiers(self, interaction: discord.Interaction):
        # Restrict command to specific server and channel
        if interaction.guild.id != 1300093554064097400 or interaction.channel.id != 1300093555217268800:
            await interaction.response.send_message(
                "Cette commande n'est disponible que dans le canal **#║╟➢👷metiers**.",
                ephemeral=True
            )
            return

        # Create dropdown options from Excel sheet names
        profession_options = [
            discord.SelectOption(label=profession, value=profession) for profession in self.professions
        ]
        view = MetiersView(profession_options, self.file_path)
        await interaction.response.send_message("Choisissez une profession :", view=view)

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
            # Load data from the selected sheet
            df = pd.read_excel(self.file_path, sheet_name=selected_profession)
            # Convert data to a presentable format
            formatted_data = "\n".join(
                f"**Nom**: {row['Nom']} | **Serveur**: {row['Serveur']} | **Niveau métier**: {row['Niveau métier']} | **Classe**: {row['Classe']}"
                for _, row in df.iterrows()
            )

            embed = discord.Embed(
                title=f"Joueurs avec la profession {selected_profession}",
                description=formatted_data,
                color=discord.Color.blue()
            )
            embed.set_footer(
                text="Astuce : Si un joueur n'est pas en ligne, ajoutez-le comme ami et vérifiez son statut en ligne."
            )
            
            # Send the result publicly in the channel
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(
                f"Erreur lors du chargement des données pour {selected_profession}: {e}"
            )

async def setup(bot):
    await bot.add_cog(Metiers(bot))
