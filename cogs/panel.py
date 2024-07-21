import discord
from discord.ext import commands
from discord import app_commands
import os

# Define references for each activity
REFERENCES = {
    'PVM': {
        'Frigost 1': ['1205679923440656384', '1056141573580148776', '1129171675540361218', '486652069831376943'],
        'Frigost 2': ['1205679923440656384', '1056141573580148776', '1129171675540361218', '486652069831376943'],
        'Frigost 3': ['998156191828029441', '966513865343004712', '449753564437413888', '1056141573580148776', '1129171675540361218', '422092705602994186', '876507383411666965'],
        'Pandala': ['998156191828029441', '966513865343004712', '449753564437413888', '1056141573580148776', '1129171675540361218', '422092705602994186', '876507383411666965'],
        'Other Zones': ['1205679923440656384', '1056141573580148776', '1129171675540361218', '486652069831376943']
    },
    'Quest': ['1205679923440656384', '998156191828029441', '449753564437413888'],
    'Farming': {
        'Legendary Weapons': ['960346191734931558', '998156191828029441', '966513865343004712', '1253198915600388217', '977510118495232030', '449753564437413888', '1129171675540361218', '486652069831376943', '1205679923440656384'],
        'Dofuses': ['960346191734931558', '998156191828029441', '966513865343004712', '1253198915600388217', '977510118495232030', '449753564437413888', '1129171675540361218', '486652069831376943', '1205679923440656384'],
        'Expensive Resources': ['960346191734931558', '998156191828029441', '966513865343004712', '1253198915600388217', '977510118495232030', '449753564437413888', '1129171675540361218', '486652069831376943', '1205679923440656384']
    },
    'Mage': {
        'EXO PA': ['1079826155751866429'],
        'EXO PM': ['1079826155751866429'],
        'EXO Summ': ['1079826155751866429'],
        'EXO Range': ['1079826155751866429'],
        'EXO Resi': ['1129171675540361218'],
        'Perfect Stats': ['1129171675540361218']
    }
}

class ActivityPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 1214430768143671377
        self.channel_id = 1264143564712050770
        self.panel_message_id = None
        self.post_panel.start()

    def cog_unload(self):
        self.post_panel.cancel()

    @tasks.loop(minutes=10)
    async def post_panel(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(self.guild_id)
        if guild:
            channel = guild.get_channel(self.channel_id)
            if channel:
                if self.panel_message_id:
                    try:
                        old_message = await channel.fetch_message(self.panel_message_id)
                        await old_message.delete()
                    except discord.NotFound:
                        pass

                description = (
                    "Welcome to the Sparta activity panel! Here you can ask and look for whatever you need:\n\n"
                    "**PVM**\n**Quest**\n**Farming**\n\n"
                    "Just click below on whatever suits you and what you are looking for."
                )

                # Path to the image (you need to update this with the actual path)
                image_path = "panel support.png"

                # Create an embed with the description and image
                embed = discord.Embed(description=description, color=discord.Color.blue())
                embed.set_image(url=f"attachment://{image_path.split('/')[-1]}")

        # Create buttons for each activity
        buttons = [
            discord.ui.Button(label='PVM', custom_id='PVM', style=discord.ButtonStyle.primary),
            discord.ui.Button(label='Quest', custom_id='Quest', style=discord.ButtonStyle.secondary),
            discord.ui.Button(label='Farming', custom_id='Farming', style=discord.ButtonStyle.success),
            discord.ui.Button(label='Mage', custom_id='Mage', style=discord.ButtonStyle.danger)
        ]

        async def button_callback(interaction: discord.Interaction):
            activity = interaction.data['custom_id']
            suggestions = REFERENCES[activity]
            if isinstance(suggestions, dict):
                # Create a select menu for sub-activities
                options = [
                    discord.SelectOption(label=sub_activity, value=sub_activity)
                    for sub_activity in suggestions.keys()
                ]
                select = discord.ui.Select(placeholder='Choose a sub-activity', options=options)

                async def select_callback(select_interaction: discord.Interaction):
                    sub_activity = select_interaction.data['values'][0]
                    await self.create_temp_channel(sub_activity, select_interaction, suggestions[sub_activity])

                select.callback = select_callback

                view = discord.ui.View()
                view.add_item(select)
                await interaction.response.send_message(f"Select a sub-activity for {activity}:", view=view, ephemeral=True)
            else:
                await self.create_temp_channel(activity, interaction, suggestions)

        for button in buttons:
            button.callback = button_callback

        view = discord.ui.View()
        for button in buttons:
            view.add_item(button)

        # Delete the old panel message if it exists
        channel = self.bot.get_channel(1264143564712050770)
        async for message in channel.history(limit=100):
            if message.author == self.bot.user:
                await message.delete()

        # Send the new panel message
        if os.path.exists(image_path):
            await channel.send(
                embed=embed,
                view=view,
                file=discord.File(image_path)
            )
        else:
            await channel.send(
                embed=embed,
                view=view
            )

    async def create_temp_channel(self, activity, interaction, references):
        category = discord.utils.get(interaction.guild.categories, name="Temporary Channels")
        if category is None:
            category = await interaction.guild.create_category("Temporary Channels")

        # Create a temporary channel for the activity
        temp_channel = await interaction.guild.create_text_channel(
            name=f"{activity}-{interaction.user.display_name}",
            category=category
        )

        # Mention the references in the new channel
        mentions = " ".join([f"<@{ref_id}>" for ref_id in references])
        description = (
            "Here you can contact the referred users for assistance with your request.\n"
            "Please provide detailed information about what you need help with and be patient until they respond. "
            "Avoid creating multiple requests."
        )
        await temp_channel.send(
            f"{interaction.user.mention}, you have been referred to: {mentions}\n\n{description}"
        )

        await interaction.followup.send(f"Temporary channel created: {temp_channel.mention}", ephemeral=True)

    @app_commands.command(name="close", description="Close the temporary channel.")
    async def close(self, interaction: discord.Interaction):
        if isinstance(interaction.channel.category, discord.CategoryChannel) and interaction.channel.category.name == "Temporary Channels":
            await interaction.channel.delete()
            await interaction.response.send_message("Channel closed.", ephemeral=True)
        else:
            await interaction.response.send_message("You can only use this command in a temporary channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ActivityPanel(bot))
