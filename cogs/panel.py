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

MAGING_REFS = {
    'Exo Pa': '1079826155751866429',
    'Exo Pm': '1079826155751866429',
    'Other': '1129171675540361218'
}

ITEMS = ["Cap", "Hat", "Boots", "Ring", "Amu", "Belt", "Weapon", "Other"]
MAGE_TYPES = ["Perfect Mage", "Exo Pa", "Exo Pm", "Exo Resi", "Exo Summ", "Exo Range", "Over element", "Other"]

class ActivityPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="panel", description="Show the Sparta activity panel.")
    async def panel(self, interaction: discord.Interaction):
        description = (
            "Hello to Sparta panel! Here you can ask and look for whatever you need:\n\n"
            "**Crafting**\n**Maging**\n**Hunting**\n**Dropping**\n**Perco Attack**\n**Frigost 3 Passage**\n\n"
            "Just click below on whatever suits you and what you are looking for."
        )

        # Path to the image (you need to update this with the actual path)
        image_path = "panel support.png"

        # Create an embed with the description and image
        embed = discord.Embed(description=description, color=discord.Color.blue())
        embed.set_image(url=f"attachment://{image_path.split('/')[-1]}")

        # Create buttons for each activity
        buttons = [
            discord.ui.Button(label='Crafting', custom_id='Crafting', style=discord.ButtonStyle.primary),
            discord.ui.Button(label='Maging', custom_id='Maging', style=discord.ButtonStyle.secondary),
            discord.ui.Button(label='Hunting', custom_id='Hunting', style=discord.ButtonStyle.success),
            discord.ui.Button(label='Dropping', custom_id='Dropping', style=discord.ButtonStyle.danger),
            discord.ui.Button(label='Perco Attack', custom_id='Perco Attack', style=discord.ButtonStyle.primary),
            discord.ui.Button(label='Frigost 3 Passage', custom_id='Frigost 3 Passage', style=discord.ButtonStyle.secondary)
        ]

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

            if activity == 'Maging':
                await ask_maging_questions(temp_channel, interaction.user)
            else:
                # Mention the references in the new channel
                references = REFERENCES[activity]
                mentions = " ".join([f"<@{ref_id}>" for ref_id in references])
                await temp_channel.send(f"{interaction.user.mention}, you have been referred to: {mentions}")

                await interaction.response.send_message(f"Temporary channel created: {temp_channel.mention}", ephemeral=True)

        for button in buttons:
            button.callback = button_callback

        view = discord.ui.View()
        for button in buttons:
            view.add_item(button)

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

async def ask_maging_questions(channel, user):
    class ItemSelect(discord.ui.Select):
        def __init__(self):
            options = [discord.SelectOption(label=item) for item in ITEMS]
            super().__init__(placeholder="What Item you want to Mage?", min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            selected_item = self.values[0]
            await interaction.response.send_message(f"You selected {selected_item}. Next question coming up...", ephemeral=True)
            await ask_mage_type_questions(channel, user, selected_item)

    view = discord.ui.View()
    view.add_item(ItemSelect())
    await channel.send(f"{user.mention}, what item do you want to mage?", view=view)

async def ask_mage_type_questions(channel, user, item):
    class MageTypeSelect(discord.ui.Select):
        def __init__(self):
            options = [discord.SelectOption(label=mage_type) for mage_type in MAGE_TYPES]
            super().__init__(placeholder="What Type Of Maging You want?", min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            selected_mage_type = self.values[0]
            await refer_user_to_expert(channel, user, item, selected_mage_type)

    view = discord.ui.View()
    view.add_item(MageTypeSelect())
    await channel.send(f"{user.mention}, what type of maging do you want?", view=view)

async def refer_user_to_expert(channel, user, item, mage_type):
    if mage_type in ['Exo Pa', 'Exo Pm']:
        ref_id = MAGING_REFS['Exo Pa']
    else:
        ref_id = MAGING_REFS['Other']

    await channel.send(f"{user.mention} wants to mage a {item} and mage {mage_type}. You have been referred to: <@{ref_id}>")

async def setup(bot):
    await bot.add_cog(ActivityPanel(bot))
