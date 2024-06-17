import discord
from discord.ext import commands
from discord import app_commands

class WriteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="write", description="Send an anonymous message with an optional image. Only admins can use this command.")
    @app_commands.describe(message="The message to send", image="Optional image to include with the message")
    async def write(self, interaction: discord.Interaction, message: str, image: discord.Attachment = None):
        # Check if the user is an admin
        if interaction.user.guild_permissions.administrator:
            # Defer the response to avoid interaction timeout
            await interaction.response.defer(ephemeral=True)

            # Prepare the message content
            content = message
            files = []

            # Check if an image is provided
            if image:
                # Download the image to a file object
                img_bytes = await image.read()
                img_file = discord.File(fp=img_bytes, filename=image.filename)
                files.append(img_file)

            # Delete the original interaction message
            await interaction.delete_original_response()

            # Send the anonymized message with the optional image
            await interaction.channel.send(content=content, files=files)
        else:
            await interaction.response.send_message("You do not have the necessary permissions to use this command.", ephemeral=True)

    @write.error
    async def write_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You do not have the necessary permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)

async def setup(bot):
    bot.tree.add_command(WriteCog(bot).write)
