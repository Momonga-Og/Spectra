import discord
from discord.ext import commands
from discord import app_commands
import re
import asyncio

class LinkFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_server_id = 1217700740949348443  # Replace with your server ID
        self.approvers = {422092705602994186, 486652069831376943}  # Replace with approver IDs
        self.pending_links = {}  # Store pending links by message ID

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
                f"{message.author.mention}, links are not allowed without approval. Your link is pending approval."
            )

            # Store the original message content
            self.pending_links[message.id] = {
                "author": message.author,
                "content": message.content,
            }

            # Notify approvers privately
            approval_message = await message.channel.send(
                f"A link has been shared by {message.author.mention}. Approvers, please review:",
                view=self.ApprovalView(self, message.id)
            )

    class ApprovalView(discord.ui.View):
        def __init__(self, cog, message_id):
            super().__init__(timeout=3600)  # 1-hour timeout
            self.cog = cog
            self.message_id = message_id

        @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
        async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Ensure the approver has permissions
            if interaction.user.id not in self.cog.approvers:
                await interaction.response.send_message(
                    "You are not authorized to approve links.", ephemeral=True
                )
                return

            pending_data = self.cog.pending_links.get(self.message_id)
            if not pending_data:
                await interaction.response.send_message(
                    "This link is no longer pending approval.", ephemeral=True
                )
                return

            # Repost the approved message
            await interaction.response.send_message(
                f"Approved by {interaction.user.mention}:
{pending_data['author'].mention}: {pending_data['content']}",
                ephemeral=False
            )

            # Clean up pending data
            self.cog.pending_links.pop(self.message_id, None)
            self.stop()

        @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger)
        async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Ensure the denier has permissions
            if interaction.user.id not in self.cog.approvers:
                await interaction.response.send_message(
                    "You are not authorized to deny links.", ephemeral=True
                )
                return

            pending_data = self.cog.pending_links.get(self.message_id)
            if not pending_data:
                await interaction.response.send_message(
                    "This link is no longer pending approval.", ephemeral=True
                )
                return

            # Notify the denial
            await interaction.response.send_message(
                f"The link shared by {pending_data['author'].mention} was denied by {interaction.user.mention}.",
                ephemeral=False
            )

            # Clean up pending data
            self.cog.pending_links.pop(self.message_id, None)
            self.stop()

async def setup(bot):
    await bot.add_cog(LinkFilter(bot))
