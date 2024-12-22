import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import os
import re

class Alerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channel_id = 1300093554399645715  # Replace with your specific channel ID

    @app_commands.command(name="alert", description="Generate a report of notifications sent in this channel for the last 7 days.")
    async def alert(self, interaction: discord.Interaction):
        # Ensure the command is only used in the specified channel
        if interaction.channel_id != self.allowed_channel_id:
            await interaction.response.send_message("This command can only be used in the designated channel.", ephemeral=True)
            return

        # Get the message history for the last 7 days
        channel = interaction.channel
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)

        # Collect relevant messages asynchronously
        messages = []
        async for message in channel.history(after=seven_days_ago):
            if message.author.bot and (message.mention_everyone or message.role_mentions):
                messages.append(message)

        # Collect notification data
        notification_data = {}
        role_summary = {}  # To track how many times each role was tagged

        for message in messages:
            author = message.author
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            roles_tagged = [role.name for role in message.role_mentions]

            # Extract additional information: attacker and outcome
            attacker_match = re.search(r"Attacker:\s*(\w+)", message.content, re.IGNORECASE)
            outcome_match = re.search(r"Outcome:\s*(Win|Loss)", message.content, re.IGNORECASE)
            attacker = attacker_match.group(1) if attacker_match else "Unknown"
            outcome = outcome_match.group(1) if outcome_match else "Not Specified"

            # Update role summary
            for role in roles_tagged:
                if role not in role_summary:
                    role_summary[role] = 0
                role_summary[role] += 1

            # Initialize data for the author if not already done
            if author.id not in notification_data:
                notification_data[author.id] = {
                    "username": author.name,
                    "notifications": []
                }

            # Append notification details
            notification_data[author.id]["notifications"].append({
                "timestamp": timestamp,
                "roles_tagged": roles_tagged,
                "attacker": attacker,
                "outcome": outcome
            })

        # Generate the report
        report_filename = f"notification_report_{now.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, "w") as report_file:
            if not notification_data:
                report_file.write("No notifications were sent in the last 7 days.\n")
            else:
                for user_id, data in notification_data.items():
                    report_file.write(f"User: {data['username']}\n")
                    report_file.write(f"Total Notifications Sent: {len(data['notifications'])}\n\n")
                    for notification in data["notifications"]:
                        report_file.write(f"  - Timestamp: {notification['timestamp']}\n")
                        report_file.write(f"    Roles Tagged: {', '.join(notification['roles_tagged']) if notification['roles_tagged'] else 'None'}\n")
                        report_file.write(f"    Attacker: {notification['attacker']}\n")
                        report_file.write(f"    Outcome: {notification['outcome']}\n\n")

                # Add role summary to the report
                report_file.write("\nSummary of Role Mentions:\n")
                for role, count in role_summary.items():
                    report_file.write(f"  - {role}: {count} times\n")

        # Notify the user and attach the file
        await interaction.response.send_message("Report generated:", file=discord.File(report_filename), ephemeral=True)

        # Clean up the file after sending
        os.remove(report_filename)

async def setup(bot):
    await bot.add_cog(Alerts(bot))
