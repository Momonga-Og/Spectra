import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
import os

# Define references for each activity
REFERENCES = {
    'Frigost 1': ['1205679923440656384', '1056141573580148776', '1129171675540361218', '486652069831376943'],
    'Frigost 2': ['1205679923440656384', '1056141573580148776', '1129171675540361218', '486652069831376943'],
    'Frigost 3': ['998156191828029441', '966513865343004712', '449753564437413888', '1056141573580148776', '1129171675540361218', '422092705602994186', '876507383411666965'],
    'Pandala': ['998156191828029441', '966513865343004712', '449753564437413888', '1056141573580148776', '1129171675540361218', '422092705602994186', '876507383411666965'],
    'Other Zones': ['1205679923440656384', '1056141573580148776', '1129171675540361218', '486652069831376943'],
    'Quest': ['1205679923440656384', '998156191828029441', '449753564437413888'],
    'Farming': ['960346191734931558', '998156191828029441', '966513865343004712', '1253198915600388217', '977510118495232030', '449753564437413888', '1129171675540361218', '486652069831376943', '1205679923440656384']
}

# Track panel usage and open tickets
panel_usage = {}
open_tickets = {}
banned_users = {}

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
                    "Welcome to the Sparta activity panel! Here you can ask for assistance with various activities:\n\n"
                    "**PVM**\n**Quest**\n**Farming**\n**Mage**\n\n"
                    "Click on the button below for the activity you need help with."
                    "\n\nأهلاً بك في لوحة أنشطة سبارتا! هنا يمكنك طلب المساعدة في مختلف الأنشطة:\n\n"
                    "**PVM**\n**Quest**\n**Farming**\n**Mage**\n\n"
                    "انقر على الزر أدناه للنشاط الذي تحتاج المساعدة فيه."
                )

                # Path to the image (you need to update this with the actual path)
                image_path = "panel_support.png"

                # Create an embed with the description and image
                embed = discord.Embed(
                    title="Sparta Activity Panel",
                    description=description,
                    color=discord.Color.blue()
                )

                # Check if the image file exists
                if os.path.exists(image_path):
                    embed.set_image(url=f"attachment://{image_path.split('/')[-1]}")

                # Create buttons for each activity
                buttons = [
                    discord.ui.Button(label='PVM', custom_id='PVM', style=discord.ButtonStyle.primary),
                    discord.ui.Button(label='Quest', custom_id='Quest', style=discord.ButtonStyle.secondary),
                    discord.ui.Button(label='Farming', custom_id='Farming', style=discord.ButtonStyle.success),
                    discord.ui.Button(label='Mage', custom_id='Mage', style=discord.ButtonStyle.danger)
                ]

                async def button_callback(interaction: discord.Interaction):
                    user_id = interaction.user.id

                    # Check if user is banned
                    if user_id in banned_users and banned_users[user_id] > datetime.now():
                        ban_time_left = banned_users[user_id] - datetime.now()
                        await interaction.response.send_message(
                            f"You are banned from using the panel for {ban_time_left.days} days, {ban_time_left.seconds // 3600} hours.",
                            ephemeral=True
                        )
                        return

                    # Check if user has used the panel in the last 24 hours
                    if user_id in panel_usage and panel_usage[user_id] > datetime.now() - timedelta(days=1):
                        await interaction.response.send_message(
                            "You can only use the panel once every 24 hours.",
                            ephemeral=True
                        )
                        return

                    # Check if user has an open ticket
                    if user_id in open_tickets:
                        await interaction.response.send_message(
                            "You already have an open ticket. Please close it before opening a new one.",
                            ephemeral=True
                        )
                        return

                    activity = interaction.data['custom_id']
                    options = []

                    if activity == 'PVM':
                        options = [
                            discord.SelectOption(label='Frigost 1', value='Frigost 1'),
                            discord.SelectOption(label='Frigost 2', value='Frigost 2'),
                            discord.SelectOption(label='Frigost 3', value='Frigost 3'),
                            discord.SelectOption(label='Pandala', value='Pandala'),
                            discord.SelectOption(label='Other Zones', value='Other Zones')
                        ]

                    if options:
                        select = discord.ui.Select(placeholder="Choose a sub-activity", options=options)
                        select.callback = await self.create_temp_channel_callback(activity, select, interaction)
                        view = discord.ui.View()
                        view.add_item(select)
                        await interaction.response.send_message(view=view, ephemeral=True)
                    else:
                        await self.create_temp_channel(activity, interaction)

                for button in buttons:
                    button.callback = button_callback

                view = discord.ui.View()
                for button in buttons:
                    view.add_item(button)

                if os.path.exists(image_path):
                    message = await channel.send(
                        embed=embed,
                        view=view,
                        file=discord.File(image_path)
                    )
                else:
                    message = await channel.send(
                        embed=embed,
                        view=view
                    )

                self.panel_message_id = message.id

    async def create_temp_channel_callback(self, activity, select, interaction):
        async def callback(select_interaction):
            sub_activity = select_interaction.data['values'][0]
            await self.create_temp_channel(sub_activity, interaction)
            await select_interaction.response.send_message(f"Temporary channel created for {sub_activity}", ephemeral=True)

        return callback

    async def create_temp_channel(self, activity, interaction):
        user_id = interaction.user.id
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Temporary Channels")
        if category is None:
            category = await guild.create_category("Temporary Channels")

        # Create a temporary channel for the activity
        temp_channel = await guild.create_text_channel(
            name=f"{activity}-{interaction.user.display_name}",
            category=category
        )

        # Refer the user to one reference at a time
        references = REFERENCES.get(activity, [])
        referred_user = references[0] if references else None
        mentions = f"<@{referred_user}>" if referred_user else "No references available."

        description = (
            "Here you can contact the referred user for assistance with your request.\n"
            "Please provide detailed information about what you need help with and be patient until they respond. "
            "Avoid creating multiple requests."
            "\n\nيمكنك هنا التواصل مع المستخدم المرجعي للحصول على المساعدة بخصوص طلبك.\n"
            "يرجى تقديم معلومات مفصلة حول ما تحتاجه وانتظر حتى يتم الرد عليك. "
            "تجنب إنشاء طلبات متعددة."
        )

        await temp_channel.send(
            f"{interaction.user.mention}, you have been referred to: {mentions}\n\n{description}"
        )

        panel_usage[user_id] = datetime.now()
        open_tickets[user_id] = temp_channel.id

        await interaction.followup.send(f"Temporary channel created: {temp_channel.mention}", ephemeral=True)

        await self.check_user_response(temp_channel, user_id)

    async def check_user_response(self, channel, user_id):
        def check(m):
            return m.channel == channel and m.author.id == user_id

        try:
            await self.bot.wait_for('message', check=check, timeout=4 * 3600)  # 4 hours
        except asyncio.TimeoutError:
            banned_users[user_id] = datetime.now() + timedelta(days=10)
            await channel.send(f"{channel.guild.get_member(user_id).mention} has been banned from using the panel for 10 days due to inactivity.")

    @app_commands.command(name="close", description="Close the temporary channel.")
    async def close(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if isinstance(interaction.channel.category, discord.CategoryChannel) and interaction.channel.category.name == "Temporary Channels":
            if user_id in open_tickets and open_tickets[user_id] == interaction.channel.id:
                del open_tickets[user_id]
            await interaction.channel.delete()
            await interaction.response.send_message("Channel closed.", ephemeral=True)
        else:
            await interaction.response.send_message("You can only use this command in a temporary channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ActivityPanel(bot))
