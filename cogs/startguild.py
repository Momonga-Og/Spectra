import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import random

# Configuration
GUILD_ID = 1300093554064097400  # Replace with your guild ID
PING_DEF_CHANNEL_ID = 1307429490158342256  # Replace with your ping channel ID
ALERTE_DEF_CHANNEL_ID = 1300093554399645715  # Replace with your alert channel ID

# Guild emojis with IDs and corresponding role IDs
GUILD_EMOJIS_ROLES = {
    "Darkness": {"emoji": "<:Darkness:1307418763276324944>", "role_id": 1300093554064097407},
    "GTO": {"emoji": "<:GTO:1307418692992237668>", "role_id": 1300093554080612363},
    "Aversion": {"emoji": "<:aversion:1307418759002198086>", "role_id": 1300093554064097409},
    "Bonnebuche": {"emoji": "<:bonnebuche:1307418760763670651>", "role_id": 1300093554080612365},
    "LMDF": {"emoji": "<:lmdf:1307418765142786179>", "role_id": 1300093554080612364},
    "Notorious": {"emoji": "<:notorious:1307418766266728500>", "role_id": 1300093554064097406},
    "Percophile": {"emoji": "<:percophile:1307418769764651228>", "role_id": 1300093554080612362},
    "Tilisquad": {"emoji": "<:tilisquad:1307418771882905600>", "role_id": 1300093554080612367},
}

# French alert messages
ALERT_MESSAGES = [
    "🚨 {role} Alerte DEF ! Connectez-vous maintenant !",
    "⚔️ {role}, il est temps de défendre !",
    "🛡️ {role} Défendez votre guilde !",
    "💥 {role} est attaquée ! Rejoignez la défense !",
    "⚠️ {role}, mobilisez votre équipe pour défendre !",
]

class ConfirmationModal(Modal):
    def __init__(self, guild_name, role_id, interaction, callback):
        super().__init__(title="Confirmer l'alerte")
        self.guild_name = guild_name
        self.role_id = role_id
        self.interaction = interaction
        self.callback = callback

        self.confirmation_input = TextInput(
            label="Confirmation",
            placeholder="Tapez CONFIRMER pour continuer",
            max_length=10,
            style=discord.TextStyle.short,
        )
        self.add_item(self.confirmation_input)

    async def on_submit(self, interaction: discord.Interaction):
        if self.confirmation_input.value.strip().upper() == "CONFIRMER":
            await self.callback(self.interaction, self.guild_name, self.role_id)
        else:
            await interaction.response.send_message("Confirmation échouée. Action annulée.", ephemeral=True)

class NoteModal(Modal):
    def __init__(self, message: discord.Message):
        super().__init__(title="Ajouter une note")
        self.message = message

        self.note_input = TextInput(
            label="Votre note",
            placeholder="Ajoutez des détails sur l'alerte (nom de la guilde attaquante, heure, etc.)",
            max_length=100,
            style=discord.TextStyle.paragraph,
        )
        self.add_item(self.note_input)

    async def on_submit(self, interaction: discord.Interaction):
        embed = self.message.embeds[0] if self.message.embeds else None
        if not embed:
            await interaction.response.send_message("Impossible de récupérer l'embed à modifier.", ephemeral=True)
            return

        existing_notes = embed.fields[0].value if embed.fields else "Aucune note."
        updated_notes = f"{existing_notes}\n- **{interaction.user.display_name}**: {self.note_input.value.strip()}"
        embed.clear_fields()
        embed.add_field(name="📝 Notes", value=updated_notes, inline=False)

        await self.message.edit(embed=embed)
        await interaction.response.send_message("Votre note a été ajoutée avec succès !", ephemeral=True)

