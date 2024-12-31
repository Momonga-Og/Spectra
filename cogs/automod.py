import discord
from discord.ext import commands
from discord import app_commands

# Define intents and bot prefix
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Apply AutoMod rules function
    async def apply_automod_rules(self, guild: discord.Guild, rules: list):
        """
        Apply multiple AutoMod rules to a server.

        Parameters:
        - guild: discord.Guild - The server where the rules will be applied.
        - rules: list - A list of rules to apply.
        """
        for rule in rules:
            try:
                await guild.create_automod_rule(
                    name=rule["name"],
                    trigger_type=rule["trigger_type"],
                    actions=rule["actions"],
                    trigger_metadata=rule.get("trigger_metadata", {})
                )
                print(f"AutoMod rule '{rule['name']}' applied to {guild.name}.")
            except Exception as e:
                print(f"Failed to apply rule '{rule['name']}': {e}")

    # Command to activate AutoMod rules
    @app_commands.command(name='automod', description='Activate AutoMod rules in this server')
    async def automod(self, interaction: discord.Interaction):
        """
        Command to activate AutoMod rules in the server.
        """
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        # Define default rules
        rules = [
            {"name": "Block Profanity", "trigger_type": 4, "actions": [{"type": 1}], "trigger_metadata": {"keyword_filter": ["badword1", "badword2", "slur1", "slur2"]}},
            {"name": "Block Spam Mentions", "trigger_type": 1, "actions": [{"type": 1}]},
            {"name": "Block Links", "trigger_type": 4, "actions": [{"type": 1}], "trigger_metadata": {"keyword_filter": ["http", "www", ".com", ".net"]}},
            {"name": "Limit Caps Usage", "trigger_type": 4, "actions": [{"type": 1}], "trigger_metadata": {"keyword_filter": ["ALLCAPS"]}},
            {"name": "Prevent Repeated Words", "trigger_type": 4, "actions": [{"type": 1}], "trigger_metadata": {"keyword_filter": ["spamword"]}},
            {"name": "Alert Admins for Violations", "trigger_type": 1, "actions": [{"type": 2, "metadata": {"channel_id": interaction.channel.id, "custom_message": "Violation detected."}}]},
            {"name": "Block Offensive Keywords", "trigger_type": 4, "actions": [{"type": 1}], "trigger_metadata": {"keyword_filter": ["offensive1", "offensive2"]}},
            {"name": "Prevent Self-Promotion", "trigger_type": 4, "actions": [{"type": 1}], "trigger_metadata": {"keyword_filter": ["subscribe", "follow"]}},
            {"name": "Block Sensitive Topics", "trigger_type": 4, "actions": [{"type": 1}], "trigger_metadata": {"keyword_filter": ["politics", "religion"]}}
        ]

        await self.apply_automod_rules(interaction.guild, rules)
        await interaction.response.send_message("AutoMod rules have been activated in this server.")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog AutoMod is ready!")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
