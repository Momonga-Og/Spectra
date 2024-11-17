import discord
from discord.ext import commands
from discord.ui import Button, View

# Configuration
GUILD_ID = 1300093554064097400
PING_DEF_CHANNEL_ID = 1307429490158342256
ALERTE_DEF_CHANNEL_ID = 1300093554399645715

# Guild emojis with names (replace with actual emoji IDs)
GUILD_EMOJIS = {
    "Darkness": "<:Darkness:123456789012345678>",   # Replace with actual emoji ID
    "GTO": "<:GTO:123456789012345679>",            # Replace with actual emoji ID
    "Aversion": "<:aversion:123456789012345680>",  # Replace with actual emoji ID
    "Bonnebuche": "<:bonnebuche:123456789012345681>",
    "LMDF": "<:lmdf:123456789012345682>",
    "Notorious": "<:notorious:123456789012345683>",
    "Percophile": "<:percophile:123456789012345684>",
    "Tilisquad": "<:tilisquad:123456789012345685>"
}

class GuildPingView(View):
    """
    Creates a panel with buttons for each guild, styled with their emojis.
    """
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        for guild_name, emoji in GUILD_EMOJIS.items():
            button = Button(label=guild_name, emoji=emoji, style=discord.ButtonStyle.primary)
            button.callback = self.create_ping_callback(guild_name)
            self.add_item(button)

    def create_ping_callback(self, guild_name):
        """
        Generates a callback function to handle button clicks for each guild.
        """
        async def callback(interaction: discord.Interaction):
            # Ensure the interaction happens in the configured server
            if interaction.guild_id != GUILD_ID:
                await interaction.response.send_message("This feature is not available in this server.", ephemeral=True)
                return

            # Get the alert channel and send a message
            alert_channel = interaction.guild.get_channel(ALERTE_DEF_CHANNEL_ID)
            if alert_channel:
                await alert_channel.send(f"@{guild_name} Alerte! 🚨")
                await interaction.response.send_message(f"Ping sent to {guild_name} in the alert channel!", ephemeral=True)
            else:
                await interaction.response.send_message("Alert channel not found!", ephemeral=True)

        return callback


class GuildAlertCog(commands.Cog):
    """
    Cog for managing the guild alert panel.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="setup_panel", help="Set up the guild alert panel in the configured channel.")
    @commands.has_permissions(administrator=True)
    async def setup_panel(self, ctx):
        """
        Command to set up or update the panel in the designated channel.
        """
        if ctx.guild.id != GUILD_ID:
            await ctx.send("This command can only be used in the configured server.")
            return

        channel = ctx.guild.get_channel(PING_DEF_CHANNEL_ID)
        if not channel:
            await ctx.send("The configured PING DEF channel does not exist.")
            return

        view = GuildPingView(self.bot)
        message_content = "Cliquez sur le logo de votre guilde pour envoyer une alerte DEF !"

        # Check for existing pinned messages and update or create
        async for message in channel.history(limit=10):
            if message.pinned:
                await message.edit(content=message_content, view=view)
                await ctx.send("Panel updated.")
                return

        # If no pinned message exists, create a new one
        new_message = await channel.send(content=message_content, view=view)
        await new_message.pin()
        await ctx.send("Panel created and pinned successfully.")

async def setup(bot: commands.Bot):
    """
    Setup function to load the cog.
    """
    await bot.add_cog(GuildAlertCog(bot))