class AlertActionView(View):
    def __init__(self, bot: commands.Bot, message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot
        self.message = message
        self.is_locked = False

        self.add_note_button = Button(
            label="Ajouter une note",
            style=discord.ButtonStyle.secondary,
            emoji="📝"
        )
        self.add_note_button.callback = self.add_note_callback
        self.add_item(self.add_note_button)

        self.won_button = Button(
            label="Won",
            style=discord.ButtonStyle.success,
        )
        self.won_button.callback = self.mark_as_won
        self.add_item(self.won_button)

        self.lost_button = Button(
            label="Lost",
            style=discord.ButtonStyle.danger,
        )
        self.lost_button.callback = self.mark_as_lost
        self.add_item(self.lost_button)

    async def add_note_callback(self, interaction: discord.Interaction):
        if interaction.channel_id != ALERTE_DEF_CHANNEL_ID:
            await interaction.response.send_message("Vous ne pouvez pas ajouter de note ici.", ephemeral=True)
            return

        modal = NoteModal(self.message)
        await interaction.response.send_modal(modal)

    async def mark_as_won(self, interaction: discord.Interaction):
        await self.mark_alert(interaction, "Gagnée", discord.Color.green())

    async def mark_as_lost(self, interaction: discord.Interaction):
        await self.mark_alert(interaction, "Perdue", discord.Color.red())

    async def mark_alert(self, interaction: discord.Interaction, status: str, color: discord.Color):
        if self.is_locked:
            await interaction.response.send_message("Cette alerte a déjà été marquée.", ephemeral=True)
            return

        self.is_locked = True
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

        embed = self.message.embeds[0]
        embed.color = color
        embed.add_field(name="Statut", value=f"L'alerte a été marquée comme **{status}** par {interaction.user.mention}.", inline=False)

        await self.message.edit(embed=embed)
        await interaction.response.send_message(f"Alerte marquée comme **{status}** avec succès.", ephemeral=True)

class GuildPingView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        for guild_name, data in GUILD_EMOJIS_ROLES.items():
            button = Button(
                label=f"  {guild_name.upper()}  ",
                emoji=data["emoji"],
                style=discord.ButtonStyle.primary
            )
            button.callback = self.create_confirmation_callback(guild_name, data["role_id"])
            self.add_item(button)

    def create_confirmation_callback(self, guild_name, role_id):
        async def callback(interaction: discord.Interaction):
            modal = ConfirmationModal(guild_name, role_id, interaction, self.send_alert)
            await interaction.response.send_modal(modal)

        return callback

    async def send_alert(self, interaction: discord.Interaction, guild_name, role_id):
        try:
            if interaction.guild_id != GUILD_ID:
                await interaction.response.send_message(
                    "Cette fonction n'est pas disponible sur ce serveur.", ephemeral=True
                )
                return

            alert_channel = interaction.guild.get_channel(ALERTE_DEF_CHANNEL_ID)
            if not alert_channel:
                await interaction.response.send_message("Canal d'alerte introuvable !", ephemeral=True)
                return

            role = interaction.guild.get_role(role_id)
            if not role:
                await interaction.response.send_message(f"Rôle pour {guild_name} introuvable !", ephemeral=True)
                return

            alert_message = random.choice(ALERT_MESSAGES).format(role=role.mention)
            embed = discord.Embed(
                title="🔔 Alerte envoyée !",
                description=f"**{interaction.user.mention}** a déclenché une alerte pour **{guild_name}**.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            embed.add_field(name="📝 Notes", value="Aucune note.", inline=False)

            sent_message = await alert_channel.send(content=alert_message, embed=embed)
            view = AlertActionView(self.bot, sent_message)
            await sent_message.edit(view=view)

            await interaction.followup.send(
                f"Alerte envoyée à {guild_name} dans le canal d'alerte !", ephemeral=True
            )

        except Exception as e:
            print(f"Error in ping callback for {guild_name}: {e}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

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
        message_content = (
            "**🎯 Panneau d'Alerte DEF**\n\n"
            "Bienvenue sur le Panneau d'Alerte Défense ! Cliquez sur le bouton de votre guilde ci-dessous pour envoyer une alerte à votre équipe. "
            "Chaque bouton correspond à une guilde, et le fait d'appuyer dessus notifiera tous les membres associés à cette guilde.\n\n"
            "💡 **Comment l'utiliser :**\n"
            "1️⃣ Cliquez sur le bouton de votre guilde.\n"
            "2️⃣ Une confirmation vous sera demandée.\n"
            "3️⃣ Vérifiez le canal d'alerte pour les mises à jour.\n"
            "4️⃣ Ajoutez des notes aux alertes si nécessaire.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⬇️ **Guildes Disponibles** ⬇️\n"
        )

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

        guild = self.bot.get_guild(GUILD_ID)
        alert_channel = guild.get_channel(ALERTE_DEF_CHANNEL_ID)
        if alert_channel:
            await alert_channel.set_permissions(
                guild.default_role, send_messages=False, add_reactions=False
            )
            print("Alert channel permissions updated.")

        print("Bot is ready.")

async def setup(bot: commands.Bot):
    await bot.add_cog(StartGuildCog(bot))
