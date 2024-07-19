import discord
from discord.ext import commands
from discord import app_commands
import pandas as pd

class Profession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = '/Professions.xlsx'
        self.professions = pd.ExcelFile(self.file_path).sheet_names

    @app_commands.command(name="profession", description="Get players by profession")
    async def profession(self, interaction: discord.Interaction):
        profession_options = [
            discord.SelectOption(label=profession, value=profession) for profession in self.professions
        ]
        view = ProfessionView(profession_options, self.file_path)
        await interaction.response.send_message("Select a profession:", view=view, ephemeral=True)

class ProfessionView(discord.ui.View):
    def __init__(self, profession_options, file_path):
        super().__init__()
        self.file_path = file_path
        self.add_item(ProfessionSelect(profession_options, file_path))

class ProfessionSelect(discord.ui.Select):
    def __init__(self, profession_options, file_path):
        super().__init__(placeholder="Choose a profession", min_values=1, max_values=1, options=profession_options)
        self.file_path = file_path

    async def callback(self, interaction: discord.Interaction):
        selected_profession = self.values[0]
        df = pd.read_excel(self.file_path, sheet_name=selected_profession)
        player_info = df.to_string(index=False)
        await interaction.response.send_message(f"Players with profession {selected_profession}:\n```{player_info}```", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Profession(bot))
