import discord
from discord.ext import commands
from discord import app_commands

# Define references for each activity
REFERENCES = {
    'Crafting': ['486652069831376943'],
    'Maging': ['1129171675540361218', '1079826155751866429'],
    'Hunting': ['1056141573580148776', '1205679923440656384', '449753564437413888'],
    'Dropping': ['1056141573580148776', '1205679923440656384', '449753564437413888'],
    'Perco Attack': ['876507383411666965', '422092705602994186', '998156191828029441', '966513865343004712'],
    'Frigost 3 Passage': ['876507383411666965']
}

class ActivityPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="panel", description="Show the Sparta activity panel.")
    async def panel(self, interaction: discord.Interaction):
        description = (
            "Hello to Sparta panel here you can ask and look for whatever you want.\n"
            "Crafting. Maging. Hunting. Dropping. Attacking Other Perco. And Frigost 3 Passage\n"
            "Just click below on whatever suits you and what you are looking for."
        )

        # Path to the image (you need to update this with the actual path)
        image_path = "panel support.png"

        # Create an embed with the description and image
        embed = discord.Embed(description=description)
        embed.set_image(url=f"attachment://{image_path.split('/')[-1]}")

        # Create buttons for each activity
        buttons = []
        for activity in REFERENCES.keys():
            buttons.append(discord.ui.Button(label=activity, custom_id=activity))

        async def button_callback(interaction: discord.Interaction):
            activity = interaction.data['custom_id']
            category = discord.utils.get(interaction.guild.categories, name="Temporary Channels")
            if category is None:
                category = await interaction.guild.create_category("Temporary Channels")

            # Create a temporary channel for the activity
            temp_channel = await interaction.guild.create_text_channel(
                name=f"{activity}-{interaction.user.display_name}",
                category=category
            )

            # Mention the references in the new channel
            references = REFERENCES[activity]
            mentions = " ".join([f"<@{ref_id}>" for ref_id in references])
            await temp_channel.send(f"{interaction.user.mention}, you have been referred to: {mentions}")

            await interaction.response.send_message(f"Temporary channel created: {temp_channel.mention}", ephemeral=True)

        for button in buttons:
            button.callback = button_callback

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Crafting", custom_id="Crafting"))
        view.add_item(discord.ui.Button(label="Maging", custom_id="Maging"))
        view.add_item(discord.ui.Button(label="Hunting", custom_id="Hunting"))
        view.add_item(discord.ui.Button(label="Dropping", custom_id="Dropping"))
        view.add_item(discord.ui.Button(label="Perco Attack", custom_id="Perco Attack"))
        view.add_item(discord.ui.Button(label="Frigost 3 Passage", custom_id="Frigost 3 Passage"))

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=False,
            file=discord.File(image_path)
        )

    @app_commands.command(name="close", description="Close the temporary channel.")
    async def close(self, interaction: discord.Interaction):
        if isinstance(interaction.channel.category, discord.CategoryChannel) and interaction.channel.category.name == "Temporary Channels":
            await interaction.channel.delete()
            await interaction.response.send_message("Channel closed.", ephemeral=True)
        else:
            await interaction.response.send_message("You can only use this command in a temporary channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ActivityPanel(bot))
