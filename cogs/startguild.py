import discord
from discord.ext import commands
from discord.ui import View, Button

# Configuration
GUILD_ID = 1300093554064097400  # Replace with your guild ID
PING_DEF_CHANNEL_ID = 1307429490158342256  # Replace with your ping channel ID
ALERTE_DEF_CHANNEL_ID = 1300093554399645715  # Replace with your alert channel ID

# Guild emojis with IDs
GUILD_EMOJIS = {
    "Darkness": "<:Darkness:1307418763276324944>",
    "GTO": "<:GTO:1307418692992237668>",
    "Aversion": "<:aversion:1307418759002198086>",
    "Bonnebuche": "<:bonnebuche:1307418760763670651>",
    "LMDF": "<:lmdf:1307418765142786179>",
    "Notorious": "<:notorious:1307418766266728500>",
    "Percophile": "<:percophile:1307418769764651228>",
    "Tilisquad": "<:tilisquad:1307418771882905600>",
}


class GuildPingView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        for guild_name, emoji in GUILD_EMOJIS.items():
            button = Button(label=guild_name, emoji=emoji, style=discord.ButtonStyle.primary)
            button.callback = self.create_ping_callback(guild_name)
            self.add_item(button)

    def create_ping_callback(self, guild_name):
        async def callback(interaction: discord.Interaction):
            if interaction.guild_id != GUILD_ID:
                await interaction.response.send_message("This feature is not available in this server.", ephemeral=True)
                return

            alert_channel = interaction.guild.get_channel(ALERTE_DEF_CHANNEL_ID)
            if not alert_channel:
                await interaction.response.send_message("Alert channel not found!", ephemeral=True)
                return

            role = discord.utils.get(interaction.guild.roles, name=f"[{guild_name}]")
            if not role:
                await interaction.response.send_message(f"Role for {guild_name} not found!", ephemeral=True)
                return

            await alert_channel.send(f"{role.mention} Alerte! 🚨")
            await interaction.response.send_message(f"Alerte sent to {guild_name} in the alert channel!", ephemeral=True)

        return callback


class StartGuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def ensure_panel(self):
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

        async for message in channel.history(limit=50):
            if message.pinned:
                await message.edit(content=message_content, view=view)
                print("Panel updated.")
                return

        new_message = await channel.send(content=message_content, view=view)
        await new_message.pin()
        print("Panel created and pinned successfully.")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.ensure_panel()
        print("Bot is ready, and the panel is ensured.")


async def setup(bot: commands.Bot):
    await bot.add_cog(StartGuildCog(bot))
