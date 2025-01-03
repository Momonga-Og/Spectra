import discord
from discord.ext import commands

class LogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    TARGET_USER_ID = 486652069831376943
    TARGET_SERVER_ID = 1214430768143671377

    def format_audit_log_entry(self, entry):
        """Format an audit log entry for reporting."""
        return (
            f"Action: {entry.action}\n"
            f"User: {entry.user} (ID: {entry.user.id})\n"
            f"Target: {entry.target}\n"
            f"Reason: {entry.reason}\n"
            f"Extra: {entry.extra}\n"
            f"Created At: {entry.created_at}"
        )

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if after.id == self.TARGET_SERVER_ID:
            user = self.bot.get_user(self.TARGET_USER_ID)
            if user:
                await user.send(f"Guild updated: {before.name} -> {after.name}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.guild.id == self.TARGET_SERVER_ID:
            user = self.bot.get_user(self.TARGET_USER_ID)
            if user:
                changes = []
                if before.roles != after.roles:
                    added_roles = set(after.roles) - set(before.roles)
                    removed_roles = set(before.roles) - set(after.roles)
                    if added_roles:
                        changes.append(f"Roles added: {', '.join(role.name for role in added_roles)}")
                    if removed_roles:
                        changes.append(f"Roles removed: {', '.join(role.name for role in removed_roles)}")
                if before.nick != after.nick:
                    changes.append(f"Nickname changed: {before.nick} -> {after.nick}")
                if changes:
                    await user.send(f"Member update for {after} (ID: {after.id}):\n" + "\n".join(changes))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id == self.TARGET_SERVER_ID:
            user = self.bot.get_user(self.TARGET_USER_ID)
            if user:
                changes = []
                if before.channel != after.channel:
                    changes.append(f"Channel: {before.channel} -> {after.channel}")
                if before.mute != after.mute:
                    changes.append(f"Mute: {before.mute} -> {after.mute}")
                if before.deaf != after.deaf:
                    changes.append(f"Deaf: {before.deaf} -> {after.deaf}")
                if changes:
                    await user.send(f"Voice state update for {member} (ID: {member.id}):\n" + "\n".join(changes))

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild.id == self.TARGET_SERVER_ID:
            user = self.bot.get_user(self.TARGET_USER_ID)
            if user:
                await user.send(f"Message deleted in {message.channel}: {message.content}")

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if before.guild.id == self.TARGET_SERVER_ID:
            user = self.bot.get_user(self.TARGET_USER_ID)
            if user:
                changes = []
                if before.name != after.name:
                    changes.append(f"Role name changed: {before.name} -> {after.name}")
                if before.permissions != after.permissions:
                    changes.append("Role permissions updated.")
                if changes:
                    await user.send(f"Role update: {before} (ID: {before.id}):\n" + "\n".join(changes))

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry):
        if entry.guild.id == self.TARGET_SERVER_ID:
            user = self.bot.get_user(self.TARGET_USER_ID)
            if user:
                formatted_entry = self.format_audit_log_entry(entry)
                await user.send(f"Audit log entry created:\n{formatted_entry}")

async def setup(bot):
    await bot.add_cog(LogCog(bot))

