import discord
from discord.ext import commands
from discord.ui import View, Button
from io import BytesIO

class PercoAttack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots or messages without attachments
        if message.author.bot or not message.attachments:
            return

        # Check if the message is sent in the specific channel
        if message.channel.id == 1300093554797842523:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    try:
                        # Attempt to download the image
                        image_data = await attachment.read()
                        image_file = BytesIO(image_data)
                        image_file.seek(0)

                        # Create a button for this specific image
                        view = PercoView()
                        file = discord.File(fp=image_file, filename=attachment.filename)
                        reposted_message = await message.channel.send(
                            file=file,
                            content=f"{message.author.mention} a posté une image :",
                            view=view
                        )

                        # Associate the button with the reposted message
                        view.set_message(reposted_message)

                    except discord.errors.NotFound:
                        await message.channel.send(
                            f"Erreur : Impossible de télécharger l'image `{attachment.filename}`. Lien non valide ou expiré.",
                            delete_after=10
                        )
            # Delete the user's original message
            await message.delete()

class PercoView(View):
    def __init__(self):
        super().__init__()
        self.message = None  # To store the message this view is attached to

    def set_message(self, message):
        """Associate this view with a specific message."""
        self.message = message

    @discord.ui.button(label="Réclamé", style=discord.ButtonStyle.green)
    async def claimed_button(self, interaction: discord.Interaction, button: Button):
        # Disable the button after it is clicked
        button.label = "Réclamé ✔"
        button.disabled = True
        await interaction.response.send_message(f"{interaction.user.mention} a réclamé le perco.", ephemeral=False)
        await interaction.message.edit(view=self)  # Update the view to disable the button

# Set up the cog
async def setup(bot):
    await bot.add_cog(PercoAttack(bot))
