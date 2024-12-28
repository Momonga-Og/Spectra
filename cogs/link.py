import discord
from discord.ext import commands
import re
import asyncio

class LinkFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_server_id = 1217700740949348443  # Replace with your server ID
        self.approvers = {422092705602994186, 486652069831376943}  # Replace with approver IDs
        self.pending_links = {}  # Store user ID and content temporarily

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages or messages not in the specified server
        if message.author.bot or not message.guild or message.guild.id != self.allowed_server_id:
            return

        # Check if the message contains a link
        url_pattern = re.compile(r"https?://\S+")
        if url_pattern.search(message.content):
            # Hide the message
            await message.delete()

            # Notify the user
            await message.channel.send(
                f"{message.author.mention}, links are not allowed without approval. "
                "Your link is pending approval by the designated approvers."
            )

            # Store the original message for approvers
            self.pending_links[message.id] = {
                "author": message.author,
                "content": message.content,
            }

            # Notify approvers with hidden details
            approval_message = await message.channel.send(
                f"A link has been shared by {message.author.mention}. Approvers, please respond below."
            )

            # Add approval buttons (green and red)
            view = discord.ui.View()
            approve_button = discord.ui.Button(style=discord.ButtonStyle.success, label="Approve")
            deny_button = discord.ui.Button(style=discord.ButtonStyle.danger, label="Deny")

            async def approve_callback(interaction: discord.Interaction):
                if interaction.user.id in self.approvers:
                    await interaction.response.send_message(
                        f"Approved by {interaction.user.mention}:
"
                        f"{message.author.mention}: {self.pending_links[message.id]['content']}",
                        ephemeral=False
                    )
                    self.pending_links.pop(message.id, None)
                    view.stop()
                else:
                    await interaction.response.send_message(
                        "You do not have permission to approve links.", ephemeral=True
                    )

            async def deny_callback(interaction: discord.Interaction):
                if interaction.user.id in self.approvers:
                    await interaction.response.send_message(
                        f"The link shared by {message.author.mention} was denied.", ephemeral=False
                    )
                    self.pending_links.pop(message.id, None)
                    view.stop()
                else:
                    await interaction.response.send_message(
                        "You do not have permission to deny links.", ephemeral=True
                    )

            approve_button.callback = approve_callback
            deny_button.callback = deny_callback
            view.add_item(approve_button)
            view.add_item(deny_button)

            await approval_message.edit(view=view)

async def setup(bot):
    await bot.add_cog(LinkFilter(bot))
