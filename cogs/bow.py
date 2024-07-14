import discord
from discord.ext import commands
from discord import app_commands
import re

class ActivityTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="prize", description="Rank people based on their activity (messages, links, media sent).")
    async def prize(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        message_counts = {}
        link_counts = {}
        media_counts = {}

        # Fetch messages from all text channels
        for channel in guild.text_channels:
            async for message in channel.history(limit=None):
                if message.author.bot:
                    continue

                user_id = message.author.id

                # Count messages
                if user_id not in message_counts:
                    message_counts[user_id] = 0
                    link_counts[user_id] = 0
                    media_counts[user_id] = 0

                message_counts[user_id] += 1

                # Count links
                if re.search(r'http[s]?://', message.content):
                    link_counts[user_id] += 1

                # Count media
                if message.attachments:
                    media_counts[user_id] += 1

        # Calculate points and prepare leaderboard
        points = {}
        for user_id in set(message_counts.keys()).union(link_counts.keys()).union(media_counts.keys()):
            points[user_id] = (
                message_counts.get(user_id, 0) +
                link_counts.get(user_id, 0) +
                media_counts.get(user_id, 0)
            )

        leaderboard = sorted(points.items(), key=lambda x: x[1], reverse=True)

        result = "Activity Leaderboard:\n"
        for user_id, point in leaderboard[:10]:  # Top 10 users
            user = guild.get_member(user_id)
            if user:
                result += (f"{user.display_name}: {point} points (Messages: {message_counts.get(user_id, 0)}, "
                           f"Links: {link_counts.get(user_id, 0)}, Media: {media_counts.get(user_id, 0)})\n")

        await interaction.followup.send(result, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ActivityTracker(bot))
