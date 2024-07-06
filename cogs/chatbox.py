import discord
from discord.ext import commands
from discord import app_commands

class ChatBox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="chatbox", description="Start an interactive chat box")
    async def chatbox(self, interaction: discord.Interaction):
        await interaction.response.send_message("Welcome to the interactive chat box! How can I help you today?", view=ChatBoxView())

class ChatBoxView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Ask a Question", style=discord.ButtonStyle.primary)
    async def ask_question(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Please type your question:", ephemeral=True)
        self.stop()  # Stop the current view to proceed with the next step

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        msg = await self.bot.wait_for('message', check=check)
        await interaction.followup.send(f"You asked: {msg.content}", view=ChatBoxOptionsView())

class ChatBoxOptionsView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.select(placeholder="Select an option", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Option 1", description="Description for option 1"),
        discord.SelectOption(label="Option 2", description="Description for option 2"),
        discord.SelectOption(label="Option 3", description="Description for option 3"),
    ])
    async def select_option(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_message(f"You selected: {select.values[0]}")

async def setup(bot):
    await bot.add_cog(ChatBox(bot))
