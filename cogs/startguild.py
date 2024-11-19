import discord
from discord.ext import commands
from discord.ui import View, Button
import random

# Configuration
GUILD_ID = 1300093554064097400  # Replace with your guild ID
PING_DEF_CHANNEL_ID = 1307429490158342256  # Replace with your ping channel ID
ALERTE_DEF_CHANNEL_ID = 1300093554399645715  # Replace with your alert channel ID

# Guild emojis with IDs and corresponding role IDs
GUILD_EMOJIS_ROLES = {
    "Darkness": {
        "emoji": "<:Darkness:1307418763276324944>",
        "role_id": 1300093554064097407,
    },
    "GTO": {
        "emoji": "<:GTO:1307418692992237668>",
        "role_id": 1300093554080612363,
    },
    "Aversion": {
        "emoji": "<:aversion:1307418759002198086>",
        "role_id": 1300093554064097409,
    },
    "Bonnebuche": {
        "emoji": "<:bonnebuche:1307418760763670651>",
        "role_id": 1300093554080612365,
    },
    "LMDF": {
        "emoji": "<:lmdf:1307418765142786179>",
        "role_id": 1300093554080612364,
    },
    "Notorious": {
        "emoji": "<:notorious:1307418766266728500>",
        "role_id": 1300093554064097406,
    },
    "Percophile": {
        "emoji": "<:percophile:1307418769764651228>",
        "role_id": 1300093554080612362,
    },
    "Tilisquad": {
        "emoji": "<:tilisquad:1307418771882905600>",
        "role_id": 1300093554080612367,
    },
}

# French alert messages
ALERT_MESSAGES = [
    "🚨 {role} Alerte DEF ! Connectez-vous maintenant !",
    "⚔️ {role}, il est temps de défendre !",
    "🛡️ {role} Défendez votre guilde !",
    "💥 {role} est attaquée ! Rejoignez la défense !",
    "⚠️ {role}, mobilisez votre équipe pour défendre !",
]


class GuildPingView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        for guild_name, data in GUILD_EMOJIS_ROLES.items():
            button = Button(
                label=guild_name,
                emoji=data["emoji"],
                style=discord.ButtonStyle.primary
            )
            button.callback = self.create_ping_callback(guild_name, data["role_id"])
            self.add_item(button)

    def create_ping_callback(self, guild_name, role_id):
        async def callback(interaction: discord.Interaction):
            if interaction.guild_id != GUILD_ID:
                await interaction.response.send_message(
                    "Cette fonction n'est pas disponible sur ce serveur.", ephemeral=True
                )
                return

            alert_channel = interaction.guild.get_channel(ALERTE_DEF_CHANNEL_ID)
            if not alert_channel:
                await interaction.response.send_message("Canal d'alerte introuvable !", ephemeral=True)
                return

            role = interaction.guild.get_role(role_id)
            if not role:
                await interaction.response.send_message(f"Rôle pour {guild_name} introuvable !", ephemeral=True)
                return

            # Choose a random alert message
            alert_message = random.choice(ALERT_MESSAGES).format(role=role.mention)

            # Send alert to the alert channel
            user_avatar = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
            embed = discord.Embed(
                title="🔔 Alerte envoyée !",
                description=f"**{interaction.user.mention}** a déclenché une alerte pour **{guild_name}**.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=user_avatar)
            await alert_channel.send(f"{alert_message}", embed=embed)

            await interaction.response.send_message(
                f"Alerte envoyée à {guild_name} dans le canal d'alerte!", ephemeral=True
            )

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

        # Lock the alert channel to only allow bot messages
        guild = self.bot.get_guild(GUILD_ID)
        alert_channel = guild.get_channel(ALERTE_DEF_CHANNEL_ID)
        if alert_channel:
            await alert_channel.set_permissions(
                guild.default_role,
                send_messages=False,
                add_reactions=False
            )
            print("Alert channel locked successfully.")

        print("Bot is ready, and the panel is ensured.")


async def setup(bot: commands.Bot):
    await bot.add_cog(StartGuildCog(bot))
