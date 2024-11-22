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


class NoteModal(Modal):
    def __init__(self, message: discord.Message):
        super().__init__(title="Ajouter une note")
        self.message = message
        self.note_input = TextInput(
            label="Votre note",
            placeholder="Ajoutez des détails ici...",
            max_length=100,
        )
        self.add_item(self.note_input)

    async def on_submit(self, interaction: discord.Interaction):
        embed = self.message.embeds[0] if self.message.embeds else None
        if not embed:
            await interaction.response.send_message("Impossible de récupérer l'embed.", ephemeral=True)
            return

        existing_notes = embed.fields[0].value if embed.fields else "Aucune note."
        updated_notes = f"{existing_notes}\n- **{interaction.user.display_name}**: {self.note_input.value.strip()}"
        embed.set_field_at(0, name="📝 Notes", value=updated_notes, inline=False)

        await self.message.edit(embed=embed)
        await interaction.response.send_message("Note ajoutée !", ephemeral=True)


class AlertView(View):
    def __init__(self, bot: commands.Bot, message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot
        self.message = message

        # Add Note Button
        self.add_note_button = Button(label="Ajouter une note", style=discord.ButtonStyle.secondary, emoji="📝")
        self.add_note_button.callback = self.add_note_callback
        self.add_item(self.add_note_button)

        # "Won" Button
        self.won_button = Button(label="Victoire", style=discord.ButtonStyle.success, emoji="✅")
        self.won_button.callback = self.won_callback
        self.add_item(self.won_button)

        # "Lost" Button
        self.lost_button = Button(label="Défaite", style=discord.ButtonStyle.danger, emoji="❌")
        self.lost_button.callback = self.lost_callback
        self.add_item(self.lost_button)

    async def add_note_callback(self, interaction: discord.Interaction):
        modal = NoteModal(self.message)
        await interaction.response.send_modal(modal)

    async def won_callback(self, interaction: discord.Interaction):
        embed = self.message.embeds[0] if self.message.embeds else None
        if embed:
            updated_description = f"{embed.description}\n- **{interaction.user.display_name}** : 🟢 Victoire"
            embed.description = updated_description
            await self.message.edit(embed=embed)
        await interaction.response.send_message("Marqué comme Victoire !", ephemeral=True)

    async def lost_callback(self, interaction: discord.Interaction):
        embed = self.message.embeds[0] if self.message.embeds else None
        if embed:
            updated_description = f"{embed.description}\n- **{interaction.user.display_name}** : 🔴 Défaite"
            embed.description = updated_description
            await self.message.edit(embed=embed)
        await interaction.response.send_message("Marqué comme Défaite !", ephemeral=True)


class GuildPingView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        for guild_name, data in GUILD_EMOJIS_ROLES.items():
            button = Button(label=f"{guild_name}", emoji=data["emoji"], style=discord.ButtonStyle.primary)
            button.callback = self.create_ping_callback(guild_name, data["role_id"])
            self.add_item(button)

    def create_ping_callback(self, guild_name, role_id):
        async def callback(interaction: discord.Interaction):
            alert_channel = interaction.guild.get_channel(ALERTE_DEF_CHANNEL_ID)
            if not alert_channel:
                await interaction.response.send_message("Canal introuvable !", ephemeral=True)
                return

            role = interaction.guild.get_role(role_id)
            if not role:
                await interaction.response.send_message(f"Rôle pour {guild_name} introuvable !", ephemeral=True)
                return

            alert_message = random.choice(ALERT_MESSAGES).format(role=role.mention)
            embed = discord.Embed(
                title="🔔 Alerte envoyée !",
                description=f"**{interaction.user.mention}** a déclenché une alerte.",
                color=discord.Color.red(),
            )
            embed.add_field(name="📝 Notes", value="Aucune note.", inline=False)

            sent_message = await alert_channel.send(alert_message, embed=embed)
            await sent_message.edit(view=AlertView(self.bot, sent_message))

            await interaction.response.send_message(f"Alerte envoyée !", ephemeral=True)

        return callback


class StartGuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready.")


async def setup(bot: commands.Bot):
    await bot.add_cog(StartGuildCog(bot))
