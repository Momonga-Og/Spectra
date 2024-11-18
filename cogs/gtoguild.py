import discord
from discord.ext import commands
from discord.ui import View, Button
import random

# Configuration for the second server
SECOND_GUILD_ID = 1234250450681724938  # Server ID
SECOND_PING_DEF_CHANNEL_ID = 1307664199438307382  # Channel for the panel
SECOND_ALERTE_DEF_CHANNEL_ID = 1307778272914051163  # Channel for alerts
SECOND_ROLE_ID = 1234591232328466494  # Role ID to tag
SECOND_EMOJI = "<:alert:1307691528096845905>"  # Emoji ID

# Predefined messages for alerts
ALERT_MESSAGES = [
    "{role_mention} 🚨 **ALERTE !** Votre percepteur est attaqué ! Connectez-vous immédiatement pour défendre.",
    "{role_mention} ⚔️ **Urgent !** Le percepteur est sous attaque. Mobilisez-vous maintenant !",
    "{role_mention} 🛡️ **DEF !** On a besoin de vous pour défendre le percepteur. Rejoignez le jeu !",
    "{role_mention} 🔔 **ATTENTION !** Une attaque sur le percepteur est en cours. Dépêchez-vous !",
    "{role_mention} 🚨 **Alerte critique !** Protégez votre percepteur avant qu’il soit trop tard !",
]


class SecondGuildPingView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

        # Single button for the panel
        button = Button(
            label="CLIQUEZ ICI",
            emoji=SECOND_EMOJI,
            style=discord.ButtonStyle.danger,
            custom_id="alert_button",
        )
        button.callback = self.alert_callback
        self.add_item(button)

    async def alert_callback(self, interaction: discord.Interaction):
        # Check the server
        if interaction.guild_id != SECOND_GUILD_ID:
            await interaction.response.send_message(
                "Cette fonction n'est pas disponible sur ce serveur.", ephemeral=True
            )
            return

        # Get the alert channel and role
        alert_channel = interaction.guild.get_channel(SECOND_ALERTE_DEF_CHANNEL_ID)
        if not alert_channel:
            await interaction.response.send_message(
                "Canal d'alerte introuvable !", ephemeral=True
            )
            return

        role = interaction.guild.get_role(SECOND_ROLE_ID)
        if not role:
            await interaction.response.send_message(
                "Le rôle de défense est introuvable !", ephemeral=True
            )
            return

        # Send a random alert message
        alert_message = random.choice(ALERT_MESSAGES).format(role_mention=role.mention)
        await alert_channel.send(alert_message)

        # Inform the user their click worked
        await interaction.response.send_message(
            f"Alerte envoyée dans le canal d'alerte !", ephemeral=True
        )


class SecondServerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def ensure_panel(self):
        # Ensure we have the guild and channel
        guild = self.bot.get_guild(SECOND_GUILD_ID)
        if not guild:
            print("Guild not found. Check the SECOND_GUILD_ID.")
            return

        channel = guild.get_channel(SECOND_PING_DEF_CHANNEL_ID)
        if not channel:
            print("Ping definition channel not found. Check the SECOND_PING_DEF_CHANNEL_ID.")
            return

        # Create the button panel
        view = SecondGuildPingView(self.bot)
        message_content = (
            "✨ **CLIQUEZ ICI SI VOTRE PERCEPTEUR EST ATTAQUÉ !** ✨\n\n"
            "⚔️ **Unissez-vous pour défendre !** Cliquez sur le bouton ci-dessous : 👇"
        )

        # Check if the panel message already exists and update or create it
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
        print("Bot is ready, and the panel is ensured for the second server.")


async def setup(bot: commands.Bot):
    await bot.add_cog(SecondServerCog(bot))
