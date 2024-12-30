import discord
from discord.ext import commands

class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracked_guild_id = 1214430768143671377  # Replace with your server ID
        self.notification_channel_id = 1214430770962239492  # Replace with your notification channel ID
        self.invites = {}

    async def fetch_invites(self):
        guild = self.bot.get_guild(self.tracked_guild_id)
        if guild:
            self.invites = {invite.code: invite for invite in await guild.invites()}

    @commands.Cog.listener()
    async def on_ready(self):
        await self.fetch_invites()
        print(f"Invite tracker is ready and monitoring guild {self.tracked_guild_id}.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != self.tracked_guild_id:
            return

        guild = member.guild
        notification_channel = guild.get_channel(self.notification_channel_id)

        try:
            new_invites = await guild.invites()
            for invite in new_invites:
                if invite.code in self.invites:
                    if invite.uses > self.invites[invite.code].uses:
                        inviter = invite.inviter
                        if notification_channel:
                            await notification_channel.send(f"{member.mention} joined the server using an invite by {inviter.mention}. (Invite Code: {invite.code})")
                        break
            self.invites = {invite.code: invite for invite in new_invites}
        except Exception as e:
            if notification_channel:
                await notification_channel.send(f"An error occurred while tracking invites: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id != self.tracked_guild_id:
            return

        notification_channel = member.guild.get_channel(self.notification_channel_id)
        if notification_channel:
            await notification_channel.send(f"{member.mention} has left the server.")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        if invite.guild.id != self.tracked_guild_id:
            return

        self.invites[invite.code] = invite

        notification_channel = invite.guild.get_channel(self.notification_channel_id)
        if notification_channel:
            await notification_channel.send(f"An invite link was created by {invite.inviter.mention}. (Invite Code: {invite.code})")

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        if invite.guild.id != self.tracked_guild_id:
            return

        if invite.code in self.invites:
            del self.invites[invite.code]

        notification_channel = invite.guild.get_channel(self.notification_channel_id)
        if notification_channel:
            await notification_channel.send(f"An invite link (Code: {invite.code}) was deleted.")

async def setup(bot):
    await bot.add_cog(InviteTracker(bot))
