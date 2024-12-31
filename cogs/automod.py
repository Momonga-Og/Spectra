import discord
from discord import app_commands
from discord.ext import commands

# Define intents and bot prefix
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Apply AutoMod rules function
    async def apply_automod_rules(self, guild: discord.Guild, rule_name: str, trigger_type: str, actions: list, **kwargs):
        """
        Apply AutoMod rules to a server.

        Parameters:
        - guild: discord.Guild - The server where the rule will be applied.
        - rule_name: str - The name of the AutoMod rule.
        - trigger_type: str - The type of trigger (e.g., 'keyword', 'mention_spam').
        - actions: list - Actions to take when the rule is triggered.
        - kwargs: Additional parameters for rule customization.
        """
        try:
            automod_rule = await guild.create_automod_rule(
                name=rule_name,
                trigger_type=trigger_type,
                actions=actions,
                **kwargs
            )
            return f"AutoMod rule '{rule_name}' created successfully."
        except Exception as e:
            return f"Failed to create AutoMod rule: {e}"

    # Command to manage AutoMod rules
    @app_commands.command(name='automod', description='Manage AutoMod rules')
    async def automod(self, interaction: discord.Interaction, rule_name: str, trigger_type: str, action_type: str):
        """
        Command to apply AutoMod rules.

        Parameters:
        - rule_name: str - Name of the rule to be created.
        - trigger_type: str - Trigger type for the rule (e.g., keyword, mention_spam).
        - action_type: str - Action type (e.g., block_message, send_alert).
        """
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        # Define actions based on input
        actions = [
            {
                "type": action_type
            }
        ]

        result = await self.apply_automod_rules(interaction.guild, rule_name, trigger_type, actions)
        await interaction.response.send_message(result)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog AutoMod is ready!")
        for guild in self.bot.guilds:
            rules = [
                {"name": "Block Spam Mentions", "trigger_type": "mention_spam", "actions": [{"type": "block_message"}]},
                {"name": "Block Profanity", "trigger_type": "keyword", "actions": [{"type": "block_message"}], "trigger_metadata": {"keyword_filter": ["badword1", "badword2"]}},
                {"name": "Limit Caps", "trigger_type": "keyword", "actions": [{"type": "block_message"}], "trigger_metadata": {"keyword_filter": ["ALLCAPS"]}},
                {"name": "Block Links", "trigger_type": "keyword", "actions": [{"type": "block_message"}], "trigger_metadata": {"keyword_filter": ["http", "www"]}},
                {"name": "Spam Prevention", "trigger_type": "mention_spam", "actions": [{"type": "send_alert"}]},
                {"name": "Alert for Profanity", "trigger_type": "keyword", "actions": [{"type": "send_alert"}], "trigger_metadata": {"keyword_filter": ["curse1", "curse2"]}},
                {"name": "Block Sensitive Words", "trigger_type": "keyword", "actions": [{"type": "block_message"}], "trigger_metadata": {"keyword_filter": ["sensitive1", "sensitive2"]}},
                {"name": "Prevent Duplicate Messages", "trigger_type": "keyword", "actions": [{"type": "block_message"}], "trigger_metadata": {"keyword_filter": ["repeated"]}},
                {"name": "Notify Admin for Violations", "trigger_type": "mention_spam", "actions": [{"type": "send_alert"}]}
            ]

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

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
