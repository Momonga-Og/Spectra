import discord
from discord.ext import commands
from discord import app_commands

class ActivityTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="prize", description="Rank people based on their activity (messages, links, media sent).")
    @app_commands.describe(limit="Number of messages to fetch for analysis (default 1000)")
    async def prize(self, interaction: discord.Interaction, limit: int = 1000):
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        message_counts = {}
        link_counts = {}
        media_counts = {}

        async for message in channel.history(limit=limit):
            if message.author.bot:
                continue

            user_id = message.author.id
            message_counts[user_id] = message_counts.get(user_id, 0) + 1

            if any(url in message.content for url in ['http://', 'https://']):
                link_counts[user_id] = link_counts.get(user_id, 0) + 1

            if message.attachments:
                media_counts[user_id] = media_counts.get(user_id, 0) + 1

        leaderboard = sorted(message_counts.items(), key=lambda x: x[1], reverse=True)

        result = "Activity Leaderboard:\n"
        for user_id, msg_count in leaderboard[:10]:  # Top 10 users
            user = interaction.guild.get_member(user_id)
            link_count = link_counts.get(user_id, 0)
            media_count = media_counts.get(user_id, 0)
            result += (f"{user.display_name}: Messages: {msg_count}, "
                       f"Links: {link_count}, Media: {media_count}\n")

        await interaction.followup.send(result)

async def setup(bot):
    await bot.add_cog(ActivityTracker(bot))
