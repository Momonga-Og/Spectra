import discord
from discord.ext import commands
from discord import app_commands

class SureCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sure", description="Send a message with buttons and an optional image.")
    async def sure(self, interaction: discord.Interaction, message: str, image_url: str = None):
        """
        Command to send a message with customizable buttons and an optional image.
        :param interaction: The interaction object representing the slash command execution.
        :param message: The message content to send.
        :param image_url: (Optional) URL of an image to include in the message.
        """

        class CustomView(discord.ui.View):
            def __init__(self, buttons_config):
                super().__init__()
                for button_config in buttons_config:
                    self.add_item(discord.ui.Button(
                        label=button_config['label'],
                        style=button_config.get('style', discord.ButtonStyle.primary),
                        url=button_config.get('url', None) if button_config.get('url') else None,
                        custom_id=button_config.get('custom_id', None)
                    ))

            @discord.ui.button(label="Default Button", style=discord.ButtonStyle.primary)
            async def default_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.send_message(f"You clicked {button.label}.", ephemeral=True)

        # Example configuration for buttons
        buttons_config = [
            {"label": "Yes", "style": discord.ButtonStyle.green},
            {"label": "No", "style": discord.ButtonStyle.red},
            # Add more buttons as needed here
        ]

        # Create the view with the configured buttons
        view = CustomView(buttons_config)

        # Create an embed if an image is provided
        embed = None
        if image_url:
            embed = discord.Embed(description=message)
            embed.set_image(url=image_url)

        # Send the message
        await interaction.response.send_message(content=message if not embed else None, embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(SureCog(bot))
