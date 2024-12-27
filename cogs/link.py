import discord
from discord.ext import commands
import re

class LinkFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_server_id = 1217700740949348443
        self.approvers = {422092705602994186, 486652069831376943}

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages or messages not in the specified server
        if message.author.bot or message.guild.id != self.allowed_server_id:
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

            # Notify approvers with the link details
            approver_mentions = ' '.join(f'<@{approver_id}>' for approver_id in self.approvers)
            approval_message = await message.channel.send(
                f"{approver_mentions}, a link has been shared by {message.author.mention}:\n"
                f"{message.content}\nReact with \u2705 to approve or \u274c to deny."
            )

            # Add reaction options for approvers
            await approval_message.add_reaction('\u2705')  # Checkmark
            await approval_message.add_reaction('\u274c')  # Crossmark

            def check(reaction, user):
                return (
                    user.id in self.approvers
                    and str(reaction.emoji) in ['\u2705', '\u274c']
                    and reaction.message.id == approval_message.id
                )

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=3600.0, check=check)

                if str(reaction.emoji) == '\u2705':
                    # Approved: repost the original message
                    await message.channel.send(
                        f"Approved by {user.mention}:\n{message.author.mention}: {message.content}"
                    )
                else:
                    # Denied: inform the user
                    await message.channel.send(
                        f"The link shared by {message.author.mention} was denied by {user.mention}."
                    )

            except TimeoutError:
                # Inform if no action is taken within 1 hour
                await message.channel.send(
                    f"The link shared by {message.author.mention} was not reviewed in time and remains denied."
                )

async def setup(bot):
    await bot.add_cog(LinkFilter(bot))
