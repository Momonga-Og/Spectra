import discord
from discord.ext import commands

class RoleLimiter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ALLOWED_ROLES = {1214430768206450690, 1215669243970981888}
    TARGET_USER_ID = 1079826155751866429
    SERVER_ID = 1214430768143671377
    INFORMATION_CHANNEL_ID = 1214430769192370201

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.guild.id != self.SERVER_ID or after.id != self.TARGET_USER_ID:
            return

        added_roles = set(after.roles) - set(before.roles)

        for role in added_roles:
            if role.id not in self.ALLOWED_ROLES:
                await after.remove_roles(role)
                information_channel = after.guild.get_channel(self.INFORMATION_CHANNEL_ID)
                if information_channel:
                    await information_channel.send(
                        f"{after.mention} is forbidden from taking any roles because they disturb the peace of the server. "
                        f"Role '{role.name}' has been removed."
                    )

async def setup(bot):
    await bot.add_cog(RoleLimiter(bot))
