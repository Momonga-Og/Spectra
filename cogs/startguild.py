import discord
from discord.ext import commands
from discord.ui import Button, View

# Configuration
GUILD_ID = 1300093554064097400  # Replace with your guild ID
PING_DEF_CHANNEL_ID = 1307429490158342256  # Replace with your ping channel ID
ALERTE_DEF_CHANNEL_ID = 1300093554399645715  # Replace with your alert channel ID

# Guild emojis with their IDs
GUILD_EMOJIS = {
    "Darkness": "<:Darkness:1307418763276324944>",
    "GTO": "<:GTO:1307418692992237668>",
    "Aversion": "<:aversion:1307418759002198086>",
    "Bonnebuche": "<:bonnebuche:1307418760763670651>",
    "LMDF": "<:lmdf:1307418765142786179>",
    "Notorious": "<:notorious:1307418766266728500>",
    "Percophile": "<:percophile:1307418769764651228>",
    "Tilisquad": "<:tilisquad:1307418771882905600>"
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

            # Get the alert channel
            alert_channel = interaction.guild.get_channel(ALERTE_DEF_CHANNEL_ID)
            if not alert_channel:
                await interaction.response.send_message("Alert channel not found!", ephemeral=True)
                return

            # Get the role corresponding to the guild
            role = discord.utils.get(interaction.guild.roles, name=f"[{guild_name}]")
            if not role:
                await interaction.response.send_message(f"Role for {guild_name} not found!", ephemeral=True)
                return

            # Send an alert in the alert channel tagging the role
            await alert_channel.send(f"{role.mention} Alerte! 🚨")

            # Acknowledge the interaction
            await interaction.response.send_message(f"Alerte sent to {guild_name} in the alert channel!", ephemeral=True)

        return callback


class GuildAlertCog(commands.Cog):
    """
    Cog for managing the guild alert panel.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def ensure_panel(self):
        """
        Ensures the panel is created and pinned in the ping definition channel.
        """
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("Guild not found. Check the GUILD_ID.")
            return

        channel = guild.get_channel(PING_DEF_CHANNEL_ID)
        if not channel:
            print("Ping definition channel not found. Check the PING_DEF_CHANNEL_ID.")
            return

        view = GuildPingView(self.bot)
        message_content = "Cliquez sur le logo de votre guilde pour envoyer une alerte DEF !"

        # Check for existing pinned messages and update or create
        async for message in channel.history(limit=50):
            if message.pinned:
                await message.edit(content=message_content, view=view)
                print("Panel updated.")
                return

        # If no pinned message exists, create a new one
        new_message = await channel.send(content=message_content, view=view)
        await new_message.pin()
        print("Panel created and pinned successfully.")

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Listener that ensures the panel is available when the bot is online.
        """
        await self.ensure_panel()
        print("Bot is ready, and the panel is ensured.")


async def setup(bot: commands.Bot):
    """
    Setup function to load the cog.
    """
    await bot.add_cog(GuildAlertCog(bot))


# Main bot entry
class MyBot(commands.Bot):
    """
    Custom bot class with a setup hook for automatic panel creation.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def setup_hook(self):
        """
        Hook to ensure the panel is created during bot initialization.
        """
        await self.add_cog(GuildAlertCog(self))


# Bot Initialization
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = MyBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# Run the bot
TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token
bot.run(TOKEN)
